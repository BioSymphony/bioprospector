#!/usr/bin/env python3
"""Check local Markdown links without touching the network."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


SKIP_DIRS = {
    ".git",
    ".runtime",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}

LINK_PATTERN = re.compile(r"!?\[[^\]]+\]\(([^)\n]+)\)")
FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)
REMOTE_SCHEMES = {"http", "https", "mailto"}


def strip_code_fences(text: str) -> str:
    return FENCE_PATTERN.sub("", text)


def iter_markdown(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        current = Path(dirpath)
        for filename in sorted(filenames):
            if filename.endswith(".md"):
                yield current / filename


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    parsed = urlparse(target)
    if parsed.scheme in REMOTE_SCHEMES:
        return None
    if parsed.scheme and parsed.scheme not in {"", "file"}:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    return path


def check_file(root: Path, path: Path) -> list[str]:
    try:
        text = strip_code_fences(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return [f"{path.relative_to(root)}: cannot decode as UTF-8 ({exc})"]

    issues: list[str] = []
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1)
        target = local_target(raw_target)
        if target is None:
            continue
        target_path = (path.parent / target).resolve() if not target.startswith("/") else Path(target)
        if not target_path.exists():
            rel = path.relative_to(root)
            issues.append(f"{rel}: missing local link target {raw_target!r}")
    return issues


def check(root: Path) -> list[str]:
    issues: list[str] = []
    for path in iter_markdown(root):
        issues.extend(check_file(root, path))
    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    issues = check(root)
    if issues:
        print("FAIL docs links")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("PASS docs links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
