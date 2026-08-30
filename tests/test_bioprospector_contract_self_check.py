#!/usr/bin/env python3
"""Tests for BioProspector joined contract self-checks."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_preflight.py"
SELF_CHECK_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_contract_self_check.py"
INPUT_AUDIT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_input_audit.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


preflight = load_module("bioprospector_preflight_for_self_check_tests", PREFLIGHT_PATH)
self_check = load_module("bioprospector_contract_self_check", SELF_CHECK_PATH)
input_audit = load_module("bioprospector_input_audit", INPUT_AUDIT_PATH)


CORE_ROWS = {
    "route_ledger": [
        "R001",
        "demo-route",
        "demo-product",
        "demo-host",
        "fed",
        "seed_route",
        "hypothesis",
        "seed",
        "unknown",
        "planning row",
    ],
    "reaction_step_ledger": [
        "S001",
        "R001",
        "1",
        "demo_transformation",
        "substrate",
        "product",
        "demo_enzyme",
        "evidence",
        "wide",
        "enzyme_draft_board",
        "planning row",
    ],
    "candidate_funnels": ["S001", "0", "0", "0", "0", "0", "0", "0", "planned", "planning row"],
    "enzyme_draft_board": [
        "E001",
        "S001",
        "candidate",
        "organism",
        "accession",
        "family",
        "domain",
        "literature",
        "validated_elsewhere",
        "unknown",
        "unknown",
        "medium",
        "review",
        "planning row",
    ],
    "route_stitching_scorecard": [
        "R001",
        "seed",
        "unknown",
        "unknown",
        "unknown",
        "unknown",
        "unknown",
        "none",
        "not_reviewed",
        "planning row",
    ],
    "resource_ledger": [
        "resource",
        "literature",
        "review_before_run",
        "open",
        "citation_only",
        "no-large-content-copy",
        "https://example.org",
        "planning row",
    ],
}


HARDENING_ROWS = {
    "organism_sample_ledger": [
        "ORG001",
        "demo organism",
        "demo strain",
        "SAMPLE001",
        "target_organism",
        "sequence",
        "declared",
        "target-dataset",
        "open_summary_only",
        "planning row",
    ],
    "target_dataset_ledger": [
        "DS001",
        "ORG001",
        "proteome",
        "demo target dataset",
        "provider_summary",
        "declared",
        "review_before_run",
        "target_evidence",
        "open_summary_only",
        "planning row",
    ],
    "target_evidence_ledger": [
        "TE001",
        "E001",
        "S001",
        "ORG001",
        "DS001",
        "target_sequence",
        "provider_summary",
        "joined",
        "evidence_supported",
        "planning row",
    ],
    "decoy_control_ledger": [
        "DC001",
        "S001",
        "decoy_query",
        "demo decoy",
        "low_or_no_hit",
        "low_or_no_hit",
        "passed",
        "true",
        "planning row",
    ],
    "execution_artifact_ledger": [
        "EX001",
        "RUN001",
        "S001",
        "real command",
        "summary",
        "s3://example/summary.json",
        "reviewed_runner",
        "false",
        "false",
        "materialized",
        "summary_hash",
        "planning row",
    ],
    "run_maturity_ledger": [
        "RUN001",
        "L0",
        "plan_exists",
        "pass",
        "campaign-manifest.json",
        "none",
        "operator",
        "planning row",
    ],
    "operator_intake_ledger": [
        "OI001",
        "provider",
        "Confirm provider before execution.",
        "RunPod reviewed, no live execution yet",
        "RunPod reviewed, no live execution yet",
        "confirmed",
        "execution",
        "true",
        "true",
        "planning row",
    ],
    "stage_contract_ledger": [
        "STG001",
        "demo execution stage",
        "CP001",
        "execution-artifact-ledger.tsv",
        "checkpoint.marker",
        "done.marker",
        "30",
        "resume command",
        "true",
        "L3",
        "completed",
        "planning row",
    ],
    "stage_progress_ledger": [
        "SP001",
        "STG001",
        "completed",
        "2026-04-30T00:00:00Z",
        "execution-artifact-ledger.tsv",
        "0",
        "",
        "",
        "none",
        "planning row",
    ],
    "provider_launch_preflight_ledger": [
        "PLP001",
        "CP001",
        "registry_auth",
        "public image or provider-side auth verified",
        "verified",
        "pass",
        "true",
        "planning row",
    ],
}


class BioProspectorContractSelfCheckTests(unittest.TestCase):
    def write_tsv(self, root: Path, key: str, row: list[str]) -> str:
        filename = f"{key}.tsv"
        headers = preflight.REQUIRED_HEADERS[key]
        (root / filename).write_text("\t".join(headers) + "\n" + "\t".join(row) + "\n", encoding="utf-8")
        return filename

    def write_campaign(self, root: Path, *, optional: dict[str, list[str]] | None = None) -> Path:
        ledgers: dict[str, str] = {}
        for key, row in CORE_ROWS.items():
            ledgers[key] = self.write_tsv(root, key, row)

        if optional:
            for key, row in optional.items():
                ledgers[key] = self.write_tsv(root, key, row)

        (root / "claim-ledger.md").write_text(
            "| Claim | Level | Evidence | Caveat |\n"
            "| --- | --- | --- | --- |\n"
            "| demo | hypothesis | seed | planning only |\n",
            encoding="utf-8",
        )
        ledgers["claim_ledger"] = "claim-ledger.md"

        (root / "target-contract.json").write_text(
            json.dumps(
                {
                    "target_molecule": "demo",
                    "host": "demo-host",
                    "campaign_goal": "demo",
                    "optimization_goals": ["highest_evidence"],
                    "hard_boundaries": ["planning_only"],
                }
            ),
            encoding="utf-8",
        )

        manifest = {
            "campaign_id": "demo",
            "campaign_name": "Demo",
            "target_contract": "target-contract.json",
            "host": "demo-host",
            "target_molecule": "demo",
            "mode": "pathway_big_bang",
            "scope": "planning_only",
            "claim_boundary": "planning only",
            "ledgers": ledgers,
        }
        path = root / "campaign-manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def test_default_planning_self_check_passes_without_real_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp))
            result = self_check.check_campaign(campaign)
            self.assertEqual("pass", result["overall"])

    def test_require_target_evidence_fails_without_joined_target_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp))
            result = self_check.check_campaign(campaign, require_target_evidence=True)
            self.assertEqual("fail", result["overall"])
            self.assertTrue(any(check["name"] == "promoted_candidate_target_evidence" for check in result["checks"] if not check["ok"]))

    def test_require_target_evidence_passes_with_joined_target_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            optional = {
                key: HARDENING_ROWS[key]
                for key in ["organism_sample_ledger", "target_dataset_ledger", "target_evidence_ledger"]
            }
            campaign = self.write_campaign(Path(tmp), optional=optional)
            result = self_check.check_campaign(campaign, require_target_evidence=True)
            self.assertEqual("pass", result["overall"])

    def test_require_decoy_controls_fails_until_wide_step_control_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp))
            result = self_check.check_campaign(campaign, require_decoy_controls=True)
            self.assertEqual("fail", result["overall"])

        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp), optional={"decoy_control_ledger": HARDENING_ROWS["decoy_control_ledger"]})
            result = self_check.check_campaign(campaign, require_decoy_controls=True)
            self.assertEqual("pass", result["overall"])

    def test_require_real_execution_rejects_mock_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mock_artifact = list(HARDENING_ROWS["execution_artifact_ledger"])
            mock_artifact[7] = "true"
            mock_artifact[8] = "true"
            campaign = self.write_campaign(Path(tmp), optional={"execution_artifact_ledger": mock_artifact})
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("fail", result["overall"])

        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp), optional={"execution_artifact_ledger": HARDENING_ROWS["execution_artifact_ledger"]})
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("pass", result["overall"])

    def test_operator_intake_planning_blocker_fails_default_self_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            intake = list(HARDENING_ROWS["operator_intake_ledger"])
            intake[1] = "target"
            intake[5] = "needs_operator"
            intake[6] = "planning"
            intake[7] = "false"
            campaign = self.write_campaign(Path(tmp), optional={"operator_intake_ledger": intake})
            result = self_check.check_campaign(campaign)
            self.assertEqual("fail", result["overall"])
            self.assertTrue(any(check["name"] == "operator_intake_planning_gate" for check in result["checks"] if not check["ok"]))

    def test_operator_intake_execution_assumption_blocks_real_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            intake = list(HARDENING_ROWS["operator_intake_ledger"])
            intake[5] = "assumed"
            campaign = self.write_campaign(
                Path(tmp),
                optional={
                    "operator_intake_ledger": intake,
                    "execution_artifact_ledger": HARDENING_ROWS["execution_artifact_ledger"],
                },
            )
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("fail", result["overall"])
            self.assertTrue(any(check["name"] == "operator_intake_execution_gate" for check in result["checks"] if not check["ok"]))

        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(
                Path(tmp),
                optional={
                    "operator_intake_ledger": HARDENING_ROWS["operator_intake_ledger"],
                    "execution_artifact_ledger": HARDENING_ROWS["execution_artifact_ledger"],
                    "provider_launch_preflight_ledger": HARDENING_ROWS["provider_launch_preflight_ledger"],
                    "stage_contract_ledger": HARDENING_ROWS["stage_contract_ledger"],
                    "stage_progress_ledger": HARDENING_ROWS["stage_progress_ledger"],
                },
            )
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("pass", result["overall"])

    def test_provider_launch_preflight_blocks_real_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            provider = list(HARDENING_ROWS["provider_launch_preflight_ledger"])
            provider[5] = "blocked"
            campaign = self.write_campaign(
                Path(tmp),
                optional={
                    "operator_intake_ledger": HARDENING_ROWS["operator_intake_ledger"],
                    "execution_artifact_ledger": HARDENING_ROWS["execution_artifact_ledger"],
                    "provider_launch_preflight_ledger": provider,
                    "stage_contract_ledger": HARDENING_ROWS["stage_contract_ledger"],
                    "stage_progress_ledger": HARDENING_ROWS["stage_progress_ledger"],
                },
            )
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("fail", result["overall"])
            self.assertTrue(any(check["name"] == "provider_launch_preflight_gate" for check in result["checks"] if not check["ok"]))

    def test_stage_fallback_blocks_real_execution_closeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            progress = list(HARDENING_ROWS["stage_progress_ledger"])
            progress[2] = "fallback"
            progress[6] = "runpod"
            progress[7] = "local"
            progress[8] = "degraded"
            campaign = self.write_campaign(
                Path(tmp),
                optional={
                    "operator_intake_ledger": HARDENING_ROWS["operator_intake_ledger"],
                    "execution_artifact_ledger": HARDENING_ROWS["execution_artifact_ledger"],
                    "provider_launch_preflight_ledger": HARDENING_ROWS["provider_launch_preflight_ledger"],
                    "stage_contract_ledger": HARDENING_ROWS["stage_contract_ledger"],
                    "stage_progress_ledger": progress,
                },
            )
            result = self_check.check_campaign(campaign, require_real_execution=True)
            self.assertEqual("fail", result["overall"])
            self.assertTrue(any(check["name"] == "no_silent_fallback_gate" for check in result["checks"] if not check["ok"]))

    def test_input_audit_reports_missing_operator_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = self.write_campaign(root)
            (root / "target-contract.json").unlink()
            audit = input_audit.audit_campaign(campaign)
            self.assertEqual("blocked", audit["audit_status"])
            self.assertTrue(any(item["item"] == "target_contract" for item in audit["missing_operator_items"]))

    def test_input_audit_rejects_paths_outside_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = self.write_campaign(root)
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["target_contract"] = "../operator-input.json"
            manifest["ledgers"]["route_ledger"] = "/outside/route-ledger.tsv"
            campaign.write_text(json.dumps(manifest), encoding="utf-8")

            audit = input_audit.audit_campaign(campaign)
            rendered = json.dumps(audit)

            self.assertEqual("blocked", audit["audit_status"])
            self.assertNotIn(str(root.parent), rendered)
            self.assertNotIn("/outside/", rendered)
            self.assertGreaterEqual(rendered.count("blocked_invalid_path"), 2)


if __name__ == "__main__":
    unittest.main()
