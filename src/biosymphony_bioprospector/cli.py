"""Console entry points for the public BioProspector checkout.

The source scripts remain in `skills/bioprospector/scripts` so Codex skills,
shell examples, and editable installs all use one implementation.
"""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

from biosymphony_bioprospector import __version__


SCRIPT_ALIASES = {
    "agent-brief": "bioprospector_agent_brief.py",
    "campaign-graph": "bioprospector_campaign_graph.py",
    "campaign-status": "bioprospector_campaign_status.py",
    "candidate-package": "bioprospector_candidate_package.py",
    "contract-self-check": "bioprospector_contract_self_check.py",
    "doctor": "bioprospector_doctor.py",
    "dossier-export": "bioprospector_dossier_export.py",
    "elasticblast-bundle": "bioprospector_elasticblast_bundle.py",
    "elasticblast-probe": "bioprospector_elasticblast_probe.py",
    "evidence-ingest": "bioprospector_evidence_ingest.py",
    "genecluster-atlas-contracts": "bioprospector_genecluster_atlas_contracts.py",
    "genecluster-atlas-normalizers": "bioprospector_genecluster_atlas_normalizers.py",
    "genecluster-atlas-plan": "bioprospector_genecluster_atlas_plan.py",
    "campaign-handoff": "bioprospector_handoff_packet.py",
    "input-audit": "bioprospector_input_audit.py",
    "issue-dry-run": "bioprospector_issue_dry_run.py",
    "new-campaign": "bioprospector_new_campaign.py",
    "pareto-rank": "bioprospector_pareto_rank.py",
    "preflight": "bioprospector_preflight.py",
    "public-demo-smoke": "bioprospector_public_demo_smoke.py",
    "retrospective": "bioprospector_retrospective.py",
    "runpod-bundle": "bioprospector_runpod_bundle.py",
    "self-learning": "bioprospector_self_learning.py",
    "stage-contract": "bioprospector_stage_contract.py",
    "workspace-status": "bioprospector_workspace_status.py",
}


COMMAND_GROUPS = {
    "Health and release": ["doctor", "workspace-status"],
    "Campaign control plane": [
        "new-campaign",
        "preflight",
        "input-audit",
        "campaign-status",
        "agent-brief",
        "campaign-handoff",
        "issue-dry-run",
        "contract-self-check",
        "stage-contract",
        "self-learning",
    ],
    "Evidence and dossier": [
        "evidence-ingest",
        "campaign-graph",
        "candidate-package",
        "pareto-rank",
        "retrospective",
        "dossier-export",
    ],
    "GeneCluster atlas": [
        "genecluster-atlas-plan",
        "genecluster-atlas-normalizers",
        "genecluster-atlas-contracts",
    ],
    "Provider readiness": [
        "runpod-bundle",
        "elasticblast-bundle",
        "elasticblast-probe",
        "public-demo-smoke",
    ],
}


def _is_checkout_root(candidate: Path) -> bool:
    scripts = candidate / "skills" / "bioprospector" / "scripts"
    schema = candidate / "schemas" / "bioprospector-ledgers.json"
    return scripts.is_dir() and schema.exists()


