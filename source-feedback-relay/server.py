#!/usr/bin/env python3
"""Receive privacy-safe job-source suggestions and forward them to one Feishu chat."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


MAX_BODY = 8 * 1024
ALLOWED_FIELDS = {"schema_version", "name", "url", "intro", "note", "fingerprint", "submitted_at"}
REQUESTS_BY_IP: dict[str, list[float]] = {}
TOKEN_CACHE = {"value": "", "expires_at": 0.0}


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"缺少环境变量：{name}")
    return value


def validate(payload: object) -> dict:
    if not isinstance(payload, dict) or set(payload) - ALLOWED_FIELDS:
        raise ValueError("请求只能包含网站建议字段")
    name = str(payload.get("name") or "").strip()
    url = str(payload.get("url") or "").strip()
    intro = str(payload.get("intro") or "").strip()
    note = str(payload.get("note") or "").strip()
    parsed = urlparse(url)
    if not name or len(name) > 80:
        raise ValueError("网站名称必须为 1–80 个字符")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or len(url) > 2048:
        raise ValueError("网站 URL 无效")
    if len(intro) > 300 or len(note) > 300:
        raise ValueError("简介和备注均不能超过 300 个字符")
    return {"name": name, "url": url, "intro": intro, "note": note}


def rate_limited(ip: str, now: float | None = None) -> bool:
    now = now or time.time()
    # ponytail: 单实例内存限流；出现多副本或真实滥用时换成共享边缘限流。
    recent = [stamp for stamp in REQUESTS_BY_IP.get(ip, []) if now - stamp < 3600]
    if len(recent) >= 10:
        REQUESTS_BY_IP[ip] = recent
        return True
    REQUESTS_BY_IP[ip] = recent + [now]
    return False


def request_json(url: str, body: dict, headers: dict | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"飞书请求失败：HTTP {error.code}") from error


def tenant_token() -> str:
    if TOKEN_CACHE["value"] and TOKEN_CACHE["expires_at"] > time.time() + 60:
        return str(TOKEN_CACHE["value"])
    result = request_json(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        {"app_id": required_env("FEISHU_APP_ID"), "app_secret": required_env("FEISHU_APP_SECRET")},
    )
    token = str(result.get("tenant_access_token") or "")
    if not token:
        raise RuntimeError("无法取得飞书机器人凭据")
    TOKEN_CACHE.update(value=token, expires_at=time.time() + int(result.get("expire") or 7200))
    return token


def message_content(item: dict) -> dict:
    rows = [[{"tag": "text", "text": f"网站：{item['name']}"}], [
        {"tag": "text", "text": "链接："},
        {"tag": "a", "href": item["url"], "text": item["url"]},
    ]]
    if item["intro"]:
        rows.append([{"tag": "text", "text": f"简介：{item['intro']}"}])
    if item["note"]:
        rows.append([{"tag": "text", "text": f"推荐理由：{item['note']}"}])
    rows.append([{"tag": "text", "text": "来源：泛函求职 Skill 用户授权分享；未包含候选人资料。"}])
    return {"zh_cn": {"title": "新岗位来源建议", "content": rows}}


def send_to_feishu(item: dict, fingerprint: str) -> str:
    result = request_json(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        {
            "receive_id": required_env("FEISHU_SOURCE_CHAT_ID"),
            "msg_type": "post",
            "content": json.dumps(message_content(item), ensure_ascii=False),
            "uuid": fingerprint[:50],
        },
        {"Authorization": f"Bearer {tenant_token()}"},
    )
    if result.get("code") != 0:
        raise RuntimeError(f"飞书发送失败：{result.get('msg') or 'unknown'}")
    return str(result.get("data", {}).get("message_id") or "")


class Handler(BaseHTTPRequestHandler):
    def reply(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        self.reply(200, {"ok": True}) if self.path == "/healthz" else self.reply(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/source-feedback":
            self.reply(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_BODY:
            self.reply(413, {"error": "invalid_body_size"})
            return
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if rate_limited(ip):
            self.reply(429, {"error": "rate_limited"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
            item = validate(payload)
            message_id = send_to_feishu(item, str(payload.get("fingerprint") or item["url"]))
            self.reply(200, {"ok": True, "delivery_status": "sent", "message_id": message_id})
        except (ValueError, json.JSONDecodeError) as error:
            self.reply(400, {"error": str(error)})
        except Exception:
            self.reply(502, {"error": "feishu_delivery_failed"})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def self_test() -> None:
    item = validate({"name": "AI Jobs", "url": "https://jobs.example", "intro": "AI 岗位", "note": "小众高质量"})
    content = message_content(item)
    assert content["zh_cn"]["title"] == "新岗位来源建议"
    assert "候选人资料" in content["zh_cn"]["content"][-1][0]["text"]
    try:
        validate({"name": "x", "url": "javascript:alert(1)", "candidate_name": "不应接收"})
        raise AssertionError("不可信字段应被拒绝")
    except ValueError:
        pass
    REQUESTS_BY_IP.clear()
    assert not any(rate_limited("127.0.0.1", now=1) for _ in range(10))
    assert rate_limited("127.0.0.1", now=1)
    print("source feedback relay self-test: ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
