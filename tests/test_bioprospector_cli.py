"""Tests for public BioProspector CLI wrappers."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH = str(REPO_ROOT / "src")


def run_cli(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = PYTHONPATH
    return subprocess.run(
        [sys.executable, "-m", "biosymphony_bioprospector.cli", *args],
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )


class BioProspectorCliTests(unittest.TestCase):
    def test_multiplexer_help_lists_public_commands(self) -> None:
        result = run_cli("--help")
        self.assertIn("agent-brief", result.stdout)
        self.assertIn("campaign-handoff", result.stdout)
        self.assertIn("campaign-status", result.stdout)
        self.assertIn("doctor", result.stdout)
        self.assertIn("genecluster-atlas-contracts", result.stdout)
        self.assertIn("genecluster-atlas-normalizers", result.stdout)
        self.assertIn("genecluster-atlas-plan", result.stdout)
        self.assertIn("preflight", result.stdout)
        self.assertIn("stage-contract", result.stdout)
        self.assertIn("workspace-status", result.stdout)

    def test_multiplexer_passes_help_to_script(self) -> None:
        result = run_cli("genecluster-atlas-plan", "--help")
        self.assertIn("Build a public-safe GeneCluster atlas plan", result.stdout)

    def test_commands_json_lists_stage_contract(self) -> None:
        result = run_cli("commands", "--json")
        self.assertIn('"version": "0.1.0"', result.stdout)
        self.assertIn('"command": "agent-brief"', result.stdout)
        self.assertIn('"command": "campaign-handoff"', result.stdout)
        self.assertIn('"command": "campaign-status"', result.stdout)
        self.assertIn('"command": "stage-contract"', result.stdout)
        self.assertIn('"command": "workspace-status"', result.stdout)

    def test_quickstart_uses_public_make_target(self) -> None:
        result = run_cli("quickstart")
        self.assertIn("make local-demo", result.stdout)
        self.assertNotIn("local-superpower-demo", result.stdout)
        self.assertIn("BIOPROSPECTOR_REPO_ROOT", result.stdout)

    def test_version_does_not_require_checkout_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_cli("--version", cwd=Path(tmpdir))

        self.assertEqual(result.stdout.strip(), "0.1.0")

    def test_multiplexer_does_not_execute_repo_shaped_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fake_scripts = root / "skills" / "bioprospector" / "scripts"
            fake_scripts.mkdir(parents=True)
            (root / "schemas").mkdir()
            (root / "schemas" / "bioprospector-ledgers.json").write_text("{}", encoding="utf-8")
            (fake_scripts / "bioprospector_preflight.py").write_text(
                "print('CWD_SENTINEL_SHOULD_NOT_RUN')\n",
                encoding="utf-8",
            )

            result = run_cli("preflight", "--help", cwd=root)

        self.assertNotIn("CWD_SENTINEL_SHOULD_NOT_RUN", result.stdout)
        self.assertIn("Validate BioProspector campaign prep artifacts", result.stdout)


if __name__ == "__main__":
    unittest.main()
