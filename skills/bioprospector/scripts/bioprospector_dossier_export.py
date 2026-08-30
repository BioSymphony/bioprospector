#!/usr/bin/env python3
"""Export a compact public-safe Markdown dossier from BioProspector ledgers."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

SIDECAR_FILENAMES = {
    "genecluster_cluster_calls": "cluster_calls.tsv",
    "genecluster_bgc_consensus": "bgc_consensus.tsv",
    "genecluster_protein_function_votes": "protein_function_votes.tsv",
    "genecluster_protein_function_jury": "protein_function_jury.tsv",
}

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def table(rows: list[dict[str, str]], columns: list[str], limit: int) -> str:
    if not rows:
        return "_No rows._\n"
    selected = rows[:limit]
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in selected:
        values = [row.get(column, "").replace("|", "/") for column in columns]
        body.append("| " + " | ".join(values) + " |")
    suffix = ""
    if len(rows) > limit:
        suffix = f"\n\n_Showing {limit} of {len(rows)} rows._"
    return "\n".join([header, divider, *body]) + suffix + "\n"


def sidecar_filename(key: str) -> str:
    if key in SIDECAR_FILENAMES:
        return SIDECAR_FILENAMES[key]
    return key.replace("_", "-") + ".tsv"


def ledger_path(base: Path, campaign: dict[str, Any], key: str, sidecar_dirs: list[Path] | None = None) -> Path | None:
    rel = campaign.get("ledgers", {}).get(key)
    if rel:
        path = declared_path(base, rel)
        if path is not None and path.exists():
            return path
    for sidecar_dir in sidecar_dirs or []:
        path = sidecar_dir / sidecar_filename(key)
        if path.exists():
            return path
    return None


def ledger_rows(base: Path, campaign: dict[str, Any], key: str, sidecar_dirs: list[Path] | None = None) -> list[dict[str, str]]:
    path = ledger_path(base, campaign, key, sidecar_dirs)
    return read_tsv(path) if path else []


def build_dossier(campaign_path: Path, row_limit: int, sidecar_dirs: list[Path] | None = None) -> str:
    campaign = load_json(campaign_path)
    base = campaign_path.parent
    sidecar_dirs = [path.resolve() for path in sidecar_dirs or []]
    contract_path = declared_path(base, campaign.get("target_contract", "target-contract.json"))
    contract = load_json(contract_path) if contract_path is not None and contract_path.exists() else {}

    target = campaign.get("target_molecule", contract.get("target_molecule", "unknown target"))
    host = campaign.get("host", contract.get("host", "unknown host"))
    lines = [
        f"# BioProspector Dossier: {target}",
        "",
        "## Boundary",
        "",
        f"- Campaign: `{campaign.get('campaign_id', 'unknown')}`",
        f"- Host: `{host}`",
        f"- Scope: `{campaign.get('scope', 'unknown')}`",
        f"- Claim boundary: {campaign.get('claim_boundary', 'not declared')}",
        "- This dossier is a compact claim-audited index over campaign outputs; it is not biological validation.",
        "- Provider-side full candidate packs hold approved AA sequences and heavy analyses; this repo stores pointers, accessions, checksums, graph edges, and summaries only.",
        "",
    ]

    hard_boundaries = contract.get("hard_boundaries", [])
    if hard_boundaries:
        lines.extend(["## Hard Boundaries", ""])
        lines.extend(f"- `{item}`" for item in hard_boundaries)
        lines.append("")

    sections = [
        (
            "Route Universe",
            "route_ledger",
            ["route_id", "route_name", "evidence_level", "route_status", "primary_risk"],
        ),
        (
            "Reaction Steps",
            "reaction_step_ledger",
            ["step_id", "route_id", "transformation", "enzyme_role", "candidate_search_width"],
        ),
        (
            "Dark Steps",
            "unknown_step_ledger",
            ["unknown_step_id", "parent_step_id", "gap_type", "candidate_search_width", "status"],
        ),
        (
            "Candidate Families",
            "enzyme_draft_board",
            ["candidate_id", "step_id", "candidate_name", "enzyme_family", "claim_level", "verdict"],
        ),
        (
            "Candidate Intelligence",
            "candidate_intelligence_ledger",
            ["intelligence_id", "candidate_id", "intelligence_type", "claim_level", "actionability"],
        ),
        (
            "Provider-Side Candidate Sequence Package",
            "candidate_sequence_ledger",
            ["candidate_id", "step_id", "sequence_type", "sequence_pointer", "checksum_or_version", "domain_map_status"],
        ),
        (
            "Domain And Motif Map",
            "domain_annotation_ledger",
            ["annotation_id", "candidate_id", "domain_source", "domain_accession", "domain_name", "confidence"],
        ),
        (
            "Cluster And Diversity Index",
            "candidate_diversity_ledger",
            ["selection_id", "step_id", "candidate_id", "cluster_or_clade", "novelty_level", "selection_status"],
        ),
        (
            "Candidate Graph",
            "candidate_graph_ledger",
            ["edge_id", "source_id", "target_id", "edge_type", "evidence_class", "claim_level"],
        ),
        (
            "Evidence Events",
            "evidence_event_ledger",
            ["event_id", "event_type", "source_tool_id", "adapter_id", "evidence_class", "join_status", "raw_data_retained"],
        ),
        (
            "Tool Execution Proof",
            "tool_execution_proof_ledger",
            ["proof_id", "tool_id", "adapter_id", "provider_id", "dry_run", "mock_tools", "status"],
        ),
        (
            "Candidate Rankings",
            "candidate_ranking_ledger",
            ["rank_id", "step_id", "candidate_id", "rank", "score", "claim_level"],
        ),
        (
            "Pareto Frontier",
            "pareto_frontier_ledger",
            ["frontier_id", "route_id", "lens", "rank", "score", "blocking_gaps", "claim_level"],
        ),
        (
            "Route Stitching",
            "route_stitching_scorecard",
            ["route_id", "route_status", "missing_steps", "integration_verdict"],
        ),
        (
            "Target Evidence",
            "target_evidence_ledger",
            ["evidence_id", "candidate_id", "step_id", "evidence_type", "join_status", "claim_level"],
        ),
        (
            "Controls",
            "decoy_control_ledger",
            ["control_id", "step_id", "control_type", "status", "blocks_promotion"],
        ),
        (
            "Maturity",
            "run_maturity_ledger",
            ["run_id", "maturity_level", "level_name", "status", "blocking_gap"],
        ),
        (
            "Run Output Packages",
            "run_output_package_ledger",
            ["package_id", "package_type", "sequence_policy", "location_or_pointer", "status"],
        ),
        (
            "GeneCluster Source Scout",
            "genecluster_source_scout_ledger",
            ["source_id", "organism_id", "taxon_name", "material_type", "scout_status", "claim_ceiling"],
        ),
        (
            "GeneCluster Route Decisions",
            "genecluster_route_decision_ledger",
            ["route_id", "organism_id", "recommended_route", "route_status", "claim_ceiling", "blockers"],
        ),
        (
            "GeneCluster Atlas Contracts",
            "genecluster_atlas_contract_ledger",
            ["contract_id", "contract_type", "expected_artifacts", "raw_artifact_policy", "claim_boundary", "status"],
        ),
        (
            "GeneCluster Cluster Calls",
            "genecluster_cluster_calls",
            ["cluster_id", "caller", "source_species", "target_species", "contig", "start", "end", "claim_level"],
        ),
        (
            "GeneCluster BGC Consensus",
            "genecluster_bgc_consensus",
            ["consensus_id", "cluster_id", "verdict", "caller_count", "disagreement_status", "claim_level"],
        ),
        (
            "GeneCluster Function Jury",
            "genecluster_protein_function_jury",
            ["protein_id", "verdict", "claim_level", "supporting_tools", "contradicting_tools", "confidence"],
        ),
    ]
    for title, key, columns in sections:
        rows = ledger_rows(base, campaign, key, sidecar_dirs)
        if rows:
            lines.extend([f"## {title}", "", table(rows, columns, row_limit), ""])

    claim_path = ledger_path(base, campaign, "claim_ledger", sidecar_dirs)
    claim_text = read_text(claim_path) if claim_path else ""
    if claim_text:
        lines.extend(["## Claims", "", claim_text.strip(), ""])

    lines.extend(
        [
            "## Closeout",
            "",
            "- Promote claims only after execution artifacts, target evidence, controls, tool proof, packages, and claim audit join cleanly.",
            "- Treat missing provider-side sequence checksums, missing cluster membership, unjoined evidence events, stale progress, or ambiguous rankings as self-learning guardrail triggers.",
            "- Keep raw biological data, full database outputs, private paths, and credentials outside the repo.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", required=True, type=Path, help="Markdown dossier output path")
    parser.add_argument("--row-limit", default=8, type=int, help="Rows per ledger section")
    parser.add_argument(
        "--sidecar-dir",
        action="append",
        type=Path,
        default=[],
        help="Optional generated ledger directory, such as .runtime/candidate-package/<campaign>",
    )
    args = parser.parse_args()

    dossier = build_dossier(args.campaign.resolve(), args.row_limit, args.sidecar_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(dossier, encoding="utf-8")
    print(f"Wrote dossier: {display_path(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
