#!/usr/bin/env python3
"""Validate an evidence-backed proposal and render a job-specific review copy."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import tempfile
import unicodedata
from pathlib import Path


FACT_CHANGES = {"fact_addition", "fact_change"}
CHANGE_TYPES = FACT_CHANGES | {"rewrite", "reorder"}
ARTIFACT_STEM = re.compile(r"^.+-\d{8}-v[1-9]\d*$")


def required_text(value: object, field: str) -> str:
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field} 不能为空")
    return value


def string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} 必须是非空字符串数组")
    return [required_text(item, field) for item in value]


def resume_path(profile: dict, profile_path: Path) -> Path:
    value = required_text(profile.get("resume", {}).get("path"), "profile.resume.path")
    path = Path(value).expanduser()
    return path if path.is_absolute() else profile_path.parent / path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filename_part(value: object, field: str) -> str:
    value = unicodedata.normalize("NFKC", required_text(value, field))
    value = re.sub(r"\s+", "", value)
    value = re.sub(r'[\\/:*?"<>|]+', "-", value).strip("-.")
    return required_text(value, field)


def expected_artifact_prefix(profile: dict, proposal: dict) -> str:
    return "-".join([
        filename_part(profile.get("identity", {}).get("name"), "profile.identity.name"),
        filename_part(proposal.get("job", {}).get("company"), "job.company"),
        filename_part(proposal.get("job", {}).get("title"), "job.title"),
    ]) + "-"


def validate(profile: dict, proposal: dict) -> tuple[list[dict], list[dict]]:
    if profile.get("schema_version") != "fanhan-career-profile-v1":
        raise ValueError("profile.schema_version 必须是 fanhan-career-profile-v1")
    if proposal.get("schema_version") != "fanhan-tailored-material-v1":
        raise ValueError("proposal.schema_version 必须是 fanhan-tailored-material-v1")

    job = proposal.get("job", {})
    required_text(job.get("id"), "job.id")
    required_text(job.get("company"), "job.company")
    required_text(job.get("title"), "job.title")
    artifact_stem = required_text(proposal.get("artifact_stem"), "artifact_stem")
    if not ARTIFACT_STEM.fullmatch(artifact_stem) or not artifact_stem.startswith(expected_artifact_prefix(profile, proposal)):
        raise ValueError("artifact_stem 必须按 姓名-目标公司-目标岗位-YYYYMMDD-vN 命名")

    sections = proposal.get("sections")
    changes = proposal.get("changes")
    if not isinstance(sections, list) or not sections:
        raise ValueError("sections 必须是非空数组")
    if not isinstance(changes, list) or not changes:
        raise ValueError("changes 必须是非空数组")

    change_by_id = {}
    for index, change in enumerate(changes):
        change_id = required_text(change.get("id"), f"changes[{index}].id")
        if change_id in change_by_id:
            raise ValueError(f"重复的 change id：{change_id}")
        change_type = change.get("type")
        if change_type not in CHANGE_TYPES:
            raise ValueError(f"{change_id}.type 必须是 {sorted(CHANGE_TYPES)} 之一")
        required_text(change.get("summary"), f"{change_id}.summary")
        string_list(change.get("jd_basis"), f"{change_id}.jd_basis")
        string_list(change.get("fact_evidence"), f"{change_id}.fact_evidence")
        confirmation = change.get("confirmation")
        if change_type in FACT_CHANGES and confirmation != "confirmed":
            raise ValueError(f"事实变更 {change_id} 未经候选人确认")
        if confirmation == "confirmed":
            required_text(change.get("confirmed_at"), f"{change_id}.confirmed_at")
        elif change_type not in FACT_CHANGES and confirmation != "not_required":
            raise ValueError(f"非事实变更 {change_id}.confirmation 必须是 not_required")
        change_by_id[change_id] = change

    referenced = set()
    for index, section in enumerate(sections):
        required_text(section.get("heading"), f"sections[{index}].heading")
        required_text(section.get("content"), f"sections[{index}].content")
        ids = string_list(section.get("change_ids"), f"sections[{index}].change_ids")
        missing = [item for item in ids if item not in change_by_id]
        if missing:
            raise ValueError(f"sections[{index}] 引用了未知变更：{missing}")
        referenced.update(ids)
    unreferenced = set(change_by_id) - referenced
    if unreferenced:
        raise ValueError(f"存在未进入成稿的变更：{sorted(unreferenced)}")
    return sections, changes


def render_markdown(job: dict, sections: list[dict], changes: list[dict]) -> str:
    lines = [f"# {job['company']}｜{job['title']}｜定制申请材料", "", f"岗位 ID：`{job['id']}`", ""]
    for section in sections:
        lines.extend([f"## {section['heading']}", "", section["content"].strip(), ""])
    lines.extend(["## JD 依据与变更记录", ""])
    for change in changes:
        lines.extend([
            f"### {change['id']}｜{change['summary']}", "",
            f"- 类型：`{change['type']}`",
            f"- JD 依据：{'；'.join(change['jd_basis'])}",
            f"- 事实证据：{'；'.join(change['fact_evidence'])}",
            f"- 候选人确认：{change['confirmation']}", "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def render_html(title: str, sections: list[dict]) -> str:
    body = []
    for section in sections:
        content = "<br>".join(html.escape(section["content"].strip()).splitlines())
        body.append(f"<section><h2>{html.escape(section['heading'])}</h2><p>{content}</p></section>")
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
@page{{size:A4;margin:14mm}}*{{box-sizing:border-box}}body{{margin:0;background:#eee;color:#222;font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.toolbar{{position:sticky;top:0;padding:10px;text-align:right;background:#fff;border-bottom:1px solid #ddd}}button{{padding:8px 14px;border:0;border-radius:6px;background:#1769e0;color:#fff;cursor:pointer}}main{{width:210mm;min-height:297mm;margin:16px auto;padding:14mm;background:#fff;box-shadow:0 2px 14px #bbb}}h2{{font-size:16px;border-bottom:1px solid #ddd;padding-bottom:4px}}p{{white-space:normal}}@media print{{body{{background:#fff}}.toolbar{{display:none}}main{{margin:0;padding:0;box-shadow:none;width:auto;min-height:auto}}}}
</style></head><body><div class="toolbar"><button type="button" onclick="window.print()">导出 PDF</button></div>
<main contenteditable="true" spellcheck="false">{''.join(body)}</main></body></html>
"""


