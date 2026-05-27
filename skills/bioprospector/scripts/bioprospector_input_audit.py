#!/usr/bin/env python3
"""Audit declared BioProspector inputs before asking an operator questions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


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

CORE_LEDGER_KEYS = {
    "route_ledger",
    "reaction_step_ledger",
    "candidate_funnels",
    "enzyme_draft_board",
    "route_stitching_scorecard",
    "resource_ledger",
    "claim_ledger",
}

RECOMMENDED_HARDENING_LEDGER_KEYS = {
    "input_audit_ledger",
    "run_maturity_ledger",
    "organism_sample_ledger",
    "query_set_ledger",
    "target_dataset_ledger",
    "target_evidence_ledger",
    "decoy_control_ledger",
    "execution_artifact_ledger",
    "operator_intake_ledger",
    "stage_contract_ledger",
    "stage_progress_ledger",
    "compute_provider_ledger",
    "provider_launch_preflight_ledger",
    "workflow_framework_ledger",
    "sequence_search_plan_ledger",
    "candidate_sequence_ledger",
    "domain_annotation_ledger",
    "candidate_intelligence_ledger",
    "literature_search_ledger",
    "candidate_diversity_ledger",
    "candidate_graph_ledger",
    "run_output_package_ledger",
}

MISSING_STATUSES = {"missing", "placeholder", "blocked"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def boolish(value: str) -> bool:
    return value.strip().lower() == "true"


def input_row(
    *,
    input_id: str,
    input_class: str,
    declared_in: str,
    expected_artifact: str,
    status: str,
    location_or_pointer: str,
    notes: str,
) -> dict[str, str]:
    return {
        "input_id": input_id,
        "input_class": input_class,
        "declared_in": declared_in,
        "expected_artifact": expected_artifact,
        "materialized_status": status,
        "location_or_pointer": location_or_pointer,
        "notes": notes,
    }


def audit_campaign(campaign_path: Path) -> dict[str, Any]:
    campaign_path = campaign_path.resolve()
    base = campaign_path.parent
    manifest = load_json(campaign_path)
    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict):
        ledgers = {}

    known_inputs: list[dict[str, str]] = []
    missing_operator_items: list[dict[str, str]] = []
    recommended_operator_items: list[dict[str, str]] = []

    missing_fields = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    for field in missing_fields:
        missing_operator_items.append(
            {
                "item": f"manifest.{field}",
                "reason": "required manifest field is absent",
                "blocking": "true",
            }
        )

    known_inputs.append(
        input_row(
            input_id="manifest",
            input_class="manifest",
            declared_in=campaign_path.name,
            expected_artifact=campaign_path.name,
            status="materialized" if campaign_path.exists() else "missing",
            location_or_pointer=campaign_path.as_posix(),
            notes="Campaign manifest read before asking operator questions.",
        )
    )

    target_contract = base / str(manifest.get("target_contract", ""))
    target_status = "materialized" if target_contract.exists() else "missing"
    known_inputs.append(
        input_row(
            input_id="target_contract",
            input_class="target_contract",
            declared_in=campaign_path.name,
            expected_artifact=manifest.get("target_contract", ""),
            status=target_status,
            location_or_pointer=target_contract.as_posix(),
            notes="Target contract declared by manifest.",
        )
    )
    if target_status == "missing":
        missing_operator_items.append(
            {
                "item": "target_contract",
                "reason": f"declared file is missing: {target_contract}",
                "blocking": "true",
            }
        )

    for key, rel in sorted(ledgers.items()):
        path = base / str(rel)
        status = "materialized" if path.exists() else "missing"
        known_inputs.append(
            input_row(
                input_id=key,
                input_class=key if key in CORE_LEDGER_KEYS else "resource",
                declared_in=campaign_path.name,
                expected_artifact=str(rel),
                status=status,
                location_or_pointer=path.as_posix(),
                notes="Ledger declared by manifest.",
            )
        )
        if status == "missing":
            missing_operator_items.append(
                {
                    "item": key,
                    "reason": f"declared ledger is missing: {path}",
                    "blocking": "true",
                }
            )

    absent_recommended = sorted(RECOMMENDED_HARDENING_LEDGER_KEYS - set(ledgers))
    for key in absent_recommended:
        recommended_operator_items.append(
            {
                "item": key,
                "reason": "recommended no-false-success ledger is not declared",
                "blocking": "false",
            }
        )

    audit_rel = ledgers.get("input_audit_ledger")
    if audit_rel:
        audit_path = base / audit_rel
        if audit_path.exists():
            for row in read_tsv(audit_path):
                status = row.get("materialized_status", "").strip()
                if boolish(row.get("operator_required", "")) and status in MISSING_STATUSES:
                    missing_operator_items.append(
                        {
                            "item": row.get("missing_operator_item") or row.get("input_id", ""),
                            "reason": row.get("notes", "input audit ledger row requires operator action"),
                            "blocking": "true",
                        }
                    )

    execution = manifest.get("execution", {})
    if not isinstance(execution, dict):
        execution = {}

    return {
        "campaign_id": manifest.get("campaign_id", ""),
        "target_molecule": manifest.get("target_molecule", ""),
        "host": manifest.get("host", ""),
        "scope": manifest.get("scope", ""),
        "known_inputs": known_inputs,
        "missing_operator_items": missing_operator_items,
        "recommended_operator_items": recommended_operator_items,
        "execution_boundary": {
            "provider_class": execution.get("provider_class", "unspecified"),
            "runpod_execution": bool(execution.get("runpod_execution", False)),
            "aws_elasticblast_execution": bool(execution.get("aws_elasticblast_execution", False)),
            "dispatch_allowed": bool(execution.get("dispatch_allowed", False)),
            "large_local_downloads": bool(execution.get("large_local_downloads", False)),
            "real_downloads": bool(execution.get("real_downloads", False)),
        },
        "audit_status": "pass" if not missing_operator_items else "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", type=Path, help="Optional output JSON path")
    args = parser.parse_args()

    audit = audit_campaign(args.campaign)
    text = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if audit["audit_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
