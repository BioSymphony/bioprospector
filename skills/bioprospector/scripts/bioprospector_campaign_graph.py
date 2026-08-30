#!/usr/bin/env python3
"""Compile a BioProspector campaign into a machine-readable planning DAG."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


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


def rows_for(base: Path, manifest: dict[str, Any], key: str) -> list[dict[str, str]]:
    rel = manifest.get("ledgers", {}).get(key)
    path = declared_path(base, rel)
    return read_tsv(path) if path else []


def public_display_path(path: Path) -> str:
    """Use stable relative paths in generated artifacts when possible."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def node(
    node_id: str,
    lane: str,
    title: str,
    *,
    depends_on: list[str] | None = None,
    required_ledgers: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    validation_commands: list[str] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "lane": lane,
        "title": title,
        "depends_on": depends_on or [],
        "required_ledgers": required_ledgers or [],
        "expected_artifacts": expected_artifacts or [],
        "validation_commands": validation_commands or [],
        "blockers": blockers or [],
    }


def compile_graph(campaign_path: Path, profile: str) -> dict[str, Any]:
    campaign_path = campaign_path.resolve()
    base = campaign_path.parent
    manifest = load_json(campaign_path)
    campaign_id = manifest.get("campaign_id", "campaign")
    steps = rows_for(base, manifest, "reaction_step_ledger")
    routes = rows_for(base, manifest, "route_ledger")
    wide_steps = {
        step.get("step_id", "")
        for step in steps
        if step.get("candidate_search_width", "") in {"wide", "frontier"}
    }

    campaign_rel = public_display_path(campaign_path)
    nodes = [
        node(
            "input_audit",
            "contract",
            "Audit declared inputs before operator questions",
            required_ledgers=["input_audit_ledger"],
            expected_artifacts=["input-audit-ledger.tsv"],
            validation_commands=[f"python3 skills/bioprospector/scripts/bioprospector_input_audit.py --campaign {campaign_rel}"],
        ),
        node(
            "operator_intake",
            "contract",
            "Resolve only true operator gaps",
            depends_on=["input_audit"],
            required_ledgers=["operator_intake_ledger"],
            blockers=["execution and L5 claim closeout require confirmed execution/closeout rows"],
        ),
        node(
            "route_universe",
            "route",
            "Route universe and dark-step hypotheses",
            depends_on=["operator_intake"],
            required_ledgers=["route_ledger", "reaction_step_ledger", "unknown_step_ledger", "pathway_inference_ledger"],
            expected_artifacts=["route-ledger.tsv", "reaction-step-ledger.tsv"],
        ),
    ]

    for step in steps:
        step_id = step.get("step_id", "step")
        width = step.get("candidate_search_width", "review")
        nodes.append(
            node(
                f"candidate_search_{step_id}",
                "evidence",
                f"Candidate search for {step_id}",
                depends_on=["route_universe"],
                required_ledgers=["sequence_search_plan_ledger", "enzyme_draft_board", "candidate_funnels"],
                expected_artifacts=["candidate-funnels.tsv", "enzyme-draft-board.tsv", "evidence-event-ledger.tsv"],
                blockers=["provider preflight required before live compute"] if width in {"wide", "frontier"} else [],
            )
        )
        nodes.append(
            node(
                f"candidate_package_{step_id}",
                "candidate_package",
                f"Package candidate indexes for {step_id}",
                depends_on=[f"candidate_search_{step_id}"],
                required_ledgers=[
                    "candidate_sequence_ledger",
                    "domain_annotation_ledger",
                    "candidate_diversity_ledger",
                    "candidate_graph_ledger",
                    "run_output_package_ledger",
                ],
                expected_artifacts=["candidate-sequence-ledger.tsv", "candidate-diversity-ledger.tsv", "candidate-graph-ledger.tsv"],
            )
        )
        if step_id in wide_steps:
            nodes.append(
                node(
                    f"decoy_controls_{step_id}",
                    "controls",
                    f"Decoy and negative-control gates for {step_id}",
                    depends_on=[f"candidate_search_{step_id}"],
                    required_ledgers=["decoy_control_ledger"],
                    expected_artifacts=["decoy-control-ledger.tsv"],
                    blockers=["failed blocking controls prevent promotion"],
                )
            )

    package_nodes = [f"candidate_package_{step.get('step_id', 'step')}" for step in steps]
    control_nodes = [f"decoy_controls_{step_id}" for step_id in sorted(wide_steps)]
    nodes.extend(
        [
            node(
                "evidence_join",
                "evidence",
                "Join evidence events, target evidence, controls, and tool proof",
                depends_on=package_nodes + control_nodes,
                required_ledgers=["evidence_event_ledger", "target_evidence_ledger", "tool_execution_proof_ledger"],
                expected_artifacts=["evidence-event-ledger.tsv", "target-evidence-ledger.tsv", "tool-execution-proof-ledger.tsv"],
            ),
            node(
                "route_stitching",
                "decision",
                "Route stitching scorecards from joined candidates",
                depends_on=["evidence_join"],
                required_ledgers=["route_stitching_scorecard", "candidate_ranking_ledger"],
                expected_artifacts=["route-stitching-scorecard.tsv", "candidate-ranking-ledger.tsv"],
            ),
            node(
                "pareto_frontier",
                "decision",
                "Pareto route frontier across several useful lenses",
                depends_on=["route_stitching"],
                required_ledgers=["pareto_frontier_ledger"],
                expected_artifacts=["pareto-frontier-ledger.tsv"],
            ),
            node(
                "self_learning_qa",
                "qa",
                "Record reusable guardrails for stalls, fallbacks, unjoined output, or ambiguous ranks",
                depends_on=["evidence_join", "pareto_frontier"],
                required_ledgers=["self_learning_skill_ledger"],
                blockers=["learning rows are process guardrails, never biological validation"],
            ),
            node(
                "final_dossier",
                "closeout",
                "Claim-audited dossier index over genes, candidates, clusters, rankings, evidence, and packages",
                depends_on=["pareto_frontier", "self_learning_qa"],
                required_ledgers=["run_output_package_ledger", "candidate_graph_ledger", "candidate_ranking_ledger", "pareto_frontier_ledger"],
                expected_artifacts=["dossier.md"],
                validation_commands=[
                    f"python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign {campaign_rel}",
                    "strict live closeout adds --require-real-execution --require-target-evidence --require-decoy-controls --require-maturity L5",
                ],
                blockers=["final dossier is an index and claim audit, not the raw sequence archive"],
            ),
        ]
    )

    return {
        "campaign_id": campaign_id,
        "target_molecule": manifest.get("target_molecule", ""),
        "host": manifest.get("host", ""),
        "profile": profile,
        "route_count": len(routes),
        "step_count": len(steps),
        "public_data_policy": "compact_ledgers_pointers_checksums_only",
        "nodes": nodes,
        "edges": [
            {"from": dependency, "to": item["node_id"]}
            for item in nodes
            for dependency in item["depends_on"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--profile",
        choices=["minimal", "core-evidence", "full-frontier", "runpod-ready", "literature-only", "dark-step", "public-demo"],
        default="full-frontier",
    )
    args = parser.parse_args()

    graph = compile_graph(args.campaign, args.profile)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote campaign graph: {public_display_path(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