def render(profile_path: Path, proposal_path: Path, output_path: Path) -> None:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    sections, changes = validate(profile, proposal)
    original = resume_path(profile, profile_path).resolve()
    if not original.is_file():
        raise ValueError("原始简历不存在")
    output = output_path.resolve()
    if output.suffix.lower() not in {".md", ".html"} or ".fanhan-job-agent" not in output.parts:
        raise ValueError("成稿必须是 .fanhan-job-agent/ 下的新 Markdown 或 HTML 文件")
    if output == original:
        raise ValueError("成稿不能覆盖原始简历")
    if output.stem != proposal["artifact_stem"]:
        raise ValueError("输出文件名必须与 artifact_stem 一致")

    original_hash = sha256(original)
    rendered = (
        render_markdown(proposal["job"], sections, changes)
        if output.suffix.lower() == ".md"
        else render_html(output.stem, sections)
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(rendered)
    if sha256(original) != original_hash:
        output.unlink(missing_ok=True)
        raise RuntimeError("原始简历在生成过程中发生变化，已删除成稿")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        original = root / "Rokid旧简历.pdf"
        original.write_bytes(b"%PDF-original")
        career_document = root / "职业经历.md"
        career_document.write_text("# 职业经历\n", encoding="utf-8")
        profile_path = root / "profile.json"
        proposal_path = root / "proposal.json"
        output = root / ".fanhan-job-agent" / "outbox" / "张三-Example-AI产品经理-20260818-v1.html"
        profile_path.write_text(json.dumps({
            "schema_version": "fanhan-career-profile-v1",
            "resume": {"path": str(original)},
            "identity": {"name": "张三"},
            "career_document": {"path": str(career_document)},
        }), encoding="utf-8")
        proposal = {
            "schema_version": "fanhan-tailored-material-v1",
            "job": {"id": "job-1", "company": "Example", "title": "AI 产品经理"},
            "artifact_stem": "张三-Example-AI产品经理-20260818-v1",
            "sections": [{
                "heading": "相关经历", "content": "负责有证据的 AI 产品交付。",
                "change_ids": ["change-1", "change-2"],
            }],
            "changes": [
                {
                    "id": "change-1", "type": "rewrite", "summary": "突出 AI 产品交付",
                    "jd_basis": ["JD 要求 AI 产品经验"], "fact_evidence": ["简历第 1 页"],
                    "confirmation": "not_required",
                },
                {
                    "id": "change-2", "type": "fact_addition", "summary": "补充交付结果",
                    "jd_basis": ["JD 要求结果证据"], "fact_evidence": ["候选人明确回答"],
                    "confirmation": "pending",
                },
            ],
        }
        proposal_path.write_text(json.dumps(proposal, ensure_ascii=False), encoding="utf-8")
        try:
            render(profile_path, proposal_path, output)
            raise AssertionError("未确认事实不应生成成稿")
        except ValueError as error:
            assert "未经候选人确认" in str(error)
        assert not output.exists()

        proposal["changes"][1].update(confirmation="confirmed", confirmed_at="2026-08-18T00:00:00Z")
        proposal_path.write_text(json.dumps(proposal, ensure_ascii=False), encoding="utf-8")
        before = sha256(original)
        render(profile_path, proposal_path, output)
        assert sha256(original) == before
        page = output.read_text(encoding="utf-8")
        assert "contenteditable=\"true\"" in page and "window.print()" in page
        assert "<title>张三-Example-AI产品经理-20260818-v1</title>" in page
        wrong_name = root / ".fanhan-job-agent" / "outbox" / "张三-Rokid-AI产品经理-20260818-v1.html"
        try:
            render(profile_path, proposal_path, wrong_name)
            raise AssertionError("不应沿用旧目标公司文件名")
        except ValueError as error:
            assert "artifact_stem" in str(error)
        try:
            render(profile_path, proposal_path, output)
            raise AssertionError("不应覆盖已有成稿")
        except FileExistsError:
            pass
    print("material_gate self-test: ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", nargs="?", help="职业档案 JSON 路径")
    parser.add_argument("proposal", nargs="?", help="定制提案 JSON 路径")
    parser.add_argument("output", nargs="?", help="独立 Markdown 或 HTML 输出路径")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.profile or not args.proposal or not args.output:
        parser.error("请提供职业档案、定制提案和输出路径")
    render(
        Path(args.profile).expanduser().resolve(),
        Path(args.proposal).expanduser().resolve(),
        Path(args.output).expanduser(),
    )
    print("定制材料已生成；原始简历未修改。HTML 可直接编辑并导出 PDF。")


if __name__ == "__main__":
    main()
