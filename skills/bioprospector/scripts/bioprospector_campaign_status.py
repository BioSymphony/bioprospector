#!/usr/bin/env python3
"""Summarize a BioProspector campaign into a compact status snapshot."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

PASS_STATUSES = {
    "pass",
    "passed",
    "ok",
    "ready",
    "approved",
    "confirmed",
    "complete",
    "completed",
    "succeeded",
    "success",
    "done",
    "none",
    "not_applicable",
    "not-applicable",
    "n/a",
}
OPEN_STATUSES = {
    "planned",
    "pending",
    "review_required",
    "not_started",
    "not_run",
    "declared",
    "assumed",
    "unknown",
    "missing",
    "skipped",
}
FAIL_STATUSES = {"fail", "failed", "blocked", "error", "stale"}
MATURITY_ORDER = ["L0", "L1", "L2", "L3", "L4", "L5"]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def ledger_path(base: Path, manifest: dict[str, Any], key: str) -> Path | None:
    rel = manifest.get("ledgers", {}).get(key)
    text = str(rel or "").strip()
    candidate = Path(text)
    if not text or candidate.is_absolute():
        return None
    resolved_base = base.resolve()
    resolved = (resolved_base / candidate).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError:
        return None
    return resolved


def rows_for(base: Path, manifest: dict[str, Any], key: str) -> list[dict[str, str]]:
    path = ledger_path(base, manifest, key)
    return read_tsv(path) if path else []


def status_value(value: Any) -> str:
    return str(value or "").strip().lower()


def truthy(value: Any) -> bool:
    return status_value(value) in {"true", "yes", "y", "1", "blocking"}


def is_pass_like(value: Any) -> bool:
    return status_value(value) in PASS_STATUSES


def count_by(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts = Counter((row.get(field) or "blank").strip() or "blank" for row in rows)
    return dict(sorted(counts.items()))


def sum_int(rows: list[dict[str, str]], field: str) -> int:
    total = 0
    for row in rows:
        try:
            total += int(str(row.get(field, "0")).strip() or "0")
        except ValueError:
            continue
    return total


def missing_ledgers(base: Path, manifest: dict[str, Any], keys: list[str]) -> list[str]:
    missing: list[str] = []
    ledgers = manifest.get("ledgers", {})
    for key in keys:
        rel = ledgers.get(key)
        if not rel:
            missing.append(f"{key}: not declared")
            continue
        path = ledger_path(base, manifest, key)
        if path is None or not path.exists():
            missing.append(f"{key}: {rel} missing")
    return missing


def highest_passed_maturity(rows: list[dict[str, str]]) -> str | None:
    passed = {
        row.get("maturity_level", "").strip()
        for row in rows
        if is_pass_like(row.get("status"))
    }
    for level in reversed(MATURITY_ORDER):
        if level in passed:
            return level
    return None


def unresolved_blocking_rows(
    rows: list[dict[str, str]],
    *,
    flag_field: str,
    status_field: str = "status",
    id_field: str,
) -> list[dict[str, str]]:
    blockers = []
    for row in rows:
        if truthy(row.get(flag_field)) and not is_pass_like(row.get(status_field)):
            blockers.append(
                {
                    "id": row.get(id_field, ""),
                    "status": row.get(status_field, ""),
                    "notes": row.get("notes", ""),
                }
            )
    return blockers


def open_operator_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        confirmation = status_value(row.get("confirmation_status"))
        if confirmation and confirmation not in PASS_STATUSES:
            out.append(
                {
                    "id": row.get("intake_id", ""),
                    "input_area": row.get("input_area", ""),
                    "required_before": row.get("required_before", ""),
                    "confirmation_status": row.get("confirmation_status", ""),
                    "planning_can_proceed": row.get("planning_can_proceed", ""),
                }
            )
    return out


def recommended_commands(campaign_path: Path, campaign_id: str) -> list[dict[str, str]]:
    campaign = display_path(campaign_path)
    safe_id = campaign_id or "campaign"
    return [
        {
            "name": "preflight",
            "command": f"python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign {campaign}",
        },
        {
            "name": "input_audit",
            "command": f"python3 skills/bioprospector/scripts/bioprospector_input_audit.py --campaign {campaign}",
        },
        {
            "name": "issue_dry_run_full_frontier",
            "command": (
                "python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py "
                f"--campaign {campaign} --prefix {safe_id.upper().replace('-', '_')[:24]} "
                f"--out .runtime/{safe_id}/linear-issues --include-profile full-frontier"
            ),
        },
        {
            "name": "campaign_graph",
            "command": (
                "python3 skills/bioprospector/scripts/bioprospector_campaign_graph.py "
                f"--campaign {campaign} --out .runtime/{safe_id}/campaign-plan.json"
            ),
        },
        {
            "name": "contract_self_check",
            "command": f"python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign {campaign}",
        },
    ]


def compile_status(campaign_path: Path) -> dict[str, Any]:
    campaign_path = campaign_path.resolve()
    base = campaign_path.parent
    manifest = load_json(campaign_path)
    ledgers = manifest.get("ledgers", {})
    required_keys = list(manifest.get("required_ledgers") or [])

    route_rows = rows_for(base, manifest, "route_ledger")
    step_rows = rows_for(base, manifest, "reaction_step_ledger")
    funnel_rows = rows_for(base, manifest, "candidate_funnels")
    candidate_rows = rows_for(base, manifest, "enzyme_draft_board")
    stitching_rows = rows_for(base, manifest, "route_stitching_scorecard")
    provider_rows = rows_for(base, manifest, "provider_launch_preflight_ledger")
    stage_rows = rows_for(base, manifest, "stage_contract_ledger")
    progress_rows = rows_for(base, manifest, "stage_progress_ledger")
    maturity_rows = rows_for(base, manifest, "run_maturity_ledger")
    input_rows = rows_for(base, manifest, "input_audit_ledger")
    intake_rows = rows_for(base, manifest, "operator_intake_ledger")
    target_evidence_rows = rows_for(base, manifest, "target_evidence_ledger")
    decoy_rows = rows_for(base, manifest, "decoy_control_ledger")
    execution_rows = rows_for(base, manifest, "execution_artifact_ledger")
    proof_rows = rows_for(base, manifest, "tool_execution_proof_ledger")

    missing_required = missing_ledgers(base, manifest, required_keys)
    provider_blockers = unresolved_blocking_rows(
        provider_rows,
        flag_field="blocking_before_launch",
        id_field="check_id",
    )
    decoy_blockers = unresolved_blocking_rows(
        decoy_rows,
        flag_field="blocks_promotion",
        id_field="control_id",
    )
    fail_closed_open = [
        {
            "id": row.get("stage_id", ""),
            "status": row.get("status", ""),
            "required_for_maturity": row.get("required_for_maturity", ""),
            "notes": row.get("notes", ""),
        }
        for row in stage_rows
        if truthy(row.get("fail_closed")) and not is_pass_like(row.get("status"))
    ]
    operator_open = open_operator_rows(intake_rows)
    input_gaps = [
        {
            "id": row.get("input_id", ""),
            "input_class": row.get("input_class", ""),
            "materialized_status": row.get("materialized_status", ""),
            "operator_required": row.get("operator_required", ""),
            "missing_operator_item": row.get("missing_operator_item", ""),
        }
        for row in input_rows
        if truthy(row.get("operator_required")) or not is_pass_like(row.get("materialized_status"))
    ]

    real_execution_rows = [
        row
        for row in execution_rows
        if not truthy(row.get("dry_run")) and not truthy(row.get("mock_tools")) and is_pass_like(row.get("status"))
    ]
    real_tool_proof_rows = [
        row
        for row in proof_rows
        if not truthy(row.get("dry_run")) and not truthy(row.get("mock_tools")) and is_pass_like(row.get("status"))
    ]

    campaign_id = manifest.get("campaign_id", "campaign")
    readiness = {
        "planning_ready": not missing_required and bool(route_rows) and bool(step_rows),
        "issue_draft_ready": not missing_required and bool(route_rows) and bool(step_rows),
        "provider_launch_ready": bool(provider_rows) and not provider_blockers,
        "promotion_ready": bool(decoy_rows) and not decoy_blockers and bool(target_evidence_rows),
        "real_execution_observed": bool(real_execution_rows),
        "real_tool_proof_observed": bool(real_tool_proof_rows),
        "highest_passed_maturity": highest_passed_maturity(maturity_rows),
    }
    readiness["strict_closeout_likely_ready"] = bool(
        readiness["promotion_ready"]
        and readiness["real_execution_observed"]
        and readiness["real_tool_proof_observed"]
        and readiness["highest_passed_maturity"] == "L5"
        and not fail_closed_open
    )

    next_actions: list[str] = []
    if missing_required:
        next_actions.append("Fix missing required ledgers before issuing worker lanes.")
    if input_gaps or operator_open:
        next_actions.append("Review input audit and operator intake before execution or closeout.")
    if provider_blockers:
        next_actions.append("Resolve provider launch preflight blockers before any paid/provider run.")
    if decoy_blockers:
        next_actions.append("Run or resolve blocking decoy controls before promoting candidates.")
    if not readiness["real_execution_observed"]:
        next_actions.append("Treat campaign outputs as planning/readiness until real execution artifacts are joined.")
    if not next_actions:
        next_actions.append("Run contract self-check, then prepare dossier or strict closeout review.")

    return {
        "campaign": {
            "campaign_id": campaign_id,
            "campaign_name": manifest.get("campaign_name", ""),
            "target_molecule": manifest.get("target_molecule", ""),
            "host": manifest.get("host", ""),
            "mode": manifest.get("mode", ""),
            "scope": manifest.get("scope", ""),
            "status": manifest.get("status", ""),
            "claim_boundary": manifest.get("claim_boundary", ""),
        },
        "ledger_health": {
            "declared_ledgers": len(ledgers),
            "required_ledgers": len(required_keys),
            "missing_required": missing_required,
        },
        "routes": {
            "count": len(route_rows),
            "by_status": count_by(route_rows, "route_status"),
            "by_class": count_by(route_rows, "route_class"),
            "evidence_levels": count_by(route_rows, "evidence_level"),
        },
        "steps": {
            "count": len(step_rows),
            "search_widths": count_by(step_rows, "candidate_search_width"),
            "evidence_needs": count_by(step_rows, "evidence_need"),
        },
        "candidates": {
            "candidate_rows": len(candidate_rows),
            "claim_levels": count_by(candidate_rows, "claim_level"),
            "verdicts": count_by(candidate_rows, "verdict"),
            "funnel_rows": len(funnel_rows),
            "raw_hits_total": sum_int(funnel_rows, "raw_hits"),
            "shortlisted_total": sum_int(funnel_rows, "shortlisted"),
            "final_picks_total": sum_int(funnel_rows, "final_picks"),
        },
        "route_stitching": {
            "rows": len(stitching_rows),
            "verdicts": count_by(stitching_rows, "integration_verdict"),
            "route_statuses": count_by(stitching_rows, "route_status"),
        },
        "execution_and_gates": {
            "provider_preflight_rows": len(provider_rows),
            "provider_blockers": provider_blockers,
            "stage_contract_rows": len(stage_rows),
            "stage_progress_rows": len(progress_rows),
            "open_fail_closed_stages": fail_closed_open,
            "target_evidence_rows": len(target_evidence_rows),
            "blocking_decoy_controls_open": decoy_blockers,
            "execution_artifact_rows": len(execution_rows),
            "tool_execution_proof_rows": len(proof_rows),
            "input_gaps": input_gaps,
            "operator_open": operator_open,
        },
        "maturity": {
            "rows": len(maturity_rows),
            "by_status": count_by(maturity_rows, "status"),
            "highest_passed": readiness["highest_passed_maturity"],
        },
        "readiness": readiness,
        "next_actions": next_actions,
        "recommended_commands": recommended_commands(campaign_path, campaign_id),
    }


def render_markdown(status: dict[str, Any]) -> str:
    campaign = status["campaign"]
    readiness = status["readiness"]
    lines = [
        f"# Campaign Status: {campaign['campaign_id']}",
        "",
        f"- Target: {campaign.get('target_molecule') or 'unknown'}",
        f"- Host: {campaign.get('host') or 'unknown'}",
        f"- Mode: {campaign.get('mode') or 'unknown'}",
        f"- Scope: {campaign.get('scope') or 'unknown'}",
        f"- Highest passed maturity: {readiness.get('highest_passed_maturity') or 'none'}",
        f"- Planning ready: {'yes' if readiness.get('planning_ready') else 'no'}",
        f"- Provider launch ready: {'yes' if readiness.get('provider_launch_ready') else 'no'}",
        f"- Promotion ready: {'yes' if readiness.get('promotion_ready') else 'no'}",
        f"- Real execution observed: {'yes' if readiness.get('real_execution_observed') else 'no'}",
        "",
        "## Counts",
        "",
        f"- Routes: {status['routes']['count']}",
        f"- Steps: {status['steps']['count']}",
        f"- Candidate rows: {status['candidates']['candidate_rows']}",
        f"- Funnel raw hits / shortlisted / final picks: "
        f"{status['candidates']['raw_hits_total']} / {status['candidates']['shortlisted_total']} / "
        f"{status['candidates']['final_picks_total']}",
        f"- Target evidence rows: {status['execution_and_gates']['target_evidence_rows']}",
        f"- Execution artifact rows: {status['execution_and_gates']['execution_artifact_rows']}",
        "",
        "## Open Gates",
        "",
    ]
    gates = status["execution_and_gates"]
    gate_items = [
        ("Missing required ledgers", status["ledger_health"]["missing_required"]),
        ("Provider blockers", gates["provider_blockers"]),
        ("Open fail-closed stages", gates["open_fail_closed_stages"]),
        ("Blocking decoy controls open", gates["blocking_decoy_controls_open"]),
        ("Input gaps", gates["input_gaps"]),
        ("Operator intake open", gates["operator_open"]),
    ]
    for label, items in gate_items:
        lines.append(f"- {label}: {len(items)}")
    lines.extend(["", "## Next Actions", ""])
    for action in status["next_actions"]:
        lines.append(f"- {action}")
    lines.extend(["", "## Useful Commands", ""])
    for item in status["recommended_commands"]:
        lines.append(f"- `{item['name']}`: `{item['command']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="Optional output path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    status = compile_status(args.campaign)
    text = (
        json.dumps(status, indent=2, sort_keys=True) + "\n"
        if args.format == "json"
        else render_markdown(status)
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote campaign status: {display_path(args.out)}")
    else:
        print(text, end="" if text.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
