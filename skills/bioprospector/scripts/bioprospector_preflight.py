#!/usr/bin/env python3
"""Validate BioProspector campaign prep artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
REPO_ROOT = SCRIPT_DIR.parents[2]

from bioprospector_schema import load_schema


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def resolve_declared_path(base: Path, value: object) -> Path | None:
    text = str(value or "").strip()
    rel = Path(text)
    if not text or rel.is_absolute():
        return None
    resolved_base = base.resolve()
    resolved = (resolved_base / rel).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError:
        return None
    return resolved


REQUIRED_MANIFEST_FIELDS = {
    "campaign_id",
    "campaign_name",
    "target_contract",
    "host",
    "target_molecule",
    "mode",
    "scope",
    "claim_boundary",
    "ledgers",
}

REQUIRED_LEDGER_KEYS = {
    "route_ledger",
    "reaction_step_ledger",
    "candidate_funnels",
    "enzyme_draft_board",
    "route_stitching_scorecard",
    "resource_ledger",
    "claim_ledger",
}

OPTIONAL_LEDGER_KEYS = {
    "unknown_step_ledger",
    "rejected_candidates",
    "provenance_log",
    "runpod_run_manifest",
    "elasticblast_search_plan",
    "elasticblast_run_ledger",
    "aws_safety_ledger",
    "literature_ledger",
    "literature_search_ledger",
    "pathway_inference_ledger",
    "unknown_gene_hypothesis_ledger",
    "enzyme_family_sweep",
    "sequence_search_plan_ledger",
    "candidate_sequence_ledger",
    "domain_annotation_ledger",
    "candidate_intelligence_ledger",
    "candidate_diversity_ledger",
    "candidate_graph_ledger",
    "run_output_package_ledger",
    "genome_mining_plan",
    "genome_hit_ledger",
    "structure_risk_ledger",
    "host_comparison_ledger",
    "assay_handoff_ledger",
    "monitoring_ledger",
    "self_learning_skill_ledger",
    "lane_status_ledger",
    "fanout_estimate_ledger",
    "partial_summary_ledger",
    "stale_output_guard_ledger",
    "input_audit_ledger",
    "operator_intake_ledger",
    "run_maturity_ledger",
    "stage_contract_ledger",
    "stage_progress_ledger",
    "tool_execution_proof_ledger",
    "organism_sample_ledger",
    "query_set_ledger",
    "target_dataset_ledger",
    "target_evidence_ledger",
    "decoy_control_ledger",
    "execution_artifact_ledger",
    "genecluster_source_scout_ledger",
    "genecluster_route_decision_ledger",
    "genecluster_atlas_contract_ledger",
    "genecluster_cluster_calls",
    "genecluster_bgc_consensus",
    "genecluster_protein_function_votes",
    "genecluster_protein_function_jury",
    "compute_provider_ledger",
    "provider_launch_preflight_ledger",
    "workflow_framework_ledger",
}

KNOWN_LEDGER_KEYS = REQUIRED_LEDGER_KEYS | OPTIONAL_LEDGER_KEYS

REQUIRED_HEADERS = {
    "route_ledger": [
        "route_id",
        "route_name",
        "target_product",
        "host",
        "feedstock_mode",
        "route_class",
        "evidence_level",
        "route_status",
        "primary_risk",
        "notes",
    ],
    "reaction_step_ledger": [
        "step_id",
        "route_id",
        "step_order",
        "transformation",
        "substrate",
        "product",
        "enzyme_role",
        "evidence_need",
        "candidate_search_width",
        "required_output",
        "notes",
    ],
    "candidate_funnels": [
        "step_id",
        "raw_hits",
        "quality_filtered",
        "domain_valid",
        "clustered_representatives",
        "evidence_reviewed",
        "shortlisted",
        "final_picks",
        "funnel_status",
        "notes",
    ],
    "enzyme_draft_board": [
        "candidate_id",
        "step_id",
        "candidate_name",
        "source_organism",
        "accession_or_source",
        "enzyme_family",
        "domain_architecture",
        "evidence_classes",
        "claim_level",
        "substrate_fit",
        "host_fit",
        "rejection_risk",
        "verdict",
        "notes",
    ],
    "route_stitching_scorecard": [
        "route_id",
        "route_status",
        "intermediate_compatibility",
        "cofactor_fit",
        "host_precursor_fit",
        "toxicity_risk",
        "transport_or_protection_need",
        "missing_steps",
        "integration_verdict",
        "notes",
    ],
    "resource_ledger": [
        "resource",
        "resource_type",
        "version",
        "license_class",
        "use_mode",
        "redistribution_policy",
        "citation_or_url",
        "notes",
    ],
    "unknown_step_ledger": [
        "unknown_step_id",
        "parent_step_id",
        "route_id",
        "gap_type",
        "substrate",
        "product",
        "transformation_hypothesis",
        "search_strategy",
        "candidate_search_width",
        "status",
        "required_evidence",
        "notes",
    ],
    "rejected_candidates": [
        "candidate_id",
        "step_id",
        "candidate_name",
        "source_organism",
        "accession_or_source",
        "rejection_stage",
        "claim_level",
        "rejection_reason",
        "evidence_classes",
        "reviewer",
        "notes",
    ],
    "elasticblast_search_plan": [
        "search_id",
        "step_id",
        "query_set",
        "program",
        "database",
        "cloud_provider",
        "region",
        "result_uri",
        "num_nodes",
        "use_preemptible",
        "thresholds",
        "max_hits",
        "budget_usd",
        "approval_status",
        "notes",
    ],
    "elasticblast_run_ledger": [
        "run_id",
        "search_id",
        "status",
        "submitted_at",
        "completed_at",
        "cloud_provider",
        "region",
        "result_uri",
        "cleanup_status",
        "estimated_cost_usd",
        "output_summary",
        "notes",
    ],
    "aws_safety_ledger": [
        "control_id",
        "control_type",
        "control_name",
        "required_status",
        "verification_mode",
        "verification_command",
        "blocking_before_submit",
        "last_verified",
        "owner",
        "notes",
    ],
    "literature_ledger": [
        "citation_id",
        "source_type",
        "identifier_or_url",
        "claim_supported",
        "evidence_class",
        "license_boundary",
        "used_in_claim_ids",
        "notes",
    ],
    "literature_search_ledger": [
        "search_id",
        "step_id",
        "topic",
        "sources",
        "query_terms",
        "recency_window_days",
        "result_cap",
        "status",
        "output_contract",
        "notes",
    ],
    "pathway_inference_ledger": [
        "hypothesis_id",
        "parent_hypothesis_id",
        "route_id",
        "evidence_sources",
        "inference_method",
        "assumption",
        "counterevidence",
        "claim_level",
        "decision",
        "notes",
    ],
    "unknown_gene_hypothesis_ledger": [
        "hypothesis_id",
        "parent_step_id",
        "route_id",
        "proposed_gene_or_module",
        "enzyme_class_or_role",
        "hypothesis_type",
        "evidence_for",
        "evidence_against",
        "claim_level",
        "next_discriminating_step",
        "status",
        "notes",
    ],
    "enzyme_family_sweep": [
        "family_id",
        "step_id",
        "seed_accessions",
        "family_scope",
        "domain_model",
        "motifs_required",
        "raw_hits",
        "clusters",
        "representatives",
        "known_activity_refs",
        "risk",
        "next_lane",
        "notes",
    ],
    "sequence_search_plan_ledger": [
        "search_id",
        "step_id",
        "query_id",
        "search_tool",
        "database",
        "provider_id",
        "remote_workdir",
        "sequence_scope",
        "max_hits",
        "thresholds",
        "budget_usd",
        "approval_status",
        "output_contract",
        "notes",
    ],
    "candidate_sequence_ledger": [
        "candidate_id",
        "step_id",
        "sequence_type",
        "sequence_pointer",
        "aa_length",
        "checksum_or_version",
        "source_database",
        "license_boundary",
        "domain_map_status",
        "notes",
    ],
    "domain_annotation_ledger": [
        "annotation_id",
        "candidate_id",
        "step_id",
        "domain_source",
        "domain_accession",
        "domain_name",
        "domain_start",
        "domain_end",
        "motif_or_active_site",
        "confidence",
        "notes",
    ],
    "candidate_intelligence_ledger": [
        "intelligence_id",
        "candidate_id",
        "step_id",
        "intelligence_type",
        "source_scope",
        "evidence_source",
        "inference_basis",
        "finding",
        "confidence",
        "claim_level",
        "actionability",
        "notes",
    ],
    "candidate_diversity_ledger": [
        "selection_id",
        "step_id",
        "candidate_id",
        "diversity_axis",
        "cluster_or_clade",
        "novelty_level",
        "host_fit_priority",
        "selection_status",
        "rationale",
        "notes",
    ],
    "candidate_graph_ledger": [
        "edge_id",
        "source_id",
        "target_id",
        "edge_type",
        "step_id",
        "evidence_class",
        "weight",
        "claim_level",
        "notes",
    ],
    "run_output_package_ledger": [
        "package_id",
        "package_type",
        "included_ledgers",
        "graph_artifact",
        "sequence_policy",
        "location_or_pointer",
        "status",
        "notes",
    ],
    "genome_mining_plan": [
        "search_id",
        "target_taxa",
        "database_or_source",
        "query_family",
        "anchor_gene",
        "neighborhood_window",
        "budget_usd",
        "approval_status",
        "notes",
    ],
    "genome_hit_ledger": [
        "hit_id",
        "search_id",
        "accession_or_locus",
        "organism",
        "contig",
        "coordinates_or_pointer",
        "domain_call",
        "neighborhood_support",
        "claim_level",
        "notes",
    ],
    "structure_risk_ledger": [
        "risk_id",
        "candidate_id",
        "structure_source",
        "confidence",
        "active_site_residues",
        "cofactor_or_membrane_risk",
        "substrate_access_risk",
        "oligomerization_risk",
        "claim_boundary",
        "verdict",
        "notes",
    ],
    "host_comparison_ledger": [
        "host",
        "route_id",
        "step_id",
        "burden",
        "precursor_fit",
        "compartment_fit",
        "toxicity",
        "analytics_fit",
        "verdict",
        "notes",
    ],
    "assay_handoff_ledger": [
        "design_id",
        "route_id",
        "candidate_ids",
        "measurable_product",
        "assay_readout",
        "controls_needed",
        "risk",
        "non_protocol_boundary",
        "claim_boundary",
        "notes",
    ],
    "monitoring_ledger": [
        "run_id",
        "issue_id",
        "lane",
        "expected_artifact",
        "heartbeat_status",
        "blocker",
        "next_review_at",
        "owner",
        "notes",
    ],
    "self_learning_skill_ledger": [
        "learning_id",
        "date",
        "campaign_id",
        "trigger",
        "hiccup_type",
        "observation",
        "hypothesis",
        "probe_or_experiment",
        "control_or_baseline",
        "expected_signal",
        "stop_loss",
        "result",
        "decision",
        "runbook_update",
        "skill_update",
        "reusable_guardrail",
        "claim_boundary",
        "owner",
        "notes",
    ],
    "input_audit_ledger": [
        "input_id",
        "input_class",
        "declared_in",
        "expected_artifact",
        "materialized_status",
        "location_or_pointer",
        "checksum_or_version",
        "operator_required",
        "missing_operator_item",
        "notes",
    ],
    "operator_intake_ledger": [
        "intake_id",
        "input_area",
        "prompt",
        "default_assumption",
        "operator_answer",
        "confirmation_status",
        "required_before",
        "planning_can_proceed",
        "skip_allowed",
        "notes",
    ],
    "run_maturity_ledger": [
        "run_id",
        "maturity_level",
        "level_name",
        "status",
        "evidence_artifact",
        "blocking_gap",
        "reviewer",
        "notes",
    ],
    "stage_contract_ledger": [
        "stage_id",
        "stage_name",
        "provider_id",
        "expected_artifact",
        "checkpoint_marker",
        "done_marker",
        "timeout_minutes",
        "resume_command",
        "fail_closed",
        "required_for_maturity",
        "status",
        "notes",
    ],
    "stage_progress_ledger": [
        "event_id",
        "stage_id",
        "event_status",
        "timestamp",
        "artifact_pointer",
        "heartbeat_age_minutes",
        "fallback_from",
        "fallback_to",
        "degraded_status",
        "notes",
    ],
    "organism_sample_ledger": [
        "organism_id",
        "taxon_name",
        "strain_or_accession",
        "sample_id",
        "role",
        "evidence_type",
        "data_status",
        "source_pointer",
        "license_boundary",
        "notes",
    ],
    "query_set_ledger": [
        "query_id",
        "step_id",
        "query_type",
        "query_label",
        "source_organism",
        "source_pointer",
        "materialized_status",
        "checksum_or_version",
        "license_boundary",
        "notes",
    ],
    "target_dataset_ledger": [
        "dataset_id",
        "organism_id",
        "dataset_type",
        "dataset_label",
        "source_pointer",
        "materialized_status",
        "checksum_or_version",
        "target_evidence_role",
        "license_boundary",
        "notes",
    ],
    "target_evidence_ledger": [
        "evidence_id",
        "candidate_id",
        "step_id",
        "organism_id",
        "dataset_id",
        "evidence_type",
        "evidence_pointer",
        "join_status",
        "claim_level",
        "notes",
    ],
    "decoy_control_ledger": [
        "control_id",
        "step_id",
        "control_type",
        "query_or_dataset",
        "expected_result",
        "observed_result",
        "status",
        "blocks_promotion",
        "notes",
    ],
    "execution_artifact_ledger": [
        "artifact_id",
        "run_id",
        "step_id",
        "command_or_issue",
        "artifact_type",
        "path_or_uri",
        "produced_by",
        "dry_run",
        "mock_tools",
        "status",
        "checksum_or_summary",
        "notes",
    ],
    "genecluster_source_scout_ledger": [
        "source_id",
        "organism_id",
        "taxon_name",
        "source_record_type",
        "source_provider",
        "source_pointer",
        "material_type",
        "acquisition_policy",
        "has_genome",
        "has_annotation",
        "has_proteome",
        "has_transcriptome",
        "scout_status",
        "claim_ceiling",
        "notes",
    ],
    "genecluster_route_decision_ledger": [
        "route_id",
        "organism_id",
        "taxon_name",
        "recommended_route",
        "route_status",
        "claim_ceiling",
        "blockers",
        "accepted_inputs",
        "rejected_routes",
        "notes",
    ],
    "genecluster_atlas_contract_ledger": [
        "contract_id",
        "contract_type",
        "required_inputs",
        "expected_artifacts",
        "validation_command",
        "raw_artifact_policy",
        "claim_boundary",
        "status",
        "notes",
    ],
    "genecluster_cluster_calls": [
        "cluster_id",
        "caller",
        "source_species",
        "target_species",
        "contig",
        "start",
        "end",
        "core_genes",
        "confidence",
        "claim_level",
    ],
    "genecluster_bgc_consensus": [
        "consensus_id",
        "cluster_id",
        "verdict",
        "caller_count",
        "agreeing_callers",
        "disagreeing_callers",
        "disagreement_status",
        "claim_level",
        "caller_versions",
        "caller_licenses",
    ],
    "genecluster_protein_function_votes": [
        "protein_id",
        "tool",
        "function_label",
        "confidence",
        "evidence_level",
        "tool_version",
        "license",
    ],
    "genecluster_protein_function_jury": [
        "protein_id",
        "verdict",
        "claim_level",
        "supporting_tools",
        "contradicting_tools",
        "confidence",
    ],
    "compute_provider_ledger": [
        "provider_id",
        "provider_class",
        "provider_name",
        "role",
        "launch_mode",
        "storage_root",
        "workdir_template",
        "secrets_boundary",
        "cost_boundary_usd",
        "status",
        "blessed_path",
        "notes",
    ],
    "provider_launch_preflight_ledger": [
        "check_id",
        "provider_id",
        "check_type",
        "expected",
        "observed",
        "status",
        "blocking_before_launch",
        "notes",
    ],
    "workflow_framework_ledger": [
        "framework_id",
        "framework_class",
        "use_case",
        "provider_classes",
        "entrypoint_or_template",
        "provenance_mode",
        "resume_supported",
        "status",
        "notes",
    ],
}

CLAIM_LEVELS = {
    "hypothesis",
    "domain_supported",
    "ortholog_supported",
    "evidence_supported",
    "characterized_elsewhere",
    "validated_elsewhere",
    "validated_in_target",
    "rejected",
}
STRICT_VALIDATION_LEVELS = {"validated_elsewhere", "validated_in_target"}
REVIEW_PENDING_TERMS = ("review_needed", "review_before_run", "needs review")

EVIDENCE_CLASSES = {
    "literature",
    "accession",
    "sequence_similarity",
    "domain",
    "motif",
    "phylogeny",
    "structure",
    "substrate",
    "kinetics",
    "host_fit",
    "route_stitching",
    "red_team",
}

ROUTE_STATUSES = {
    "seed",
    "expanded",
    "under_review",
    "shortlisted",
    "killed",
    "needs_missing_step",
}

SEARCH_WIDTHS = {"tiny", "narrow", "medium", "wide", "frontier"}

ELASTICBLAST_PROGRAMS = {"blastp", "blastx", "blastn", "tblastn", "tblastx"}
ELASTICBLAST_CLOUD_PROVIDERS = {"aws", "gcp"}
ELASTICBLAST_APPROVAL_STATUSES = {
    "planned",
    "operator_review_required",
    "approved",
    "submitted",
    "blocked",
    "cancelled",
}
ELASTICBLAST_RUN_STATUSES = {"planned", "submitted", "running", "succeeded", "failed", "deleted", "cancelled"}
ELASTICBLAST_CLEANUP_STATUSES = {"not_started", "not_required", "pending", "verified_deleted", "needs_review"}
AWS_SAFETY_REQUIRED_STATUSES = {"planned", "required", "verified", "blocked", "not_applicable"}
LANE_APPROVAL_STATUSES = {"planned", "operator_review_required", "approved", "blocked", "cancelled"}
PATHWAY_INFERENCE_DECISIONS = {"open", "continue", "split", "parked", "killed", "promote", "needs_evidence"}
UNKNOWN_GENE_STATUSES = {"open", "review", "shortlisted", "rejected", "parked", "killed"}
LITERATURE_SEARCH_STATUSES = {"planned", "running", "completed", "partial", "blocked", "not_started"}
SEQUENCE_SEARCH_TOOLS = {"blastp", "diamond", "mmseqs", "hmmer", "psiblast", "elasticblast", "foldseek"}
SEQUENCE_SCOPES = {
    "protein_aa_only",
    "translated_orf",
    "domain_model_only",
    "structure_model_only",
    "nucleotide_reference",
}
SEQUENCE_TYPES = {"protein_aa", "protein_fragment", "translated_protein", "domain_model", "reference_pointer", "provider_pointer"}
DOMAIN_MAP_STATUSES = {"planned", "mapped", "partial", "failed", "not_required"}
DOMAIN_CONFIDENCE = {"planned", "low", "medium", "high", "unknown"}
INTELLIGENCE_TYPES = {
    "public_reference_enzyme",
    "engineered_variant",
    "mutant_variant",
    "natural_variant",
    "signal_peptide",
    "transit_peptide",
    "transmembrane",
    "ptm",
    "localization",
    "motif",
    "cofactor",
    "oligomer",
    "expression_context",
    "canonical_inference",
    "counterevidence",
    "other",
}
INTELLIGENCE_SOURCE_SCOPES = {
    "public_reviewed",
    "public_unreviewed",
    "literature",
    "close_canonical_match",
    "candidate_sequence",
    "template_design",
    "provider_summary",
    "operator_supplied",
    "other",
}
INTELLIGENCE_CONFIDENCE = DOMAIN_CONFIDENCE | {"review_required", "not_observed"}
INTELLIGENCE_ACTIONABILITY = {
    "use_as_anchor",
    "prioritize",
    "deprioritize",
    "review",
    "preserve",
    "park",
    "block",
    "not_applicable",
}
CANDIDATE_NOVELTY_LEVELS = {"canonical", "close_homolog", "diverse_homolog", "remote_homolog", "weird_or_novel"}
CANDIDATE_SELECTION_STATUSES = {"planned", "shortlist", "selected", "rejected", "parked"}
GRAPH_EDGE_TYPES = {
    "route_step",
    "step_candidate",
    "candidate_domain",
    "candidate_literature",
    "candidate_host_risk",
    "candidate_diversity_cluster",
    "candidate_package",
}
RUN_PACKAGE_TYPES = {"runpod_readiness", "candidate_data_pack", "graph_pack", "literature_pack", "final_dossier"}
RUN_PACKAGE_STATUSES = {"planned", "materialized", "partial", "blocked", "deleted"}
RISK_VERDICTS = {"unknown", "review", "pass", "watch", "blocked", "reject"}
HOST_VERDICTS = {"unknown", "review", "preferred", "acceptable", "risky", "blocked"}
ASSAY_BOUNDARY_FLAGS = {"true", "false"}
MONITORING_HEARTBEATS = {"planned", "waiting", "running", "blocked", "stale", "stalled", "complete", "not_started"}
SELF_LEARNING_HICCUP_TYPES = {
    "planning_gap",
    "input_gap",
    "provider_failure",
    "tool_failure",
    "stale_progress",
    "false_success_risk",
    "evidence_ambiguity",
    "scale_fanout",
    "fallback",
    "cost_overrun",
    "data_policy_risk",
    "claim_boundary",
    "other",
}
SELF_LEARNING_DECISIONS = {
    "keep",
    "update_runbook",
    "update_skill",
    "update_template",
    "add_validator",
    "add_preflight",
    "add_issue_lane",
    "park",
    "retry",
    "stop",
    "escalate",
    "no_change",
}
OPERATOR_INTAKE_AREAS = {
    "target",
    "host",
    "scope",
    "inputs",
    "data_policy",
    "provider",
    "budget",
    "success_criteria",
    "claim_boundary",
    "unknowns",
}
OPERATOR_INTAKE_STATUSES = {"unasked", "assumed", "confirmed", "skipped", "needs_operator", "blocked"}
OPERATOR_INTAKE_REQUIRED_BEFORE = {"planning", "execution", "claim_closeout", "never"}
INPUT_CLASSES = {
    "manifest",
    "target_contract",
    "operator_intake",
    "route_ledger",
    "reaction_step_ledger",
    "organism_sample",
    "query_set",
    "target_dataset",
    "resource",
    "result_summary",
    "provenance",
}
MATERIALIZED_STATUSES = {"declared", "missing", "placeholder", "materialized", "not_required", "blocked"}
BOOLEAN_FLAGS = {"true", "false"}
MATURITY_LEVELS = {"L0", "L1", "L2", "L3", "L4", "L5"}
STAGE_REQUIRED_FOR_MATURITY = MATURITY_LEVELS | {"never"}
MATURITY_STATUSES = {"not_started", "planned", "blocked", "pass", "fail", "not_applicable"}
STAGE_STATUSES = {"planned", "ready", "running", "completed", "failed", "partial", "skipped", "blocked"}
STAGE_PROGRESS_STATUSES = {"started", "heartbeat", "completed", "failed", "partial", "fallback", "skipped", "resumed", "stalled"}
DEGRADED_STATUSES = {"none", "partial", "degraded", "blocked", "stalled"}
ORGANISM_SAMPLE_ROLES = {
    "target_host",
    "target_organism",
    "source_organism",
    "reference_organism",
    "decoy",
    "negative_control",
}
ORGANISM_DATA_STATUSES = {"declared", "materialized", "missing", "reference_only", "blocked", "not_required"}
QUERY_TYPES = {
    "gene",
    "protein",
    "molecule",
    "reaction",
    "spectrum",
    "domain_model",
    "motif",
    "structure",
    "literature_claim",
}
DATASET_TYPES = {
    "genome",
    "transcriptome",
    "proteome",
    "metabolome",
    "spectra",
    "literature",
    "accession_set",
    "annotation",
    "reference_only",
}
TARGET_EVIDENCE_ROLES = {
    "target_evidence",
    "reference_context",
    "host_context",
    "decoy",
    "negative_control",
    "not_evidence",
}
TARGET_EVIDENCE_TYPES = {
    "target_sequence",
    "target_expression",
    "target_genome_context",
    "target_metabolite",
    "target_spectrum",
    "target_assay",
    "reference_hit",
    "homolog_hit",
    "literature_only",
    "negative_control",
}
JOIN_STATUSES = {"joined", "pending", "missing", "not_applicable", "reference_only"}
DECOY_CONTROL_TYPES = {
    "decoy_query",
    "negative_taxon",
    "shuffled_sequence",
    "unrelated_family",
    "blank_search",
    "reciprocal_check",
}
CONTROL_STATUSES = {"planned", "passed", "failed", "blocked", "not_run", "not_required"}
EXECUTION_ARTIFACT_STATUSES = {"planned", "materialized", "missing", "failed", "deleted"}
COMPUTE_PROVIDER_CLASSES = {
    "local_lite",
    "local_full",
    "runpod_manual_pod",
    "runpod_ssh_pod",
    "ssh_hpc",
    "cloud_vm",
    "neocloud_vm",
    "managed_workflow",
    "elasticblast_cloud",
    "other",
}
COMPUTE_PROVIDER_ROLES = {
    "blessed_default",
    "blessed_escalation",
    "blessed_compatible",
    "local_smoke",
    "local_full",
    "wide_blast_escalation",
    "fallback",
    "future",
    "not_recommended",
}
COMPUTE_PROVIDER_STATUSES = {
    "planned",
    "review_required",
    "approved",
    "blocked",
    "deprecated",
    "not_recommended",
}
PROVIDER_PREFLIGHT_CHECK_TYPES = {
    "image_digest_pin",
    "registry_auth",
    "image_pull",
    "network_volume",
    "workdir",
    "cost_guardrail",
    "secrets_boundary",
    "branch_snapshot",
    "provider_payload_size",
    "issue_body",
    "data_policy",
    "stage_contract",
    "tool_execution_proof",
    "candidate_intelligence_tools",
    "public_api_access",
    "provider_egress_policy",
    "no_progress_stop_loss",
}
PROVIDER_PREFLIGHT_STATUSES = {"planned", "pass", "fail", "blocked", "review_required", "not_applicable"}
WORKFLOW_FRAMEWORK_CLASSES = {
    "shell_script",
    "python_cli",
    "nextflow",
    "snakemake",
    "cwl",
    "wdl",
    "notebook",
    "managed_workflow",
    "manual",
    "other",
}
WORKFLOW_FRAMEWORK_STATUSES = {"planned", "review_required", "approved", "blocked", "deferred"}
TOOL_CLASSES = {
    "sequence_search",
    "domain_search",
    "structure_search",
    "reaction_reference",
    "genome_context",
    "bgc_mining",
    "literature_search",
    "candidate_intelligence",
    "workflow_runner",
    "repository_security",
    "provenance",
    "other",
}
ADAPTER_STATUSES = {"planned", "active", "deprecated", "blocked", "review_required"}
EVIDENCE_EVENT_TYPES = {
    "sequence_hit",
    "domain_hit",
    "structure_neighbor",
    "reaction_reference",
    "genome_context",
    "bgc_cluster",
    "literature_claim",
    "candidate_intelligence",
    "decoy_result",
    "tool_proof",
    "package_index",
    "ranking",
    "other",
}
PRIVATE_DATA_STATUSES = {"none", "redacted", "external_pointer_only", "blocked"}
TOOL_PROOF_STATUSES = {"planned", "materialized", "partial", "blocked", "failed"}
ACTIVE_PROVIDER_STATUSES = {"planned", "review_required", "approved"}
ACTIVE_FRAMEWORK_STATUSES = {"planned", "review_required", "approved"}

NON_DEFAULT_BLESSED_PROVIDER_ROLES = {
    "blessed_escalation",
    "blessed_compatible",
    "wide_blast_escalation",
}
NON_DEFAULT_BLESSED_PROVIDER_CLASSES = {
    "elasticblast_cloud",
    "neocloud_vm",
    "cloud_vm",
    "ssh_hpc",
    "managed_workflow",
    "local_full",
}


def _schema_set(schema: dict, name: str, fallback: set[str]) -> set[str]:
    values = schema.get("enums", {}).get(name)
    if values is None:
        return fallback
    return set(values)


def _apply_external_schema() -> None:
    """Use the repo schema as the shared contract, with local constants as bootstrap fallback."""
    global REQUIRED_MANIFEST_FIELDS
    global REQUIRED_LEDGER_KEYS
    global OPTIONAL_LEDGER_KEYS
    global KNOWN_LEDGER_KEYS
    global REQUIRED_HEADERS
    global CLAIM_LEVELS
    global EVIDENCE_CLASSES
    global ROUTE_STATUSES
    global SEARCH_WIDTHS
    global ELASTICBLAST_PROGRAMS
    global ELASTICBLAST_CLOUD_PROVIDERS
    global ELASTICBLAST_APPROVAL_STATUSES
    global ELASTICBLAST_RUN_STATUSES
    global ELASTICBLAST_CLEANUP_STATUSES
    global AWS_SAFETY_REQUIRED_STATUSES
    global LANE_APPROVAL_STATUSES
    global PATHWAY_INFERENCE_DECISIONS
    global UNKNOWN_GENE_STATUSES
    global LITERATURE_SEARCH_STATUSES
    global SEQUENCE_SEARCH_TOOLS
    global SEQUENCE_SCOPES
    global SEQUENCE_TYPES
    global DOMAIN_MAP_STATUSES
    global DOMAIN_CONFIDENCE
    global INTELLIGENCE_TYPES
    global INTELLIGENCE_SOURCE_SCOPES
    global INTELLIGENCE_CONFIDENCE
    global INTELLIGENCE_ACTIONABILITY
    global CANDIDATE_NOVELTY_LEVELS
    global CANDIDATE_SELECTION_STATUSES
    global GRAPH_EDGE_TYPES
    global RUN_PACKAGE_TYPES
    global RUN_PACKAGE_STATUSES
    global RISK_VERDICTS
    global HOST_VERDICTS
    global ASSAY_BOUNDARY_FLAGS
    global MONITORING_HEARTBEATS
    global SELF_LEARNING_HICCUP_TYPES
    global SELF_LEARNING_DECISIONS
    global OPERATOR_INTAKE_AREAS
    global OPERATOR_INTAKE_STATUSES
    global OPERATOR_INTAKE_REQUIRED_BEFORE
    global INPUT_CLASSES
    global MATERIALIZED_STATUSES
    global BOOLEAN_FLAGS
    global MATURITY_LEVELS
    global STAGE_REQUIRED_FOR_MATURITY
    global MATURITY_STATUSES
    global STAGE_STATUSES
    global STAGE_PROGRESS_STATUSES
    global DEGRADED_STATUSES
    global ORGANISM_SAMPLE_ROLES
    global ORGANISM_DATA_STATUSES
    global QUERY_TYPES
    global DATASET_TYPES
    global TARGET_EVIDENCE_ROLES
    global TARGET_EVIDENCE_TYPES
    global JOIN_STATUSES
    global DECOY_CONTROL_TYPES
    global CONTROL_STATUSES
    global EXECUTION_ARTIFACT_STATUSES
    global COMPUTE_PROVIDER_CLASSES
    global COMPUTE_PROVIDER_ROLES
    global COMPUTE_PROVIDER_STATUSES
    global PROVIDER_PREFLIGHT_CHECK_TYPES
    global PROVIDER_PREFLIGHT_STATUSES
    global WORKFLOW_FRAMEWORK_CLASSES
    global WORKFLOW_FRAMEWORK_STATUSES
    global TOOL_CLASSES
    global ADAPTER_STATUSES
    global EVIDENCE_EVENT_TYPES
    global PRIVATE_DATA_STATUSES
    global TOOL_PROOF_STATUSES
    global ACTIVE_PROVIDER_STATUSES
    global ACTIVE_FRAMEWORK_STATUSES
    global NON_DEFAULT_BLESSED_PROVIDER_ROLES
    global NON_DEFAULT_BLESSED_PROVIDER_CLASSES

    try:
        schema = load_schema()
    except FileNotFoundError:
        return

    REQUIRED_MANIFEST_FIELDS = set(schema.get("required_manifest_fields", REQUIRED_MANIFEST_FIELDS))
    REQUIRED_LEDGER_KEYS = set(schema.get("required_ledger_keys", REQUIRED_LEDGER_KEYS))
    OPTIONAL_LEDGER_KEYS = set(schema.get("optional_ledger_keys", OPTIONAL_LEDGER_KEYS))
    KNOWN_LEDGER_KEYS = REQUIRED_LEDGER_KEYS | OPTIONAL_LEDGER_KEYS
    REQUIRED_HEADERS = {
        key: list(value)
        for key, value in schema.get("ledger_headers", REQUIRED_HEADERS).items()
    }
    CLAIM_LEVELS = _schema_set(schema, "claim_levels", CLAIM_LEVELS)
    EVIDENCE_CLASSES = _schema_set(schema, "evidence_classes", EVIDENCE_CLASSES)
    ROUTE_STATUSES = _schema_set(schema, "route_statuses", ROUTE_STATUSES)
    SEARCH_WIDTHS = _schema_set(schema, "search_widths", SEARCH_WIDTHS)
    ELASTICBLAST_PROGRAMS = _schema_set(schema, "elasticblast_programs", ELASTICBLAST_PROGRAMS)
    ELASTICBLAST_CLOUD_PROVIDERS = _schema_set(schema, "elasticblast_cloud_providers", ELASTICBLAST_CLOUD_PROVIDERS)
    ELASTICBLAST_APPROVAL_STATUSES = _schema_set(schema, "elasticblast_approval_statuses", ELASTICBLAST_APPROVAL_STATUSES)
    ELASTICBLAST_RUN_STATUSES = _schema_set(schema, "elasticblast_run_statuses", ELASTICBLAST_RUN_STATUSES)
    ELASTICBLAST_CLEANUP_STATUSES = _schema_set(schema, "elasticblast_cleanup_statuses", ELASTICBLAST_CLEANUP_STATUSES)
    AWS_SAFETY_REQUIRED_STATUSES = _schema_set(schema, "aws_safety_required_statuses", AWS_SAFETY_REQUIRED_STATUSES)
    LANE_APPROVAL_STATUSES = _schema_set(schema, "lane_approval_statuses", LANE_APPROVAL_STATUSES)
    PATHWAY_INFERENCE_DECISIONS = _schema_set(schema, "pathway_inference_decisions", PATHWAY_INFERENCE_DECISIONS)
    UNKNOWN_GENE_STATUSES = _schema_set(schema, "unknown_gene_statuses", UNKNOWN_GENE_STATUSES)
    LITERATURE_SEARCH_STATUSES = _schema_set(schema, "literature_search_statuses", LITERATURE_SEARCH_STATUSES)
    SEQUENCE_SEARCH_TOOLS = _schema_set(schema, "sequence_search_tools", SEQUENCE_SEARCH_TOOLS)
    SEQUENCE_SCOPES = _schema_set(schema, "sequence_scopes", SEQUENCE_SCOPES)
    SEQUENCE_TYPES = _schema_set(schema, "sequence_types", SEQUENCE_TYPES)
    DOMAIN_MAP_STATUSES = _schema_set(schema, "domain_map_statuses", DOMAIN_MAP_STATUSES)
    DOMAIN_CONFIDENCE = _schema_set(schema, "domain_confidence", DOMAIN_CONFIDENCE)
    INTELLIGENCE_TYPES = _schema_set(schema, "intelligence_types", INTELLIGENCE_TYPES)
    INTELLIGENCE_SOURCE_SCOPES = _schema_set(schema, "intelligence_source_scopes", INTELLIGENCE_SOURCE_SCOPES)
    INTELLIGENCE_CONFIDENCE = _schema_set(schema, "intelligence_confidence", INTELLIGENCE_CONFIDENCE)
    INTELLIGENCE_ACTIONABILITY = _schema_set(schema, "intelligence_actionability", INTELLIGENCE_ACTIONABILITY)
    CANDIDATE_NOVELTY_LEVELS = _schema_set(schema, "candidate_novelty_levels", CANDIDATE_NOVELTY_LEVELS)
    CANDIDATE_SELECTION_STATUSES = _schema_set(schema, "candidate_selection_statuses", CANDIDATE_SELECTION_STATUSES)
    GRAPH_EDGE_TYPES = _schema_set(schema, "graph_edge_types", GRAPH_EDGE_TYPES)
    RUN_PACKAGE_TYPES = _schema_set(schema, "run_package_types", RUN_PACKAGE_TYPES)
    RUN_PACKAGE_STATUSES = _schema_set(schema, "run_package_statuses", RUN_PACKAGE_STATUSES)
    RISK_VERDICTS = _schema_set(schema, "risk_verdicts", RISK_VERDICTS)
    HOST_VERDICTS = _schema_set(schema, "host_verdicts", HOST_VERDICTS)
    ASSAY_BOUNDARY_FLAGS = _schema_set(schema, "assay_boundary_flags", ASSAY_BOUNDARY_FLAGS)
    MONITORING_HEARTBEATS = _schema_set(schema, "monitoring_heartbeats", MONITORING_HEARTBEATS)
    SELF_LEARNING_HICCUP_TYPES = _schema_set(schema, "self_learning_hiccup_types", SELF_LEARNING_HICCUP_TYPES)
    SELF_LEARNING_DECISIONS = _schema_set(schema, "self_learning_decisions", SELF_LEARNING_DECISIONS)
    OPERATOR_INTAKE_AREAS = _schema_set(schema, "operator_intake_areas", OPERATOR_INTAKE_AREAS)
    OPERATOR_INTAKE_STATUSES = _schema_set(schema, "operator_intake_statuses", OPERATOR_INTAKE_STATUSES)
    OPERATOR_INTAKE_REQUIRED_BEFORE = _schema_set(schema, "operator_intake_required_before", OPERATOR_INTAKE_REQUIRED_BEFORE)
    INPUT_CLASSES = _schema_set(schema, "input_classes", INPUT_CLASSES)
    MATERIALIZED_STATUSES = _schema_set(schema, "materialized_statuses", MATERIALIZED_STATUSES)
    BOOLEAN_FLAGS = _schema_set(schema, "boolean_flags", BOOLEAN_FLAGS)
    MATURITY_LEVELS = _schema_set(schema, "maturity_levels", MATURITY_LEVELS)
    STAGE_REQUIRED_FOR_MATURITY = _schema_set(schema, "stage_required_for_maturity", STAGE_REQUIRED_FOR_MATURITY)
    MATURITY_STATUSES = _schema_set(schema, "maturity_statuses", MATURITY_STATUSES)
    STAGE_STATUSES = _schema_set(schema, "stage_statuses", STAGE_STATUSES)
    STAGE_PROGRESS_STATUSES = _schema_set(schema, "stage_progress_statuses", STAGE_PROGRESS_STATUSES)
    DEGRADED_STATUSES = _schema_set(schema, "degraded_statuses", DEGRADED_STATUSES)
    ORGANISM_SAMPLE_ROLES = _schema_set(schema, "organism_sample_roles", ORGANISM_SAMPLE_ROLES)
    ORGANISM_DATA_STATUSES = _schema_set(schema, "organism_data_statuses", ORGANISM_DATA_STATUSES)
    QUERY_TYPES = _schema_set(schema, "query_types", QUERY_TYPES)
    DATASET_TYPES = _schema_set(schema, "dataset_types", DATASET_TYPES)
    TARGET_EVIDENCE_ROLES = _schema_set(schema, "target_evidence_roles", TARGET_EVIDENCE_ROLES)
    TARGET_EVIDENCE_TYPES = _schema_set(schema, "target_evidence_types", TARGET_EVIDENCE_TYPES)
    JOIN_STATUSES = _schema_set(schema, "join_statuses", JOIN_STATUSES)
    DECOY_CONTROL_TYPES = _schema_set(schema, "decoy_control_types", DECOY_CONTROL_TYPES)
    CONTROL_STATUSES = _schema_set(schema, "control_statuses", CONTROL_STATUSES)
    EXECUTION_ARTIFACT_STATUSES = _schema_set(schema, "execution_artifact_statuses", EXECUTION_ARTIFACT_STATUSES)
    COMPUTE_PROVIDER_CLASSES = _schema_set(schema, "compute_provider_classes", COMPUTE_PROVIDER_CLASSES)
    COMPUTE_PROVIDER_ROLES = _schema_set(schema, "compute_provider_roles", COMPUTE_PROVIDER_ROLES)
    COMPUTE_PROVIDER_STATUSES = _schema_set(schema, "compute_provider_statuses", COMPUTE_PROVIDER_STATUSES)
    PROVIDER_PREFLIGHT_CHECK_TYPES = _schema_set(schema, "provider_preflight_check_types", PROVIDER_PREFLIGHT_CHECK_TYPES)
    PROVIDER_PREFLIGHT_STATUSES = _schema_set(schema, "provider_preflight_statuses", PROVIDER_PREFLIGHT_STATUSES)
    WORKFLOW_FRAMEWORK_CLASSES = _schema_set(schema, "workflow_framework_classes", WORKFLOW_FRAMEWORK_CLASSES)
    WORKFLOW_FRAMEWORK_STATUSES = _schema_set(schema, "workflow_framework_statuses", WORKFLOW_FRAMEWORK_STATUSES)
    TOOL_CLASSES = _schema_set(schema, "tool_classes", TOOL_CLASSES)
    ADAPTER_STATUSES = _schema_set(schema, "adapter_statuses", ADAPTER_STATUSES)
    EVIDENCE_EVENT_TYPES = _schema_set(schema, "evidence_event_types", EVIDENCE_EVENT_TYPES)
    PRIVATE_DATA_STATUSES = _schema_set(schema, "private_data_statuses", PRIVATE_DATA_STATUSES)
    TOOL_PROOF_STATUSES = _schema_set(schema, "tool_proof_statuses", TOOL_PROOF_STATUSES)
    ACTIVE_PROVIDER_STATUSES = _schema_set(schema, "active_provider_statuses", ACTIVE_PROVIDER_STATUSES)
    ACTIVE_FRAMEWORK_STATUSES = _schema_set(schema, "active_framework_statuses", ACTIVE_FRAMEWORK_STATUSES)
    NON_DEFAULT_BLESSED_PROVIDER_ROLES = _schema_set(
        schema, "non_default_blessed_provider_roles", NON_DEFAULT_BLESSED_PROVIDER_ROLES
    )
    NON_DEFAULT_BLESSED_PROVIDER_CLASSES = _schema_set(
        schema, "non_default_blessed_provider_classes", NON_DEFAULT_BLESSED_PROVIDER_CLASSES
    )


_apply_external_schema()

IGNORED_ARTIFACT_SCAN_DIRS = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".runtime",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "env",
    "node_modules",
    "out",
    "temp",
    "tmp",
    "venv",
}

BIOLOGICAL_DATA_SUFFIXES = {
    ".2bit",
    ".aln",
    ".amb",
    ".ann",
    ".bam",
    ".bcf",
    ".bcif",
    ".bt2",
    ".bt2l",
    ".bwt",
    ".cif",
    ".cram",
    ".dmnd",
    ".fa",
    ".faa",
    ".fasta",
    ".ffn",
    ".fna",
    ".fq",
    ".gb",
    ".gbff",
    ".gbk",
    ".gff",
    ".gff3",
    ".gtf",
    ".hmm",
    ".mmi",
    ".msa",
    ".pdb",
    ".phr",
    ".pin",
    ".psq",
    ".sam",
    ".sto",
    ".vcf",
}

COMPRESSED_BIOLOGICAL_SUFFIXES = {
    f"{suffix}.gz" for suffix in BIOLOGICAL_DATA_SUFFIXES
} | {
    f"{suffix}.bgz" for suffix in BIOLOGICAL_DATA_SUFFIXES
}

MODEL_WEIGHT_SUFFIXES = {
    ".ckpt",
    ".h5",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
}

BIOLOGICAL_ARCHIVE_NAME_TOKENS = {
    "alphafold",
    "blast",
    "genbank",
    "genome",
    "metagenome",
    "mmseqs",
    "proteome",
    "reads",
    "uniprot",
    "uniref",
}

ARCHIVE_SUFFIXES = {
    ".tar",
    ".tar.gz",
    ".tgz",
    ".zip",
}

MAX_LOCAL_ARTIFACT_BYTES = 25 * 1024 * 1024


@dataclass
class CheckResult:
    ok: bool
    message: str


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        headers = list(reader.fieldnames or [])
        return headers, list(reader)


def missing(required: Iterable[str], actual: Iterable[str]) -> list[str]:
    actual_set = set(actual)
    return [field for field in required if field not in actual_set]


def invalid_values(rows: Iterable[dict[str, str]], column: str, allowed: set[str]) -> list[str]:
    values = {
        row.get(column, "").strip()
        for row in rows
        if row.get(column, "").strip() not in allowed
    }
    return sorted(values)


def strict_validation_rows_with_review_terms(rows: Iterable[dict[str, str]]) -> list[str]:
    invalid: list[str] = []
    for index, row in enumerate(rows, start=2):
        levels = {row.get("claim_level", "").strip(), row.get("evidence_level", "").strip()}
        if not levels.intersection(STRICT_VALIDATION_LEVELS):
            continue
        row_text = "\t".join(str(value).lower() for value in row.values())
        if not any(term in row_text for term in REVIEW_PENDING_TERMS):
            continue
        row_id = (
            row.get("candidate_id")
            or row.get("route_id")
            or row.get("evidence_id")
            or row.get("intelligence_id")
            or f"line {index}"
        )
        invalid.append(str(row_id))
    return invalid


def invalid_float_range(
    rows: Iterable[dict[str, str]],
    column: str,
    *,
    minimum_exclusive: float | None = None,
    maximum_exclusive: float | None = None,
) -> list[str]:
    invalid: set[str] = set()
    for row in rows:
        value = row.get(column, "").strip()
        if not value:
            invalid.add(value)
            continue
        try:
            parsed = float(value)
        except ValueError:
            invalid.add(value)
            continue
        if minimum_exclusive is not None and parsed <= minimum_exclusive:
            invalid.add(value)
        if maximum_exclusive is not None and parsed >= maximum_exclusive:
            invalid.add(value)
    return sorted(invalid)


def invalid_int_range(
    rows: Iterable[dict[str, str]],
    column: str,
    *,
    minimum_inclusive: int | None = None,
    maximum_inclusive: int | None = None,
) -> list[str]:
    invalid: set[str] = set()
    for row in rows:
        value = row.get(column, "").strip()
        if not value:
            invalid.add(value)
            continue
        try:
            parsed = int(value)
        except ValueError:
            invalid.add(value)
            continue
        if minimum_inclusive is not None and parsed < minimum_inclusive:
            invalid.add(value)
        if maximum_inclusive is not None and parsed > maximum_inclusive:
            invalid.add(value)
    return sorted(invalid)


def invalid_json_values(rows: Iterable[dict[str, str]], column: str) -> list[str]:
    invalid: set[str] = set()
    for row in rows:
        value = row.get(column, "").strip()
        if not value or value in {"{}", "[]", "not_applicable"}:
            continue
        try:
            json.loads(value)
        except json.JSONDecodeError:
            invalid.add(value)
    return sorted(invalid)


def markdown_table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def is_markdown_separator(cells: list[str]) -> bool:
    return all(cell.replace("-", "").replace(":", "").strip() == "" for cell in cells)


def check_manifest(path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    manifest = load_json(path)
    manifest_missing = missing(REQUIRED_MANIFEST_FIELDS, manifest)
    results.append(
        CheckResult(
            not manifest_missing,
            f"manifest required fields: {'ok' if not manifest_missing else ', '.join(manifest_missing)}",
        )
    )

    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict):
        results.append(CheckResult(False, "manifest ledgers must be an object"))
        return results

    unknown_ledgers = sorted(set(ledgers) - KNOWN_LEDGER_KEYS)
    results.append(
        CheckResult(
            not unknown_ledgers,
            f"manifest ledger keys: {'ok' if not unknown_ledgers else ', '.join(unknown_ledgers)}",
        )
    )

    ledger_missing = missing(REQUIRED_LEDGER_KEYS, ledgers)
    results.append(
        CheckResult(
            not ledger_missing,
            f"manifest ledgers: {'ok' if not ledger_missing else ', '.join(ledger_missing)}",
        )
    )

    required_ledgers = manifest.get("required_ledgers", [])
    if required_ledgers:
        if not isinstance(required_ledgers, list) or not all(isinstance(key, str) for key in required_ledgers):
            results.append(CheckResult(False, "manifest required_ledgers must be a list of ledger keys"))
        else:
            unknown_required = sorted(set(required_ledgers) - KNOWN_LEDGER_KEYS)
            required_missing = missing(required_ledgers, ledgers)
            results.append(
                CheckResult(
                    not unknown_required,
                    "manifest required_ledgers keys: "
                    f"{'ok' if not unknown_required else ', '.join(unknown_required)}",
                )
            )
            results.append(
                CheckResult(
                    not required_missing,
                    "manifest required_ledgers present: "
                    f"{'ok' if not required_missing else ', '.join(required_missing)}",
                )
            )

    base = path.parent
    for key, rel in ledgers.items():
        ledger_path = resolve_declared_path(base, rel)
        if ledger_path is None:
            results.append(CheckResult(False, f"{key} path stays inside campaign directory"))
            continue
        results.append(CheckResult(ledger_path.exists(), f"{key} exists: {display_path(ledger_path)}"))
        if key == "runpod_run_manifest" and ledger_path.exists() and ledger_path.suffix == ".json":
            try:
                load_json(ledger_path)
            except json.JSONDecodeError as exc:
                results.append(CheckResult(False, f"runpod_run_manifest JSON parses: {exc}"))
            else:
                results.append(CheckResult(True, "runpod_run_manifest JSON parses"))

    target_contract = resolve_declared_path(base, manifest.get("target_contract", ""))
    if target_contract is None:
        results.append(CheckResult(False, "target contract path stays inside campaign directory"))
    else:
        results.append(CheckResult(target_contract.exists(), f"target contract exists: {display_path(target_contract)}"))

    if target_contract is not None and target_contract.exists():
        contract = load_json(target_contract)
        for field in ["target_molecule", "host", "campaign_goal", "optimization_goals", "hard_boundaries"]:
            results.append(CheckResult(field in contract, f"target contract field `{field}` present"))

    if manifest.get("scope") != "planning_only":
        results.append(CheckResult(False, "scope should remain `planning_only` until execution policies are added"))

    return results


def check_claim_ledger(manifest_path: Path) -> list[CheckResult]:
    manifest = load_json(manifest_path)
    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict):
        return []
    rel = ledgers.get("claim_ledger")
    if not rel:
        return []

    path = resolve_declared_path(manifest_path.parent, rel)
    if path is None:
        return [CheckResult(False, "claim_ledger path stays inside campaign directory")]
    if not path.exists():
        return []

    results: list[CheckResult] = []
    header: list[str] | None = None
    level_index: int | None = None
    invalid: set[str] = set()

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = markdown_table_cells(line)
        lowered = [cell.lower() for cell in cells]
        if "level" in lowered:
            header = lowered
            level_index = lowered.index("level")
            continue
        if header is None or level_index is None or is_markdown_separator(cells):
            continue
        if len(cells) <= level_index:
            continue
        level = cells[level_index].strip()
        if level and level not in CLAIM_LEVELS:
            invalid.add(level)

    results.append(
        CheckResult(
            not invalid,
            f"claim_ledger claim levels: {'ok' if not invalid else ', '.join(sorted(invalid))}",
        )
    )
    return results


def check_tsv_ledgers(manifest_path: Path) -> list[CheckResult]:
    manifest = load_json(manifest_path)
    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict):
        return []
    base = manifest_path.parent
    results: list[CheckResult] = []
    ledger_rows_by_key: dict[str, list[dict[str, str]]] = {}

    for key, required_headers in REQUIRED_HEADERS.items():
        rel = ledgers.get(key)
        if not rel:
            continue
        path = resolve_declared_path(base, rel)
        if path is None:
            results.append(CheckResult(False, f"{key} path stays inside campaign directory"))
            continue
        if not path.exists():
            continue
        headers, rows = read_tsv(path)
        ledger_rows_by_key[key] = rows
        header_missing = missing(required_headers, headers)
        results.append(
            CheckResult(
                not header_missing,
                f"{key} headers: {'ok' if not header_missing else ', '.join(header_missing)}",
            )
        )
        if key != "enzyme_draft_board":
            results.append(CheckResult(bool(rows), f"{key} has at least one row"))

        strict_validation_review_rows = strict_validation_rows_with_review_terms(rows)
        results.append(
            CheckResult(
                not strict_validation_review_rows,
                f"{key} strict validation review caveats: "
                f"{'ok' if not strict_validation_review_rows else ', '.join(strict_validation_review_rows)}",
            )
        )

        if key == "reaction_step_ledger" and "candidate_search_width" in headers:
            invalid_widths = invalid_values(rows, "candidate_search_width", SEARCH_WIDTHS)
            results.append(
                CheckResult(
                    not invalid_widths,
                    f"reaction_step_ledger search widths: {'ok' if not invalid_widths else ', '.join(invalid_widths)}",
                )
            )

        if key == "unknown_step_ledger" and "candidate_search_width" in headers:
            invalid_widths = invalid_values(rows, "candidate_search_width", SEARCH_WIDTHS)
            results.append(
                CheckResult(
                    not invalid_widths,
                    f"unknown_step_ledger search widths: {'ok' if not invalid_widths else ', '.join(invalid_widths)}",
                )
            )

        if key in {"route_ledger", "route_stitching_scorecard"} and "route_status" in headers:
            invalid_statuses = invalid_values(rows, "route_status", ROUTE_STATUSES)
            results.append(
                CheckResult(
                    not invalid_statuses,
                    f"{key} route statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                )
            )

        if key == "route_ledger" and "evidence_level" in headers:
            invalid_claims = invalid_values(rows, "evidence_level", CLAIM_LEVELS)
            results.append(
                CheckResult(
                    not invalid_claims,
                    f"route_ledger evidence levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                )
            )

        if key == "enzyme_draft_board" and "claim_level" in headers:
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.append(
                CheckResult(
                    not invalid_claims,
                    f"enzyme_draft_board claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                )
            )

        if key == "rejected_candidates" and "claim_level" in headers:
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.append(
                CheckResult(
                    not invalid_claims,
                    f"rejected_candidates claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                )
            )

        if key == "literature_ledger":
            invalid_evidence = invalid_values(rows, "evidence_class", EVIDENCE_CLASSES)
            results.append(
                CheckResult(
                    not invalid_evidence,
                    f"literature_ledger evidence classes: {'ok' if not invalid_evidence else ', '.join(invalid_evidence)}",
                )
            )

        if key == "pathway_inference_ledger":
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            invalid_decisions = invalid_values(rows, "decision", PATHWAY_INFERENCE_DECISIONS)
            results.extend(
                [
                    CheckResult(
                        not invalid_claims,
                        "pathway_inference_ledger claim levels: "
                        f"{'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                    CheckResult(
                        not invalid_decisions,
                        "pathway_inference_ledger decisions: "
                        f"{'ok' if not invalid_decisions else ', '.join(invalid_decisions)}",
                    ),
                ]
            )

        if key == "unknown_gene_hypothesis_ledger":
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            invalid_statuses = invalid_values(rows, "status", UNKNOWN_GENE_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_claims,
                        "unknown_gene_hypothesis_ledger claim levels: "
                        f"{'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "unknown_gene_hypothesis_ledger statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "enzyme_family_sweep":
            invalid_raw_hits = invalid_int_range(rows, "raw_hits", minimum_inclusive=0)
            invalid_clusters = invalid_int_range(rows, "clusters", minimum_inclusive=0)
            invalid_representatives = invalid_int_range(rows, "representatives", minimum_inclusive=0)
            results.extend(
                [
                    CheckResult(
                        not invalid_raw_hits,
                        f"enzyme_family_sweep raw_hits: {'ok' if not invalid_raw_hits else ', '.join(invalid_raw_hits)}",
                    ),
                    CheckResult(
                        not invalid_clusters,
                        f"enzyme_family_sweep clusters: {'ok' if not invalid_clusters else ', '.join(invalid_clusters)}",
                    ),
                    CheckResult(
                        not invalid_representatives,
                        "enzyme_family_sweep representatives: "
                        f"{'ok' if not invalid_representatives else ', '.join(invalid_representatives)}",
                    ),
                ]
            )

        if key == "literature_search_ledger":
            invalid_statuses = invalid_values(rows, "status", LITERATURE_SEARCH_STATUSES)
            invalid_recency = invalid_int_range(rows, "recency_window_days", minimum_inclusive=0)
            invalid_result_cap = invalid_int_range(rows, "result_cap", minimum_inclusive=1, maximum_inclusive=500)
            results.extend(
                [
                    CheckResult(
                        not invalid_statuses,
                        "literature_search_ledger statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_recency,
                        "literature_search_ledger recency windows: "
                        f"{'ok' if not invalid_recency else ', '.join(invalid_recency)}",
                    ),
                    CheckResult(
                        not invalid_result_cap,
                        "literature_search_ledger result caps: "
                        f"{'ok' if not invalid_result_cap else ', '.join(invalid_result_cap)}",
                    ),
                ]
            )

        if key == "sequence_search_plan_ledger":
            invalid_tools = invalid_values(rows, "search_tool", SEQUENCE_SEARCH_TOOLS)
            invalid_scopes = invalid_values(rows, "sequence_scope", SEQUENCE_SCOPES)
            invalid_hits = invalid_int_range(rows, "max_hits", minimum_inclusive=1, maximum_inclusive=20000)
            invalid_budgets = invalid_float_range(rows, "budget_usd", minimum_exclusive=0, maximum_exclusive=100)
            invalid_approval = invalid_values(rows, "approval_status", LANE_APPROVAL_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_tools,
                        "sequence_search_plan_ledger search tools: "
                        f"{'ok' if not invalid_tools else ', '.join(invalid_tools)}",
                    ),
                    CheckResult(
                        not invalid_scopes,
                        "sequence_search_plan_ledger sequence scopes: "
                        f"{'ok' if not invalid_scopes else ', '.join(invalid_scopes)}",
                    ),
                    CheckResult(
                        not invalid_hits,
                        f"sequence_search_plan_ledger max_hits: {'ok' if not invalid_hits else ', '.join(invalid_hits)}",
                    ),
                    CheckResult(
                        not invalid_budgets,
                        "sequence_search_plan_ledger budgets: "
                        f"{'ok' if not invalid_budgets else ', '.join(invalid_budgets)}",
                    ),
                    CheckResult(
                        not invalid_approval,
                        "sequence_search_plan_ledger approval statuses: "
                        f"{'ok' if not invalid_approval else ', '.join(invalid_approval)}",
                    ),
                ]
            )

        if key == "candidate_sequence_ledger":
            invalid_types = invalid_values(rows, "sequence_type", SEQUENCE_TYPES)
            invalid_lengths = invalid_int_range(rows, "aa_length", minimum_inclusive=0)
            invalid_domain_statuses = invalid_values(rows, "domain_map_status", DOMAIN_MAP_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_types,
                        f"candidate_sequence_ledger sequence types: {'ok' if not invalid_types else ', '.join(invalid_types)}",
                    ),
                    CheckResult(
                        not invalid_lengths,
                        f"candidate_sequence_ledger aa lengths: {'ok' if not invalid_lengths else ', '.join(invalid_lengths)}",
                    ),
                    CheckResult(
                        not invalid_domain_statuses,
                        "candidate_sequence_ledger domain map statuses: "
                        f"{'ok' if not invalid_domain_statuses else ', '.join(invalid_domain_statuses)}",
                    ),
                ]
            )

        if key == "domain_annotation_ledger":
            invalid_starts = invalid_int_range(rows, "domain_start", minimum_inclusive=0)
            invalid_ends = invalid_int_range(rows, "domain_end", minimum_inclusive=0)
            invalid_confidence = invalid_values(rows, "confidence", DOMAIN_CONFIDENCE)
            invalid_ranges = sorted(
                {
                    row.get("annotation_id", "")
                    for row in rows
                    if row.get("domain_start", "").strip().isdigit()
                    and row.get("domain_end", "").strip().isdigit()
                    and int(row["domain_start"]) > int(row["domain_end"])
                    and int(row["domain_end"]) != 0
                }
            )
            results.extend(
                [
                    CheckResult(
                        not invalid_starts,
                        f"domain_annotation_ledger domain starts: {'ok' if not invalid_starts else ', '.join(invalid_starts)}",
                    ),
                    CheckResult(
                        not invalid_ends,
                        f"domain_annotation_ledger domain ends: {'ok' if not invalid_ends else ', '.join(invalid_ends)}",
                    ),
                    CheckResult(
                        not invalid_ranges,
                        "domain_annotation_ledger ranges: "
                        f"{'ok' if not invalid_ranges else ', '.join(invalid_ranges)}",
                    ),
                    CheckResult(
                        not invalid_confidence,
                        "domain_annotation_ledger confidence: "
                        f"{'ok' if not invalid_confidence else ', '.join(invalid_confidence)}",
                    ),
                ]
            )

        if key == "candidate_intelligence_ledger":
            invalid_types = invalid_values(rows, "intelligence_type", INTELLIGENCE_TYPES)
            invalid_scopes = invalid_values(rows, "source_scope", INTELLIGENCE_SOURCE_SCOPES)
            invalid_confidence = invalid_values(rows, "confidence", INTELLIGENCE_CONFIDENCE)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            invalid_actionability = invalid_values(rows, "actionability", INTELLIGENCE_ACTIONABILITY)
            results.extend(
                [
                    CheckResult(
                        not invalid_types,
                        "candidate_intelligence_ledger intelligence types: "
                        f"{'ok' if not invalid_types else ', '.join(invalid_types)}",
                    ),
                    CheckResult(
                        not invalid_scopes,
                        "candidate_intelligence_ledger source scopes: "
                        f"{'ok' if not invalid_scopes else ', '.join(invalid_scopes)}",
                    ),
                    CheckResult(
                        not invalid_confidence,
                        "candidate_intelligence_ledger confidence: "
                        f"{'ok' if not invalid_confidence else ', '.join(invalid_confidence)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        "candidate_intelligence_ledger claim levels: "
                        f"{'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                    CheckResult(
                        not invalid_actionability,
                        "candidate_intelligence_ledger actionability: "
                        f"{'ok' if not invalid_actionability else ', '.join(invalid_actionability)}",
                    ),
                ]
            )

        if key == "candidate_diversity_ledger":
            invalid_novelty = invalid_values(rows, "novelty_level", CANDIDATE_NOVELTY_LEVELS)
            invalid_statuses = invalid_values(rows, "selection_status", CANDIDATE_SELECTION_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_novelty,
                        "candidate_diversity_ledger novelty levels: "
                        f"{'ok' if not invalid_novelty else ', '.join(invalid_novelty)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "candidate_diversity_ledger selection statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "candidate_graph_ledger":
            invalid_edge_types = invalid_values(rows, "edge_type", GRAPH_EDGE_TYPES)
            invalid_evidence = invalid_values(rows, "evidence_class", EVIDENCE_CLASSES)
            invalid_weights = invalid_float_range(rows, "weight", minimum_exclusive=-0.01)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.extend(
                [
                    CheckResult(
                        not invalid_edge_types,
                        "candidate_graph_ledger edge types: "
                        f"{'ok' if not invalid_edge_types else ', '.join(invalid_edge_types)}",
                    ),
                    CheckResult(
                        not invalid_evidence,
                        "candidate_graph_ledger evidence classes: "
                        f"{'ok' if not invalid_evidence else ', '.join(invalid_evidence)}",
                    ),
                    CheckResult(
                        not invalid_weights,
                        f"candidate_graph_ledger weights: {'ok' if not invalid_weights else ', '.join(invalid_weights)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        f"candidate_graph_ledger claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                ]
            )

        if key == "run_output_package_ledger":
            invalid_package_types = invalid_values(rows, "package_type", RUN_PACKAGE_TYPES)
            invalid_statuses = invalid_values(rows, "status", RUN_PACKAGE_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_package_types,
                        "run_output_package_ledger package types: "
                        f"{'ok' if not invalid_package_types else ', '.join(invalid_package_types)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "run_output_package_ledger statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "genome_mining_plan":
            invalid_budgets = invalid_float_range(rows, "budget_usd", minimum_exclusive=0, maximum_exclusive=100)
            invalid_approval = invalid_values(rows, "approval_status", LANE_APPROVAL_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_budgets,
                        f"genome_mining_plan budgets: {'ok' if not invalid_budgets else ', '.join(invalid_budgets)}",
                    ),
                    CheckResult(
                        not invalid_approval,
                        "genome_mining_plan approval statuses: "
                        f"{'ok' if not invalid_approval else ', '.join(invalid_approval)}",
                    ),
                ]
            )

        if key == "genome_hit_ledger":
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.append(
                CheckResult(
                    not invalid_claims,
                    f"genome_hit_ledger claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                )
            )

        if key == "structure_risk_ledger":
            invalid_verdicts = invalid_values(rows, "verdict", RISK_VERDICTS)
            results.append(
                CheckResult(
                    not invalid_verdicts,
                    f"structure_risk_ledger verdicts: {'ok' if not invalid_verdicts else ', '.join(invalid_verdicts)}",
                )
            )

        if key == "host_comparison_ledger":
            invalid_verdicts = invalid_values(rows, "verdict", HOST_VERDICTS)
            results.append(
                CheckResult(
                    not invalid_verdicts,
                    f"host_comparison_ledger verdicts: {'ok' if not invalid_verdicts else ', '.join(invalid_verdicts)}",
                )
            )

        if key == "assay_handoff_ledger":
            invalid_flags = invalid_values(rows, "non_protocol_boundary", ASSAY_BOUNDARY_FLAGS)
            results.append(
                CheckResult(
                    not invalid_flags,
                    f"assay_handoff_ledger non_protocol_boundary: {'ok' if not invalid_flags else ', '.join(invalid_flags)}",
                )
            )

        if key == "monitoring_ledger":
            invalid_heartbeats = invalid_values(rows, "heartbeat_status", MONITORING_HEARTBEATS)
            results.append(
                CheckResult(
                    not invalid_heartbeats,
                    f"monitoring_ledger heartbeat statuses: {'ok' if not invalid_heartbeats else ', '.join(invalid_heartbeats)}",
                )
            )

        if key == "self_learning_skill_ledger":
            invalid_hiccups = invalid_values(rows, "hiccup_type", SELF_LEARNING_HICCUP_TYPES)
            invalid_decisions = invalid_values(rows, "decision", SELF_LEARNING_DECISIONS)
            invalid_runbook = invalid_values(rows, "runbook_update", BOOLEAN_FLAGS)
            invalid_skill = invalid_values(rows, "skill_update", BOOLEAN_FLAGS)
            invalid_guardrail = invalid_values(rows, "reusable_guardrail", BOOLEAN_FLAGS)
            results.extend(
                [
                    CheckResult(
                        not invalid_hiccups,
                        "self_learning_skill_ledger hiccup types: "
                        f"{'ok' if not invalid_hiccups else ', '.join(invalid_hiccups)}",
                    ),
                    CheckResult(
                        not invalid_decisions,
                        "self_learning_skill_ledger decisions: "
                        f"{'ok' if not invalid_decisions else ', '.join(invalid_decisions)}",
                    ),
                    CheckResult(
                        not invalid_runbook,
                        "self_learning_skill_ledger runbook_update flags: "
                        f"{'ok' if not invalid_runbook else ', '.join(invalid_runbook)}",
                    ),
                    CheckResult(
                        not invalid_skill,
                        "self_learning_skill_ledger skill_update flags: "
                        f"{'ok' if not invalid_skill else ', '.join(invalid_skill)}",
                    ),
                    CheckResult(
                        not invalid_guardrail,
                        "self_learning_skill_ledger reusable_guardrail flags: "
                        f"{'ok' if not invalid_guardrail else ', '.join(invalid_guardrail)}",
                    ),
                ]
            )

        if key == "input_audit_ledger":
            invalid_classes = invalid_values(rows, "input_class", INPUT_CLASSES)
            invalid_statuses = invalid_values(rows, "materialized_status", MATERIALIZED_STATUSES)
            invalid_operator = invalid_values(rows, "operator_required", BOOLEAN_FLAGS)
            results.extend(
                [
                    CheckResult(
                        not invalid_classes,
                        f"input_audit_ledger input classes: {'ok' if not invalid_classes else ', '.join(invalid_classes)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "input_audit_ledger materialized statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_operator,
                        "input_audit_ledger operator_required flags: "
                        f"{'ok' if not invalid_operator else ', '.join(invalid_operator)}",
                    ),
                ]
            )

        if key == "operator_intake_ledger":
            invalid_areas = invalid_values(rows, "input_area", OPERATOR_INTAKE_AREAS)
            invalid_statuses = invalid_values(rows, "confirmation_status", OPERATOR_INTAKE_STATUSES)
            invalid_required = invalid_values(rows, "required_before", OPERATOR_INTAKE_REQUIRED_BEFORE)
            invalid_planning = invalid_values(rows, "planning_can_proceed", BOOLEAN_FLAGS)
            invalid_skip = invalid_values(rows, "skip_allowed", BOOLEAN_FLAGS)
            results.extend(
                [
                    CheckResult(
                        not invalid_areas,
                        "operator_intake_ledger input areas: "
                        f"{'ok' if not invalid_areas else ', '.join(invalid_areas)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "operator_intake_ledger confirmation statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_required,
                        "operator_intake_ledger required_before values: "
                        f"{'ok' if not invalid_required else ', '.join(invalid_required)}",
                    ),
                    CheckResult(
                        not invalid_planning,
                        "operator_intake_ledger planning_can_proceed flags: "
                        f"{'ok' if not invalid_planning else ', '.join(invalid_planning)}",
                    ),
                    CheckResult(
                        not invalid_skip,
                        "operator_intake_ledger skip_allowed flags: "
                        f"{'ok' if not invalid_skip else ', '.join(invalid_skip)}",
                    ),
                ]
            )

        if key == "run_maturity_ledger":
            invalid_levels = invalid_values(rows, "maturity_level", MATURITY_LEVELS)
            invalid_statuses = invalid_values(rows, "status", MATURITY_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_levels,
                        f"run_maturity_ledger maturity levels: {'ok' if not invalid_levels else ', '.join(invalid_levels)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"run_maturity_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "stage_contract_ledger":
            invalid_timeouts = invalid_int_range(rows, "timeout_minutes", minimum_inclusive=1)
            invalid_fail_closed = invalid_values(rows, "fail_closed", BOOLEAN_FLAGS)
            invalid_required = invalid_values(rows, "required_for_maturity", STAGE_REQUIRED_FOR_MATURITY)
            invalid_statuses = invalid_values(rows, "status", STAGE_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_timeouts,
                        f"stage_contract_ledger timeout minutes: {'ok' if not invalid_timeouts else ', '.join(invalid_timeouts)}",
                    ),
                    CheckResult(
                        not invalid_fail_closed,
                        "stage_contract_ledger fail_closed flags: "
                        f"{'ok' if not invalid_fail_closed else ', '.join(invalid_fail_closed)}",
                    ),
                    CheckResult(
                        not invalid_required,
                        "stage_contract_ledger required_for_maturity values: "
                        f"{'ok' if not invalid_required else ', '.join(invalid_required)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"stage_contract_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "stage_progress_ledger":
            invalid_event_statuses = invalid_values(rows, "event_status", STAGE_PROGRESS_STATUSES)
            invalid_heartbeat = invalid_int_range(rows, "heartbeat_age_minutes", minimum_inclusive=0)
            invalid_degraded = invalid_values(rows, "degraded_status", DEGRADED_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_event_statuses,
                        "stage_progress_ledger event statuses: "
                        f"{'ok' if not invalid_event_statuses else ', '.join(invalid_event_statuses)}",
                    ),
                    CheckResult(
                        not invalid_heartbeat,
                        "stage_progress_ledger heartbeat ages: "
                        f"{'ok' if not invalid_heartbeat else ', '.join(invalid_heartbeat)}",
                    ),
                    CheckResult(
                        not invalid_degraded,
                        "stage_progress_ledger degraded statuses: "
                        f"{'ok' if not invalid_degraded else ', '.join(invalid_degraded)}",
                    ),
                ]
            )

        if key == "organism_sample_ledger":
            invalid_roles = invalid_values(rows, "role", ORGANISM_SAMPLE_ROLES)
            invalid_statuses = invalid_values(rows, "data_status", ORGANISM_DATA_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_roles,
                        f"organism_sample_ledger roles: {'ok' if not invalid_roles else ', '.join(invalid_roles)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "organism_sample_ledger data statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "query_set_ledger":
            invalid_query_types = invalid_values(rows, "query_type", QUERY_TYPES)
            invalid_statuses = invalid_values(rows, "materialized_status", MATERIALIZED_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_query_types,
                        f"query_set_ledger query types: {'ok' if not invalid_query_types else ', '.join(invalid_query_types)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "query_set_ledger materialized statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "target_dataset_ledger":
            invalid_dataset_types = invalid_values(rows, "dataset_type", DATASET_TYPES)
            invalid_statuses = invalid_values(rows, "materialized_status", MATERIALIZED_STATUSES)
            invalid_roles = invalid_values(rows, "target_evidence_role", TARGET_EVIDENCE_ROLES)
            results.extend(
                [
                    CheckResult(
                        not invalid_dataset_types,
                        "target_dataset_ledger dataset types: "
                        f"{'ok' if not invalid_dataset_types else ', '.join(invalid_dataset_types)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "target_dataset_ledger materialized statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_roles,
                        "target_dataset_ledger evidence roles: "
                        f"{'ok' if not invalid_roles else ', '.join(invalid_roles)}",
                    ),
                ]
            )

        if key == "target_evidence_ledger":
            invalid_evidence_types = invalid_values(rows, "evidence_type", TARGET_EVIDENCE_TYPES)
            invalid_joins = invalid_values(rows, "join_status", JOIN_STATUSES)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.extend(
                [
                    CheckResult(
                        not invalid_evidence_types,
                        "target_evidence_ledger evidence types: "
                        f"{'ok' if not invalid_evidence_types else ', '.join(invalid_evidence_types)}",
                    ),
                    CheckResult(
                        not invalid_joins,
                        f"target_evidence_ledger join statuses: {'ok' if not invalid_joins else ', '.join(invalid_joins)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        f"target_evidence_ledger claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                ]
            )

        if key == "decoy_control_ledger":
            invalid_control_types = invalid_values(rows, "control_type", DECOY_CONTROL_TYPES)
            invalid_statuses = invalid_values(rows, "status", CONTROL_STATUSES)
            invalid_blocks = invalid_values(rows, "blocks_promotion", BOOLEAN_FLAGS)
            results.extend(
                [
                    CheckResult(
                        not invalid_control_types,
                        "decoy_control_ledger control types: "
                        f"{'ok' if not invalid_control_types else ', '.join(invalid_control_types)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"decoy_control_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_blocks,
                        "decoy_control_ledger blocks_promotion flags: "
                        f"{'ok' if not invalid_blocks else ', '.join(invalid_blocks)}",
                    ),
                ]
            )

        if key == "execution_artifact_ledger":
            invalid_dry_run = invalid_values(rows, "dry_run", BOOLEAN_FLAGS)
            invalid_mock_tools = invalid_values(rows, "mock_tools", BOOLEAN_FLAGS)
            invalid_statuses = invalid_values(rows, "status", EXECUTION_ARTIFACT_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_dry_run,
                        f"execution_artifact_ledger dry_run flags: {'ok' if not invalid_dry_run else ', '.join(invalid_dry_run)}",
                    ),
                    CheckResult(
                        not invalid_mock_tools,
                        "execution_artifact_ledger mock_tools flags: "
                        f"{'ok' if not invalid_mock_tools else ', '.join(invalid_mock_tools)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "execution_artifact_ledger statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "compute_provider_ledger":
            invalid_classes = invalid_values(rows, "provider_class", COMPUTE_PROVIDER_CLASSES)
            invalid_roles = invalid_values(rows, "role", COMPUTE_PROVIDER_ROLES)
            invalid_statuses = invalid_values(rows, "status", COMPUTE_PROVIDER_STATUSES)
            invalid_blessed = invalid_values(rows, "blessed_path", BOOLEAN_FLAGS)
            invalid_costs = invalid_float_range(rows, "cost_boundary_usd", minimum_exclusive=-0.01)
            blessed_rows = [row for row in rows if row.get("blessed_path", "").strip() == "true"]
            blessed_runpod = any(
                row.get("provider_class", "").strip().startswith("runpod_")
                and row.get("status", "").strip() in ACTIVE_PROVIDER_STATUSES
                for row in blessed_rows
            )
            inactive_blessed = sorted(
                {
                    row.get("provider_id", "").strip() or row.get("provider_class", "").strip()
                    for row in blessed_rows
                    if row.get("status", "").strip() not in ACTIVE_PROVIDER_STATUSES
                }
            )
            incompatible_blessed = sorted(
                {
                    row.get("provider_id", "").strip() or row.get("provider_class", "").strip()
                    for row in blessed_rows
                    if not row.get("provider_class", "").strip().startswith("runpod_")
                    and (
                        row.get("provider_class", "").strip() not in NON_DEFAULT_BLESSED_PROVIDER_CLASSES
                        or row.get("role", "").strip() not in NON_DEFAULT_BLESSED_PROVIDER_ROLES
                    )
                }
            )
            results.extend(
                [
                    CheckResult(
                        not invalid_classes,
                        f"compute_provider_ledger provider classes: {'ok' if not invalid_classes else ', '.join(invalid_classes)}",
                    ),
                    CheckResult(
                        not invalid_roles,
                        f"compute_provider_ledger roles: {'ok' if not invalid_roles else ', '.join(invalid_roles)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"compute_provider_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_blessed,
                        "compute_provider_ledger blessed_path flags: "
                        f"{'ok' if not invalid_blessed else ', '.join(invalid_blessed)}",
                    ),
                    CheckResult(
                        not invalid_costs,
                        f"compute_provider_ledger cost boundaries: {'ok' if not invalid_costs else ', '.join(invalid_costs)}",
                    ),
                    CheckResult(
                        blessed_runpod,
                        "compute_provider_ledger reviewed RunPod path: "
                        f"{'ok' if blessed_runpod else 'missing active runpod_* row with blessed_path=true'}",
                    ),
                    CheckResult(
                        not inactive_blessed,
                        "compute_provider_ledger active blessed paths: "
                        f"{'ok' if not inactive_blessed else ', '.join(inactive_blessed)}",
                    ),
                    CheckResult(
                        not incompatible_blessed,
                        "compute_provider_ledger non-default blessed path roles: "
                        f"{'ok' if not incompatible_blessed else ', '.join(incompatible_blessed)}",
                    ),
                ]
            )

        if key == "provider_launch_preflight_ledger":
            invalid_check_types = invalid_values(rows, "check_type", PROVIDER_PREFLIGHT_CHECK_TYPES)
            invalid_statuses = invalid_values(rows, "status", PROVIDER_PREFLIGHT_STATUSES)
            invalid_blocking = invalid_values(rows, "blocking_before_launch", BOOLEAN_FLAGS)
            results.extend(
                [
                    CheckResult(
                        not invalid_check_types,
                        "provider_launch_preflight_ledger check types: "
                        f"{'ok' if not invalid_check_types else ', '.join(invalid_check_types)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        "provider_launch_preflight_ledger statuses: "
                        f"{'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_blocking,
                        "provider_launch_preflight_ledger blocking flags: "
                        f"{'ok' if not invalid_blocking else ', '.join(invalid_blocking)}",
                    ),
                ]
            )

        if key == "workflow_framework_ledger":
            invalid_classes = invalid_values(rows, "framework_class", WORKFLOW_FRAMEWORK_CLASSES)
            invalid_resume = invalid_values(rows, "resume_supported", BOOLEAN_FLAGS)
            invalid_statuses = invalid_values(rows, "status", WORKFLOW_FRAMEWORK_STATUSES)
            invalid_provider_refs: set[str] = set()
            active_runpod_framework = False
            for row in rows:
                provider_refs = [
                    value.strip()
                    for value in row.get("provider_classes", "").replace(",", ";").split(";")
                    if value.strip()
                ]
                for provider_ref in provider_refs:
                    if provider_ref != "all_providers" and provider_ref not in COMPUTE_PROVIDER_CLASSES:
                        invalid_provider_refs.add(provider_ref)
                if row.get("status", "").strip() in ACTIVE_FRAMEWORK_STATUSES and (
                    "all_providers" in provider_refs or any(ref.startswith("runpod_") for ref in provider_refs)
                ):
                    active_runpod_framework = True
            results.extend(
                [
                    CheckResult(
                        not invalid_classes,
                        "workflow_framework_ledger framework classes: "
                        f"{'ok' if not invalid_classes else ', '.join(invalid_classes)}",
                    ),
                    CheckResult(
                        not invalid_resume,
                        "workflow_framework_ledger resume_supported flags: "
                        f"{'ok' if not invalid_resume else ', '.join(invalid_resume)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"workflow_framework_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_provider_refs,
                        "workflow_framework_ledger provider class refs: "
                        f"{'ok' if not invalid_provider_refs else ', '.join(sorted(invalid_provider_refs))}",
                    ),
                    CheckResult(
                        active_runpod_framework,
                        "workflow_framework_ledger active RunPod-compatible framework: "
                        f"{'ok' if active_runpod_framework else 'missing active runpod_* or all_providers framework'}",
                    ),
                ]
            )

        if key == "tool_registry_ledger":
            invalid_classes = invalid_values(rows, "tool_class", TOOL_CLASSES)
            invalid_statuses = invalid_values(rows, "status", ADAPTER_STATUSES)
            results.extend(
                [
                    CheckResult(
                        not invalid_classes,
                        f"tool_registry_ledger tool classes: {'ok' if not invalid_classes else ', '.join(invalid_classes)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"tool_registry_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                ]
            )

        if key == "adapter_contract_ledger":
            invalid_statuses = invalid_values(rows, "status", ADAPTER_STATUSES)
            results.append(
                CheckResult(
                    not invalid_statuses,
                    f"adapter_contract_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                )
            )

        if key == "evidence_event_ledger":
            invalid_event_types = invalid_values(rows, "event_type", EVIDENCE_EVENT_TYPES)
            invalid_evidence = invalid_values(rows, "evidence_class", EVIDENCE_CLASSES)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            invalid_joins = invalid_values(rows, "join_status", JOIN_STATUSES)
            invalid_raw_flags = invalid_values(rows, "raw_data_retained", BOOLEAN_FLAGS)
            raw_retained = sorted(
                {
                    row.get("event_id", "").strip()
                    for row in rows
                    if row.get("raw_data_retained", "").strip() == "true"
                }
            )
            invalid_private_statuses = invalid_values(rows, "private_data_status", PRIVATE_DATA_STATUSES)
            invalid_metrics = invalid_json_values(rows, "metrics_json")
            results.extend(
                [
                    CheckResult(
                        not invalid_event_types,
                        "evidence_event_ledger event types: "
                        f"{'ok' if not invalid_event_types else ', '.join(invalid_event_types)}",
                    ),
                    CheckResult(
                        not invalid_evidence,
                        "evidence_event_ledger evidence classes: "
                        f"{'ok' if not invalid_evidence else ', '.join(invalid_evidence)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        f"evidence_event_ledger claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                    CheckResult(
                        not invalid_joins,
                        f"evidence_event_ledger join statuses: {'ok' if not invalid_joins else ', '.join(invalid_joins)}",
                    ),
                    CheckResult(
                        not invalid_raw_flags,
                        "evidence_event_ledger raw_data_retained flags: "
                        f"{'ok' if not invalid_raw_flags else ', '.join(invalid_raw_flags)}",
                    ),
                    CheckResult(
                        not raw_retained,
                        "evidence_event_ledger raw data retained in repo: "
                        f"{'ok' if not raw_retained else ', '.join(raw_retained)}",
                    ),
                    CheckResult(
                        not invalid_private_statuses,
                        "evidence_event_ledger private data statuses: "
                        f"{'ok' if not invalid_private_statuses else ', '.join(invalid_private_statuses)}",
                    ),
                    CheckResult(
                        not invalid_metrics,
                        "evidence_event_ledger metrics_json: "
                        f"{'ok' if not invalid_metrics else ', '.join(invalid_metrics)}",
                    ),
                ]
            )

        if key == "tool_execution_proof_ledger":
            invalid_dry_run = invalid_values(rows, "dry_run", BOOLEAN_FLAGS)
            invalid_mock_tools = invalid_values(rows, "mock_tools", BOOLEAN_FLAGS)
            invalid_statuses = invalid_values(rows, "status", TOOL_PROOF_STATUSES)
            invalid_exit_statuses = sorted(
                {
                    row.get("exit_status", "").strip()
                    for row in rows
                    if row.get("exit_status", "").strip()
                    and row.get("exit_status", "").strip() not in {"planned", "not_applicable", "blocked"}
                    and not row.get("exit_status", "").strip().lstrip("-").isdigit()
                }
            )
            results.extend(
                [
                    CheckResult(
                        not invalid_dry_run,
                        f"tool_execution_proof_ledger dry_run flags: {'ok' if not invalid_dry_run else ', '.join(invalid_dry_run)}",
                    ),
                    CheckResult(
                        not invalid_mock_tools,
                        "tool_execution_proof_ledger mock_tools flags: "
                        f"{'ok' if not invalid_mock_tools else ', '.join(invalid_mock_tools)}",
                    ),
                    CheckResult(
                        not invalid_statuses,
                        f"tool_execution_proof_ledger statuses: {'ok' if not invalid_statuses else ', '.join(invalid_statuses)}",
                    ),
                    CheckResult(
                        not invalid_exit_statuses,
                        "tool_execution_proof_ledger exit_status values: "
                        f"{'ok' if not invalid_exit_statuses else ', '.join(invalid_exit_statuses)}",
                    ),
                ]
            )

        if key == "candidate_ranking_ledger":
            invalid_ranks = invalid_int_range(rows, "rank", minimum_inclusive=1)
            invalid_scores = invalid_float_range(rows, "score", minimum_exclusive=-0.01)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.extend(
                [
                    CheckResult(
                        not invalid_ranks,
                        f"candidate_ranking_ledger ranks: {'ok' if not invalid_ranks else ', '.join(invalid_ranks)}",
                    ),
                    CheckResult(
                        not invalid_scores,
                        f"candidate_ranking_ledger scores: {'ok' if not invalid_scores else ', '.join(invalid_scores)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        "candidate_ranking_ledger claim levels: "
                        f"{'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                ]
            )

        if key == "pareto_frontier_ledger":
            invalid_ranks = invalid_int_range(rows, "rank", minimum_inclusive=1)
            invalid_scores = invalid_float_range(rows, "score", minimum_exclusive=-0.01)
            invalid_claims = invalid_values(rows, "claim_level", CLAIM_LEVELS)
            results.extend(
                [
                    CheckResult(
                        not invalid_ranks,
                        f"pareto_frontier_ledger ranks: {'ok' if not invalid_ranks else ', '.join(invalid_ranks)}",
                    ),
                    CheckResult(
                        not invalid_scores,
                        f"pareto_frontier_ledger scores: {'ok' if not invalid_scores else ', '.join(invalid_scores)}",
                    ),
                    CheckResult(
                        not invalid_claims,
                        f"pareto_frontier_ledger claim levels: {'ok' if not invalid_claims else ', '.join(invalid_claims)}",
                    ),
                ]
            )

        if key == "elasticblast_search_plan":
            invalid_programs = invalid_values(rows, "program", ELASTICBLAST_PROGRAMS)
            invalid_providers = invalid_values(rows, "cloud_provider", ELASTICBLAST_CLOUD_PROVIDERS)
            invalid_approval = invalid_values(rows, "approval_status", ELASTICBLAST_APPROVAL_STATUSES)
            invalid_budgets = invalid_float_range(rows, "budget_usd", minimum_exclusive=0, maximum_exclusive=100)
            invalid_nodes = invalid_int_range(rows, "num_nodes", minimum_inclusive=1, maximum_inclusive=16)
            invalid_preemptible = invalid_values(rows, "use_preemptible", {"true", "false"})
            results.extend(
                [
                    CheckResult(
                        not invalid_programs,
                        "elasticblast_search_plan programs: "
                        f"{'ok' if not invalid_programs else ', '.join(invalid_programs)}",
                    ),
                    CheckResult(
                        not invalid_providers,
                        "elasticblast_search_plan cloud providers: "
                        f"{'ok' if not invalid_providers else ', '.join(invalid_providers)}",
                    ),
                    CheckResult(
                        not invalid_approval,
                        "elasticblast_search_plan approval statuses: "
                        f"{'ok' if not invalid_approval else ', '.join(invalid_approval)}",
                    ),
                    CheckResult(
                        not invalid_budgets,
                        "elasticblast_search_plan budgets: "
                        f"{'ok' if not invalid_budgets else ', '.join(invalid_budgets)}",
                    ),
                    CheckResult(
                        not invalid_nodes,
                        "elasticblast_search_plan num_nodes: "
                        f"{'ok' if not invalid_nodes else ', '.join(invalid_nodes)}",
                    ),
                    CheckResult(
                        not invalid_preemptible,
                        "elasticblast_search_plan use_preemptible: "
                        f"{'ok' if not invalid_preemptible else ', '.join(invalid_preemptible)}",
                    ),
                ]
            )

        if key == "elasticblast_run_ledger":
            invalid_run_statuses = invalid_values(rows, "status", ELASTICBLAST_RUN_STATUSES)
            invalid_providers = invalid_values(rows, "cloud_provider", ELASTICBLAST_CLOUD_PROVIDERS)
            invalid_cleanup = invalid_values(rows, "cleanup_status", ELASTICBLAST_CLEANUP_STATUSES)
            invalid_costs = invalid_float_range(rows, "estimated_cost_usd", minimum_exclusive=-0.01, maximum_exclusive=100)
            results.extend(
                [
                    CheckResult(
                        not invalid_run_statuses,
                        "elasticblast_run_ledger statuses: "
                        f"{'ok' if not invalid_run_statuses else ', '.join(invalid_run_statuses)}",
                    ),
                    CheckResult(
                        not invalid_providers,
                        "elasticblast_run_ledger cloud providers: "
                        f"{'ok' if not invalid_providers else ', '.join(invalid_providers)}",
                    ),
                    CheckResult(
                        not invalid_cleanup,
                        "elasticblast_run_ledger cleanup statuses: "
                        f"{'ok' if not invalid_cleanup else ', '.join(invalid_cleanup)}",
                    ),
                    CheckResult(
                        not invalid_costs,
                        "elasticblast_run_ledger estimated costs: "
                        f"{'ok' if not invalid_costs else ', '.join(invalid_costs)}",
                    ),
                ]
            )

        if key == "aws_safety_ledger":
            invalid_required = invalid_values(rows, "required_status", AWS_SAFETY_REQUIRED_STATUSES)
            invalid_blocking = invalid_values(rows, "blocking_before_submit", {"true", "false"})
            results.extend(
                [
                    CheckResult(
                        not invalid_required,
                        "aws_safety_ledger required statuses: "
                        f"{'ok' if not invalid_required else ', '.join(invalid_required)}",
                    ),
                    CheckResult(
                        not invalid_blocking,
                        "aws_safety_ledger blocking flags: "
                        f"{'ok' if not invalid_blocking else ', '.join(invalid_blocking)}",
                    ),
                ]
            )

    def values(key: str, column: str) -> set[str]:
        return {
            row.get(column, "").strip()
            for row in ledger_rows_by_key.get(key, [])
            if row.get(column, "").strip()
        }

    tool_ids = values("tool_registry_ledger", "tool_id")
    adapter_ids = values("adapter_contract_ledger", "adapter_id")
    step_ids = values("reaction_step_ledger", "step_id")
    candidate_ids = values("enzyme_draft_board", "candidate_id")
    query_ids = values("query_set_ledger", "query_id")

    if tool_ids and "adapter_contract_ledger" in ledger_rows_by_key:
        unknown_tool_refs = sorted(
            {
                row.get("tool_id", "").strip()
                for row in ledger_rows_by_key["adapter_contract_ledger"]
                if row.get("tool_id", "").strip() and row.get("tool_id", "").strip() not in tool_ids
            }
        )
        results.append(
            CheckResult(
                not unknown_tool_refs,
                "adapter_contract_ledger tool refs: "
                f"{'ok' if not unknown_tool_refs else ', '.join(unknown_tool_refs)}",
            )
        )

    if adapter_ids and "tool_registry_ledger" in ledger_rows_by_key:
        unknown_adapter_refs = sorted(
            {
                row.get("adapter_id", "").strip()
                for row in ledger_rows_by_key["tool_registry_ledger"]
                if row.get("adapter_id", "").strip() and row.get("adapter_id", "").strip() not in adapter_ids
            }
        )
        results.append(
            CheckResult(
                not unknown_adapter_refs,
                "tool_registry_ledger adapter refs: "
                f"{'ok' if not unknown_adapter_refs else ', '.join(unknown_adapter_refs)}",
            )
        )

    if "evidence_event_ledger" in ledger_rows_by_key:
        event_rows = ledger_rows_by_key["evidence_event_ledger"]
        if tool_ids:
            unknown_tools = sorted(
                {
                    row.get("event_id", "").strip()
                    for row in event_rows
                    if row.get("source_tool_id", "").strip()
                    and row.get("source_tool_id", "").strip() not in tool_ids
                }
            )
            results.append(
                CheckResult(
                    not unknown_tools,
                    "evidence_event_ledger source tool refs: "
                    f"{'ok' if not unknown_tools else ', '.join(unknown_tools)}",
                )
            )
        if adapter_ids:
            unknown_adapters = sorted(
                {
                    row.get("event_id", "").strip()
                    for row in event_rows
                    if row.get("adapter_id", "").strip()
                    and row.get("adapter_id", "").strip() not in adapter_ids
                }
            )
            results.append(
                CheckResult(
                    not unknown_adapters,
                    "evidence_event_ledger adapter refs: "
                    f"{'ok' if not unknown_adapters else ', '.join(unknown_adapters)}",
                )
            )
        unknown_steps = sorted(
            {
                row.get("event_id", "").strip()
                for row in event_rows
                if row.get("step_id", "").strip() and row.get("step_id", "").strip() not in step_ids
            }
        )
        unknown_candidates = sorted(
            {
                row.get("event_id", "").strip()
                for row in event_rows
                if row.get("candidate_id", "").strip()
                and candidate_ids
                and row.get("candidate_id", "").strip() not in candidate_ids
            }
        )
        unknown_queries = sorted(
            {
                row.get("event_id", "").strip()
                for row in event_rows
                if row.get("query_id", "").strip()
                and query_ids
                and row.get("query_id", "").strip() not in query_ids
            }
        )
        results.extend(
            [
                CheckResult(
                    not unknown_steps,
                    f"evidence_event_ledger step refs: {'ok' if not unknown_steps else ', '.join(unknown_steps)}",
                ),
                CheckResult(
                    not unknown_candidates,
                    "evidence_event_ledger candidate refs: "
                    f"{'ok' if not unknown_candidates else ', '.join(unknown_candidates)}",
                ),
                CheckResult(
                    not unknown_queries,
                    f"evidence_event_ledger query refs: {'ok' if not unknown_queries else ', '.join(unknown_queries)}",
                ),
            ]
        )

    if "tool_execution_proof_ledger" in ledger_rows_by_key:
        proof_rows = ledger_rows_by_key["tool_execution_proof_ledger"]
        if tool_ids:
            unknown_tools = sorted(
                {
                    row.get("proof_id", "").strip()
                    for row in proof_rows
                    if row.get("tool_id", "").strip() and row.get("tool_id", "").strip() not in tool_ids
                }
            )
            results.append(
                CheckResult(
                    not unknown_tools,
                    "tool_execution_proof_ledger tool refs: "
                    f"{'ok' if not unknown_tools else ', '.join(unknown_tools)}",
                )
            )
        if adapter_ids:
            unknown_adapters = sorted(
                {
                    row.get("proof_id", "").strip()
                    for row in proof_rows
                    if row.get("adapter_id", "").strip()
                    and row.get("adapter_id", "").strip() not in adapter_ids
                }
            )
            results.append(
                CheckResult(
                    not unknown_adapters,
                    "tool_execution_proof_ledger adapter refs: "
                    f"{'ok' if not unknown_adapters else ', '.join(unknown_adapters)}",
                )
            )

    if "candidate_ranking_ledger" in ledger_rows_by_key and candidate_ids:
        unknown_rank_candidates = sorted(
            {
                row.get("rank_id", "").strip()
                for row in ledger_rows_by_key["candidate_ranking_ledger"]
                if row.get("candidate_id", "").strip() not in candidate_ids
            }
        )
        results.append(
            CheckResult(
                not unknown_rank_candidates,
                "candidate_ranking_ledger candidate refs: "
                f"{'ok' if not unknown_rank_candidates else ', '.join(unknown_rank_candidates)}",
            )
        )

    return results


def has_suffix(path: Path, suffixes: set[str]) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in suffixes)


def local_artifact_reason(path: Path, size_bytes: int) -> str | None:
    name = path.name.lower()
    if has_suffix(path, BIOLOGICAL_DATA_SUFFIXES | COMPRESSED_BIOLOGICAL_SUFFIXES):
        return "biological data file extension"
    if has_suffix(path, MODEL_WEIGHT_SUFFIXES):
        return "model weight file extension"
    if has_suffix(path, ARCHIVE_SUFFIXES) and any(token in name for token in BIOLOGICAL_ARCHIVE_NAME_TOKENS):
        return "biological database/archive name"
    if size_bytes > MAX_LOCAL_ARTIFACT_BYTES:
        return f"large local artifact > {MAX_LOCAL_ARTIFACT_BYTES // (1024 * 1024)} MiB"
    return None


def scan_local_artifacts(repo_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not repo_root.exists():
        return [CheckResult(False, f"repo root exists: {display_path(repo_root)}")]
    if not repo_root.is_dir():
        return [CheckResult(False, f"repo root is a directory: {display_path(repo_root)}")]

    findings: list[str] = []
    for current_root, dirs, files in os.walk(repo_root):
        current = Path(current_root)
        dirs[:] = [directory for directory in dirs if directory not in IGNORED_ARTIFACT_SCAN_DIRS]

        for filename in files:
            path = current / filename
            try:
                size_bytes = path.stat().st_size
            except OSError as exc:
                findings.append(f"{display_path(path)}: cannot stat ({exc})")
                continue
            reason = local_artifact_reason(path, size_bytes)
            if reason:
                findings.append(f"{display_path(path)}: {reason}")

    results.append(
        CheckResult(
            not findings,
            "local artifact scan: ok" if not findings else "local artifact scan found " + "; ".join(findings),
        )
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--repo-root", type=Path, help="Repository root for optional local artifact scan")
    parser.add_argument(
        "--scan-local-artifacts",
        action="store_true",
        help="Fail if repo root contains raw/heavy biological artifacts outside ignored runtime/build locations",
    )
    args = parser.parse_args()

    campaign = args.campaign.resolve()
    if not campaign.exists():
        print(f"FAIL campaign not found: {display_path(campaign)}")
        return 1

    checks = check_manifest(campaign) + check_tsv_ledgers(campaign) + check_claim_ledger(campaign)
    if args.scan_local_artifacts:
        if args.repo_root is None:
            checks.append(CheckResult(False, "--scan-local-artifacts requires --repo-root PATH"))
        else:
            checks.extend(scan_local_artifacts(args.repo_root.resolve()))
    failed = [check for check in checks if not check.ok]

    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"{status} {check.message}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
