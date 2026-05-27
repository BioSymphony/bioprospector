#!/usr/bin/env python3
"""Create a compact public-safe BioProspector campaign scaffold."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_schema import ledger_headers, load_schema


NON_TSV_LEDGER_FILES = {
    "claim_ledger": "claim-ledger.md",
    "provenance_log": "provenance.jsonl",
    "runpod_run_manifest": "runpod-run-manifest.json",
}


def slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "_", "-", "/", ":"}:
            cleaned.append("-")
    out = "".join(cleaned).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "campaign"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_tsv(path: Path, headers: list[str], row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerow({header: row.get(header, "") for header in headers})


def ledger_filename(key: str) -> str:
    return NON_TSV_LEDGER_FILES.get(key, f"{key.replace('_', '-')}.tsv")


def default_row(key: str, target: str, host: str, campaign_id: str) -> dict[str, str]:
    rows = {
        "route_ledger": {
            "route_id": "R001",
            "route_name": "public-seed-route",
            "target_product": target,
            "host": host,
            "feedstock_mode": "to_be_selected",
            "route_class": "seed_route",
            "evidence_level": "hypothesis",
            "route_status": "seed",
            "primary_risk": "insufficient_evidence",
            "notes": "Generated scaffold row; replace with target-specific route hypotheses.",
        },
        "reaction_step_ledger": {
            "step_id": "S001",
            "route_id": "R001",
            "step_order": "1",
            "transformation": "target_specific_transformation_to_define",
            "substrate": "substrate_to_define",
            "product": target,
            "enzyme_role": "enzyme_or_module_to_define",
            "evidence_need": "literature_and_accession_review",
            "candidate_search_width": "medium",
            "required_output": "enzyme_draft_board",
            "notes": "Generated scaffold row; split dark steps before heavy search.",
        },
        "candidate_funnels": {
            "step_id": "S001",
            "raw_hits": "0",
            "quality_filtered": "0",
            "domain_valid": "0",
            "clustered_representatives": "0",
            "evidence_reviewed": "0",
            "shortlisted": "0",
            "final_picks": "0",
            "funnel_status": "not_started",
            "notes": "No search has run.",
        },
        "enzyme_draft_board": {
            "candidate_id": "E001",
            "step_id": "S001",
            "candidate_name": "candidate_family_to_define",
            "source_organism": "public_context_to_define",
            "accession_or_source": "review_before_run",
            "enzyme_family": "family_to_define",
            "domain_architecture": "domain_review_needed",
            "evidence_classes": "literature",
            "claim_level": "hypothesis",
            "substrate_fit": "unknown",
            "host_fit": "unknown",
            "rejection_risk": "high",
            "verdict": "review",
            "notes": "Generated scaffold candidate; not biological validation.",
        },
        "route_stitching_scorecard": {
            "route_id": "R001",
            "route_status": "seed",
            "intermediate_compatibility": "unknown",
            "cofactor_fit": "unknown",
            "host_precursor_fit": "unknown",
            "toxicity_risk": "unknown",
            "transport_or_protection_need": "unknown",
            "missing_steps": "unknown",
            "integration_verdict": "not_reviewed",
            "notes": "Generated scaffold row; no route completion claim.",
        },
        "resource_ledger": {
            "resource": "public_literature_and_accessions",
            "resource_type": "public_reference",
            "version": "review_before_run",
            "license_class": "open_summary_only",
            "use_mode": "citation_and_accession_review",
            "redistribution_policy": "no_raw_database_or_full_text_copy",
            "citation_or_url": "to_be_curated",
            "notes": "Use accession ids, citations, checksums, and compact summaries.",
        },
        "self_learning_skill_ledger": {
            "learning_id": "SL001",
            "date": date.today().isoformat(),
            "campaign_id": campaign_id,
            "trigger": "campaign_scaffold_created",
            "hiccup_type": "planning_gap",
            "observation": "New campaign scaffold needs target-specific review before execution.",
            "hypothesis": "A reusable scaffold row prevents agents from skipping the learning loop after setup hiccups.",
            "probe_or_experiment": "Run preflight and update this row only if a reusable process lesson appears.",
            "control_or_baseline": "Known-good public demo campaign.",
            "expected_signal": "Campaign setup issues are captured as process learning, not biological evidence.",
            "stop_loss": "Do not open live execution from this row.",
            "result": "not_run",
            "decision": "keep",
            "runbook_update": "false",
            "skill_update": "false",
            "reusable_guardrail": "true",
            "claim_boundary": "Process learning only; not biological validation.",
            "owner": "operator",
            "notes": "Replace or update after a real reusable hiccup.",
        },
    }
    return rows[key]


def write_claim_ledger(path: Path, target: str, host: str) -> None:
    text = f"""# Claim Ledger

