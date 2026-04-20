#!/usr/bin/env python3
"""Validate changed files on a PR against pr-path-policy.yaml."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def _spec(patterns: list[str]) -> PathSpec:
    lines = [p for p in patterns if p and str(p).strip()]
    return PathSpec.from_lines(GitWildMatchPattern, lines)


def _matches_any(spec: PathSpec, path: str) -> bool:
    return spec.match_file(path)


def _load_policy(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _changed_files(base: str, head: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout or "git diff failed\n")
        raise SystemExit(2)
    out: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip().replace("\\", "/")
        if line:
            out.append(line)
    return out


def _parse_labels(raw: str) -> set[str]:
    parts = [p.strip() for p in raw.replace(" ", ",").split(",")]
    return {p for p in parts if p}


def main() -> None:
    base = os.environ.get("BASE_SHA", "").strip()
    head = os.environ.get("HEAD_SHA", "").strip()
    if not base or not head:
        sys.stderr.write("BASE_SHA and HEAD_SHA must be set\n")
        raise SystemExit(2)

    policy_path = Path(os.environ.get("POLICY_FILE", "pr-path-policy.yaml"))
    if not policy_path.is_file():
        sys.stderr.write(f"Missing policy file: {policy_path}\n")
        raise SystemExit(2)

    policy = _load_policy(policy_path)
    co = policy.get("content_only") or {}
    co_label = str(co.get("label", "content-only")).strip()
    co_allow = co.get("allow") or []
    co_deny = co.get("deny") or []
    if not isinstance(co_allow, list):
        co_allow = []
    if not isinstance(co_deny, list):
        co_deny = []

    gl = policy.get("global") or {}
    global_deny = gl.get("deny") or []
    if not isinstance(global_deny, list):
        global_deny = []

    labels = _parse_labels(os.environ.get("PR_LABELS", ""))
    content_only_mode = bool(co_label and co_label in labels)

    files = _changed_files(base, head)

    violations: list[str] = []

    allow_spec = _spec([str(x) for x in co_allow])
    co_deny_spec = _spec([str(x) for x in co_deny])
    global_deny_spec = _spec([str(x) for x in global_deny])

    for path in files:
        norm = path.replace("\\", "/")

        if global_deny and _matches_any(global_deny_spec, norm):
            violations.append(f"[global.deny] {norm}")
            continue

        if not content_only_mode:
            continue

        if co_deny and _matches_any(co_deny_spec, norm):
            violations.append(f"[content_only.deny] {norm}")
            continue

        if not co_allow:
            violations.append(f"[content_only.allow] (no allow rules) {norm}")
            continue

        if not _matches_any(allow_spec, norm):
            violations.append(f"[content_only.allow] {norm}")

    if violations:
        sys.stderr.write("PR path policy violations:\n")
        for v in violations:
            sys.stderr.write(f"  - {v}\n")
        if content_only_mode:
            sys.stderr.write(
                f"\nThis PR is labeled '{co_label}': "
                "only allowed paths may change.\n"
            )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
