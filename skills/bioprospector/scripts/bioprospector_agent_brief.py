#!/usr/bin/env python3
"""Build an orchestrator-ready BioProspector agent brief."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

MODE_DESCRIPTIONS = {
    "local": "Keep the campaign local in .runtime and use one capable agent to drive the next bounded lane.",
    "goal": "Use the prompt as a /goal-style starter for a capable agent that will plan, run local checks, and summarize next lanes.",
    "symphony-linear": "Use local issue drafts and the campaign graph as the source for reviewed Symphony/Linear work.",
    "cloud-readiness": "Prepare provider contracts and launch blockers only; do not launch compute from this brief.",
    "live-closeout": "Review a completed external run against strict evidence, artifact, control, and claim gates.",
}

AGENT_LABELS = {
    "generic": "capable coding/research agent",
    "codex": "Codex",
    "claude": "Claude Code",
}


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


def command_record(name: str, parts: list[str]) -> dict[str, str]:
    return {"name": name, "command": shell_join(parts)}


def build_commands(
    *,
    campaign: Path,
    out_dir: Path,
    prefix: str,
    profile: str,
    mode: str,
    campaign_id: str,
) -> list[dict[str, str]]:
    campaign_arg = display_path(campaign)
    out_arg = display_path(out_dir)
    commands = [
        command_record(
            "preflight",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_preflight.py",
                "--campaign",
                campaign_arg,
            ],
        ),
        command_record(
            "input_audit",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_input_audit.py",
                "--campaign",
                campaign_arg,
            ],
        ),
        command_record(
            "campaign_status",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_campaign_status.py",
                "--campaign",
                campaign_arg,
                "--out",
                f"{out_arg}/campaign-status.md",
                "--format",
                "markdown",
            ],
        ),
        command_record(
            "campaign_graph",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_campaign_graph.py",
                "--campaign",
                campaign_arg,
                "--out",
                f"{out_arg}/campaign-plan.json",
                "--profile",
                profile,
            ],
        ),
        command_record(
            "handoff_packet",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_handoff_packet.py",
                "--campaign",
                campaign_arg,
                "--out",
                f"{out_arg}/handoff",
                "--prefix",
                prefix,
                "--profile",
                profile,
            ],
        ),
        command_record(
            "issue_dry_run",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_issue_dry_run.py",
                "--campaign",
                campaign_arg,
                "--prefix",
                prefix,
                "--out",
                f"{out_arg}/linear-issues",
                "--include-profile",
                "full-frontier",
            ],
        ),
        command_record(
            "planning_self_check",
            [
                "python3",
                "skills/bioprospector/scripts/bioprospector_contract_self_check.py",
                "--campaign",
                campaign_arg,
            ],
        ),
    ]
    if mode in {"cloud-readiness", "live-closeout"}:
        commands.extend(
            [
                command_record(
                    "runpod_readiness",
                    [
                        "python3",
                        "skills/bioprospector/scripts/bioprospector_runpod_bundle.py",
                        "--campaign",
                        campaign_arg,
                        "--out",
                        f".runtime/runpod-readiness/{campaign_id}",
                    ],
                ),
                command_record(
                    "elasticblast_readiness",
                    [
                        "python3",
                        "skills/bioprospector/scripts/bioprospector_elasticblast_bundle.py",
                        "--campaign",
                        campaign_arg,
                        "--out",
                        f".runtime/elasticblast-readiness/{campaign_id}",
                        "--bucket-uri",
                        "s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast",
                        "--database",
                        "nr",
                        "--budget-usd",
                        "25",
                    ],
                ),
            ]
        )
    if mode == "live-closeout":
        commands.append(
            command_record(
                "strict_closeout_self_check",
                [
                    "python3",
                    "skills/bioprospector/scripts/bioprospector_contract_self_check.py",
                    "--campaign",
                    campaign_arg,
                    "--require-real-execution",
                    "--require-target-evidence",
                    "--require-decoy-controls",
                    "--require-maturity",
                    "L5",
                ],
            )
        )
    return commands


def summarize_lanes(graph: dict[str, Any]) -> dict[str, int]:
    counts = Counter(node.get("lane", "unknown") for node in graph.get("nodes", []))
    return dict(sorted(counts.items()))


def build_goal_prompt(
    *,
    status: dict[str, Any],
    lane_counts: dict[str, int],
    commands: list[dict[str, str]],
    agent: str,
    mode: str,
) -> str:
    campaign = status["campaign"]
    agent_label = AGENT_LABELS[agent]
    command_lines = "\n".join(f"{index}. {item['command']}" for index, item in enumerate(commands[:7], start=1))
    next_actions = "\n".join(f"- {action}" for action in status["next_actions"])
    lane_summary = ", ".join(f"{lane}={count}" for lane, count in lane_counts.items()) or "no lanes compiled"
    return (
        f"Use the BioProspector skill in this checkout as a control plane for {campaign.get('target_molecule') or 'the target'} "
        f"in {campaign.get('host') or 'the selected host'}. You are the {agent_label}; BioProspector supplies schemas, "
        "ledgers, validators, issue-style drafts, and handoff artifacts, but you handle orchestration and judgment.\n\n"
        f"Mode: {mode}. {MODE_DESCRIPTIONS[mode]}\n"
        f"Campaign id: {campaign['campaign_id']}\n"
        f"Claim boundary: {campaign.get('claim_boundary') or 'design intelligence and prioritization only'}\n"
        f"Compiled lane mix: {lane_summary}\n\n"
        "Start by running these local commands, adjusting only paths/prefixes if the operator chose a different campaign:\n"
        f"{command_lines}\n\n"
        "Then decide the next bounded work lane. If Symphony, Linear, or another tracker is available, treat generated issue "
        "drafts as the reviewed source for tracker tasks. If the user says /goal or has no tracker, keep the same lanes under "
        ".runtime and close with a compact dossier-style summary.\n\n"
        "Operator loop: after input audit, ask at most three grouped questions for true blockers. Planning may continue on "
        "reversible assumptions, but execution, cloud spend, candidate promotion, and L5 closeout need explicit gates.\n\n"
        "Safety boundary: do not launch providers, mutate Linear, submit AWS jobs, download databases, paste secrets, or "
        "write raw/private biological data into the repo, tracker, chat, or publishable artifacts. If the operator later "
        "approves real local or cloud execution, keep raw/heavy outputs in user-approved external workdirs, volumes, or "
        "buckets and return compact ledgers, pointers, checksums, summaries, and dossiers. Mock, dry-run, planned, or "
        "readiness rows are not evidence.\n\n"
        "Current next actions:\n"
        f"{next_actions}\n\n"
        "Closeout should report files/artifacts generated, validation commands and results, claim level, unresolved blockers, "
        "and explicit confirmation that no provider launch, cloud mutation, tracker mutation, database download, or raw/private "
        "data write into repo/tracker/chat/publishable artifacts occurred."
    )


def render_markdown(
    *,
    status: dict[str, Any],
    lane_counts: dict[str, int],
    commands: list[dict[str, str]],
    prompt: str,
    mode: str,
    agent: str,
    files: dict[str, str],
) -> str:
    campaign = status["campaign"]
    readiness = status["readiness"]
    lines = [
        f"# BioProspector Agent Brief: {campaign['campaign_id']}",
        "",
        "## Purpose",
        "",
        "This brief is for a capable coding/research agent, a Symphony + Linear sidecar, or a `/goal`-style orchestrator.",
        "BioProspector is the campaign control plane: it provides contracts, ledgers, validators, local drafts, and review artifacts.",
        "The agent or external orchestrator still owns sequencing, tracker operations, provider execution, and final judgment.",
        "",
        "## Campaign Snapshot",
        "",
        f"- Target: {campaign.get('target_molecule') or 'unknown'}",
        f"- Host: {campaign.get('host') or 'unknown'}",
        f"- Mode: {campaign.get('mode') or 'unknown'}",
        f"- Brief mode: {mode}",
        f"- Agent profile: {agent}",
        f"- Planning ready: {'yes' if readiness.get('planning_ready') else 'no'}",
        f"- Provider launch ready: {'yes' if readiness.get('provider_launch_ready') else 'no'}",
        f"- Strict closeout likely ready: {'yes' if readiness.get('strict_closeout_likely_ready') else 'no'}",
        "",
        "## Lane Mix",
        "",
    ]
    for lane, count in lane_counts.items():
        lines.append(f"- {lane}: {count}")
    lines.extend(["", "## Ready-To-Paste Goal Prompt", "", "```text", prompt, "```", "", "## Starting Commands", ""])
    for item in commands:
        lines.append(f"- `{item['name']}`: `{item['command']}`")
    lines.extend(["", "## Current Next Actions", ""])
    for action in status["next_actions"]:
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Orchestrator Boundary",
            "",
            "- This repo does not need to implement every step a strong agent can reason through.",
            "- Use Symphony/Linear, `/goal`, local scripts, or user-chosen cloud resources as orchestration surfaces.",
            "- Keep most work local and review-only until operator gates approve wider action.",
            "- Treat generated tracker drafts as source material, not automatic tracker mutations.",
            "- Treat provider readiness bundles as contracts, not proof of execution.",
            "- Keep real raw/heavy outputs in user-approved external workdirs, volumes, or buckets; return compact ledgers, pointers, checksums, summaries, and dossiers.",
            "",
            "## Generated Files",
            "",
        ]
    )
    for label, path in sorted(files.items()):
        lines.append(f"- {label}: `{path}`")
    lines.append("")
    return "\n".join(lines)


def build_brief(
    campaign: Path,
    out_dir: Path,
    *,
    prefix: str,
    profile: str,
    mode: str,
    agent: str,
) -> dict[str, Any]:
    status_mod = load_script_module("_bioprospector_campaign_status_for_agent_brief", "bioprospector_campaign_status.py")
    graph_mod = load_script_module("_bioprospector_campaign_graph_for_agent_brief", "bioprospector_campaign_graph.py")

    campaign = campaign.resolve()
    out_dir = out_dir.resolve()
    status = status_mod.compile_status(campaign)
    graph = graph_mod.compile_graph(campaign, profile)
    lane_counts = summarize_lanes(graph)
    commands = build_commands(
        campaign=campaign,
        out_dir=out_dir,
        prefix=prefix,
        profile=profile,
        mode=mode,
        campaign_id=status["campaign"]["campaign_id"],
    )
    prompt = build_goal_prompt(status=status, lane_counts=lane_counts, commands=commands, agent=agent, mode=mode)

    files = {
        "agent_brief_md": display_path(out_dir / "agent-brief.md"),
        "agent_brief_json": display_path(out_dir / "agent-brief.json"),
        "goal_prompt_txt": display_path(out_dir / "agent-goal-prompt.txt"),
        "commands_sh": display_path(out_dir / "commands.sh"),
    }
    write_text(out_dir / "agent-goal-prompt.txt", prompt + "\n")
    write_text(
        out_dir / "commands.sh",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "# Review commands before running. This file is generated for agent kickoff.\n\n"
        + "\n".join(item["command"] for item in commands)
        + "\n",
    )
    write_text(
        out_dir / "agent-brief.md",
        render_markdown(
            status=status,
            lane_counts=lane_counts,
            commands=commands,
            prompt=prompt,
            mode=mode,
            agent=agent,
            files=files,
        ),
    )
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_id": status["campaign"]["campaign_id"],
        "target_molecule": status["campaign"].get("target_molecule", ""),
        "host": status["campaign"].get("host", ""),
        "mode": mode,
        "agent": agent,
        "profile": profile,
        "prefix": prefix,
        "lane_counts": lane_counts,
        "files": files,
        "commands": commands,
        "readiness": status["readiness"],
        "safety": {
            "expects_capable_agent_or_external_orchestrator": True,
            "replaces_orchestrator": False,
            "launches_providers": False,
            "mutates_tracker_or_linear": False,
            "downloads_databases": False,
            "writes_raw_private_data_to_repo_tracker_or_chat": False,
            "allows_user_owned_external_result_locations": True,
            "returns_compact_ledgers_pointers_hashes_summaries_dossiers": True,
            "materializes_raw_biological_data": False,
        },
    }
    write_json(out_dir / "agent-brief.json", manifest)
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
    parser.add_argument("--mode", choices=sorted(MODE_DESCRIPTIONS), default="goal")
    parser.add_argument("--agent", choices=sorted(AGENT_LABELS), default="generic")
    args = parser.parse_args()

    manifest = build_brief(
        args.campaign,
        args.out,
        prefix=args.prefix,
        profile=args.profile,
        mode=args.mode,
        agent=args.agent,
    )
    print(f"Wrote agent brief: {display_path(args.out)}")
    print(f"Campaign: {manifest['campaign_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
