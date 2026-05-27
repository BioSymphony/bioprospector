#!/usr/bin/env python3
"""Join BioProspector inputs, execution artifacts, evidence, and claims."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMOTION_CLAIM_LEVELS = {
    "domain_supported",
    "ortholog_supported",
    "evidence_supported",
    "characterized_elsewhere",
    "validated_elsewhere",
    "validated_in_target",
}

TARGET_EVIDENCE_TYPES = {
    "target_sequence",
    "target_expression",
    "target_genome_context",
    "target_metabolite",
    "target_spectrum",
    "target_assay",
}

MATURITY_ORDER = ["L0", "L1", "L2", "L3", "L4", "L5"]


@dataclass
class Check:
    ok: bool
    name: str
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "name": self.name, "detail": self.detail}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def optional_tsv(base: Path, ledgers: dict[str, str], key: str) -> list[dict[str, str]]:
    rel = ledgers.get(key)
    if not rel:
        return []
    path = base / rel
    if not path.exists():
        return []
    return read_tsv(path)


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def id_set(rows: list[dict[str, str]], key: str) -> set[str]:
    return {row.get(key, "").strip() for row in rows if row.get(key, "").strip()}


def format_missing(values: set[str]) -> str:
    return ", ".join(sorted(values)) if values else "ok"


def check_campaign(
    campaign_path: Path,
    *,
    require_real_execution: bool = False,
    require_target_evidence: bool = False,
    require_decoy_controls: bool = False,
    require_maturity: str | None = None,
) -> dict[str, Any]:
    campaign_path = campaign_path.resolve()
    base = campaign_path.parent
    manifest = load_json(campaign_path)
    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict):
        ledgers = {}

    steps = optional_tsv(base, ledgers, "reaction_step_ledger")
    candidates = optional_tsv(base, ledgers, "enzyme_draft_board")
    funnels = optional_tsv(base, ledgers, "candidate_funnels")
    target_evidence = optional_tsv(base, ledgers, "target_evidence_ledger")
    organisms = optional_tsv(base, ledgers, "organism_sample_ledger")
    datasets = optional_tsv(base, ledgers, "target_dataset_ledger")
    controls = optional_tsv(base, ledgers, "decoy_control_ledger")
    artifacts = optional_tsv(base, ledgers, "execution_artifact_ledger")
    intake = optional_tsv(base, ledgers, "operator_intake_ledger")
    stage_contracts = optional_tsv(base, ledgers, "stage_contract_ledger")
    stage_progress = optional_tsv(base, ledgers, "stage_progress_ledger")
    provider_preflight = optional_tsv(base, ledgers, "provider_launch_preflight_ledger")
    maturity = optional_tsv(base, ledgers, "run_maturity_ledger")
    query_sets = optional_tsv(base, ledgers, "query_set_ledger")
    sequence_searches = optional_tsv(base, ledgers, "sequence_search_plan_ledger")
    candidate_sequences = optional_tsv(base, ledgers, "candidate_sequence_ledger")
    domain_annotations = optional_tsv(base, ledgers, "domain_annotation_ledger")
    candidate_diversity = optional_tsv(base, ledgers, "candidate_diversity_ledger")
    candidate_graph = optional_tsv(base, ledgers, "candidate_graph_ledger")
    output_packages = optional_tsv(base, ledgers, "run_output_package_ledger")
    evidence_events = optional_tsv(base, ledgers, "evidence_event_ledger")
    tool_proofs = optional_tsv(base, ledgers, "tool_execution_proof_ledger")
    candidate_rankings = optional_tsv(base, ledgers, "candidate_ranking_ledger")
    pareto_frontier = optional_tsv(base, ledgers, "pareto_frontier_ledger")
    self_learning = optional_tsv(base, ledgers, "self_learning_skill_ledger")

    checks: list[Check] = []

    step_ids = id_set(steps, "step_id")
    candidate_ids = id_set(candidates, "candidate_id")
    organism_ids = id_set(organisms, "organism_id")
    dataset_ids = id_set(datasets, "dataset_id")
    stage_ids = id_set(stage_contracts, "stage_id")
    query_ids = id_set(query_sets, "query_id")

    candidate_step_missing = {
        row.get("candidate_id", "")
        for row in candidates
        if row.get("step_id", "").strip() not in step_ids
    }
    checks.append(
        Check(
            not candidate_step_missing,
            "candidate_step_join",
            f"candidate step ids join reaction steps: {format_missing(candidate_step_missing)}",
        )
    )

    funnel_step_missing = {
        row.get("step_id", "")
        for row in funnels
        if row.get("step_id", "").strip() not in step_ids
    }
    checks.append(
        Check(
            not funnel_step_missing,
            "candidate_funnel_step_join",
            f"candidate funnel step ids join reaction steps: {format_missing(funnel_step_missing)}",
        )
    )

    progress_stage_missing = {
        row.get("event_id", "")
        for row in stage_progress
        if row.get("stage_id", "").strip() not in stage_ids
    }
    checks.append(
        Check(
            not progress_stage_missing,
            "stage_progress_contract_join",
            f"stage progress rows join stage contracts: {format_missing(progress_stage_missing)}",
        )
    )

    sequence_search_step_missing = {
        row.get("search_id", "")
        for row in sequence_searches
        if row.get("step_id", "").strip() not in step_ids
    }
    checks.append(
        Check(
            not sequence_search_step_missing,
            "sequence_search_step_join",
            f"sequence search rows join reaction steps: {format_missing(sequence_search_step_missing)}",
        )
    )

    if query_sets:
        sequence_search_query_missing = {
            row.get("search_id", "")
            for row in sequence_searches
            if row.get("query_id", "").strip() not in query_ids
        }
        checks.append(
            Check(
                not sequence_search_query_missing,
                "sequence_search_query_join",
                f"sequence search rows join query-set ledger: {format_missing(sequence_search_query_missing)}",
            )
        )

    candidate_sequence_step_missing = {
        row.get("candidate_id", "")
        for row in candidate_sequences
        if row.get("step_id", "").strip() not in step_ids
    }
    checks.append(
        Check(
            not candidate_sequence_step_missing,
            "candidate_sequence_step_join",
            f"candidate sequence rows join reaction steps: {format_missing(candidate_sequence_step_missing)}",
        )
    )

    if candidate_ids:
        candidate_sequence_missing = {
            row.get("candidate_id", "")
            for row in candidate_sequences
            if row.get("candidate_id", "").strip() not in candidate_ids
        }
        domain_candidate_missing = {
            row.get("annotation_id", "")
            for row in domain_annotations
            if row.get("candidate_id", "").strip() not in candidate_ids
        }
        diversity_candidate_missing = {
            row.get("selection_id", "")
            for row in candidate_diversity
            if row.get("candidate_id", "").strip() not in candidate_ids
        }
        checks.extend(
            [
                Check(
                    not candidate_sequence_missing,
                    "candidate_sequence_candidate_join",
                    f"candidate sequence rows join enzyme draft board: {format_missing(candidate_sequence_missing)}",
                ),
                Check(
                    not domain_candidate_missing,
                    "domain_annotation_candidate_join",
                    f"domain annotations join enzyme draft board: {format_missing(domain_candidate_missing)}",
                ),
                Check(
                    not diversity_candidate_missing,
                    "candidate_diversity_candidate_join",
                    f"candidate diversity rows join enzyme draft board: {format_missing(diversity_candidate_missing)}",
                ),
            ]
        )

    graph_step_candidate_missing = {
        row.get("edge_id", "")
        for row in candidate_graph
        if row.get("edge_type", "").strip() == "step_candidate"
        and (
            row.get("source_id", "").strip() not in step_ids
            or (candidate_ids and row.get("target_id", "").strip() not in candidate_ids)
        )
    }
    if candidate_graph:
        checks.append(
            Check(
                not graph_step_candidate_missing,
                "candidate_graph_step_candidate_join",
                "candidate graph step_candidate edges join steps and candidates: "
                f"{format_missing(graph_step_candidate_missing)}",
            )
        )

    event_step_missing = {
        row.get("event_id", "")
        for row in evidence_events
        if row.get("step_id", "").strip() and row.get("step_id", "").strip() not in step_ids
    }
    event_candidate_missing = {
        row.get("event_id", "")
        for row in evidence_events
        if row.get("candidate_id", "").strip()
        and candidate_ids
        and row.get("candidate_id", "").strip() not in candidate_ids
    }
    event_raw_retained = {
        row.get("event_id", "")
        for row in evidence_events
        if as_bool(row.get("raw_data_retained", ""))
    }
    if evidence_events:
        checks.extend(
            [
                Check(
                    not event_step_missing,
                    f"evidence_event_step_join",
                    f"evidence events join reaction steps: {format_missing(event_step_missing)}",
                ),
                Check(
                    not event_candidate_missing,
                    "evidence_event_candidate_join",
                    f"evidence events join candidates: {format_missing(event_candidate_missing)}",
                ),
                Check(
                    not event_raw_retained,
                    "evidence_event_no_raw_data",
                    f"repo-tracked evidence events retain no raw data: {format_missing(event_raw_retained)}",
                ),
            ]
        )

    ranking_candidate_missing = {
        row.get("rank_id", "")
        for row in candidate_rankings
        if candidate_ids and row.get("candidate_id", "").strip() not in candidate_ids
    }
    if candidate_rankings:
        checks.append(
            Check(
                not ranking_candidate_missing,
                "candidate_ranking_candidate_join",
                f"candidate rankings join enzyme draft board: {format_missing(ranking_candidate_missing)}",
            )
        )

    pareto_candidate_missing: set[str] = set()
    for row in pareto_frontier:
        for candidate_id in row.get("candidate_ids", "").replace(",", ";").split(";"):
            candidate_id = candidate_id.strip()
            if candidate_id and candidate_ids and candidate_id not in candidate_ids:
                pareto_candidate_missing.add(row.get("frontier_id", ""))
    if pareto_frontier:
        checks.append(
            Check(
                not pareto_candidate_missing,
                "pareto_frontier_candidate_join",
                f"Pareto frontier candidate ids join candidates: {format_missing(pareto_candidate_missing)}",
            )
        )

    evidence_candidate_missing = {
        row.get("evidence_id", "")
        for row in target_evidence
        if row.get("candidate_id", "").strip() not in candidate_ids
    }
    checks.append(
        Check(
            not evidence_candidate_missing,
            "target_evidence_candidate_join",
            f"target evidence candidate ids join candidates: {format_missing(evidence_candidate_missing)}",
        )
    )

    evidence_step_missing = {
        row.get("evidence_id", "")
        for row in target_evidence
        if row.get("step_id", "").strip() not in step_ids
    }
    checks.append(
        Check(
            not evidence_step_missing,
            "target_evidence_step_join",
            f"target evidence step ids join reaction steps: {format_missing(evidence_step_missing)}",
        )
    )

    if organisms:
        evidence_organism_missing = {
            row.get("evidence_id", "")
            for row in target_evidence
            if row.get("organism_id", "").strip() not in organism_ids
        }
        checks.append(
            Check(
                not evidence_organism_missing,
                "target_evidence_organism_join",
                f"target evidence organism ids join organism/sample ledger: {format_missing(evidence_organism_missing)}",
            )
        )

    if datasets:
        evidence_dataset_missing = {
            row.get("evidence_id", "")
            for row in target_evidence
            if row.get("dataset_id", "").strip() not in dataset_ids
        }
        checks.append(
            Check(
                not evidence_dataset_missing,
                "target_evidence_dataset_join",
                f"target evidence dataset ids join target dataset ledger: {format_missing(evidence_dataset_missing)}",
            )
        )

    joined_target_evidence_by_candidate = {
        row.get("candidate_id", "").strip()
        for row in target_evidence
        if row.get("join_status", "").strip() == "joined"
        and row.get("evidence_type", "").strip() in TARGET_EVIDENCE_TYPES
    }
    candidates_requiring_target_evidence = {
        row.get("candidate_id", "").strip()
        for row in candidates
        if row.get("claim_level", "").strip() == "validated_in_target"
    }
    if require_target_evidence:
        candidates_requiring_target_evidence |= {
            row.get("candidate_id", "").strip()
            for row in candidates
            if row.get("claim_level", "").strip() in PROMOTION_CLAIM_LEVELS
            and row.get("verdict", "").strip() not in {"reject", "rejected", "parked"}
        }
    missing_target_evidence = candidates_requiring_target_evidence - joined_target_evidence_by_candidate
    checks.append(
        Check(
            not missing_target_evidence,
            "promoted_candidate_target_evidence",
            "promoted or target-validated candidates have joined target evidence: "
            f"{format_missing(missing_target_evidence)}",
        )
    )

    wide_steps = {
        row.get("step_id", "").strip()
        for row in steps
        if row.get("candidate_search_width", "").strip() in {"wide", "frontier"}
    }
    passed_blocking_controls = {
        row.get("step_id", "").strip()
        for row in controls
        if row.get("status", "").strip() == "passed" and as_bool(row.get("blocks_promotion", ""))
    }
    failed_blocking_controls = {
        row.get("control_id", "").strip()
        for row in controls
        if row.get("status", "").strip() == "failed" and as_bool(row.get("blocks_promotion", ""))
    }
    checks.append(
        Check(
            not failed_blocking_controls,
            "failed_blocking_controls",
            f"no blocking decoy/negative controls failed: {format_missing(failed_blocking_controls)}",
        )
    )
    if require_decoy_controls:
        missing_controls = wide_steps - passed_blocking_controls
        checks.append(
            Check(
                not missing_controls,
                "wide_step_decoy_controls",
                f"wide/frontier steps have passed blocking controls: {format_missing(missing_controls)}",
            )
        )

    real_artifacts = [
        row
        for row in artifacts
        if row.get("status", "").strip() == "materialized"
        and not as_bool(row.get("dry_run", ""))
        and not as_bool(row.get("mock_tools", ""))
    ]
    mock_materialized = [
        row.get("artifact_id", "")
        for row in artifacts
        if row.get("status", "").strip() == "materialized"
        and (as_bool(row.get("dry_run", "")) or as_bool(row.get("mock_tools", "")))
    ]
    real_tool_proofs = [
        row
        for row in tool_proofs
        if row.get("status", "").strip() == "materialized"
        and not as_bool(row.get("dry_run", ""))
        and not as_bool(row.get("mock_tools", ""))
    ]
    mock_tool_proofs = {
        row.get("proof_id", "")
        for row in tool_proofs
        if row.get("status", "").strip() == "materialized"
        and (as_bool(row.get("dry_run", "")) or as_bool(row.get("mock_tools", "")))
    }
    if require_real_execution:
        checks.append(
            Check(
                bool(real_artifacts),
                "real_execution_artifact",
                "at least one materialized non-mock, non-dry-run execution artifact exists: "
                f"{'ok' if real_artifacts else 'missing'}",
            )
        )
        if tool_proofs:
            checks.append(
                Check(
                    bool(real_tool_proofs),
                    "real_tool_execution_proof",
                    "tool proof ledger has at least one materialized non-mock, non-dry-run proof row: "
                    f"{'ok' if real_tool_proofs else 'missing'}",
                )
            )
        blocking_provider_checks = {
            row.get("check_id", "").strip()
            for row in provider_preflight
            if as_bool(row.get("blocking_before_launch", ""))
            and row.get("status", "").strip() != "pass"
        }
        checks.append(
            Check(
                not blocking_provider_checks,
                "provider_launch_preflight_gate",
                "blocking provider launch preflight checks pass before real execution: "
                f"{format_missing(blocking_provider_checks)}",
            )
        )
    checks.append(
        Check(
            True,
            "mock_materialized_artifacts_visible",
            f"mock/dry-run materialized artifacts are visible, not treated as proof: {format_missing(set(mock_materialized))}",
        )
    )
    checks.append(
        Check(
            True,
            "mock_tool_proofs_visible",
            f"mock/dry-run tool proof rows are visible, not treated as proof: {format_missing(mock_tool_proofs)}",
        )
    )

    passed_maturity = {row.get("maturity_level", "").strip() for row in maturity if row.get("status", "").strip() == "pass"}
    if require_maturity:
        required_index = MATURITY_ORDER.index(require_maturity)
        required_levels = set(MATURITY_ORDER[: required_index + 1])
        missing_levels = required_levels - passed_maturity
        checks.append(
            Check(
                not missing_levels,
                "required_maturity_levels",
                f"maturity levels through {require_maturity} pass: {format_missing(missing_levels)}",
            )
        )

    completed_stage_ids = {
        row.get("stage_id", "").strip()
        for row in stage_progress
        if row.get("event_status", "").strip() == "completed"
    }
    failed_closed_stages = {
        row.get("stage_id", "").strip()
        for row in stage_contracts
        if as_bool(row.get("fail_closed", ""))
        and row.get("status", "").strip() in {"failed", "blocked", "partial", "skipped"}
    }
    checks.append(
        Check(
            not failed_closed_stages,
            f"stage_fail_closed_status",
            f"no fail-closed stages are failed, blocked, partial, or skipped: {format_missing(failed_closed_stages)}",
        )
    )

    degraded_progress_events = {
        row.get("event_id", "").strip()
        for row in stage_progress
        if row.get("event_status", "").strip() == "fallback"
        or row.get("degraded_status", "").strip() in {"partial", "degraded", "blocked"}
        or row.get("fallback_from", "").strip()
        or row.get("fallback_to", "").strip()
    }
    if require_real_execution or require_maturity == "L5":
        checks.append(
            Check(
                not degraded_progress_events,
                "no_silent_fallback_gate",
                "real closeout has no fallback, degraded, partial, or blocked progress events: "
                f"{format_missing(degraded_progress_events)}",
            )
        )

    if require_real_execution:
        required_execution_stages = {
            row.get("stage_id", "").strip()
            for row in stage_contracts
            if row.get("required_for_maturity", "").strip() in {"L3", "L4", "L5"}
            and as_bool(row.get("fail_closed", ""))
        }
        incomplete_execution_stages = required_execution_stages - completed_stage_ids
        checks.append(
            Check(
                not incomplete_execution_stages,
                "stage_completion_gate",
                "fail-closed execution stages have completed progress events: "
                f"{format_missing(incomplete_execution_stages)}",
            )
        )

        incomplete_output_packages = {
            row.get("package_id", "").strip()
            for row in output_packages
            if row.get("status", "").strip() != "materialized"
        }
        checks.append(
            Check(
                not incomplete_output_packages,
                "run_output_package_materialized",
                "real closeout output packages are materialized: "
                f"{format_missing(incomplete_output_packages)}",
            )
        )

        placeholder_checksums = {
            "",
            "review_before_run",
            "provider_side_checksum_pending",
            "pending_live_checksum",
            "compact_input",
        }
        sequence_package_placeholders = {
            row.get("candidate_id", "").strip()
            for row in candidate_sequences
            if not row.get("sequence_pointer", "").strip()
            or row.get("checksum_or_version", "").strip() in placeholder_checksums
        }
        if candidate_sequences:
            checks.append(
                Check(
                    not sequence_package_placeholders,
                    "candidate_sequence_package_checksums",
                    "real closeout candidate sequence pointers and checksums are materialized: "
                    f"{format_missing(sequence_package_placeholders)}",
                )
            )

            diversity_candidate_ids = id_set(candidate_diversity, "candidate_id")
            missing_cluster_membership = id_set(candidate_sequences, "candidate_id") - diversity_candidate_ids
            checks.append(
                Check(
                    not missing_cluster_membership,
                    "candidate_cluster_membership",
                    "real closeout candidate sequence rows have cluster/diversity membership: "
                    f"{format_missing(missing_cluster_membership)}",
                )
            )

        unjoined_evidence_events = {
            row.get("event_id", "").strip()
            for row in evidence_events
            if row.get("join_status", "").strip() in {"pending", "missing"}
        }
        if evidence_events:
            checks.append(
                Check(
                    not unjoined_evidence_events,
                    "evidence_events_joined_for_closeout",
                    "real closeout has no pending or missing evidence-event joins: "
                    f"{format_missing(unjoined_evidence_events)}",
                )
            )

        guardrail_triggers = (
            set(incomplete_output_packages)
            | set(sequence_package_placeholders)
            | set(unjoined_evidence_events)
            | set(failed_blocking_controls)
        )
        if guardrail_triggers:
            checks.append(
                Check(
                    bool(self_learning),
                    "self_learning_guardrail_for_closeout_hiccup",
                    "failed joins, missing packages, failed controls, or package checksum gaps create a learning guardrail row: "
                    f"{'ok' if self_learning else 'missing'}",
                )
            )

    planning_intake_blockers = {
        row.get("intake_id", "").strip()
        for row in intake
        if row.get("required_before", "").strip() == "planning"
        and (
            not as_bool(row.get("planning_can_proceed", ""))
            or row.get("confirmation_status", "").strip() in {"unasked", "needs_operator", "blocked"}
        )
    }
    checks.append(
        Check(
            not planning_intake_blockers,
            "operator_intake_planning_gate",
            f"operator intake has no planning blockers: {format_missing(planning_intake_blockers)}",
        )
    )

    if require_real_execution:
        execution_intake_blockers = {
            row.get("intake_id", "").strip()
            for row in intake
            if row.get("required_before", "").strip() == "execution"
            and row.get("confirmation_status", "").strip() != "confirmed"
        }
        checks.append(
            Check(
                not execution_intake_blockers,
                "operator_intake_execution_gate",
                "operator intake rows required before execution are confirmed: "
                f"{format_missing(execution_intake_blockers)}",
            )
        )

    if require_maturity == "L5":
        claim_closeout_intake_blockers = {
            row.get("intake_id", "").strip()
            for row in intake
            if row.get("required_before", "").strip() == "claim_closeout"
            and row.get("confirmation_status", "").strip() != "confirmed"
        }
        checks.append(
            Check(
                not claim_closeout_intake_blockers,
                "operator_intake_claim_closeout_gate",
                "operator intake rows required before claim closeout are confirmed: "
                f"{format_missing(claim_closeout_intake_blockers)}",
            )
        )

    maturity_claims_execution = "L3" in passed_maturity
    if maturity_claims_execution:
        checks.append(
            Check(
                bool(real_artifacts),
                "maturity_l3_artifact_proof",
                "L3 execution cannot pass without materialized non-mock execution artifact: "
                f"{'ok' if real_artifacts else 'missing'}",
            )
        )
        if tool_proofs:
            checks.append(
                Check(
                    bool(real_tool_proofs),
                    "maturity_l3_tool_proof",
                    "L3 execution cannot pass from mock or dry-run tool proof: "
                    f"{'ok' if real_tool_proofs else 'missing'}",
                )
            )

    maturity_claims_joined_evidence = "L4" in passed_maturity
    if maturity_claims_joined_evidence:
        checks.append(
            Check(
                bool(target_evidence),
                "maturity_l4_evidence_join",
                "L4 evidence-joined cannot pass without target-evidence rows: "
                f"{'ok' if target_evidence else 'missing'}",
            )
        )

    failed = [check for check in checks if not check.ok]
    return {
        "campaign_id": manifest.get("campaign_id", ""),
        "target_molecule": manifest.get("target_molecule", ""),
        "host": manifest.get("host", ""),
        "requirements": {
            "require_real_execution": require_real_execution,
            "require_target_evidence": require_target_evidence,
            "require_decoy_controls": require_decoy_controls,
            "require_maturity": require_maturity,
        },
        "summary": {
            "checks": len(checks),
            "passed": len(checks) - len(failed),
            "failed": len(failed),
        },
        "checks": [check.as_dict() for check in checks],
        "overall": "pass" if not failed else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", type=Path, help="Optional output JSON path")
    parser.add_argument("--require-real-execution", action="store_true")
    parser.add_argument("--require-target-evidence", action="store_true")
    parser.add_argument("--require-decoy-controls", action="store_true")
    parser.add_argument("--require-maturity", choices=MATURITY_ORDER)
    args = parser.parse_args()

    result = check_campaign(
        args.campaign,
        require_real_execution=args.require_real_execution,
        require_target_evidence=args.require_target_evidence,
        require_decoy_controls=args.require_decoy_controls,
        require_maturity=args.require_maturity,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
