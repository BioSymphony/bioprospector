#!/usr/bin/env python3
"""Ensure docs/README.md links every top-level docs Markdown file."""

from __future__ import annotations

import sys
from pathlib import Path


def missing_docs(root: Path) -> list[str]:
    docs_dir = root / "docs"
    index = docs_dir / "README.md"
    text = index.read_text(encoding="utf-8")
    missing: list[str] = []
    for path in sorted(docs_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        if path.name not in text:
            missing.append(path.name)
    return missing


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    missing = missing_docs(root)
    if missing:
        print("FAIL docs index")
        for name in missing:
            print(f"- docs/README.md does not list {name}")
        return 1
    print("PASS docs index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
