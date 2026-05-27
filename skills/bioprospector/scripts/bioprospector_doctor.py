#!/usr/bin/env python3
"""Check a public BioProspector checkout without network or provider mutation."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bioprospector_schema import load_schema


CORE_SCRIPTS = [
    "bioprospector_preflight.py",
    "bioprospector_contract_self_check.py",
    "bioprospector_issue_dry_run.py",
    "bioprospector_campaign_graph.py",
    "bioprospector_candidate_package.py",
    "bioprospector_pareto_rank.py",
    "bioprospector_dossier_export.py",
    "bioprospector_genecluster_atlas_plan.py",
    "bioprospector_genecluster_atlas_normalizers.py",
    "bioprospector_genecluster_atlas_contracts.py",
]

EXAMPLES = [
    "skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json",
    "skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json",
    "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json",
]

OPTIONAL_TOOLS = {
    "aws": "AWS ElasticBLAST readiness review",
    "blastp": "local NCBI BLAST searches",
    "docker": "containerized local workflows",
    "foldseek": "structure-neighbor searches",
    "git": "release hygiene and tracked-file checks",
    "hmmscan": "HMMER domain scans",
    "mmseqs": "local sequence clustering/search",
    "runpodctl": "operator-reviewed RunPod workflows",
}

NON_TSV_LEDGER_KEYS = {"claim_ledger", "provenance_log", "runpod_run_manifest"}


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)


def check_schema(root: Path) -> dict[str, Any]:
    path = root / "schemas" / "bioprospector-ledgers.json"
    try:
        schema = load_schema(path)
    except Exception as exc:  # noqa: BLE001 - report parse/load errors without crashing.
        return {"ok": False, "path": rel(path, root), "error": str(exc)}
    required = schema.get("required_ledger_keys", [])
    optional = schema.get("optional_ledger_keys", [])
    headers = schema.get("ledger_headers", {})
    missing_headers = sorted(
        key for key in list(required) + list(optional) if key not in headers and key not in NON_TSV_LEDGER_KEYS
    )
    return {
        "ok": not missing_headers,
        "path": rel(path, root),
        "schema_version": schema.get("schema_version"),
        "required_ledger_keys": len(required),
        "optional_ledger_keys": len(optional),
        "ledger_headers": len(headers),
        "missing_headers": missing_headers,
    }


def check_scripts(root: Path) -> dict[str, Any]:
    scripts_dir = root / "skills" / "bioprospector" / "scripts"
    missing = [name for name in CORE_SCRIPTS if not (scripts_dir / name).exists()]
    return {"ok": not missing, "checked": len(CORE_SCRIPTS), "missing": missing}


def check_examples(root: Path) -> dict[str, Any]:
    missing = [path for path in EXAMPLES if not (root / path).exists()]
    return {"ok": not missing, "checked": len(EXAMPLES), "missing": missing}


def check_optional_tools() -> dict[str, Any]:
    tools: dict[str, dict[str, str]] = {}
    for name, purpose in OPTIONAL_TOOLS.items():
        path = shutil.which(name)
        tools[name] = {
            "available": str(path is not None).lower(),
            "purpose": purpose,
            "note": "optional; not required for local release checks",
        }
    return {
        "ok": True,
        "available_count": sum(1 for item in tools.values() if item["available"] == "true"),
        "tools": tools,
    }


def check_public_audit(root: Path, include_runtime: bool) -> dict[str, Any]:
    audit = root / "scripts" / "public_audit.py"
    if not audit.exists():
        return {"ok": False, "error": "scripts/public_audit.py missing"}
    tree = run([sys.executable, str(audit), "."], root)
    checks = {
        "tree": {
            "ok": tree.returncode == 0,
            "summary": "PASS public audit" if tree.returncode == 0 else "FAIL public audit",
        }
    }
    ok = tree.returncode == 0
    runtime = root / ".runtime"
    if include_runtime and runtime.exists():
        runtime_result = run([sys.executable, str(audit), ".runtime"], root)
        checks["runtime"] = {
            "ok": runtime_result.returncode == 0,
            "summary": "PASS public audit" if runtime_result.returncode == 0 else "FAIL public audit",
        }
        ok = ok and runtime_result.returncode == 0
    elif include_runtime:
        checks["runtime"] = {"ok": True, "summary": "no .runtime directory present"}
    return {"ok": ok, "checks": checks}


def check_git_tracked_forbidden(root: Path) -> dict[str, Any]:
    git = shutil.which("git")
    if git is None:
        return {"ok": True, "available": False, "note": "git unavailable; public_audit still scans tree"}
    result = run([git, "ls-files", ".runtime", "logs", "internal", "private"], root)
    if result.returncode != 0:
        return {
            "ok": True,
            "available": True,
            "note": "not a git checkout; skipped tracked-file check after public_audit tree scan",
        }
    files = [line for line in result.stdout.splitlines() if line.strip()]
    return {"ok": not files, "available": True, "tracked_forbidden_files": files}


def doctor(root: Path, include_runtime: bool) -> dict[str, Any]:
    root = root.resolve()
    checks = {
        "python": {
            "ok": sys.version_info >= (3, 10),
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "minimum": "3.10",
        },
        "schema": check_schema(root),
        "scripts": check_scripts(root),
        "examples": check_examples(root),
        "optional_tools": check_optional_tools(),
        "public_audit": check_public_audit(root, include_runtime),
        "git_tracked_forbidden": check_git_tracked_forbidden(root),
    }
    required = ["python", "schema", "scripts", "examples", "public_audit", "git_tracked_forbidden"]
    ok = all(bool(checks[name].get("ok")) for name in required)
    return {
        "ok": ok,
        "repo": ".",
        "mode": "local_no_network_no_provider_mutation",
        "checks": checks,
    }


def print_text(report: dict[str, Any]) -> None:
    print("BioProspector doctor:", "ok" if report["ok"] else "failed")
    print(f"Mode: {report['mode']}")
    for name, check in report["checks"].items():
        status = "ok" if check.get("ok") else "failed"
        print(f"- {name}: {status}")
        if name == "optional_tools":
            print(f"  optional tools available: {check['available_count']}/{len(check['tools'])}")
        for key in ("missing", "missing_headers", "tracked_forbidden_files"):
            values = check.get(key) or []
            if values:
                print(f"  {key}: {', '.join(values)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="BioProspector repository root")
    parser.add_argument("--include-runtime", action="store_true", help="Also audit ignored .runtime output when it exists")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)

    report = doctor(args.repo_root, include_runtime=args.include_runtime)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
