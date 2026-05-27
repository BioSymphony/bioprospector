"""Tests for public BioProspector handoff packet generation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_handoff_packet.py"
CAMPAIGN = REPO_ROOT / "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


handoff = load_module("bioprospector_handoff_packet", SCRIPT_PATH)


class BioProspectorHandoffPacketTests(unittest.TestCase):
    def test_build_packet_writes_public_review_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "handoff"
            manifest = handoff.build_packet(
                CAMPAIGN,
                out,
                prefix="HUPERZINE",
                profile="public-demo",
                include_issue_drafts=False,
            )

            self.assertTrue((out / "handoff.md").exists())
            self.assertTrue((out / "campaign-status.json").exists())
            self.assertTrue((out / "campaign-plan.json").exists())
            self.assertTrue((out / "commands.sh").exists())
            self.assertFalse((out / "issue-drafts").exists())
            self.assertFalse(manifest["safety"]["launches_providers"])
            self.assertFalse(manifest["safety"]["mutates_linear"])
            self.assertEqual("pathway-big-bang-huperzine-frontier-public-v0", manifest["campaign_id"])
            handoff_md = (out / "handoff.md").read_text(encoding="utf-8")
            self.assertIn("review-only", handoff_md)
            self.assertIn("repo, tracker, chat, or publishable artifacts", handoff_md)
            self.assertIn("user-approved external workdirs", handoff_md)

    def test_cli_writes_handoff_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "handoff"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--campaign",
                    str(CAMPAIGN),
                    "--out",
                    str(out),
                    "--prefix",
                    "HUPERZINE",
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            manifest = json.loads((out / "handoff-manifest.json").read_text(encoding="utf-8"))
            self.assertIn("Wrote handoff packet", result.stdout)
            self.assertEqual("HUPERZINE", manifest["prefix"])


if __name__ == "__main__":
    unittest.main()
