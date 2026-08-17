#!/usr/bin/env python3
"""Validate an evidence-backed resume proposal and render an independent Markdown copy."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


FACT_CHANGES = {"fact_addition", "fact_change"}
CHANGE_TYPES = FACT_CHANGES | {"rewrite", "reorder"}


def required_text(value: object, field: str) -> str:
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field} 不能为空")
    return value


def string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} 必须是非空字符串数组")
    values = [required_text(item, field) for item in value]
    return values


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


def validate(profile: dict, proposal: dict) -> tuple[list[dict], list[dict]]:
    if profile.get("schema_version") != "fanhan-career-profile-v1":
        raise ValueError("profile.schema_version 必须是 fanhan-career-profile-v1")
    if proposal.get("schema_version") != "fanhan-tailored-material-v1":
        raise ValueError("proposal.schema_version 必须是 fanhan-tailored-material-v1")

    job = proposal.get("job", {})
    required_text(job.get("id"), "job.id")
    required_text(job.get("title"), "job.title")
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


def render(profile_path: Path, proposal_path: Path, output_path: Path) -> None:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    sections, changes = validate(profile, proposal)
    original = resume_path(profile, profile_path).resolve()
    if not original.is_file():
        raise ValueError("原始简历不存在")
    output = output_path.resolve()
    if output.suffix.lower() != ".md" or ".fanhan-job-agent" not in output.parts:
        raise ValueError("成稿必须是 .fanhan-job-agent/ 下的新 Markdown 文件")
    if output == original:
        raise ValueError("成稿不能覆盖原始简历")

    original_hash = sha256(original)
    job = proposal["job"]
    lines = [f"# {job['title']}｜定制申请材料", "", f"岗位 ID：`{job['id']}`", ""]
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
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines).rstrip() + "\n")
    if sha256(original) != original_hash:
        output.unlink(missing_ok=True)
        raise RuntimeError("原始简历在生成过程中发生变化，已删除成稿")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        original = root / "resume.pdf"
        original.write_bytes(b"%PDF-original")
        profile_path = root / "profile.json"
        proposal_path = root / "proposal.json"
        output = root / ".fanhan-job-agent" / "tailored-test.md"
        profile_path.write_text(json.dumps({
            "schema_version": "fanhan-career-profile-v1",
            "resume": {"path": str(original)},
        }), encoding="utf-8")
        proposal = {
            "schema_version": "fanhan-tailored-material-v1",
            "job": {"id": "job-1", "title": "AI 产品经理"},
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

        proposal["changes"][1].update(confirmation="confirmed", confirmed_at="2026-08-17T00:00:00Z")
        proposal_path.write_text(json.dumps(proposal, ensure_ascii=False), encoding="utf-8")
        before = sha256(original)
        render(profile_path, proposal_path, output)
        assert sha256(original) == before
        assert "JD 依据与变更记录" in output.read_text(encoding="utf-8")
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
    parser.add_argument("output", nargs="?", help="独立 Markdown 输出路径")
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
    print("定制材料已生成；原始简历未修改。")


if __name__ == "__main__":
    main()
