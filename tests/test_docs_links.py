#!/usr/bin/env python3
"""Tests for local Markdown link checking."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts/check_docs_links.py"


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


class DocsLinkTests(unittest.TestCase):
    def test_current_repo_docs_links_pass(self) -> None:
        result = run_checker(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS docs links", result.stdout)

    def test_missing_local_markdown_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")

            result = run_checker(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing local link target", result.stdout)

    def test_remote_links_and_code_fences_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text(
                "\n".join(
                    [
                        "[remote](https://example.org)",
                        "```markdown",
                        "[not checked](missing.md)",
                        "```",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_absolute_file_and_escaping_links_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repository"
            root.mkdir()
            (root / "README.md").write_text(
                "[file URL](file:///tmp/private.md)\n"
                "[absolute](/tmp/private.md)\n"
                "[escape](../../private.md)\n",
                encoding="utf-8",
            )

            result = run_checker(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe local link scheme", result.stdout)
        self.assertIn("absolute local link target", result.stdout)
        self.assertIn("escapes the repository", result.stdout)

    def test_missing_local_anchor_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "guide.md").write_text("# Existing heading\n", encoding="utf-8")
            (root / "README.md").write_text("[missing](guide.md#missing-heading)\n", encoding="utf-8")

            result = run_checker(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing local link anchor", result.stdout)

    def test_existing_local_anchor_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "guide.md").write_text("# Existing heading\n", encoding="utf-8")
            (root / "README.md").write_text("[heading](guide.md#existing-heading)\n", encoding="utf-8")

            result = run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
