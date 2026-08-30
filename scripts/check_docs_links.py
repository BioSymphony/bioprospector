#!/usr/bin/env python3
"""Check local Markdown links without touching the network."""

from __future__ import annotations

import argparse
import html
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
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXPLICIT_ID_PATTERN = re.compile(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']", re.IGNORECASE)
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


def local_target(raw_target: str) -> tuple[str, str] | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    parsed = urlparse(target)
    if parsed.scheme in REMOTE_SCHEMES:
        return None
    if parsed.scheme:
        return "", "unsafe_scheme"
    path = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    return path, fragment


def github_anchor(text: str) -> str:
    value = html.unescape(text).strip().lower()
    value = re.sub(r"!?\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("`", "").replace("*", "").replace("_", "")
    value = re.sub(r"[^\w\s-]", "", value)
    return re.sub(r"\s+", "-", value).strip("-")


def markdown_anchors(path: Path) -> set[str]:
    text = strip_code_fences(path.read_text(encoding="utf-8"))
    anchors = set(EXPLICIT_ID_PATTERN.findall(text))
    counts: dict[str, int] = {}
    for match in HEADING_PATTERN.finditer(text):
        base = github_anchor(match.group(1))
        if not base:
            continue
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def check_file(root: Path, path: Path) -> list[str]:
    try:
        text = strip_code_fences(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return [f"{path.relative_to(root)}: cannot decode as UTF-8 ({exc})"]

    issues: list[str] = []
    for match in LINK_PATTERN.finditer(text):
        raw_target = match.group(1)
        parsed_target = local_target(raw_target)
        if parsed_target is None:
            continue
        target, fragment = parsed_target
        rel = path.relative_to(root)
        if fragment == "unsafe_scheme":
            issues.append(f"{rel}: unsafe local link scheme")
            continue
        if target and Path(target).is_absolute():
            issues.append(f"{rel}: absolute local link target is not allowed")
            continue
        target_path = path if not target else (path.parent / target).resolve()
        try:
            target_path.relative_to(root.resolve())
        except ValueError:
            issues.append(f"{rel}: local link target escapes the repository")
            continue
        if not target_path.exists():
            issues.append(f"{rel}: missing local link target {raw_target!r}")
            continue
        if fragment and target_path.is_file() and target_path.suffix.lower() == ".md":
            try:
                anchors = markdown_anchors(target_path)
            except UnicodeDecodeError as exc:
                issues.append(f"{rel}: cannot decode linked Markdown as UTF-8 ({exc})")
                continue
            if fragment not in anchors:
                issues.append(f"{rel}: missing local link anchor {fragment!r}")
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
