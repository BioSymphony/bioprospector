#!/usr/bin/env python3
"""Tests for the public-release audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "scripts/public_audit.py"


def run_audit(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT), str(root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


class PublicAuditTests(unittest.TestCase):
    def test_current_repo_passes_public_audit(self) -> None:
        result = run_audit(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS public audit", result.stdout)

    def test_pytest_cache_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache = root / ".pytest_cache" / "v" / "cache"
            cache.mkdir(parents=True)
            (cache / "nodeids").write_text("[]\n", encoding="utf-8")

            result = run_audit(root)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS public audit", result.stdout)

    def test_git_tracked_runtime_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            runtime = root / ".runtime"
            runtime.mkdir()
            leaked = runtime / "provider-summary.txt"
            leaked.write_text("summary only but still forbidden when tracked\n", encoding="utf-8")
            subprocess.run(["git", "add", str(leaked)], cwd=root, check=True, capture_output=True)

            result = run_audit(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tracked forbidden directory component '.runtime'", result.stdout)

    def test_git_tracked_build_artifact_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            dist = root / "dist"
            dist.mkdir()
            artifact = dist / "package.whl"
            artifact.write_text("placeholder package artifact\n", encoding="utf-8")
            subprocess.run(["git", "add", str(artifact)], cwd=root, check=True, capture_output=True)

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tracked forbidden directory component 'dist'", result.stdout)

    def test_secret_like_literal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "config.txt"
            leaked.write_text("api_" + "key = " + "abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")

            result = run_audit(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible secret pattern", result.stdout)

    def test_aws_iam_unique_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "identity.txt"
            leaked.write_text(("AI" + "DAEXAMPLEUSERID123456") + "\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible secret pattern", result.stdout)

    def test_aws_account_arn_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            account_id = "".join(["123", "456", "789", "012"])
            leaked = root / "arn.txt"
            leaked.write_text(f"arn:aws:iam::{account_id}:user/example\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible secret pattern", result.stdout)

    def test_standalone_aws_account_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            account_id = "".join(["123", "456", "789", "012"])
            leaked = root / "account.txt"
            leaked.write_text(f"account={account_id}\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible provider identifier (aws account id)", result.stdout)

    def test_provider_id_assignment_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "pod.json"
            leaked.write_text('{"pod_' + 'id": "abc123def456"}\n', encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible provider identifier (provider id assignment)", result.stdout)

    def test_runpod_proxy_url_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "proxy.txt"
            leaked.write_text("https://abc123." + "proxy." + "runpod.net/status\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible provider identifier (runpod proxy url)", result.stdout)

    def test_private_registry_image_assignment_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "image.txt"
            leaked.write_text("image = registry.example.internal" + "/team/private:latest\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible provider identifier (private registry image assignment)", result.stdout)

    def test_yaml_api_key_literal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "workflow.yaml"
            leaked.write_text("api_" + "key: " + "abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible secret pattern", result.stdout)

    def test_non_placeholder_s3_uri_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "provider.tsv"
            leaked.write_text("result_uri\t" + "s3" + "://private-operator-bucket/results\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-placeholder S3 URI", result.stdout)

    def test_runtime_root_scan_rejects_private_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = Path(tmpdir) / ".runtime"
            runtime.mkdir()
            leaked = runtime / "campaign-plan.json"
            leaked.write_text('{"path": "' + "/" + "Users" + '/example/workspace"}\n', encoding="utf-8")

            result = run_audit(runtime)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden text", result.stdout)

    def test_public_process_cleanup_terms_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "release.md"
            leaked.write_text("## " + "Scr" + "ub Rules\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden text", result.stdout)


if __name__ == "__main__":
    unittest.main()
