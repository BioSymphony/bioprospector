"""Tests for redacted workspace status snapshots."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_workspace_status.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


workspace_status = load_module("bioprospector_workspace_status", SCRIPT_PATH)


def run_git(path: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=path, check=True, text=True, capture_output=True)


def commit_all(path: Path, message: str) -> None:
    run_git(path, "add", ".")
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=BioProspector Test",
            "-c",
            "user.email=bioprospector-test@example.invalid",
            "commit",
            "-m",
            message,
        ],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )


def make_repo(path: Path, *, branch: str = "main") -> None:
    path.mkdir(parents=True)
    run_git(path, "init", "-b", "main")
    (path / ".gitignore").write_text(".runtime/\n", encoding="utf-8")
    (path / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    (path / "Makefile").write_text("test:\n\t@true\n", encoding="utf-8")
    (path / "pyproject.toml").write_text("[project]\nname = \"test\"\n", encoding="utf-8")
    (path / "docs").mkdir()
    (path / "docs" / "PUBLIC_RELEASE_PREP.md").write_text("# Release\n", encoding="utf-8")
    (path / "docs" / "PRIVACY_SECURITY_MODEL.md").write_text("# Privacy\n", encoding="utf-8")
    (path / "schemas").mkdir()
    (path / "schemas" / "bioprospector-ledgers.json").write_text("{}", encoding="utf-8")
    commit_all(path, "Initial public-safe repo")
    if branch != "main":
        run_git(path, "checkout", "-b", branch)
        (path / "README.md").write_text(f"# Test Repo\n\nBranch {branch}\n", encoding="utf-8")
        commit_all(path, "Branch update")


class BioProspectorWorkspaceStatusTests(unittest.TestCase):
    def test_default_status_hides_dirty_runtime_names_and_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "checkout"
            make_repo(root, branch="codex/local")
            (root / ".runtime" / "runtime-dir-should-not-print").mkdir(parents=True)
            (root / "local-filename-should-not-print.txt").write_text("local scratch\n", encoding="utf-8")

            status = workspace_status.compile_workspace_status(root=root)
            rendered = workspace_status.render_markdown(status)

            self.assertEqual("local_checkout_status", status["scope"])
            self.assertFalse(status["redaction_defaults"]["branch_name"])
            self.assertIsNone(status["repo"]["git"]["branch"])
            self.assertFalse(status["redaction_defaults"]["dirty_file_names"])
            self.assertFalse(status["redaction_defaults"]["runtime_dir_names"])
            self.assertEqual(1, status["repo"]["git"]["dirty_count"])
            self.assertEqual([], status["repo"]["git"]["dirty_files"])
            self.assertEqual(1, status["repo"]["runtime"]["top_level_dir_count"])
            self.assertEqual([], status["repo"]["runtime"]["latest_dirs"])
            self.assertNotIn(str(root), rendered)
            self.assertNotIn("local-filename-should-not-print", rendered)
            self.assertNotIn("runtime-dir-should-not-print", rendered)
            self.assertIn("Remote/network actions: `none`", rendered)

    def test_explicit_status_flags_show_local_debug_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "checkout"
            make_repo(root)
            (root / ".runtime" / "local-demo").mkdir(parents=True)
            (root / "scratch.txt").write_text("local scratch\n", encoding="utf-8")

            status = workspace_status.compile_workspace_status(
                root=root,
                include_branch=True,
                include_dirty_files=True,
                include_runtime_dirs=True,
                include_commit_subjects=True,
            )
            rendered = workspace_status.render_markdown(status)

            self.assertEqual("main", status["repo"]["git"]["branch"])
            self.assertIn("?? scratch.txt", status["repo"]["git"]["dirty_files"])
            self.assertEqual(".runtime/local-demo", status["repo"]["runtime"]["latest_dirs"][0]["path"])
            self.assertIn("Initial public-safe repo", rendered)
            self.assertIn(".runtime/local-demo", rendered)

    def test_cli_writes_json_with_redacted_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "checkout"
            make_repo(root)
            out = Path(tmpdir) / "status.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--repo-root",
                    str(root),
                    "--format",
                    "json",
                    "--out",
                    str(out),
                ],
                cwd=root,
                check=True,
                text=True,
                capture_output=True,
            )

            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(".", data["repo"]["root"])
            self.assertEqual("none", data["remote_network_actions"])
            self.assertFalse(data["redaction_defaults"]["absolute_paths"])
            self.assertFalse(data["redaction_defaults"]["branch_name"])


if __name__ == "__main__":
    unittest.main()
