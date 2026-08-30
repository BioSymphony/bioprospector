#!/usr/bin/env python3
"""Tests for BioProspector campaign preflight schemas."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_preflight.py"

spec = importlib.util.spec_from_file_location("bioprospector_preflight", PREFLIGHT_PATH)
assert spec and spec.loader
preflight = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = preflight
spec.loader.exec_module(preflight)


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
        "medium",
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
        "hypothesis",
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

OPTIONAL_ROWS = {
    "literature_ledger": [
        "LIT001",
        "literature",
        "https://example.org",
        "claim",
        "literature",
        "citation_only",
        "C001",
        "planning row",
    ],
    "literature_search_ledger": [
        "LS001",
        "S001",
        "demo activity literature",
        "PubMed;OpenAlex;UniProt",
        "demo enzyme activity",
        "3650",
        "25",
        "planned",
        "citation_ids_and_claim_summaries_only",
        "planning row",
    ],
    "pathway_inference_ledger": [
        "PI001",
        "",
        "R001",
        "route-ledger",
        "chemistry_decomposition",
        "assumption",
        "counterevidence",
        "hypothesis",
        "open",
        "planning row",
    ],
    "unknown_gene_hypothesis_ledger": [
        "UGH001",
        "S001",
        "R001",
        "candidate_module",
        "enzyme_class",
        "multi_gene_module",
        "evidence",
        "counterevidence",
        "hypothesis",
        "next_step",
        "open",
        "planning row",
    ],
    "enzyme_family_sweep": [
        "FAM001",
        "S001",
        "seed",
        "family_scope",
        "domain_model",
        "motif",
        "0",
        "0",
        "0",
        "LIT001",
        "risk",
        "evidence_lane",
        "planning row",
    ],
    "sequence_search_plan_ledger": [
        "SS001",
        "S001",
        "Q001",
        "blastp",
        "swissprot",
        "CP001",
        "/workspace/bioprospector/runs/demo/work/S001",
        "protein_aa_only",
        "500",
        "evalue<=1e-10;identity>=30",
        "25.00",
        "operator_review_required",
        "candidate_sequence_ledger;domain_annotation_ledger",
        "planning row",
    ],
    "candidate_sequence_ledger": [
        "E001",
        "S001",
        "protein_aa",
        "provider_output_after_run:S001/candidate-data-pack/protein-aa.faa#E001",
        "0",
        "review_before_run",
        "swissprot",
        "accession_summary_only",
        "planned",
        "planning row",
    ],
    "domain_annotation_ledger": [
        "DA001",
        "E001",
        "S001",
        "Pfam-A",
        "PF00000",
        "demo domain",
        "0",
        "0",
        "motif_review_needed",
        "planned",
        "planning row",
    ],
    "candidate_intelligence_ledger": [
        "CI001",
        "E001",
        "S001",
        "signal_peptide",
        "candidate_sequence",
        "domain-annotation-ledger.tsv",
        "N-terminal sequence review",
        "Signal peptide status is unknown and needs review before expression ranking.",
        "review_required",
        "hypothesis",
        "review",
        "planning row",
    ],
    "candidate_diversity_ledger": [
        "DIV001",
        "S001",
        "E001",
        "canonical_vs_diverse",
        "demo_cluster",
        "canonical",
        "medium",
        "planned",
        "seed candidate bin",
        "planning row",
    ],
    "candidate_graph_ledger": [
        "EDGE001",
        "S001",
        "E001",
        "step_candidate",
        "S001",
        "sequence_similarity",
        "0.50",
        "hypothesis",
        "planning row",
    ],
    "run_output_package_ledger": [
        "PKG001",
        "candidate_data_pack",
        "candidate_sequence_ledger;domain_annotation_ledger",
        "candidate_graph.tsv",
        "protein_aa_only",
        "provider_output_after_run:outputs/candidate-data-pack",
        "planned",
        "planning row",
    ],
    "genome_mining_plan": [
        "GM001",
        "taxa",
        "source",
        "family",
        "anchor",
        "25kb",
        "25.00",
        "operator_review_required",
        "planning row",
    ],
    "genome_hit_ledger": [
        "GH001",
        "GM001",
        "accession",
        "organism",
        "contig",
        "pointer",
        "domain",
        "pending",
        "hypothesis",
        "planning row",
    ],
    "structure_risk_ledger": [
        "SR001",
        "E001",
        "planned",
        "unknown",
        "review_needed",
        "unknown",
        "unknown",
        "unknown",
        "not_validation",
        "review",
        "planning row",
    ],
    "host_comparison_ledger": [
        "demo-host",
        "R001",
        "S001",
        "medium",
        "unknown",
        "unknown",
        "unknown",
        "unknown",
        "review",
        "planning row",
    ],
    "assay_handoff_ledger": [
        "AH001",
        "R001",
        "E001",
        "product",
        "readout",
        "controls",
        "risk",
        "true",
        "non_protocol",
        "planning row",
    ],
    "monitoring_ledger": [
        "MON001",
        "ISSUE-1",
        "lane",
        "artifact",
        "planned",
        "none",
        "manual_review",
        "operator",
        "planning row",
    ],
    "self_learning_skill_ledger": [
        "SL001",
        "2026-05-06",
        "demo",
        "stage stalled",
        "stale_progress",
        "Heartbeat continued without ledger growth.",
        "A no-progress probe would have stopped the run earlier.",
        "Add stale-window fixture and preflight row.",
        "Prior run with heartbeat-only monitoring.",
        "Fixture emits stalled status before budget cap.",
        "30 minute stale window",
        "not_run",
        "update_runbook",
        "true",
        "false",
        "true",
        "Process learning only; not biological validation.",
        "operator",
        "planning row",
    ],
    "input_audit_ledger": [
        "IA001",
        "manifest",
        "campaign-manifest.json",
        "campaign-manifest.json",
        "materialized",
        "campaign-manifest.json",
        "git_tracked",
        "false",
        "none",
        "planning row",
    ],
    "operator_intake_ledger": [
        "OI001",
        "target",
        "Confirm target molecule for this campaign.",
        "demo",
        "demo",
        "confirmed",
        "planning",
        "true",
        "true",
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
    "stage_contract_ledger": [
        "STG001",
        "demo stage",
        "CP001",
        "artifact.tsv",
        "checkpoint.marker",
        "done.marker",
        "30",
        "resume command",
        "true",
        "L3",
        "planned",
        "planning row",
    ],
    "stage_progress_ledger": [
        "SP001",
        "STG001",
        "heartbeat",
        "2026-04-30T00:00:00Z",
        "artifact.tsv",
        "0",
        "",
        "",
        "none",
        "planning row",
    ],
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
    "query_set_ledger": [
        "Q001",
        "S001",
        "protein",
        "demo query",
        "demo organism",
        "accession",
        "declared",
        "review_before_run",
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
        "not_run",
        "planned",
        "true",
        "planning row",
    ],
    "execution_artifact_ledger": [
        "EX001",
        "RUN001",
        "S001",
        "mock command",
        "summary",
        ".runtime/mock.json",
        "mock_runner",
        "true",
        "true",
        "planned",
        "not_materialized",
        "planning row",
    ],
    "compute_provider_ledger": [
        "CP001",
        "runpod_manual_pod",
        "RunPod manual Pod",
        "blessed_default",
        "manual_ui_plus_scripts",
        "/workspace",
        "/workspace/bioprospector/runs/{campaign_id}",
        "no_secrets_in_repo",
        "99.00",
        "planned",
        "true",
        "planning row",
    ],
    "provider_launch_preflight_ledger": [
        "PLP001",
        "CP001",
        "registry_auth",
        "public image or provider-side auth verified",
        "review before run",
        "review_required",
        "true",
        "planning row",
    ],
    "workflow_framework_ledger": [
        "WF001",
        "python_cli",
        "ledger_validation",
        "all_providers",
        "skills/bioprospector/scripts/*.py",
        "json_summary",
        "false",
        "approved",
        "planning row",
    ],
}


class BioProspectorPreflightTests(unittest.TestCase):
    def write_tsv(self, root: Path, key: str, row: list[str], *, drop_last_header: bool = False) -> str:
        filename = f"{key}.tsv"
        headers = list(preflight.REQUIRED_HEADERS[key])
        if drop_last_header:
            headers = headers[:-1]
            row = row[: len(headers)]
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

    def run_checks(self, campaign: Path) -> list:
        return (
            preflight.check_manifest(campaign)
            + preflight.check_tsv_ledgers(campaign)
            + preflight.check_claim_ledger(campaign)
        )

    def assert_all_ok(self, checks: list) -> None:
        failed = [check.message for check in checks if not check.ok]
        self.assertEqual([], failed)

    def test_optional_ledgers_may_be_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp))
            self.assert_all_ok(self.run_checks(campaign))

    def test_valid_optional_ledgers_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            campaign = self.write_campaign(Path(tmp), optional=OPTIONAL_ROWS)
            self.assert_all_ok(self.run_checks(campaign))

    def test_missing_required_header_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = self.write_campaign(root)
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["ledgers"]["literature_ledger"] = self.write_tsv(
                root, "literature_ledger", OPTIONAL_ROWS["literature_ledger"], drop_last_header=True
            )
            campaign.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "literature_ledger headers" in check.message for check in checks))

    def test_invalid_claim_level_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["pathway_inference_ledger"])
            bad_row[7] = "too_confident"
            campaign = self.write_campaign(Path(tmp), optional={"pathway_inference_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "pathway_inference_ledger claim levels" in check.message for check in checks))

    def test_validated_claim_with_review_needed_caveat_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(CORE_ROWS["enzyme_draft_board"])
            bad_row[8] = "validated_elsewhere"
            bad_row[13] = "Public report needs review before use."
            original = CORE_ROWS["enzyme_draft_board"]
            CORE_ROWS["enzyme_draft_board"] = bad_row
            try:
                campaign = self.write_campaign(Path(tmp))
            finally:
                CORE_ROWS["enzyme_draft_board"] = original
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "enzyme_draft_board strict validation review caveats" in check.message for check in checks)
            )

    def test_invalid_search_width_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_step = list(CORE_ROWS["reaction_step_ledger"])
            bad_step[8] = "too_wide"
            original = CORE_ROWS["reaction_step_ledger"]
            CORE_ROWS["reaction_step_ledger"] = bad_step
            try:
                campaign = self.write_campaign(root)
            finally:
                CORE_ROWS["reaction_step_ledger"] = original
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "reaction_step_ledger search widths" in check.message for check in checks))

    def test_unknown_manifest_ledger_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = self.write_campaign(root)
            (root / "mystery.tsv").write_text("field\nvalue\n", encoding="utf-8")
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["ledgers"]["mystery_ledger"] = "mystery.tsv"
            campaign.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "manifest ledger keys" in check.message for check in checks))

    def test_invalid_maturity_level_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["run_maturity_ledger"])
            bad_row[1] = "L9"
            campaign = self.write_campaign(Path(tmp), optional={"run_maturity_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "run_maturity_ledger maturity levels" in check.message for check in checks))

    def test_invalid_stage_contract_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["stage_contract_ledger"])
            bad_row[10] = "desired_running"
            campaign = self.write_campaign(Path(tmp), optional={"stage_contract_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "stage_contract_ledger statuses" in check.message for check in checks))

    def test_invalid_stage_progress_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["stage_progress_ledger"])
            bad_row[2] = "desiredStatus_RUNNING"
            campaign = self.write_campaign(Path(tmp), optional={"stage_progress_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "stage_progress_ledger event statuses" in check.message for check in checks))

    def test_invalid_provider_launch_preflight_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["provider_launch_preflight_ledger"])
            bad_row[5] = "looks_ok"
            campaign = self.write_campaign(Path(tmp), optional={"provider_launch_preflight_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "provider_launch_preflight_ledger statuses" in check.message for check in checks)
            )

    def test_invalid_decoy_control_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["decoy_control_ledger"])
            bad_row[6] = "unsupported_status"
            campaign = self.write_campaign(Path(tmp), optional={"decoy_control_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "decoy_control_ledger statuses" in check.message for check in checks))

    def test_invalid_sequence_search_tool_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["sequence_search_plan_ledger"])
            bad_row[3] = "magicblastbutnotreally"
            campaign = self.write_campaign(Path(tmp), optional={"sequence_search_plan_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "sequence_search_plan_ledger search tools" in check.message for check in checks))

    def test_invalid_candidate_sequence_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["candidate_sequence_ledger"])
            bad_row[2] = "full_construct"
            campaign = self.write_campaign(Path(tmp), optional={"candidate_sequence_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "candidate_sequence_ledger sequence types" in check.message for check in checks))

    def test_invalid_candidate_intelligence_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["candidate_intelligence_ledger"])
            bad_row[3] = "docking_score"
            campaign = self.write_campaign(Path(tmp), optional={"candidate_intelligence_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "candidate_intelligence_ledger intelligence types" in check.message for check in checks)
            )

    def test_invalid_candidate_graph_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["candidate_graph_ledger"])
            bad_row[7] = "definitely_produces"
            campaign = self.write_campaign(Path(tmp), optional={"candidate_graph_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "candidate_graph_ledger claim levels" in check.message for check in checks))

    def test_invalid_self_learning_hiccup_type_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["self_learning_skill_ledger"])
            bad_row[4] = "just_vibes"
            campaign = self.write_campaign(Path(tmp), optional={"self_learning_skill_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "self_learning_skill_ledger hiccup types" in check.message for check in checks))

    def test_invalid_self_learning_boolean_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["self_learning_skill_ledger"])
            bad_row[13] = "maybe"
            campaign = self.write_campaign(Path(tmp), optional={"self_learning_skill_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "self_learning_skill_ledger runbook_update flags" in check.message for check in checks)
            )

    def test_invalid_output_package_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["run_output_package_ledger"])
            bad_row[6] = "looks_done"
            campaign = self.write_campaign(Path(tmp), optional={"run_output_package_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "run_output_package_ledger statuses" in check.message for check in checks))

    def test_invalid_operator_intake_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["operator_intake_ledger"])
            bad_row[5] = "sort_of_confirmed"
            campaign = self.write_campaign(Path(tmp), optional={"operator_intake_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "operator_intake_ledger confirmation statuses" in check.message for check in checks)
            )

    def test_invalid_operator_intake_required_before_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["operator_intake_ledger"])
            bad_row[6] = "whenever"
            campaign = self.write_campaign(Path(tmp), optional={"operator_intake_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "operator_intake_ledger required_before values" in check.message for check in checks)
            )

    def test_invalid_operator_intake_boolean_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["operator_intake_ledger"])
            bad_row[7] = "mostly"
            campaign = self.write_campaign(Path(tmp), optional={"operator_intake_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "operator_intake_ledger planning_can_proceed flags" in check.message for check in checks)
            )

    def test_invalid_compute_provider_class_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            bad_row[1] = "mystery_cloud"
            campaign = self.write_campaign(Path(tmp), optional={"compute_provider_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "compute_provider_ledger provider classes" in check.message for check in checks))

    def test_compute_provider_requires_blessed_runpod_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            bad_row[1] = "cloud_vm"
            bad_row[10] = "true"
            campaign = self.write_campaign(Path(tmp), optional={"compute_provider_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "compute_provider_ledger reviewed RunPod path" in check.message for check in checks))

    def test_compute_provider_rejects_incompatible_non_default_blessed_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runpod_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            cloud_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            cloud_row[0] = "CP002"
            cloud_row[1] = "cloud_vm"
            cloud_row[2] = "Cloud VM"
            cloud_row[3] = "fallback"
            cloud_row[10] = "true"
            root = Path(tmp)
            campaign = self.write_campaign(root)
            headers = preflight.REQUIRED_HEADERS["compute_provider_ledger"]
            (root / "compute_provider_ledger.tsv").write_text(
                "\t".join(headers) + "\n" + "\t".join(runpod_row) + "\n" + "\t".join(cloud_row) + "\n",
                encoding="utf-8",
            )
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["ledgers"]["compute_provider_ledger"] = "compute_provider_ledger.tsv"
            campaign.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(not check.ok and "compute_provider_ledger non-default blessed path roles" in check.message for check in checks)
            )

    def test_compute_provider_allows_role_specific_non_default_blessed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runpod_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            aws_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            aws_row[0] = "CP002"
            aws_row[1] = "elasticblast_cloud"
            aws_row[2] = "AWS ElasticBLAST"
            aws_row[3] = "wide_blast_escalation"
            aws_row[10] = "true"
            neocloud_row = list(OPTIONAL_ROWS["compute_provider_ledger"])
            neocloud_row[0] = "CP003"
            neocloud_row[1] = "neocloud_vm"
            neocloud_row[2] = "Neocloud VM"
            neocloud_row[3] = "blessed_compatible"
            neocloud_row[10] = "true"
            root = Path(tmp)
            campaign = self.write_campaign(root)
            headers = preflight.REQUIRED_HEADERS["compute_provider_ledger"]
            (root / "compute_provider_ledger.tsv").write_text(
                "\t".join(headers)
                + "\n"
                + "\t".join(runpod_row)
                + "\n"
                + "\t".join(aws_row)
                + "\n"
                + "\t".join(neocloud_row)
                + "\n",
                encoding="utf-8",
            )
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["ledgers"]["compute_provider_ledger"] = "compute_provider_ledger.tsv"
            campaign.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            self.assert_all_ok(self.run_checks(campaign))

    def test_invalid_workflow_framework_class_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["workflow_framework_ledger"])
            bad_row[1] = "magicflow"
            campaign = self.write_campaign(Path(tmp), optional={"workflow_framework_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "workflow_framework_ledger framework classes" in check.message for check in checks))

    def test_invalid_workflow_framework_provider_ref_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["workflow_framework_ledger"])
            bad_row[3] = "mystery_provider"
            campaign = self.write_campaign(Path(tmp), optional={"workflow_framework_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(any(not check.ok and "workflow_framework_ledger provider class refs" in check.message for check in checks))

    def test_manifest_paths_cannot_escape_campaign_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = self.write_campaign(root)
            manifest = json.loads(campaign.read_text(encoding="utf-8"))
            manifest["target_contract"] = "../target-contract.json"
            manifest["ledgers"]["route_ledger"] = "/outside/route-ledger.tsv"
            campaign.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            checks = self.run_checks(campaign)

            messages = [check.message for check in checks if not check.ok]
            self.assertTrue(any("route_ledger path stays inside" in message for message in messages))
            self.assertTrue(any("target contract path stays inside" in message for message in messages))
            self.assertNotIn("/outside/", "\n".join(messages))

    def test_workflow_framework_requires_active_runpod_compatible_framework(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_row = list(OPTIONAL_ROWS["workflow_framework_ledger"])
            bad_row[3] = "cloud_vm"
            campaign = self.write_campaign(Path(tmp), optional={"workflow_framework_ledger": bad_row})
            checks = self.run_checks(campaign)
            self.assertTrue(
                any(
                    not check.ok and "workflow_framework_ledger active RunPod-compatible framework" in check.message
                    for check in checks
                )
            )


if __name__ == "__main__":
    unittest.main()
