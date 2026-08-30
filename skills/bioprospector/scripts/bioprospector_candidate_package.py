#!/usr/bin/env python3
"""Build public-safe candidate package indexes from BioProspector ledgers."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
REPO_ROOT = SCRIPT_DIR.parents[2]

from bioprospector_schema import ledger_headers


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def declared_path(base: Path, value: object) -> Path | None:
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


CLAIM_SCORE = {
    "validated_in_target": 100.0,
    "evidence_supported": 80.0,
    "validated_elsewhere": 72.0,
    "characterized_elsewhere": 66.0,
    "ortholog_supported": 55.0,
    "domain_supported": 45.0,
    "hypothesis": 25.0,
    "rejected": 0.0,
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def rows_for(base: Path, manifest: dict[str, Any], key: str) -> list[dict[str, str]]:
    rel = manifest.get("ledgers", {}).get(key)
    path = declared_path(base, rel)
    return read_tsv(path) if path else []


def safe_token(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)[:96] or "unknown"


def candidate_score(candidate: dict[str, str], target_evidence: list[dict[str, str]], controls: list[dict[str, str]]) -> float:
    score = CLAIM_SCORE.get(candidate.get("claim_level", "").strip(), 20.0)
    verdict = candidate.get("verdict", "").strip().lower()
    if verdict in {"selected", "select", "final_pick"}:
        score += 20.0
    elif verdict in {"shortlist", "shortlisted"}:
        score += 12.0
    elif verdict in {"reject", "rejected", "killed"}:
        score -= 100.0
    risk = candidate.get("rejection_risk", "").strip().lower()
    if risk == "low":
        score += 6.0
    elif risk == "medium":
        score -= 6.0
    elif risk == "high":
        score -= 18.0
    host_fit = candidate.get("host_fit", "").strip().lower()
    if host_fit in {"preferred", "good"}:
        score += 10.0
    elif host_fit == "acceptable":
        score += 5.0
    elif host_fit in {"risky", "blocked"}:
        score -= 20.0
    classes = {value.strip() for value in candidate.get("evidence_classes", "").replace(",", ";").split(";") if value.strip()}
    score += min(len(classes) * 3.0, 12.0)
    joined = [
        row for row in target_evidence
        if row.get("candidate_id") == candidate.get("candidate_id") and row.get("join_status") == "joined"
    ]
    score += min(len(joined) * 10.0, 20.0)
    failed_controls = [
        row for row in controls
        if row.get("step_id") == candidate.get("step_id")
        and row.get("status") == "failed"
        and row.get("blocks_promotion") == "true"
    ]
    if failed_controls:
        score -= 50.0
    return max(score, 0.0)


def route_step_ids(steps: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for step in steps:
        route_id = step.get("route_id", "").strip()
        step_id = step.get("step_id", "").strip()
        if route_id and step_id:
            grouped[route_id].append(step_id)
    return dict(grouped)


def build_candidate_package(
    campaign_path: Path,
    *,
    out_dir: Path,
    run_id: str,
    provider_pointer: str,
    package_status: str,
) -> dict[str, int]:
    campaign_path = campaign_path.resolve()
    base = campaign_path.parent
    manifest = load_json(campaign_path)
    headers = ledger_headers()

    campaign_id = manifest.get("campaign_id", "campaign")
    package_id = f"PKG-{safe_token(campaign_id)}-{safe_token(run_id)}"
    routes = rows_for(base, manifest, "route_ledger")
    steps = rows_for(base, manifest, "reaction_step_ledger")
    candidates = rows_for(base, manifest, "enzyme_draft_board")
    target_evidence = rows_for(base, manifest, "target_evidence_ledger")
    controls = rows_for(base, manifest, "decoy_control_ledger")
    existing_domains = rows_for(base, manifest, "domain_annotation_ledger")
    route_scores = rows_for(base, manifest, "route_stitching_scorecard")

    active_candidates = [
        candidate for candidate in candidates
        if candidate.get("verdict", "").strip().lower() not in {"reject", "rejected", "killed"}
    ]
    score_by_candidate = {
        candidate.get("candidate_id", ""): candidate_score(candidate, target_evidence, controls)
        for candidate in active_candidates
    }

    sequence_rows = []
    diversity_rows = []
    graph_rows = []
    ranking_rows = []
    candidates_by_step: dict[str, list[dict[str, str]]] = defaultdict(list)

    family_counts: dict[tuple[str, str], int] = defaultdict(int)
    for candidate in active_candidates:
        candidate_id = candidate.get("candidate_id", "").strip()
        step_id = candidate.get("step_id", "").strip()
        family = candidate.get("enzyme_family", "").strip() or "review_family"
        family_counts[(step_id, family)] += 1
        occurrence = family_counts[(step_id, family)]
        sequence_rows.append(
            {
                "candidate_id": candidate_id,
                "step_id": step_id,
                "sequence_type": "provider_pointer",
                "sequence_pointer": f"{provider_pointer.rstrip('/')}/protein-aa/{safe_token(candidate_id)}.faa",
                "aa_length": "0",
                "checksum_or_version": "provider_side_checksum_pending",
                "source_database": candidate.get("accession_or_source", "review_before_run"),
                "license_boundary": "accession_summary_only",
                "domain_map_status": "planned",
                "notes": "Provider-side full protein AA sequence pack required; public repo stores pointer and pending checksum only.",
            }
        )
        novelty = "canonical" if occurrence == 1 else "close_homolog"
        if candidate.get("claim_level") == "hypothesis" and occurrence > 2:
            novelty = "diverse_homolog"
        diversity_rows.append(
            {
                "selection_id": f"DIV-{safe_token(step_id)}-{safe_token(candidate_id)}",
                "step_id": step_id,
                "candidate_id": candidate_id,
                "diversity_axis": "enzyme_family",
                "cluster_or_clade": family,
                "novelty_level": novelty,
                "host_fit_priority": candidate.get("host_fit", "unknown"),
                "selection_status": "shortlist" if candidate.get("verdict", "").strip() in {"review", "shortlist"} else "planned",
                "rationale": "Package index keeps family diversity visible before compression.",
                "notes": "Planning cluster assignment; live package must join real cluster membership.",
            }
        )
        graph_rows.append(
            {
                "edge_id": f"EDGE-{safe_token(step_id)}-{safe_token(candidate_id)}",
                "source_id": step_id,
                "target_id": candidate_id,
                "edge_type": "step_candidate",
                "step_id": step_id,
                "evidence_class": "sequence_similarity" if "sequence" in candidate.get("evidence_classes", "") else "literature",
                "weight": f"{min(score_by_candidate[candidate_id] / 100.0, 1.0):.3f}",
                "claim_level": candidate.get("claim_level", "hypothesis"),
                "notes": "Candidate joined to route step for package graph.",
            }
        )
        graph_rows.append(
            {
                "edge_id": f"EDGE-{safe_token(candidate_id)}-{safe_token(package_id)}",
                "source_id": candidate_id,
                "target_id": package_id,
                "edge_type": "candidate_package",
                "step_id": step_id,
                "evidence_class": "route_stitching",
                "weight": "1.000",
                "claim_level": candidate.get("claim_level", "hypothesis"),
                "notes": "Candidate represented in provider-side package index.",
            }
        )
        candidates_by_step[step_id].append(candidate)

    for step in steps:
        route_id = step.get("route_id", "")
        step_id = step.get("step_id", "")
        graph_rows.append(
            {
                "edge_id": f"EDGE-{safe_token(route_id)}-{safe_token(step_id)}",
                "source_id": route_id,
                "target_id": step_id,
                "edge_type": "route_step",
                "step_id": step_id,
                "evidence_class": "route_stitching",
                "weight": "1.000",
                "claim_level": "hypothesis",
                "notes": "Route step dependency from campaign ledgers.",
            }
        )

    for step_id, step_candidates in sorted(candidates_by_step.items()):
        ranked = sorted(step_candidates, key=lambda row: score_by_candidate.get(row.get("candidate_id", ""), 0.0), reverse=True)
        for rank, candidate in enumerate(ranked, start=1):
            candidate_id = candidate.get("candidate_id", "")
            score = score_by_candidate.get(candidate_id, 0.0)
            ranking_rows.append(
                {
                    "rank_id": f"RANK-{safe_token(step_id)}-{rank:03d}",
                    "step_id": step_id,
                    "candidate_id": candidate_id,
                    "rank": str(rank),
                    "score": f"{score:.2f}",
                    "rank_basis": "claim_level;evidence_classes;target_evidence;controls;host_fit;rejection_risk",
                    "evidence_summary": candidate.get("evidence_classes", "review_before_run"),
                    "caveats": "Ranking is prioritization intelligence, not validation.",
                    "claim_level": candidate.get("claim_level", "hypothesis"),
                    "package_id": package_id,
                    "notes": "Generated from compact joined candidate ledgers.",
                }
            )

    route_to_steps = route_step_ids(steps)
    route_status_by_id = {row.get("route_id", ""): row for row in route_scores}
    pareto_rows = []
    lenses = [
        "minimal_genes",
        "highest_evidence",
        "clearest_validation_handoff",
        "best_host_fit",
        "ambitious_de_novo",
        "diversity_library",
    ]
    route_metrics: dict[str, dict[str, float | str]] = {}
    for route in routes:
        route_id = route.get("route_id", "")
        step_ids = route_to_steps.get(route_id, [])
        top_scores = []
        host_bonus = 0.0
        diversity = 0.0
        characterized = 0.0
        candidate_ids = []
        for step_id in step_ids:
            step_ranked = sorted(candidates_by_step.get(step_id, []), key=lambda row: score_by_candidate.get(row.get("candidate_id", ""), 0.0), reverse=True)
            if not step_ranked:
                continue
            top = step_ranked[0]
            candidate_ids.append(top.get("candidate_id", ""))
            top_scores.append(score_by_candidate.get(top.get("candidate_id", ""), 0.0))
            if top.get("host_fit") in {"preferred", "acceptable"}:
                host_bonus += 1.0
            if top.get("claim_level") in {"characterized_elsewhere", "validated_elsewhere", "evidence_supported"}:
                characterized += 1.0
            diversity += len({row.get("enzyme_family", "") for row in candidates_by_step.get(step_id, [])})
        avg_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        missing = route_status_by_id.get(route_id, {}).get("missing_steps", route.get("primary_risk", "review"))
        route_metrics[route_id] = {
            "minimal_genes": max(0.0, 100.0 - (len(step_ids) * 8.0) + avg_score / 10.0),
            "highest_evidence": avg_score,
            "clearest_validation_handoff": characterized * 20.0 + avg_score / 5.0,
            "best_host_fit": host_bonus * 20.0 + avg_score / 5.0,
            "ambitious_de_novo": (20.0 if "de_novo" in route.get("route_class", "") else 5.0) + diversity * 8.0,
            "diversity_library": diversity * 15.0 + avg_score / 10.0,
            "candidate_ids": ";".join(candidate_ids),
            "blocking_gaps": missing,
        }
    for lens in lenses:
        ranked_routes = sorted(routes, key=lambda row: float(route_metrics.get(row.get("route_id", ""), {}).get(lens, 0.0)), reverse=True)
        for rank, route in enumerate(ranked_routes, start=1):
            route_id = route.get("route_id", "")
            metrics = route_metrics.get(route_id, {})
            pareto_rows.append(
                {
                    "frontier_id": f"PARETO-{lens}-{rank:03d}",
                    "route_id": route_id,
                    "lens": lens,
                    "rank": str(rank),
                    "score": f"{float(metrics.get(lens, 0.0)):.2f}",
                    "rationale": f"{lens} view from joined candidate, route, control, and host-fit signals.",
                    "candidate_ids": str(metrics.get("candidate_ids", "")),
                    "blocking_gaps": str(metrics.get("blocking_gaps", "review")),
                    "claim_level": route.get("evidence_level", "hypothesis"),
                    "package_id": package_id,
                    "notes": "Pareto output preserves multiple winners instead of forcing one best route.",
                }
            )

    package_rows = [
        {
            "package_id": package_id,
            "package_type": "sequence_pack",
            "included_ledgers": "candidate-sequence-ledger.tsv",
            "graph_artifact": "candidate-graph-ledger.tsv",
            "sequence_policy": "provider_side_full_protein_aa_pack_no_repo_fastas",
            "location_or_pointer": provider_pointer,
            "status": package_status,
            "notes": "Full approved AA sequences live provider-side; public repo stores pointers, checksums, accessions, and license boundaries.",
        },
        {
            "package_id": f"{package_id}-CLUSTERS",
            "package_type": "cluster_pack",
            "included_ledgers": "candidate-diversity-ledger.tsv;domain-annotation-ledger.tsv",
            "graph_artifact": "candidate-graph-ledger.tsv",
            "sequence_policy": "cluster_membership_only_no_raw_sequences",
            "location_or_pointer": provider_pointer,
            "status": package_status,
            "notes": "Cluster and domain indexes only; live package must materialize representatives and checksums externally.",
        },
        {
            "package_id": f"{package_id}-GRAPH",
            "package_type": "graph_pack",
            "included_ledgers": "candidate-graph-ledger.tsv;candidate-ranking-ledger.tsv;pareto-frontier-ledger.tsv",
            "graph_artifact": "candidate-graph-ledger.tsv",
            "sequence_policy": "graph_edges_only",
            "location_or_pointer": provider_pointer,
            "status": package_status,
            "notes": "Machine-readable campaign graph edges and ranking indexes.",
        },
        {
            "package_id": f"{package_id}-DOSSIER",
            "package_type": "final_dossier",
            "included_ledgers": "all_package_indexes",
            "graph_artifact": "candidate-graph-ledger.tsv",
            "sequence_policy": "dossier_indexes_provider_side_package",
            "location_or_pointer": provider_pointer,
            "status": "planned",
            "notes": "Final L5 dossier remains blocked until strict self-check passes.",
        },
    ]

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "candidate_sequence_ledger": sequence_rows,
        "candidate_diversity_ledger": diversity_rows,
        "candidate_graph_ledger": graph_rows,
        "run_output_package_ledger": package_rows,
        "candidate_ranking_ledger": ranking_rows,
        "pareto_frontier_ledger": pareto_rows,
    }
    if existing_domains:
        outputs["domain_annotation_ledger"] = existing_domains
    for key, rows in outputs.items():
        filename = key.replace("_", "-") + ".tsv"
        write_tsv(out_dir / filename, headers[key], rows)

    package_manifest = {
        "campaign_id": campaign_id,
        "run_id": run_id,
        "package_id": package_id,
        "provider_pointer": provider_pointer,
        "package_status": package_status,
        "public_repo_policy": "indexes_only_no_raw_sequences",
        "outputs": sorted([path.name for path in out_dir.glob("*.tsv")]),
    }
    (out_dir / "candidate-package-manifest.json").write_text(
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {key: len(rows) for key, rows in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for package indexes")
    parser.add_argument("--run-id", default="PACKAGE")
    parser.add_argument(
        "--provider-pointer",
        default="provider-output://review-before-run/candidate-package",
        help="External provider-side location pointer for full AA sequences and analyses",
    )
    parser.add_argument("--package-status", choices=["planned", "materialized", "partial", "blocked", "deleted"], default="planned")
    args = parser.parse_args()

    counts = build_candidate_package(
        args.campaign,
        out_dir=args.out,
        run_id=args.run_id,
        provider_pointer=args.provider_pointer,
        package_status=args.package_status,
    )
    print(json.dumps({"out": display_path(args.out), "counts": counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
