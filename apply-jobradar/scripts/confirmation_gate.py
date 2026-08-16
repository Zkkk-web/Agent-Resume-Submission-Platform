#!/usr/bin/env python3
"""Bind final confirmation to the exact application state without storing material content."""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload(args):
    return {
        "company": args.company.strip(),
        "job_title": args.job_title.strip(),
        "job_url": args.job_url.strip(),
        "application_url": args.application_url.strip(),
        "resume_sha256": file_hash(args.resume),
        "portfolio_sha256": file_hash(args.portfolio) if args.portfolio else "",
        "form_field_names": sorted(set(args.field_name)),
        "final_action": args.final_action.strip(),
    }


def fingerprint(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def self_test():
    with tempfile.TemporaryDirectory() as directory:
        resume = Path(directory) / "resume.txt"
        resume.write_text("version one", encoding="utf-8")
        value = {
            "company": "Example", "job_title": "Engineer", "job_url": "https://jobradar.cc/jobs/1",
            "application_url": "https://example.com/apply/1", "resume_sha256": file_hash(resume),
            "portfolio_sha256": "", "form_field_names": ["email"], "final_action": "Submit",
        }
        first = fingerprint(value)
        assert first == fingerprint(dict(value))
        resume.write_text("version two", encoding="utf-8")
        assert first != fingerprint(dict(value, resume_sha256=file_hash(resume)))
    print("confirmation_gate self-test: ok")


def build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--company", required=True)
        child.add_argument("--job-title", required=True)
        child.add_argument("--job-url", required=True)
        child.add_argument("--application-url", required=True)
        child.add_argument("--resume", required=True, type=Path)
        child.add_argument("--portfolio", type=Path)
        child.add_argument("--field-name", action="append", default=[])
        child.add_argument("--final-action", required=True)
        if command == "verify":
            child.add_argument("--expected", required=True)
    subparsers.add_parser("self-test")
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "self-test":
        self_test()
        return
    current = payload(args)
    current_fingerprint = fingerprint(current)
    if args.command == "verify" and current_fingerprint != args.expected:
        print("confirmation_stale")
        raise SystemExit(2)
    print(json.dumps({"fingerprint": current_fingerprint, "summary": current}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
