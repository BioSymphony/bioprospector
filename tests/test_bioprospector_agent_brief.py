"""Tests for public BioProspector agent brief generation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_agent_brief.py"
CAMPAIGN = REPO_ROOT / "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


agent_brief = load_module("bioprospector_agent_brief", SCRIPT_PATH)


class BioProspectorAgentBriefTests(unittest.TestCase):
    def test_build_brief_writes_public_goal_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "agent-brief"
            manifest = agent_brief.build_brief(
                CAMPAIGN,
                out,
                prefix="HUPERZINE",
                profile="public-demo",
                mode="goal",
                agent="claude",
            )

            self.assertTrue((out / "agent-brief.md").exists())
            self.assertTrue((out / "agent-brief.json").exists())
            self.assertTrue((out / "agent-goal-prompt.txt").exists())
            self.assertTrue((out / "commands.sh").exists())
            self.assertFalse(manifest["safety"]["launches_providers"])
            self.assertFalse(manifest["safety"]["mutates_tracker_or_linear"])
            self.assertTrue(manifest["safety"]["expects_capable_agent_or_external_orchestrator"])
            self.assertEqual("public-demo", manifest["profile"])

            prompt = (out / "agent-goal-prompt.txt").read_text(encoding="utf-8")
            self.assertIn("You are the Claude Code", prompt)
            self.assertIn("/goal", prompt)
            self.assertIn("do not launch providers", prompt)
            self.assertIn("repo, tracker, chat, or publishable artifacts", prompt)
            self.assertIn("user-approved external workdirs", prompt)
            self.assertTrue(manifest["safety"]["allows_user_owned_external_result_locations"])
            self.assertFalse(manifest["safety"]["writes_raw_private_data_to_repo_tracker_or_chat"])

    def test_cli_writes_agent_brief_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "agent-brief"
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
                    "--profile",
                    "public-demo",
                    "--mode",
                    "symphony-linear",
                ],
                cwd=REPO_ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            manifest = json.loads((out / "agent-brief.json").read_text(encoding="utf-8"))
            self.assertIn("Wrote agent brief", result.stdout)
            self.assertEqual("HUPERZINE", manifest["prefix"])
            self.assertEqual("symphony-linear", manifest["mode"])

    def test_external_paths_are_not_written_to_brief_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "agent-brief"
            agent_brief.build_brief(
                CAMPAIGN,
                out,
                prefix="HUPERZINE",
                profile="public-demo",
                mode="goal",
                agent="generic",
            )

            rendered = "\n".join(path.read_text(encoding="utf-8") for path in out.iterdir())
            self.assertNotIn(str(out), rendered)
            self.assertIn("REPLACE_ME_EXTERNAL_PATH", rendered)


if __name__ == "__main__":
    unittest.main()
