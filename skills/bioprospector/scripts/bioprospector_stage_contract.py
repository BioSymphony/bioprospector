#!/usr/bin/env python3
"""Validate BioProspector stage contracts, progress rows, and closeout proof."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTRACT_COLUMNS = {
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
}

PROGRESS_COLUMNS = {
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
}

ARTIFACT_COLUMNS = {
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
}

TERMINAL_PROGRESS = {"completed", "failed", "partial", "skipped", "stalled"}
BAD_PROGRESS = {"failed", "stalled"}
DEGRADED_VALUES = {"blocked", "degraded", "partial", "stalled"}
LIVE_MATURITY = {"L3", "L4", "L5"}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = [{key: (value or "").strip() for key, value in row.items() if key is not None} for row in reader]
        fieldnames = set(reader.fieldnames or [])
    return rows, errors + ([] if fieldnames else [f"{path} is missing a TSV header"])


def optional_tsv(path: Path | None) -> tuple[list[dict[str, str]], list[str]]:
    if path is None:
        return [], []
    if not path.exists():
        return [], [f"missing ledger: {path}"]
    return read_tsv(path)


def manifest_ledger_path(campaign: Path, key: str) -> Path | None:
    manifest = read_json(campaign)
    ledgers = manifest.get("ledgers", {})
    if not isinstance(ledgers, dict) or key not in ledgers:
        return None
    return campaign.parent / str(ledgers[key])


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def parse_float(value: str) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def latest_progress(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest: dict[str, tuple[datetime, int, dict[str, str]]] = {}
    for index, row in enumerate(rows):
        stage_id = row.get("stage_id", "")
        timestamp = parse_timestamp(row.get("timestamp", "")) or datetime.fromtimestamp(index, timezone.utc)
        if stage_id and (stage_id not in latest or timestamp >= latest[stage_id][0]):
            latest[stage_id] = (timestamp, index, row)
    return {stage_id: item[2] for stage_id, item in latest.items()}


def split_artifacts(value: str) -> list[str]:
    parts = []
    for chunk in value.replace(",", ";").replace("|", ";").split(";"):
        text = chunk.strip()
        if text:
            parts.append(text)
    return parts


def artifact_is_path(value: str) -> bool:
    return "/" in value or "." in Path(value).name


def artifact_exists(artifact: str, artifact_root: Path) -> bool:
    path = Path(artifact)
    if path.is_absolute():
        return path.exists()
    return (artifact_root / path).exists()


def validate_headers(rows: list[dict[str, str]], required: set[str], label: str) -> list[str]:
    if not rows:
        return []
    fields = set(rows[0])
    missing = sorted(required - fields)
    return [f"{label} missing columns: {', '.join(missing)}"] if missing else []


def check_stage_contracts(
    stage_contracts: list[dict[str, str]],
    stage_progress: list[dict[str, str]],
    execution_artifacts: list[dict[str, str]],
    *,
    artifact_root: Path,
    check_expected_artifacts: bool = False,
    require_terminal: bool = False,
    require_real_execution: bool = False,
    max_heartbeat_age_minutes: float | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(validate_headers(stage_contracts, CONTRACT_COLUMNS, "stage_contract_ledger"))
    errors.extend(validate_headers(stage_progress, PROGRESS_COLUMNS, "stage_progress_ledger"))
    errors.extend(validate_headers(execution_artifacts, ARTIFACT_COLUMNS, "execution_artifact_ledger"))

    stage_ids = [row.get("stage_id", "") for row in stage_contracts]
    duplicate_stage_ids = sorted({stage_id for stage_id in stage_ids if stage_id and stage_ids.count(stage_id) > 1})
    for stage_id in duplicate_stage_ids:
        errors.append(f"duplicate stage_id: {stage_id}")

    contract_ids = {stage_id for stage_id in stage_ids if stage_id}
    progress_ids = {row.get("stage_id", "") for row in stage_progress if row.get("stage_id", "")}
    unknown_progress = sorted(progress_ids - contract_ids)
    if unknown_progress:
        errors.append("stage_progress_ledger references unknown stage_id values: " + ", ".join(unknown_progress))

    latest = latest_progress(stage_progress)
    materialized_artifacts = {
        row.get("path_or_uri", "")
        for row in execution_artifacts
        if row.get("status", "") == "materialized"
        and not as_bool(row.get("dry_run", ""))
        and not as_bool(row.get("mock_tools", ""))
    }

    for row in stage_contracts:
        stage_id = row.get("stage_id", "")
        label = stage_id or "unnamed stage"
        if not stage_id:
            errors.append("stage_contract_ledger row missing stage_id")
        if not row.get("expected_artifact"):
            errors.append(f"{label}: expected_artifact is required")
        if not row.get("checkpoint_marker"):
            errors.append(f"{label}: checkpoint_marker is required")
        if not row.get("done_marker"):
            errors.append(f"{label}: done_marker is required")
        timeout = parse_float(row.get("timeout_minutes", ""))
        if timeout is None or timeout <= 0:
            errors.append(f"{label}: timeout_minutes must be positive")
        if not row.get("resume_command"):
            errors.append(f"{label}: resume_command is required")
        if as_bool(row.get("fail_closed", "")) and row.get("status", "") in {"failed", "blocked", "partial", "skipped"}:
            errors.append(f"{label}: fail_closed stage has non-success contract status {row.get('status', '')}")

        progress = latest.get(stage_id)
        if require_terminal and progress is None:
            errors.append(f"{label}: missing progress event")
        if progress:
            status = progress.get("event_status", "")
            degraded = progress.get("degraded_status", "")
            if require_terminal and status not in TERMINAL_PROGRESS:
                errors.append(f"{label}: latest progress is not terminal: {status}")
            if as_bool(row.get("fail_closed", "")) and status in BAD_PROGRESS:
                errors.append(f"{label}: fail_closed stage latest progress is {status}")
            if require_real_execution and row.get("required_for_maturity", "") in LIVE_MATURITY:
                if status != "completed":
                    errors.append(f"{label}: live closeout requires completed progress")
                if degraded in DEGRADED_VALUES or status in {"fallback", "partial", "skipped"}:
                    errors.append(f"{label}: live closeout cannot use degraded, fallback, partial, or skipped progress")
            if max_heartbeat_age_minutes is not None:
                age = parse_float(progress.get("heartbeat_age_minutes", ""))
                if age is not None and age > max_heartbeat_age_minutes:
                    errors.append(f"{label}: heartbeat_age_minutes {age:g} exceeds {max_heartbeat_age_minutes:g}")
        elif as_bool(row.get("fail_closed", "")) and row.get("status", "") in {"running", "ready"}:
            warnings.append(f"{label}: fail_closed active stage has no progress row")

        if check_expected_artifacts:
            for artifact in split_artifacts(row.get("expected_artifact", "")):
                if not artifact_is_path(artifact):
                    continue
                exists_locally = artifact_exists(artifact, artifact_root)
                materialized = artifact in materialized_artifacts or str(artifact_root / artifact) in materialized_artifacts
                if not exists_locally and not materialized:
                    errors.append(f"{label}: expected artifact is not present or materialized: {artifact}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "stage_count": len(stage_contracts),
        "progress_stage_count": len(progress_ids),
        "materialized_real_artifact_count": len(materialized_artifacts),
    }


def resolve_inputs(args: argparse.Namespace) -> tuple[Path | None, Path | None, Path | None, Path]:
    campaign = args.campaign.resolve() if args.campaign else None
    contract = args.stage_contract_ledger
    progress = args.stage_progress_ledger
    artifacts = args.execution_artifact_ledger
    artifact_root = args.artifact_root
    if campaign:
        contract = contract or manifest_ledger_path(campaign, "stage_contract_ledger")
        progress = progress or manifest_ledger_path(campaign, "stage_progress_ledger")
        artifacts = artifacts or manifest_ledger_path(campaign, "execution_artifact_ledger")
        artifact_root = artifact_root or campaign.parent
    return contract, progress, artifacts, (artifact_root or Path.cwd()).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, help="Campaign manifest with stage and artifact ledgers")
    parser.add_argument("--stage-contract-ledger", type=Path)
    parser.add_argument("--stage-progress-ledger", type=Path)
    parser.add_argument("--execution-artifact-ledger", type=Path)
    parser.add_argument("--artifact-root", type=Path, help="Root used for relative expected-artifact checks")
    parser.add_argument("--check-expected-artifacts", action="store_true")
    parser.add_argument("--require-terminal", action="store_true")
    parser.add_argument("--require-real-execution", action="store_true")
    parser.add_argument("--max-heartbeat-age-minutes", type=float)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    contract_path, progress_path, artifact_path, artifact_root = resolve_inputs(args)
    errors: list[str] = []
    if not contract_path:
        errors.append("supply --campaign or --stage-contract-ledger")
    contracts, contract_errors = optional_tsv(contract_path)
    progress, progress_errors = optional_tsv(progress_path)
    artifacts, artifact_errors = optional_tsv(artifact_path)
    errors.extend(contract_errors + progress_errors + artifact_errors)
    report = check_stage_contracts(
        contracts,
        progress,
        artifacts,
        artifact_root=artifact_root,
        check_expected_artifacts=args.check_expected_artifacts,
        require_terminal=args.require_terminal,
        require_real_execution=args.require_real_execution,
        max_heartbeat_age_minutes=args.max_heartbeat_age_minutes,
    )
    report["errors"] = errors + report["errors"]
    report["ok"] = not report["errors"]
    report["inputs"] = {
        "stage_contract_ledger": str(contract_path) if contract_path else "",
        "stage_progress_ledger": str(progress_path) if progress_path else "",
        "execution_artifact_ledger": str(artifact_path) if artifact_path else "",
        "artifact_root": str(artifact_root),
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("BioProspector stage contract:", "ok" if report["ok"] else "failed")
        for error in report["errors"]:
            print(f"ERROR: {error}")
        for warning in report["warnings"]:
            print(f"WARN: {warning}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
