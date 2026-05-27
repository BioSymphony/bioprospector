#!/usr/bin/env python3
"""Append a validated BioProspector self-learning row after a process hiccup."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_schema import enum_values, ledger_headers


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_ledger(campaign: Path | None, ledger: Path | None) -> tuple[str, Path]:
    campaign_id = "campaign-id"
    if campaign:
        manifest = load_json(campaign)
        campaign_id = manifest.get("campaign_id", campaign_id)
    if ledger:
        return campaign_id, ledger
    if not campaign:
        raise ValueError("provide --campaign or --ledger")
    rel = manifest.get("ledgers", {}).get("self_learning_skill_ledger", "self-learning-skill-ledger.tsv")
    return campaign_id, campaign.parent / rel


def append_row(path: Path, row: dict[str, str]) -> None:
    headers = ledger_headers()["self_learning_skill_ledger"]
    exists = path.exists() and path.stat().st_size > 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow({header: row.get(header, "") for header in headers})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, help="Campaign manifest; used for campaign id and default ledger path")
    parser.add_argument("--ledger", type=Path, help="Explicit self-learning ledger path")
    parser.add_argument("--learning-id", help="Stable learning row id")
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--hiccup-type", required=True)
    parser.add_argument("--observation", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--probe", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--expected-signal", required=True)
    parser.add_argument("--stop-loss", required=True)
    parser.add_argument("--result", default="not_run")
    parser.add_argument("--decision", default="update_runbook")
    parser.add_argument("--runbook-update", choices=["true", "false"], default="true")
    parser.add_argument("--skill-update", choices=["true", "false"], default="false")
    parser.add_argument("--reusable-guardrail", choices=["true", "false"], default="true")
    parser.add_argument("--claim-boundary", default="Process learning only; not biological validation.")
    parser.add_argument("--owner", default="operator")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    try:
        campaign_id, ledger_path = resolve_ledger(args.campaign.resolve() if args.campaign else None, args.ledger)
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1

    hiccup_types = enum_values("self_learning_hiccup_types")
    decisions = enum_values("self_learning_decisions")
    if args.hiccup_type not in hiccup_types:
        print(f"FAIL invalid --hiccup-type {args.hiccup_type!r}; expected one of: {', '.join(sorted(hiccup_types))}")
        return 1
    if args.decision not in decisions:
        print(f"FAIL invalid --decision {args.decision!r}; expected one of: {', '.join(sorted(decisions))}")
        return 1

    learning_id = args.learning_id or f"SL-{date.today().isoformat()}-{args.hiccup_type}"
    row = {
        "learning_id": learning_id,
        "date": date.today().isoformat(),
        "campaign_id": campaign_id,
        "trigger": args.trigger,
        "hiccup_type": args.hiccup_type,
        "observation": args.observation,
        "hypothesis": args.hypothesis,
        "probe_or_experiment": args.probe,
        "control_or_baseline": args.baseline,
        "expected_signal": args.expected_signal,
        "stop_loss": args.stop_loss,
        "result": args.result,
        "decision": args.decision,
        "runbook_update": args.runbook_update,
        "skill_update": args.skill_update,
        "reusable_guardrail": args.reusable_guardrail,
        "claim_boundary": args.claim_boundary,
        "owner": args.owner,
        "notes": args.notes,
    }
    append_row(ledger_path.resolve(), row)
    print(f"Appended self-learning row {learning_id} to {ledger_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
