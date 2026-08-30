#!/usr/bin/env python3
"""Build a public-safe GeneCluster atlas plan from BioProspector ledgers.

The planner is intentionally local-light: it reads compact public campaign
ledgers, writes scout/route/contract ledgers, and refuses local raw biological
artifact pointers. It does not call networks, materialize sequences, or launch
providers.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_schema import ledger_headers


SOURCE_SCOUT_KEY = "genecluster_source_scout_ledger"
ROUTE_DECISION_KEY = "genecluster_route_decision_ledger"
ATLAS_CONTRACT_KEY = "genecluster_atlas_contract_ledger"

RAW_HEAVY_SUFFIXES = (
    ".fastq",
    ".fastq.gz",
    ".fq",
    ".fq.gz",
    ".sra",
    ".bam",
    ".sam",
    ".cram",
    ".fa",
    ".faa",
    ".fasta",
    ".fna",
    ".ffn",
    ".gb",
    ".gbff",
    ".gbk",
    ".gff",
    ".gff3",
    ".gtf",
    ".dmnd",
    ".hmm",
    ".bt2",
    ".bt2l",
    ".pin",
    ".phr",
    ".psq",
    ".nin",
    ".nhr",
    ".nsq",
)

MISSING = {"", "-", "na", "n/a", "none", "null", "missing", "not_applicable"}
BLOCKED_STATUS = {"blocked", "failed", "missing", "not_available"}
READY_STATUS = {"available", "materialized", "ready", "provider_ready", "public_pointer"}
DECLARED_STATUS = {"declared", "planned", "review_before_run", "review_required"}

ROUTE_RANK = {
    "next_experiment_design": 0,
    "candidate_search": 1,
    "transcript_first": 2,
    "genome_context": 2,
    "annotation_direct_then_context": 3,
}


def clean(value: Any) -> str:
    return str(value or "").strip()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean(value).lower()).strip("_")


def is_missing(value: Any) -> bool:
    return slug(clean(value)) in MISSING


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def declared_path(base: Path, value: object) -> Path | None:
    text = clean(value)
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [{key: clean(value) for key, value in row.items() if key is not None} for row in reader]


def read_optional_ledger(base: Path, ledgers: dict[str, str], key: str) -> list[dict[str, str]]:
    rel = ledgers.get(key)
    if not rel:
        return []
    path = declared_path(base, rel)
    if path is None or not path.exists():
        return []
    return read_tsv(path)


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def pointer_has_raw_heavy_artifact(pointer: str) -> bool:
    text = clean(pointer)
    if not text or text.startswith("provider_output_after_run:") or text.startswith("summary_pointer:"):
        return False
    lower = text.lower()
    if "://" in lower:
        # Remote URLs and accessions are public pointers until a materializer has
        # reviewed terms and output policy; the planner does not fetch them.
        return False
    return any(lower.endswith(suffix) for suffix in RAW_HEAVY_SUFFIXES)


def material_status(row: dict[str, str]) -> str:
    return slug(row.get("materialized_status") or row.get("data_status") or row.get("status"))


def is_blocked(row: dict[str, str]) -> bool:
    return material_status(row) in BLOCKED_STATUS


def is_ready(row: dict[str, str]) -> bool:
    return material_status(row) in READY_STATUS


def is_declared(row: dict[str, str]) -> bool:
    return material_status(row) in DECLARED_STATUS or is_ready(row)


def dataset_kind(row: dict[str, str]) -> str:
    return slug(row.get("dataset_type") or row.get("evidence_type") or row.get("role"))


def evidence_materials(datasets: list[dict[str, str]]) -> dict[str, bool]:
    usable = [row for row in datasets if is_declared(row) and not is_blocked(row)]
    return {
        "has_genome": any(dataset_kind(row) == "genome" for row in usable),
        "has_annotation": any(dataset_kind(row) in {"annotation", "gff", "gene_annotation"} for row in usable),
        "has_proteome": any(dataset_kind(row) == "proteome" for row in usable),
        "has_transcriptome": any(dataset_kind(row) == "transcriptome" for row in usable),
        "has_ready_material": any(is_ready(row) for row in usable),
    }


def controls_status(decoy_rows: list[dict[str, str]]) -> tuple[bool, str]:
    if not decoy_rows:
        return False, "no decoy-control-ledger rows declared"
    control_types = {slug(row.get("control_type", "")) for row in decoy_rows}
    expected = {"shuffled_sequence", "negative_taxon", "unrelated_family", "reciprocal_check"}
    present = sorted(control_types & expected)
    if not present:
        return False, "decoy-control-ledger lacks shuffled, negative, unrelated, or reciprocal controls"
    return True, ";".join(present)


def query_status(query_rows: list[dict[str, str]]) -> tuple[bool, str]:
    if not query_rows:
        return False, "no query-set-ledger rows declared"
    query_types = sorted({clean(row.get("query_type", "unknown")) or "unknown" for row in query_rows})
    return True, ";".join(query_types)


def route_for_materials(materials: dict[str, bool], controls_ok: bool, queries_ok: bool) -> tuple[str, str, list[str]]:
    blockers: list[str] = []
    if not queries_ok:
        blockers.append("query seeds are not declared")
    if not controls_ok:
        blockers.append("negative/decoy controls are not declared")

    if materials["has_annotation"] and (materials["has_proteome"] or materials["has_genome"]):
        route = "annotation_direct_then_context"
        ceiling = "L3_annotation_neighborhood_ready"
    elif materials["has_transcriptome"]:
        route = "transcript_first"
        ceiling = "L2_transcript_candidate_ready"
    elif materials["has_genome"]:
        route = "genome_context"
        ceiling = "L2_coordinate_context_ready"
    elif materials["has_proteome"]:
        route = "candidate_search"
        ceiling = "L1_sequence_candidate_ready"
    else:
        route = "next_experiment_design"
        ceiling = "L0_plan_only"
        blockers.append("no genome, annotation, proteome, or transcriptome dataset is declared")

    if blockers and ROUTE_RANK[route] > 1:
        ceiling = "L1_controls_or_queries_pending"
    return route, ceiling, blockers


def organism_rows(manifest: dict[str, Any], samples: list[dict[str, str]]) -> list[dict[str, str]]:
    if samples:
        return samples
    host = clean(manifest.get("host", "target_host"))
    return [
        {
            "organism_id": "ORG001",
            "taxon_name": host,
            "role": "target_host",
            "evidence_type": "planning_context",
            "data_status": "declared",
            "source_pointer": "campaign-manifest.json",
            "license_boundary": "not_applicable",
            "notes": "Synthesized fallback row because no organism-sample-ledger was declared.",
        }
    ]


def find_raw_pointer_errors(rows_by_name: dict[str, list[dict[str, str]]]) -> list[str]:
    errors: list[str] = []
    pointer_fields = {
        "source_pointer",
        "evidence_pointer",
        "location_or_pointer",
        "accession_or_source",
        "path_or_uri",
    }
    for ledger_name, rows in rows_by_name.items():
        for index, row in enumerate(rows, start=2):
            for field in pointer_fields:
                if pointer_has_raw_heavy_artifact(row.get(field, "")):
                    errors.append(f"{ledger_name} line {index} local raw/heavy pointer in {field}")
                    row[field] = "REPLACE_ME_EXTERNAL_PATH"
    return errors


def build_source_rows(
    organisms: list[dict[str, str]],
    datasets: list[dict[str, str]],
    errors: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    datasets_by_org: dict[str, list[dict[str, str]]] = {}
    for row in datasets:
        datasets_by_org.setdefault(row.get("organism_id", ""), []).append(row)

    for organism in organisms:
        organism_id = organism.get("organism_id", "")
        org_datasets = datasets_by_org.get(organism_id, [])
        materials = evidence_materials(org_datasets)
        scout_status = "metadata_declared"
        if any(is_blocked(row) for row in org_datasets):
            scout_status = "blocked_dataset_present"
        elif materials["has_ready_material"]:
            scout_status = "ready_pointer_declared"
        elif not org_datasets:
            scout_status = "no_dataset_declared"

        source_provider = "manifest_ledgers"
        source_pointer = organism.get("source_pointer", "")
        if org_datasets:
            source_provider = ";".join(sorted({clean(row.get("dataset_type", "dataset")) or "dataset" for row in org_datasets}))
            source_pointer = ";".join(clean(row.get("source_pointer", "")) for row in org_datasets if clean(row.get("source_pointer", "")))

        if pointer_has_raw_heavy_artifact(source_pointer):
            errors.append(f"organism {organism_id} uses a local raw/heavy source pointer")
            source_pointer = "REPLACE_ME_EXTERNAL_PATH"

        rows.append(
            {
                "source_id": f"SRC-{organism_id or len(rows) + 1:>03}".replace(" ", "0"),
                "organism_id": organism_id or f"ORG{len(rows) + 1:03}",
                "taxon_name": organism.get("taxon_name", ""),
                "source_record_type": organism.get("role", "source_organism"),
                "source_provider": source_provider,
                "source_pointer": source_pointer or "not_declared",
                "material_type": ";".join(sorted({dataset_kind(row) for row in org_datasets if dataset_kind(row)})) or "planning_context",
                "acquisition_policy": "metadata_only_no_network_no_raw_download",
                "has_genome": str(materials["has_genome"]).lower(),
                "has_annotation": str(materials["has_annotation"]).lower(),
                "has_proteome": str(materials["has_proteome"]).lower(),
                "has_transcriptome": str(materials["has_transcriptome"]).lower(),
                "scout_status": scout_status,
                "claim_ceiling": "L0_plan_only" if scout_status == "no_dataset_declared" else "L1_metadata_ready",
                "notes": organism.get("notes", ""),
            }
        )
    return rows


def build_route_rows(
    organisms: list[dict[str, str]],
    datasets: list[dict[str, str]],
    query_rows: list[dict[str, str]],
    decoy_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    controls_ok, controls_note = controls_status(decoy_rows)
    queries_ok, queries_note = query_status(query_rows)
    datasets_by_org: dict[str, list[dict[str, str]]] = {}
    for row in datasets:
        datasets_by_org.setdefault(row.get("organism_id", ""), []).append(row)

    rows: list[dict[str, str]] = []
    for organism in organisms:
        organism_id = organism.get("organism_id", "")
        org_datasets = datasets_by_org.get(organism_id, [])
        materials = evidence_materials(org_datasets)
        route, ceiling, blockers = route_for_materials(materials, controls_ok, queries_ok)
        accepted_inputs = [key for key, value in materials.items() if value and key != "has_ready_material"]
        rejected_routes = []
        if not materials["has_annotation"]:
            rejected_routes.append("annotation_direct")
        if not materials["has_transcriptome"]:
            rejected_routes.append("transcript_first")
        if not materials["has_genome"]:
            rejected_routes.append("genome_context")
        rows.append(
            {
                "route_id": f"GCA-{len(rows) + 1:03}",
                "organism_id": organism_id or f"ORG{len(rows) + 1:03}",
                "taxon_name": organism.get("taxon_name", ""),
                "recommended_route": route,
                "route_status": "ready_for_issue_dry_run" if not blockers else "planning_with_blockers",
                "claim_ceiling": ceiling,
                "blockers": ";".join(blockers) or "none",
                "accepted_inputs": ";".join(accepted_inputs) or "metadata_only",
                "rejected_routes": ";".join(rejected_routes) or "none",
                "notes": f"queries={queries_note}; controls={controls_note}",
            }
        )

    selected = max(rows, key=lambda row: ROUTE_RANK.get(row["recommended_route"], 0), default={})
    summary = {
        "controls_ok": controls_ok,
        "controls": controls_note,
        "queries_ok": queries_ok,
        "queries": queries_note,
        "selected_route": selected.get("recommended_route", "none"),
        "selected_claim_ceiling": selected.get("claim_ceiling", "L0_plan_only"),
    }
    return rows, summary


def build_contract_rows(campaign_path: Path, manifest: dict[str, Any], out_dir: Path) -> list[dict[str, str]]:
    campaign_arg = display_path(campaign_path)
    plan_arg = display_path(out_dir)
    claim_boundary = clean(manifest.get("claim_boundary", "planning only"))
    validation = (
        "python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py "
        f"--campaign {campaign_arg} --out {plan_arg}"
    )
    return [
        {
            "contract_id": "GCA-C01",
            "contract_type": "stage0_source_route_scout",
            "required_inputs": "campaign-manifest.json;organism-sample-ledger.tsv;target-dataset-ledger.tsv;query-set-ledger.tsv;decoy-control-ledger.tsv",
            "expected_artifacts": "genecluster-source-scout-ledger.tsv;genecluster-route-decision-ledger.tsv;genecluster-atlas-plan.json",
            "validation_command": validation,
            "raw_artifact_policy": "summary_ledgers_only_no_raw_sequences_no_local_databases",
            "claim_boundary": claim_boundary,
            "status": "planned",
            "notes": "First gate before any genome-context, BGC, synteny, or provider work.",
        },
        {
            "contract_id": "GCA-C02",
            "contract_type": "provider_neutral_sequence_search",
            "required_inputs": "sequence-search-plan-ledger.tsv;compute-provider-ledger.tsv;provider-launch-preflight-ledger.tsv;stage-contract-ledger.tsv",
            "expected_artifacts": "candidate-funnels.tsv;target-evidence-ledger.tsv;execution-artifact-ledger.tsv;tool-execution-proof-ledger.tsv",
            "validation_command": "python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign " + campaign_arg,
            "raw_artifact_policy": "provider_side_bulk_data_compact_evidence_events_only",
            "claim_boundary": claim_boundary,
            "status": "planned",
            "notes": "Search execution remains a separate operator-approved lane.",
        },
        {
            "contract_id": "GCA-C03",
            "contract_type": "cluster_and_function_jury",
            "required_inputs": "genome-hit-ledger.tsv;target-evidence-ledger.tsv;tool-execution-proof-ledger.tsv;claim-ledger.md",
            "expected_artifacts": "cluster consensus notes;protein function jury notes;claim-ledger.md updates;red-team-report.md",
            "validation_command": "python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign " + campaign_arg,
            "raw_artifact_policy": "coordinates_and_summaries_only_no_gff_or_fasta_pullback",
            "claim_boundary": claim_boundary,
            "status": "planned",
            "notes": "Physical neighborhood claims require coordinate evidence; transcript-only hits stay candidate-level.",
        },
        {
            "contract_id": "GCA-C04",
            "contract_type": "review_surface_and_dossier",
            "required_inputs": "claim-ledger.md;execution-artifact-ledger.tsv;tool-execution-proof-ledger.tsv;run-output-package-ledger.tsv",
            "expected_artifacts": "public-safe dossier markdown;campaign graph json;package index pointers",
            "validation_command": "python3 scripts/public_audit.py .",
            "raw_artifact_policy": "dossier_indexes_provider_pointers_and_checksums_only",
            "claim_boundary": claim_boundary,
            "status": "planned",
            "notes": "The final public artifact is a claim-bounded review surface, not raw search output.",
        },
    ]


def build_plan(campaign_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = load_json(campaign_path)
    base = campaign_path.parent
    ledgers = manifest.get("ledgers", {})

    samples = read_optional_ledger(base, ledgers, "organism_sample_ledger")
    datasets = read_optional_ledger(base, ledgers, "target_dataset_ledger")
    queries = read_optional_ledger(base, ledgers, "query_set_ledger")
    decoys = read_optional_ledger(base, ledgers, "decoy_control_ledger")
    evidence = read_optional_ledger(base, ledgers, "target_evidence_ledger")
    execution = read_optional_ledger(base, ledgers, "execution_artifact_ledger")

    errors = find_raw_pointer_errors(
        {
            "organism_sample_ledger": samples,
            "target_dataset_ledger": datasets,
            "query_set_ledger": queries,
            "target_evidence_ledger": evidence,
            "execution_artifact_ledger": execution,
        }
    )
    organisms = organism_rows(manifest, samples)
    source_rows = build_source_rows(organisms, datasets, errors)
    route_rows, route_summary = build_route_rows(organisms, datasets, queries, decoys)
    contract_rows = build_contract_rows(campaign_path, manifest, out_dir)

    headers = ledger_headers()
    paths = {
        "source_scout_ledger": out_dir / "genecluster-source-scout-ledger.tsv",
        "route_decision_ledger": out_dir / "genecluster-route-decision-ledger.tsv",
        "atlas_contract_ledger": out_dir / "genecluster-atlas-contract-ledger.tsv",
        "plan_json": out_dir / "genecluster-atlas-plan.json",
    }
    write_tsv(paths["source_scout_ledger"], headers[SOURCE_SCOUT_KEY], source_rows)
    write_tsv(paths["route_decision_ledger"], headers[ROUTE_DECISION_KEY], route_rows)
    write_tsv(paths["atlas_contract_ledger"], headers[ATLAS_CONTRACT_KEY], contract_rows)

    warnings: list[str] = []
    if not datasets:
        warnings.append("no target-dataset-ledger rows found; plan is L0 only")
    if not queries:
        warnings.append("no query-set-ledger rows found; sequence search lanes are blocked")
    if not decoys:
        warnings.append("no decoy-control-ledger rows found; candidate promotion is blocked")

    plan = {
        "schema_version": "bioprospector_genecluster_atlas_plan.v1",
        "campaign_id": manifest.get("campaign_id"),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "route_summary": route_summary,
        "counts": {
            "organisms": len(organisms),
            "datasets": len(datasets),
            "queries": len(queries),
            "decoy_controls": len(decoys),
            "source_rows": len(source_rows),
            "route_rows": len(route_rows),
            "contract_rows": len(contract_rows),
        },
        "outputs": {key: display_path(path) for key, path in paths.items()},
    }
    paths["plan_json"].write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for GeneCluster atlas planning ledgers")
    parser.add_argument("--json", action="store_true", help="Print plan JSON to stdout")
    args = parser.parse_args()

    plan = build_plan(args.campaign, args.out)
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"Wrote GeneCluster atlas plan to {display_path(args.out)}")
    return 0 if plan["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