Generated public-safe scaffold for `{target}` in `{host}`.

| claim_id | claim | claim_level | evidence | caveat |
| --- | --- | --- | --- | --- |
| C001 | `{target}` is the planning target for this BioProspector campaign. | hypothesis | target contract | Not biological validation. |
| C002 | No production, route completion, host validation, construct design, or assay success is claimed. | evidence_supported | scaffold boundary | Upgrade only after joined execution artifacts, target evidence, controls, and claim audit. |
"""
    path.write_text(text, encoding="utf-8")


def write_target_contract(path: Path, contract: dict[str, Any]) -> None:
    path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scaffold_campaign(target_contract: Path, out: Path, campaign_id: str | None = None) -> Path:
    schema = load_schema()
    headers = ledger_headers(schema)
    contract = load_json(target_contract)
    target = contract.get("target_molecule", "target_to_define")
    host = contract.get("host", "host_to_be_selected")
    cid = campaign_id or f"pathway-big-bang-{slug(target)}-{slug(host)}-v0"

    out.mkdir(parents=True, exist_ok=True)
    write_target_contract(out / "target-contract.json", contract)

    ledger_keys = list(schema["required_ledger_keys"])
    if "self_learning_skill_ledger" in headers:
        ledger_keys.append("self_learning_skill_ledger")
    ledgers: dict[str, str] = {}
    for key in ledger_keys:
        filename = ledger_filename(key)
        ledgers[key] = filename
        path = out / filename
        if key == "claim_ledger":
            write_claim_ledger(path, target, host)
        elif key in headers:
            write_tsv(path, headers[key], default_row(key, target, host, cid))

    provenance_path = out / "provenance.jsonl"
    provenance_path.write_text(
        json.dumps(
            {
                "event_id": "P001",
                "timestamp": date.today().isoformat(),
                "artifact": "campaign-manifest.json",
                "event_type": "campaign_scaffold_created",
                "source": "bioprospector_new_campaign.py",
                "claim_boundary": "Planning scaffold only; no execution or biological validation.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    ledgers["provenance_log"] = "provenance.jsonl"

    manifest = {
        "campaign_id": cid,
        "campaign_name": f"Pathway Big Bang: {target}",
        "status": "draft",
        "target_contract": "target-contract.json",
        "host": host,
        "target_molecule": target,
        "mode": "pathway_big_bang",
        "scope": "planning_only",
        "claim_boundary": (
            "Generated scaffold only. Do not claim production, route completion, host validation, "
            "construct design, assay success, or live execution."
        ),
        "ledgers": ledgers,
        "required_ledgers": sorted(ledgers),
        "execution": {
            "provider_class": "planning_only",
            "runpod_execution": False,
            "aws_elasticblast_execution": False,
            "dispatch_allowed": False,
            "large_local_downloads": False,
        },
    }
    manifest_path = out / "campaign-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-contract", required=True, type=Path, help="Target contract JSON.")
    parser.add_argument("--out", required=True, type=Path, help="Output campaign directory.")
    parser.add_argument("--campaign-id", help="Override generated campaign id.")
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args()

    if args.out.exists():
        if not args.force:
            print(f"FAIL output already exists: {args.out}")
            return 1
        shutil.rmtree(args.out)

    manifest = scaffold_campaign(args.target_contract.resolve(), args.out.resolve(), args.campaign_id)
    print(f"Wrote campaign scaffold: {manifest}")
    print("Next commands:")
    print(f"  python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign {manifest}")
    print(f"  python3 skills/bioprospector/scripts/bioprospector_input_audit.py --campaign {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
