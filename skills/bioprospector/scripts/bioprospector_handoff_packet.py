#!/usr/bin/env python3
"""Build a local BioProspector campaign handoff packet for agents/reviewers."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


def load_script_module(module_name: str, filename: str):
    path = SCRIPT_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise RuntimeError("a required BioProspector script is missing; reinstall or repair the checkout")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "REPLACE_ME_EXTERNAL_PATH"


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def status_counts(status: dict[str, Any]) -> list[str]:
    gates = status["execution_and_gates"]
    return [
        f"- Routes: {status['routes']['count']}",
        f"- Steps: {status['steps']['count']}",
        f"- Candidate rows: {status['candidates']['candidate_rows']}",
        f"- Open provider blockers: {len(gates['provider_blockers'])}",
        f"- Open blocking decoy controls: {len(gates['blocking_decoy_controls_open'])}",
        f"- Open fail-closed stages: {len(gates['open_fail_closed_stages'])}",
        f"- Real execution observed: {'yes' if status['readiness']['real_execution_observed'] else 'no'}",
        f"- Highest passed maturity: {status['readiness']['highest_passed_maturity'] or 'none'}",
    ]


def render_handoff_markdown(
    *,
    status: dict[str, Any],
    files: dict[str, str],
    commands: list[dict[str, str]],
    include_issue_drafts: bool,
) -> str:
    campaign = status["campaign"]
    lines = [
        f"# BioProspector Handoff: {campaign['campaign_id']}",
        "",
        "## Campaign",
        "",
        f"- Target: {campaign.get('target_molecule') or 'unknown'}",
        f"- Host: {campaign.get('host') or 'unknown'}",
        f"- Mode: {campaign.get('mode') or 'unknown'}",
        f"- Scope: {campaign.get('scope') or 'unknown'}",
        f"- Status: {campaign.get('status') or 'unknown'}",
        "",
        "## Snapshot",
        "",
        *status_counts(status),
        "",
        "## Next Actions",
        "",
    ]
    for action in status["next_actions"]:
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Generated Files",
            "",
        ]
    )
    for label, path in sorted(files.items()):
        lines.append(f"- {label}: `{path}`")
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for command in commands:
        lines.append(f"- `{command['name']}`: `{command['command']}`")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- This packet is local and review-only.",
            "- It does not launch providers, seed Linear, download databases, or write raw/private biological data into the repo, tracker, chat, or publishable artifacts.",
            "- Real raw/heavy outputs belong in user-approved external workdirs, volumes, or buckets; return compact ledgers, pointers, checksums, summaries, and dossiers.",
            "- Mock, dry-run, readiness, or planned rows remain non-evidence until joined to real execution artifacts.",
            f"- Issue drafts generated in this packet: {'yes' if include_issue_drafts else 'no'}",
            "",
        ]
    )
    return "\n".join(lines)


def build_commands(campaign: Path, out_dir: Path, prefix: str, profile: str) -> list[dict[str, str]]:
    campaign_arg = display_path(campaign)
    out_arg = display_path(out_dir)
    return [
        {
            "name": "preflight",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_preflight.py",
                    "--campaign",
                    campaign_arg,
                ]
            ),
        },
        {
            "name": "input_audit",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_input_audit.py",
                    "--campaign",
                    campaign_arg,
                ]
            ),
        },
        {
            "name": "campaign_status",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_campaign_status.py",
                    "--campaign",
                    campaign_arg,
                    "--out",
                    f"{out_arg}/campaign-status.json",
                ]
            ),
        },
        {
            "name": "campaign_graph",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_campaign_graph.py",
                    "--campaign",
                    campaign_arg,
                    "--out",
                    f"{out_arg}/campaign-plan.json",
                    "--profile",
                    profile,
                ]
            ),
        },
        {
            "name": "issue_dry_run",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_issue_dry_run.py",
                    "--campaign",
                    campaign_arg,
                    "--prefix",
                    prefix,
                    "--out",
                    f"{out_arg}/issue-drafts",
                    "--include-profile",
                    "full-frontier",
                ]
            ),
        },
        {
            "name": "contract_self_check",
            "command": shell_join(
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_contract_self_check.py",
                    "--campaign",
                    campaign_arg,
                ]
            ),
        },
    ]


def run_issue_drafts(campaign: Path, out_dir: Path, prefix: str) -> dict[str, Any]:
    issue_dir = out_dir / "issue-drafts"
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "bioprospector_issue_dry_run.py"),
        "--campaign",
        str(campaign),
        "--prefix",
        prefix,
        "--out",
        str(issue_dir),
        "--include-profile",
        "full-frontier",
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    write_text(out_dir / "issue-dry-run.stdout.txt", result.stdout)
    if result.stderr:
        write_text(out_dir / "issue-dry-run.stderr.txt", result.stderr)
    return {
        "issue_dir": display_path(issue_dir),
        "stdout": display_path(out_dir / "issue-dry-run.stdout.txt"),
        "count": len(list(issue_dir.glob("*.md"))),
    }


def build_packet(
    campaign: Path,
    out_dir: Path,
    *,
    prefix: str,
    profile: str,
    include_issue_drafts: bool,
) -> dict[str, Any]:
    status_mod = load_script_module("_bioprospector_campaign_status_for_handoff", "bioprospector_campaign_status.py")
    graph_mod = load_script_module("_bioprospector_campaign_graph_for_handoff", "bioprospector_campaign_graph.py")

    campaign = campaign.resolve()
    out_dir = out_dir.resolve()
    status = status_mod.compile_status(campaign)
    graph = graph_mod.compile_graph(campaign, profile)
    commands = build_commands(campaign, out_dir, prefix, profile)

    files = {
        "campaign_status_json": display_path(out_dir / "campaign-status.json"),
        "campaign_status_md": display_path(out_dir / "campaign-status.md"),
        "campaign_plan_json": display_path(out_dir / "campaign-plan.json"),
        "commands_sh": display_path(out_dir / "commands.sh"),
        "handoff_md": display_path(out_dir / "handoff.md"),
        "handoff_manifest_json": display_path(out_dir / "handoff-manifest.json"),
    }

    write_json(out_dir / "campaign-status.json", status)
    write_text(out_dir / "campaign-status.md", status_mod.render_markdown(status))
    write_json(out_dir / "campaign-plan.json", graph)
    write_text(
        out_dir / "commands.sh",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "# Review commands before running. This file is generated for operator handoff.\n\n"
        + "\n".join(command["command"] for command in commands)
        + "\n",
    )

    issue_result: dict[str, Any] | None = None
    if include_issue_drafts:
        issue_result = run_issue_drafts(campaign, out_dir, prefix)
        files["issue_drafts"] = issue_result["issue_dir"]

    handoff_md = render_handoff_markdown(
        status=status,
        files=files,
        commands=commands,
        include_issue_drafts=include_issue_drafts,
    )
    write_text(out_dir / "handoff.md", handoff_md)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_id": status["campaign"]["campaign_id"],
        "target_molecule": status["campaign"].get("target_molecule", ""),
        "host": status["campaign"].get("host", ""),
        "profile": profile,
        "prefix": prefix,
        "files": files,
        "issue_drafts": issue_result or {"generated": False},
        "safety": {
            "launches_providers": False,
            "mutates_linear": False,
            "downloads_databases": False,
            "materializes_raw_biological_data": False,
        },
        "readiness": status["readiness"],
    }
    write_json(out_dir / "handoff-manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prefix", default="BIOPROSPECTOR")
    parser.add_argument(
        "--profile",
        choices=[
            "minimal",
            "core-evidence",
            "full-frontier",
            "runpod-ready",
            "live-closeout",
            "literature-only",
            "dark-step",
            "public-demo",
        ],
        default="full-frontier",
    )
    parser.add_argument("--include-issue-drafts", action="store_true")
    args = parser.parse_args()

    manifest = build_packet(
        args.campaign,
        args.out,
        prefix=args.prefix,
        profile=args.profile,
        include_issue_drafts=args.include_issue_drafts,
    )
    print(f"Wrote handoff packet: {display_path(args.out)}")
    print(f"Campaign: {manifest['campaign_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
