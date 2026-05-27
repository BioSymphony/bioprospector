#!/usr/bin/env python3
"""Tests for BioProspector dry-run issue generation."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_DRY_RUN_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_issue_dry_run.py"

spec = importlib.util.spec_from_file_location("bioprospector_issue_dry_run", ISSUE_DRY_RUN_PATH)
assert spec and spec.loader
issue_dry_run = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = issue_dry_run
spec.loader.exec_module(issue_dry_run)


class IssueProfileTests(unittest.TestCase):
    def test_candidate_intelligence_lanes_are_default_on(self) -> None:
        options = issue_dry_run.resolve_include_options(None, {})

        enabled = {name for name, value in options.items() if value}
        self.assertEqual(enabled, {"include_candidate_intelligence_lanes"})

    def test_full_frontier_profile_enables_every_include_flag(self) -> None:
        options = issue_dry_run.resolve_include_options("full-frontier", {})

        self.assertEqual(set(options), set(issue_dry_run.INCLUDE_FLAG_ATTRS))
        self.assertTrue(all(options.values()))

    def test_core_evidence_profile_is_intentionally_small(self) -> None:
        options = issue_dry_run.resolve_include_options("core-evidence", {})

        enabled = {name for name, value in options.items() if value}
        self.assertEqual(
            enabled,
            {
                "include_candidate_intelligence_lanes",
                "include_evidence_lanes",
                "include_literature_lanes",
                "include_decoy_control_lanes",
            },
        )

    def test_profiles_and_explicit_flags_are_additive(self) -> None:
        options = issue_dry_run.resolve_include_options(
            "core-evidence",
            {"include_candidate_package_lanes": True, "include_sequence_search_lanes": True},
        )

        self.assertTrue(options["include_evidence_lanes"])
        self.assertTrue(options["include_literature_lanes"])
        self.assertTrue(options["include_decoy_control_lanes"])
        self.assertTrue(options["include_candidate_package_lanes"])
        self.assertTrue(options["include_sequence_search_lanes"])
        self.assertFalse(options["include_runpod_prep"])

    def test_full_frontier_profile_generates_drift_sensitive_lanes(self) -> None:
        campaign = REPO_ROOT / "skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json"
        options = issue_dry_run.resolve_include_options("full-frontier", {})
        issues = issue_dry_run.build_issues(campaign, "NOOTKATONE", **options)

        self.assertIn("NOOTKATONE-scale-control-00-fanout-and-partial-closeout.md", issues)
        self.assertIn("NOOTKATONE-self-learning-00-skill-update-after-hiccup.md", issues)
        self.assertIn("NOOTKATONE-candidate-intelligence-70-sequence-and-literature.md", issues)
        self.assertIn("NOOTKATONE-candidate-package-80-graph-and-dossier.md", issues)
        self.assertIn("NOOTKATONE-genecluster-atlas-60-source-route-and-jury.md", issues)
        self.assertIn("NOOTKATONE-tool-execution-proof-00-callable-commands.md", issues)
        self.assertIn("NOOTKATONE-route-rule-00-retrosynthesis-expansion.md", issues)
        self.assertIn("NOOTKATONE-review-surface-00-graph-dossier.md", issues)
        self.assertTrue(any(name.startswith("NOOTKATONE-sequence-search-step-") for name in issues))
        self.assertIn("lane:claude", issues["NOOTKATONE-99-red-team.md"])
        self.assertIn("lane:claude", issues["NOOTKATONE-decoy-control-00-negative-gate.md"])
        self.assertIn("lane:claude", issues["NOOTKATONE-contract-self-check-99-final-join.md"])


if __name__ == "__main__":
    unittest.main()
