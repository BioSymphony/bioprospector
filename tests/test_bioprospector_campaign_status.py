"""Tests for public BioProspector campaign status snapshots."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_campaign_status.py"
CAMPAIGN = REPO_ROOT / "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


campaign_status = load_module("bioprospector_campaign_status", SCRIPT_PATH)


class BioProspectorCampaignStatusTests(unittest.TestCase):
    def test_compile_status_summarizes_public_demo_gates(self) -> None:
        status = campaign_status.compile_status(CAMPAIGN)

        self.assertEqual("pathway-big-bang-huperzine-frontier-public-v0", status["campaign"]["campaign_id"])
        self.assertTrue(status["readiness"]["planning_ready"])
        self.assertFalse(status["readiness"]["strict_closeout_likely_ready"])
        self.assertGreater(len(status["execution_and_gates"]["provider_blockers"]), 0)
        self.assertGreater(len(status["execution_and_gates"]["blocking_decoy_controls_open"]), 0)
        self.assertTrue(any(item["name"] == "issue_dry_run_full_frontier" for item in status["recommended_commands"]))

    def test_cli_writes_public_status_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            json_out = tmp / "status.json"
            md_out = tmp / "status.md"
            subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--campaign", str(CAMPAIGN), "--out", str(json_out)],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--campaign",
                    str(CAMPAIGN),
                    "--out",
                    str(md_out),
                    "--format",
                    "markdown",
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertEqual("huperzine A", json.loads(json_out.read_text(encoding="utf-8"))["campaign"]["target_molecule"])
            self.assertIn("Campaign Status", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
