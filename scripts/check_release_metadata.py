#!/usr/bin/env python3
"""Check public package metadata and version consistency."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


def read_pyproject(root: Path) -> dict:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))


def read_init_version(root: Path) -> str | None:
    text = (root / "src" / "biosymphony_bioprospector" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def read_citation_version(root: Path) -> str | None:
    text = (root / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"^version:\s*['\"]?([^'\"\n]+)['\"]?", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def issues(root: Path) -> list[str]:
    out: list[str] = []
    pyproject = read_pyproject(root)
    project = pyproject.get("project", {})
    version = project.get("version")
    init_version = read_init_version(root)
    citation_version = read_citation_version(root)
    if version != init_version or version != citation_version:
        out.append(
            "version mismatch: "
            f"pyproject={version!r}, package={init_version!r}, citation={citation_version!r}"
        )
    urls = project.get("urls") or {}
    for key in ("Homepage", "Repository", "Documentation", "Issues"):
        if key not in urls:
            out.append(f"missing project.urls entry: {key}")
    optional = project.get("optional-dependencies") or {}
    for key in ("dev", "release"):
        if key not in optional:
            out.append(f"missing optional dependency group: {key}")
    if "biosymphony-bioprospector" != project.get("name"):
        out.append("unexpected project name")
    if project.get("requires-python") != ">=3.11":
        out.append("requires-python should stay >=3.11 unless CI/docs are updated")
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    found = issues(root)
    if found:
        print("FAIL release metadata")
        for issue in found:
            print(f"- {issue}")
        return 1
    print("PASS release metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
