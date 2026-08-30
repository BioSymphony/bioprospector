#!/usr/bin/env python3
"""Scan local runtime run folders and emit a public-safe retrospective TSV.

This helper summarizes local after-run artifacts without exposing provider
resource identifiers. It is for audit and closeout triage only: rows summarize
tool/provider outcomes, artifact presence, cleanup records, and timing hints;
they do not validate biology, target production, enzyme function, or pathway
completion.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO / ".runtime"
DEFAULT_OUT = REPO / ".runtime" / "retrospective-ledger.tsv"

COLUMNS = [
    "run_dir",
    "run_id",
    "provider",
    "profile",
    "issue",
    "provider_resource_seen",
    "provider_resource_ref",
    "max_cost_usd",
    "max_minutes",
    "start_iso",
    "end_iso",
    "duration_min",
    "final_status",
    "error",
    "steps_total",
    "steps_failed",
    "artifacts_present",
    "cleanup_status",
    "notes",
]


def recorded_number(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ""
    return "recorded"


def normalize_status(value: Any) -> str:
    status = str(value or "").strip().lower()
    if status in {"success", "succeeded", "complete", "completed", "done"}:
        return "succeeded"
    if status in {"fail", "failed", "error"}:
        return "failed"
    if status in {"pending", "queued", "running", "stuck_submitting", "unknown"}:
        return status
    return "unknown" if status else ""


def normalize_cleanup_status(value: Any) -> str:
    status = str(value or "").strip().lower()
    if status in {"success", "succeeded", "complete", "completed", "done", "deleted", "removed"}:
        return "completed"
    if status in {"fail", "failed", "error"}:
        return "failed"
    return "recorded" if status else ""


def load_json(path: Path) -> Any | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def blank_row(run_dir: Path, provider: str) -> dict[str, Any]:
    row: dict[str, Any] = {column: "" for column in COLUMNS}
    row["run_dir"] = "recorded"
    row["provider"] = provider
    row["provider_resource_seen"] = "no"
    return row


def mark_provider_resource(row: dict[str, Any], seen: bool) -> None:
    if seen:
        row["provider_resource_seen"] = "yes"
        row["provider_resource_ref"] = "redacted"


def parse_provider_after_run(run_dir: Path) -> dict[str, Any]:
    row = blank_row(run_dir, "runpod")
    resource_record = load_json(run_dir / "runpod_resource_record.json") or {}
    preview = resource_record.get("preview") or {}
    plan = preview.get("plan") or {}
    contract = preview.get("contract") or {}
    compute = plan.get("compute") or {}
    egress = (plan.get("execution") or {}).get("artifact_egress") or {}
    matches = (resource_record.get("duplicate_check") or {}).get("active_matches") or []

    raw_run_id = contract.get("run_id")
    if raw_run_id:
        row["run_id"] = "recorded"
    if compute.get("profile"):
        row["profile"] = "recorded"
    if compute.get("max_estimated_cost_usd") is not None:
        row["max_cost_usd"] = recorded_number(compute["max_estimated_cost_usd"])
    if compute.get("max_runtime_minutes") is not None:
        row["max_minutes"] = recorded_number(compute["max_runtime_minutes"])
    mark_provider_resource(row, bool(matches and matches[0].get("id")))

    summary = load_json(run_dir / "trusted_after_run_summary.json") or {}
    if summary.get("issue_identifier"):
        row["issue"] = "recorded"
    if not row["run_id"] and summary.get("run_id"):
        row["run_id"] = "recorded"
    row["final_status"] = normalize_status(summary.get("final_status", row["final_status"]))
    if summary.get("error"):
        row["error"] = "present"

    steps = summary.get("steps") or []
    row["steps_total"] = len(steps) if steps else ""
    failed = [step for step in steps if step.get("returncode") not in (0, None)]
    row["steps_failed"] = len(failed) if steps else ""
    timing_recorded = any(step.get("started_at") or step.get("ended_at") for step in steps)

    create_response = (
        load_json(run_dir / "create_pod_response.json")
        or load_json(run_dir / "create_pod.stdout.json")
        or load_json(run_dir / "create_pod.json")
        or {}
    )
    raw_resource_ref = create_response.get("pod_id") or (create_response.get("response") or {}).get("pod_id")
    mark_provider_resource(row, bool(raw_resource_ref))

    probe = run_dir / "probe_loop.ndjson"
    if probe.exists() and not row["start_iso"]:
        try:
            with probe.open("r", encoding="utf-8") as handle:
                lines = [json.loads(line) for line in handle if line.strip()]
            if lines:
                timing_recorded = True
        except (OSError, json.JSONDecodeError):
            pass

    cleanup = load_json(run_dir / "cleanup_response.json") or load_json(run_dir / "runpod_cleanup_record.json") or {}
    if cleanup:
        row["cleanup_status"] = normalize_cleanup_status(cleanup.get("status") or cleanup.get("action"))

    artifact_dir = run_dir / "runpod-execution"
    artifact_archive = run_dir / "runpod-execution.tar.gz"
    if artifact_dir.exists() or artifact_archive.exists():
        row["artifacts_present"] = "yes"
    elif egress.get("archive_path"):
        row["artifacts_present"] = "no"

    if not row["final_status"]:
        row["final_status"] = "unknown"
        if row["artifacts_present"] == "yes":
            row["final_status"] = "succeeded"
        elif row["error"]:
            row["final_status"] = "failed"

    notes: list[str] = []
    if egress.get("mode"):
        notes.append("egress_mode_recorded")
    if timing_recorded:
        notes.append("timing_recorded")
    if row["provider_resource_seen"] == "yes":
        notes.append("provider_resource_identifier_redacted")
    if row["provider_resource_seen"] == "yes" and not cleanup:
        notes.append("cleanup_record_missing")
    row["notes"] = "; ".join(notes)
    return row


def parse_elasticblast(run_dir: Path) -> dict[str, Any]:
    row = blank_row(run_dir, "elasticblast")
    row["run_id"] = "recorded"

    state = ""
    for log_name in ("status.log", "submit.log"):
        path = run_dir / log_name
        if not path.exists():
            continue
        try:
            lines = path.read_text(encoding="utf-8").strip().splitlines()
        except OSError:
            continue
        if lines:
            state = lines[-1]
            if log_name == "status.log":
                break

    state_upper = state.upper()
    if state_upper.startswith("SUBMITTING"):
        row["final_status"] = "stuck_submitting"
    elif "SEARCH SUCCEEDED" in state_upper or state_upper.startswith(("DONE", "SUCCESS")):
        row["final_status"] = "succeeded"
    elif state_upper.startswith(("FAILED", "ERROR")):
        row["final_status"] = "failed"
    else:
        row["final_status"] = "unknown"

    results = list(run_dir.glob("**/*.tsv")) + list(run_dir.glob("**/*.xml")) + list(run_dir.glob("**/results*"))
    row["artifacts_present"] = "yes" if results else "no"
    row["notes"] = "status_log_read" if state else ""
    return row


def discover_runs(root: Path) -> list[Path]:
    root = root.resolve()
    if not root.exists():
        return []
    runs: list[Path] = []
    for item in sorted(root.iterdir()):
        if not item.is_dir():
            continue
        name = item.name
        has_provider_record = (item / "runpod_resource_record.json").exists() or (
            item / "trusted_after_run_summary.json"
        ).exists()
        if has_provider_record and ("after-run" in name or name.startswith(("runpod-", "provider-"))):
            runs.append(item)
            continue
        if name.startswith("elasticblast-smoke") or (item / "status.log").exists() or (item / "submit.log").exists():
            runs.append(item)
    return runs


def manifest_expected_artifacts(manifest_path: Path) -> list[str]:
    manifest = load_json(manifest_path) or {}
    execution = manifest.get("execution") or {}
    return list(execution.get("expected_artifacts") or [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Runtime directory to scan")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output TSV path")
    parser.add_argument("--manifest", type=Path, help="Optional campaign manifest for expected_artifacts audit")
    parser.add_argument("--quiet", action="store_true", help="Skip summary output")
    args = parser.parse_args()

    root = args.root.resolve()
    out_path = args.out.resolve()
    if not root.exists():
        print("error: runtime root not found; run make local-demo or pass --root <directory>", file=sys.stderr)
        return 2

    rows: list[dict[str, Any]] = []
    for ordinal, run_dir in enumerate(discover_runs(root), start=1):
        try:
            if run_dir.name.startswith("elasticblast") or (run_dir / "status.log").exists() or (run_dir / "submit.log").exists():
                row = parse_elasticblast(run_dir)
            else:
                row = parse_provider_after_run(run_dir)
            public_run_ref = f"run-{ordinal:03d}"
            row["run_dir"] = public_run_ref
            if row["run_id"]:
                row["run_id"] = public_run_ref
            rows.append(row)
        except (OSError, ValueError) as exc:
            print(f"warn: skipped one run ({type(exc).__name__})", file=sys.stderr)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    if not args.quiet:
        provider_resources = sum(1 for row in rows if row["provider_resource_seen"] == "yes")
        print(
            "runs scanned: "
            f"{len(rows)} (runpod={sum(1 for row in rows if row['provider'] == 'runpod')}, "
            f"elasticblast={sum(1 for row in rows if row['provider'] == 'elasticblast')})",
            file=sys.stderr,
        )
        print(
            "  succeeded: "
            f"{sum(1 for row in rows if row['final_status'] == 'succeeded')}, "
            f"failed: {sum(1 for row in rows if row['final_status'] == 'failed')}, "
            f"stuck/unknown: {sum(1 for row in rows if row['final_status'] in {'stuck_submitting', 'unknown'})}",
            file=sys.stderr,
        )
        print(f"  provider resources redacted: {provider_resources}", file=sys.stderr)
        print("retrospective ledger written", file=sys.stderr)

        if args.manifest:
            expected = manifest_expected_artifacts(args.manifest)
            if expected:
                print(f"\nexpected artifacts declared: {len(expected)}", file=sys.stderr)
                print("cross-reference them in approved external storage", file=sys.stderr)
            else:
                print("\nno execution.expected_artifacts declared", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
