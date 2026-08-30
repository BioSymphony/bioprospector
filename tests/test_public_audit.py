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

    def test_git_tracked_environment_file_is_rejected_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            environment = root / ("." + "env.production")
            environment.write_text("placeholder only\n", encoding="utf-8")
            subprocess.run(["git", "add", str(environment)], cwd=root, check=True, capture_output=True)

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tracked forbidden filename pattern", result.stdout)

    def test_git_tracked_private_key_filename_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            key_file = root / ("deploy" + ".pem")
            key_file.write_text("encoded placeholder\n", encoding="utf-8")
            subprocess.run(["git", "add", str(key_file)], cwd=root, check=True, capture_output=True)

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tracked forbidden filename pattern", result.stdout)

    def test_git_tracked_credential_config_filenames_are_rejected(self) -> None:
        for filename in (".envrc", ".netrc", ".pypirc", ".npmrc", ".git-credentials"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
                credential_file = root / filename
                credential_file.write_text("synthetic placeholder\n", encoding="utf-8")
                subprocess.run(["git", "add", "-f", str(credential_file)], cwd=root, check=True, capture_output=True)

                result = run_audit(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("tracked forbidden filename pattern", result.stdout)

    def test_git_tracked_symbolic_link_is_rejected_without_reading_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            target = root.parent / "outside-public-audit-target.txt"
            link = root / "external-pointer.txt"
            link.symlink_to(target)
            subprocess.run(["git", "add", str(link)], cwd=root, check=True, capture_output=True)

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symbolic link is not allowed", result.stdout)

    def test_untracked_directory_symbolic_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repository"
            target = Path(tmpdir) / "external-directory"
            root.mkdir()
            target.mkdir()
            (root / "external-directory").symlink_to(target, target_is_directory=True)

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symbolic link is not allowed", result.stdout)

    def test_skipped_directory_symbolic_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "repository"
            target = Path(tmpdir) / "external-runtime"
            root.mkdir()
            target.mkdir()
            runtime_link = root / ".runtime"
            runtime_link.symlink_to(target, target_is_directory=True)

            parent_result = run_audit(root)
            direct_result = run_audit(runtime_link)

            self.assertNotEqual(parent_result.returncode, 0)
            self.assertIn("symbolic link is not allowed", parent_result.stdout)
            self.assertNotEqual(direct_result.returncode, 0)
            self.assertIn("symbolic link", direct_result.stdout)

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
            self.assertIn("possible private path", result.stdout)

    def test_linux_user_home_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "path.txt"
            leaked.write_text("/" + "home" + "/example-user/workspace/output.tsv\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible private path", result.stdout)

    def test_user_home_root_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "path.txt"
            leaked.write_text("/" + "home" + "/example-user\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible private path", result.stdout)

    def test_windows_user_home_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaked = root / "path.txt"
            leaked.write_text("C:" + "\\Users\\example-user\\workspace\\output.tsv\n", encoding="utf-8")

            result = run_audit(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("possible private path", result.stdout)

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
