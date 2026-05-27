#!/usr/bin/env python3
"""Tests for BioProspector stage contract validation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_stage_contract.py"
NOOTKATONE = REPO_ROOT / "skills/bioprospector/examples/nootkatone-yeast-v0"
CAMPAIGN = NOOTKATONE / "campaign-manifest.json"


def run_stage_contract(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


class StageContractTests(unittest.TestCase):
    def test_public_demo_contract_passes_default_review_gate(self) -> None:
        result = run_stage_contract("--campaign", str(CAMPAIGN), "--json")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertGreaterEqual(report["stage_count"], 5)

    def test_require_real_execution_blocks_skipped_live_stage(self) -> None:
        result = run_stage_contract("--campaign", str(CAMPAIGN), "--require-real-execution", "--json")

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertTrue(any("live closeout" in error for error in report["errors"]))

    def test_require_terminal_blocks_incomplete_stage_progress(self) -> None:
        result = run_stage_contract("--campaign", str(CAMPAIGN), "--require-terminal", "--json")

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertTrue(any("not terminal" in error or "missing progress" in error for error in report["errors"]))

    def test_heartbeat_age_gate_blocks_stale_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            contract = root / "stage-contract-ledger.tsv"
            progress = root / "stage-progress-ledger.tsv"
            artifacts = root / "execution-artifact-ledger.tsv"
            shutil.copyfile(NOOTKATONE / contract.name, contract)
            shutil.copyfile(NOOTKATONE / artifacts.name, artifacts)
            progress_text = (NOOTKATONE / progress.name).read_text(encoding="utf-8")
            progress.write_text(progress_text.replace("\t0\t\t\tnone\tRunPod", "\t999\t\t\tnone\tRunPod"), encoding="utf-8")

            result = run_stage_contract(
                "--stage-contract-ledger",
                str(contract),
                "--stage-progress-ledger",
                str(progress),
                "--execution-artifact-ledger",
                str(artifacts),
                "--max-heartbeat-age-minutes",
                "10",
                "--json",
            )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertTrue(any("heartbeat_age_minutes" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