def repo_root() -> Path:
    env_root = os.environ.get("BIOPROSPECTOR_REPO_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if _is_checkout_root(candidate):
            return candidate
        raise SystemExit(
            "BIOPROSPECTOR_REPO_ROOT does not point at a BioProspector checkout "
            "with skills/bioprospector/scripts and schemas/bioprospector-ledgers.json."
        )

    # Editable installs resolve to <repo>/src/biosymphony_bioprospector/cli.py.
    # We intentionally do not probe Path.cwd(); console scripts must not execute
    # arbitrary repo-shaped code from the caller's working directory.
    for candidate in Path(__file__).resolve().parents:
        if _is_checkout_root(candidate):
            return candidate
    raise SystemExit(
        "Could not locate a BioProspector checkout. Install in editable mode from "
        "the checkout, run with PYTHONPATH=src from the checkout, or set "
        "BIOPROSPECTOR_REPO_ROOT explicitly."
    )


def run_script(script_name: str, argv: list[str] | None = None) -> int:
    root = repo_root()
    script_path = root / "skills" / "bioprospector" / "scripts" / script_name
    if not script_path.exists():
        raise SystemExit("A required BioProspector script is missing; reinstall or repair the checkout.")

    old_argv = sys.argv[:]
    try:
        sys.argv = [str(script_path), *(argv if argv is not None else sys.argv[1:])]
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        sys.argv = old_argv
    return 0


def _print_help() -> None:
    commands = "\n".join(f"  {name}" for name in sorted(SCRIPT_ALIASES))
    print(
        "BioSymphony BioProspector public CLI\n\n"
        "Usage:\n"
        "  bioprospector <command> [args...]\n"
        "  bioprospector commands [--json]\n"
        "  bioprospector quickstart\n"
        "  bioprospector --version\n"
        "  bioprospector-preflight [args...]\n\n"
        "Commands:\n"
        f"{commands}\n\n"
        "All commands are local control-plane helpers. They do not launch RunPod, "
        "submit ElasticBLAST, seed Linear, or download databases unless a future "
        "operator adds and reviews an execution command.\n\n"
        "For safety, packaged entry points only execute scripts from the editable "
        "checkout that owns this CLI, or from BIOPROSPECTOR_REPO_ROOT when set."
    )


def _command_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    grouped = {name: group for group, names in COMMAND_GROUPS.items() for name in names}
    for name, script in sorted(SCRIPT_ALIASES.items()):
        records.append({"command": name, "script": script, "group": grouped.get(name, "Other")})
    return records


def _print_commands(*, json_output: bool = False) -> None:
    records = _command_records()
    if json_output:
        print(json.dumps({"version": __version__, "commands": records}, indent=2, sort_keys=True))
        return
    for group, names in COMMAND_GROUPS.items():
        print(group)
        for name in names:
            print(f"  {name}")


def _print_quickstart() -> None:
    print(
        "BioProspector quickstart\n\n"
        "1. python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime\n"
        "2. make local-demo\n"
        "3. python3 scripts/public_audit.py .\n"
        "4. make release-check\n\n"
        "Editable CLI smoke:\n"
        "  PYTHONPATH=src python3 -m biosymphony_bioprospector.cli commands\n\n"
        "Packaged entry points are checkout launchers. Install editable from this "
        "repo or set BIOPROSPECTOR_REPO_ROOT when running from another directory.\n\n"
        "The public lane stays local and review-only: no pods, cloud jobs, database "
        "downloads, Linear writes, or raw/private data writes into repo, tracker, "
        "chat, or publishable artifacts."
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        _print_help()
        return 0
    if args[0] in {"--version", "version"}:
        print(__version__)
        return 0
    if args[0] == "commands":
        _print_commands(json_output="--json" in args[1:])
        return 0
    if args[0] == "quickstart":
        _print_quickstart()
        return 0

    command = args.pop(0).replace("_", "-")
    script_name = SCRIPT_ALIASES.get(command)
    if not script_name:
        _print_help()
        raise SystemExit(f"Unknown BioProspector command: {command}")
    return run_script(script_name, args)


def campaign_graph() -> int:
    return run_script("bioprospector_campaign_graph.py")


def agent_brief() -> int:
    return run_script("bioprospector_agent_brief.py")


def campaign_status() -> int:
    return run_script("bioprospector_campaign_status.py")


def campaign_handoff() -> int:
    return run_script("bioprospector_handoff_packet.py")


def candidate_package() -> int:
    return run_script("bioprospector_candidate_package.py")


def contract_self_check() -> int:
    return run_script("bioprospector_contract_self_check.py")


def doctor() -> int:
    return run_script("bioprospector_doctor.py")


def dossier_export() -> int:
    return run_script("bioprospector_dossier_export.py")


def elasticblast_bundle() -> int:
    return run_script("bioprospector_elasticblast_bundle.py")


def elasticblast_probe() -> int:
    return run_script("bioprospector_elasticblast_probe.py")


def evidence_ingest() -> int:
    return run_script("bioprospector_evidence_ingest.py")


def genecluster_atlas_contracts() -> int:
    return run_script("bioprospector_genecluster_atlas_contracts.py")


def genecluster_atlas_normalizers() -> int:
    return run_script("bioprospector_genecluster_atlas_normalizers.py")


def genecluster_atlas_plan() -> int:
    return run_script("bioprospector_genecluster_atlas_plan.py")


def input_audit() -> int:
    return run_script("bioprospector_input_audit.py")


def issue_dry_run() -> int:
    return run_script("bioprospector_issue_dry_run.py")


def new_campaign() -> int:
    return run_script("bioprospector_new_campaign.py")


def pareto_rank() -> int:
    return run_script("bioprospector_pareto_rank.py")


def preflight() -> int:
    return run_script("bioprospector_preflight.py")


def public_demo_smoke() -> int:
    return run_script("bioprospector_public_demo_smoke.py")


def retrospective() -> int:
    return run_script("bioprospector_retrospective.py")


def runpod_bundle() -> int:
    return run_script("bioprospector_runpod_bundle.py")


def self_learning() -> int:
    return run_script("bioprospector_self_learning.py")


def stage_contract() -> int:
    return run_script("bioprospector_stage_contract.py")


def workspace_status() -> int:
    return run_script("bioprospector_workspace_status.py")


if __name__ == "__main__":
    raise SystemExit(main())
