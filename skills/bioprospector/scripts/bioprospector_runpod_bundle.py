#!/usr/bin/env python3
"""Create a prep-only RunPod readiness bundle for a BioProspector campaign.

This generator does not call the RunPod API, install packages, or download
databases. It writes reviewable launch/readiness files under `.runtime/` so an
operator can inspect the plan before creating a manual RunPod Pod.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_ROOT = REPO_ROOT / ".runtime"
NETWORK_VOLUME_MOUNT = "/workspace"
REMOTE_WORKDIR_TEMPLATE = "/workspace/bioprospector/runs/{campaign_id}"
DEFAULT_BUDGET_USD = 99.0
IMAGE_ACCESS_VALUES = {"unknown", "public", "private_auth_required", "private_auth_verified"}

PLANNED_TOOLS: list[dict[str, Any]] = [
    {
        "name": "Python 3",
        "purpose": "runner glue, TSV/JSON processing, provenance summaries",
        "readiness_check": "python3 --version",
        "stage": "required_for_readiness",
    },
    {
        "name": "MMseqs2",
        "purpose": "large-scale protein clustering and sensitive sequence search",
        "readiness_check": "command -v mmseqs",
        "stage": "planned_search_tool",
    },
    {
        "name": "DIAMOND",
        "purpose": "fast protein similarity search against curated public sets",
        "readiness_check": "command -v diamond",
        "stage": "planned_search_tool",
    },
    {
        "name": "BLAST+",
        "purpose": "compatibility search and spot checks with local databases",
        "readiness_check": "command -v blastp",
        "stage": "planned_search_tool",
    },
    {
        "name": "HMMER or pyhmmer",
        "purpose": "domain and family model searches, especially Pfam-A",
        "readiness_check": "command -v hmmscan or python import pyhmmer",
        "stage": "planned_domain_tool",
    },
    {
        "name": "seqkit",
        "purpose": "FASTA/FASTQ inspection and lightweight sequence transforms",
        "readiness_check": "command -v seqkit",
        "stage": "planned_sequence_utility",
    },
    {
        "name": "NCBI Datasets CLI",
        "purpose": "accession-stable public genome/protein set retrieval when approved",
        "readiness_check": "command -v datasets",
        "stage": "planned_public_data_tool",
    },
    {
        "name": "DuckDB",
        "purpose": "local analytical tables and compact evidence stores",
        "readiness_check": "python import duckdb or command -v duckdb",
        "stage": "planned_analysis_tool",
    },
    {
        "name": "Polars or pandas",
        "purpose": "ledger joins, filtering, and summary exports",
        "readiness_check": "python import polars or pandas",
        "stage": "planned_analysis_tool",
    },
    {
        "name": "RDKit",
        "purpose": "small-molecule descriptors, reaction normalization support, chemistry checks",
        "readiness_check": "python import rdkit",
        "stage": "planned_chemistry_tool",
    },
    {
        "name": "COBRApy",
        "purpose": "host-fit and metabolic context review where models are available",
        "readiness_check": "python import cobra",
        "stage": "planned_host_fit_tool",
    },
    {
        "name": "Nextflow or Snakemake",
        "purpose": "resumable workflow execution after readiness is approved",
        "readiness_check": "command -v nextflow or command -v snakemake",
        "stage": "planned_workflow_runner",
    },
]

PLANNED_DATABASES: list[dict[str, str]] = [
    {
        "name": "Swiss-Prot",
        "policy": "public/open-first curated protein search set",
        "remote_cache": "/workspace/bioprospector/db/swissprot",
        "status": "planned; do not download during bundle generation",
    },
    {
        "name": "selected UniRef",
        "policy": "public/open-first clustered proteins, selected by campaign scope",
        "remote_cache": "/workspace/bioprospector/db/uniref-selected",
        "status": "planned; stage only after scout review",
    },
    {
        "name": "selected RefSeq protein sets",
        "policy": "public/open-first accession-based protein sets",
        "remote_cache": "/workspace/bioprospector/db/refseq-protein-selected",
        "status": "planned; stage only after target taxa are reviewed",
    },
    {
        "name": "Pfam-A HMMs",
        "policy": "public/open-first domain model set with attribution",
        "remote_cache": "/workspace/bioprospector/db/pfam-a",
        "status": "planned; use for HMMER/pyhmmer domain checks",
    },
    {
        "name": "Rhea",
        "policy": "public/open-first reaction database with citation",
        "remote_cache": "/workspace/bioprospector/db/rhea",
        "status": "planned metadata/reference table",
    },
    {
        "name": "ChEBI",
        "policy": "public/open-first chemistry ontology with citation",
        "remote_cache": "/workspace/bioprospector/db/chebi",
        "status": "planned metadata/reference table",
    },
    {
        "name": "MetaNetX",
        "policy": "public/open-first reaction cross-reference with attribution",
        "remote_cache": "/workspace/bioprospector/db/metanetx",
        "status": "planned metadata/reference table",
    },
    {
        "name": "MIBiG metadata",
        "policy": "public/open-first natural product/BGC metadata with citation",
        "remote_cache": "/workspace/bioprospector/db/mibig-metadata",
        "status": "planned metadata/reference table",
    },
]

DEFERRED_RESTRICTED_RESOURCES: list[dict[str, str]] = [
    {
        "resource": "private, proprietary, collaborator-restricted, or unpublished sequences",
        "reason": "blocked for this bundle; require explicit rights, secure transfer, and separate approval",
    },
    {
        "resource": "raw reads, genome mirrors, BLAST/MMseqs/DIAMOND databases, and model weights",
        "reason": "never store in this repo; keep only on approved provider volumes or external stores",
    },
    {
        "resource": "full nr",
        "reason": "defer until curated/public-first scout searches justify storage and compute cost",
    },
    {
        "resource": "full metagenome mirrors",
        "reason": "defer until candidate funnels prove value and storage budget is approved",
    },
    {
        "resource": "full InterProScan on unclustered hits",
        "reason": "defer until raw hits are compressed to a smaller reviewed set",
    },
    {
        "resource": "bulk BRENDA or BioCyc integration",
        "reason": "license and redistribution review required before use",
    },
    {
        "resource": "structure prediction or docking for thousands of candidates",
        "reason": "defer until candidate shortlist and scientific question justify GPU spend",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "_", "-", "/", ":"}:
            cleaned.append("-")
    out = "".join(cleaned).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "campaign"


def image_has_digest(image: str) -> bool:
    return "@sha256:" in image


def image_registry_host(image: str) -> str:
    first = image.split("/", 1)[0]
    if "." in first or ":" in first or first == "localhost":
        return first
    return "docker.io"


def image_pull_contract(image: str, image_access: str) -> dict[str, Any]:
    digest_pinned = image_has_digest(image)
    registry = image_registry_host(image)
    auth_required = image_access == "private_auth_required"
    auth_verified = image_access in {"public", "private_auth_verified"}
    launch_blockers: list[str] = []
    if not digest_pinned:
        launch_blockers.append("image_not_digest_pinned")
    if auth_required:
        launch_blockers.append("private_registry_auth_not_verified")
    if image_access == "unknown":
        launch_blockers.append("image_access_unknown")
    return {
        "image": image,
        "registry": registry,
        "image_access": image_access,
        "digest_pinned": digest_pinned,
        "registry_auth_required": auth_required,
        "registry_auth_verified": auth_verified,
        "launch_blockers": launch_blockers,
        "policy": (
            "Before live launch, the provider must be able to pull the exact image. "
            "Private GHCR or other private registry images require provider-side auth verified outside this repo."
        ),
    }


def resolve_output_dir(out_arg: Path | None, campaign_id: str) -> Path:
    if out_arg is None:
        out = RUNTIME_ROOT / "runpod-readiness" / slug(campaign_id)
    else:
        out = out_arg.expanduser()
        if not out.is_absolute():
            out = (REPO_ROOT / out).resolve()
    out = out.resolve()
    if not path_is_under(out, RUNTIME_ROOT):
        raise ValueError(f"output directory must be under {RUNTIME_ROOT}")
    return out


def campaign_file_hashes(campaign_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    base = campaign_path.parent
    files: list[Path] = [campaign_path]

    target_contract = manifest.get("target_contract")
    if isinstance(target_contract, str) and target_contract:
        files.append(base / target_contract)

    ledgers = manifest.get("ledgers")
    if isinstance(ledgers, dict):
        for rel in ledgers.values():
            if isinstance(rel, str) and rel:
                files.append(base / rel)

    hashes = []
    seen: set[Path] = set()
    for path in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        hashes.append(
            {
                "path": repo_relative(resolved),
                "exists": str(resolved.exists()).lower(),
                "sha256": sha256_file(resolved) if resolved.exists() else "",
            }
        )
    return hashes


def campaign_resources(campaign_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    ledgers = manifest.get("ledgers")
    if not isinstance(ledgers, dict):
        return []
    rel = ledgers.get("resource_ledger")
    if not isinstance(rel, str) or not rel:
        return []
    path = campaign_path.parent / rel
    if not path.exists():
        return []
    return read_tsv(path)


def search_width_summary(campaign_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    ledgers = manifest.get("ledgers")
    if not isinstance(ledgers, dict):
        return {"steps": 0, "by_width": {}, "frontier_or_wide_steps": []}
    rel = ledgers.get("reaction_step_ledger")
    if not isinstance(rel, str) or not rel:
        return {"steps": 0, "by_width": {}, "frontier_or_wide_steps": []}
    path = campaign_path.parent / rel
    if not path.exists():
        return {"steps": 0, "by_width": {}, "frontier_or_wide_steps": []}

    rows = read_tsv(path)
    by_width: dict[str, int] = {}
    high_width_steps: list[dict[str, str]] = []
    for row in rows:
        width = row.get("candidate_search_width", "unspecified") or "unspecified"
        by_width[width] = by_width.get(width, 0) + 1
        if width in {"wide", "frontier"}:
            high_width_steps.append(
                {
                    "step_id": row.get("step_id", ""),
                    "route_id": row.get("route_id", ""),
                    "enzyme_role": row.get("enzyme_role", ""),
                    "candidate_search_width": width,
                }
            )
    return {"steps": len(rows), "by_width": by_width, "frontier_or_wide_steps": high_width_steps}


def build_manifest(
    *,
    campaign_path: Path,
    campaign: dict[str, Any],
    out_dir: Path,
    image: str,
    image_access: str,
    scout_budget_usd: float,
) -> dict[str, Any]:
    campaign_id = str(campaign["campaign_id"])
    remote_workdir = REMOTE_WORKDIR_TEMPLATE.format(campaign_id=campaign_id)
    manifest_remote_workdir = (
        campaign.get("execution", {}).get("remote_workdir")
        if isinstance(campaign.get("execution"), dict)
        else None
    )
    remote_workdir_notes = []
    if manifest_remote_workdir and manifest_remote_workdir != remote_workdir:
        remote_workdir_notes.append(
            f"Campaign manifest remote_workdir was {manifest_remote_workdir}; readiness bundle uses {remote_workdir}."
        )

    return {
        "schema": "biosymphony.bioprospector.runpod_readiness_bundle.v1",
        "generated_at": utc_now(),
        "generator": repo_relative(Path(__file__)),
        "source_campaign": {
            "path": repo_relative(campaign_path),
            "sha256": sha256_file(campaign_path),
            "campaign_manifest": campaign,
            "related_file_hashes": campaign_file_hashes(campaign_path, campaign),
        },
        "campaign": {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("campaign_name", ""),
            "target_molecule": campaign.get("target_molecule", ""),
            "host": campaign.get("host", ""),
            "mode": campaign.get("mode", ""),
            "scope": campaign.get("scope", ""),
            "claim_boundary": campaign.get("claim_boundary", ""),
            "search_width_summary": search_width_summary(campaign_path, campaign),
        },
        "runpod_contract": {
            "provider_class": "runpod_manual_pod",
            "launch_mode": "manual_pod_plus_scripts",
            "runpod_api_calls": "not_allowed_in_this_bundle",
            "network_volume_mount": NETWORK_VOLUME_MOUNT,
            "remote_workdir": remote_workdir,
            "remote_workdir_notes": remote_workdir_notes,
            "image": image,
            "image_pull_contract": image_pull_contract(image, image_access),
            "image_policy": "pin a digest before live execution; placeholder images are readiness-only",
            "scout_guardrail": {
                "max_spend_usd_exclusive": 100,
                "configured_budget_usd": scout_budget_usd,
                "policy": "stop before reaching $100; escalate only after candidate-funnel review",
            },
            "remote_directory_layout": [
                f"{remote_workdir}/inputs",
                f"{remote_workdir}/db",
                f"{remote_workdir}/work",
                f"{remote_workdir}/outputs",
                f"{remote_workdir}/provenance",
            ],
            "artifact_policy": {
                "keep_remote": [
                    "raw reads",
                    "large sequence databases",
                    "workflow work directories",
                    "model weights",
                    "large intermediate search outputs",
                ],
                "copy_back_local": [
                    "run_summary.json",
                    "candidate-funnels.tsv updates",
                    "enzyme-draft-board.tsv updates",
                    "sequence-search-plan-ledger.tsv updates",
                    "candidate-sequence-ledger.tsv with AA-only pointers and checksums",
                    "domain-annotation-ledger.tsv with compact domain spans and motif summaries",
                    "literature-search-ledger.tsv with compact citation/search summaries",
                    "candidate-diversity-ledger.tsv with selected diversity classes",
                    "candidate-graph-ledger.tsv or graph summary edges",
                    "run-output-package-ledger.tsv package index",
                    "route-stitching-scorecard.tsv updates",
                    "provenance summaries",
                    "versions.json",
                    "licenses.tsv",
                ],
            },
            "candidate_package_contract": {
                "graph_artifacts": [
                    "candidate_graph.json",
                    "candidate_graph.tsv",
                    "candidate_graph.graphml",
                ],
                "sequence_policy": "protein_aa_only_or_provider_pointer; no nucleotide constructs, raw all-hit dumps, or private sequences copied back",
                "domain_policy": "domain spans, motif summaries, active-site notes, source database, accession/version, and confidence only",
                "literature_policy": "query terms, sources, citation identifiers, claim summaries, and license boundaries only; no full text mirrors",
                "diversity_policy": [
                    "canonical characterized seeds",
                    "close homologs",
                    "diverse homologs",
                    "remote homologs",
                    "weird_or_novel candidates kept separate from normal homolog hits",
                ],
                "ranking_views": [
                    "minimal_genes",
                    "highest_evidence",
                    "best_host_fit",
                    "clearest_validation_handoff",
                    "ambitious_de_novo",
                    "diversity_library",
                ],
            },
        },
        "data_policy": {
            "policy_name": "public/open-first",
            "allowed_first": [
                "public accessions",
                "open or openly documented reference databases",
                "derived summaries with citations",
                "checksums and remote paths",
            ],
            "not_allowed_without_separate_approval": [
                "private sequences",
                "unpublished constructs",
                "proprietary datasets",
                "collaborator-restricted data",
                "credentials or tokens in repo files",
            ],
        },
        "planned_tools": PLANNED_TOOLS,
        "planned_databases": PLANNED_DATABASES,
        "campaign_resource_ledger": campaign_resources(campaign_path, campaign),
        "deferred_restricted_resources": DEFERRED_RESTRICTED_RESOURCES,
        "bundle_files": {
            "run_manifest": "runpod-run-manifest.json",
            "setup_script": "setup-runpod-readiness.sh",
            "mock_runner_command_plan": "mock-runner-command-plan.md",
            "provider_launch_preflight": "provider-launch-preflight.tsv",
            "readme": "README.md",
        },
        "local_output": {
            "path": repo_relative(out_dir),
            "gitignore_policy": ".runtime/ is ignored; generated bundle output should stay outside git",
        },
        "review_gates_before_live_run": [
            "Run BioProspector preflight on the campaign manifest.",
            "Review this runpod-run-manifest.json and the public/open-first data policy.",
            "Review provider-launch-preflight.tsv; every blocking row must pass before launch.",
            "Confirm image is digest-pinned or intentionally scout-only.",
            "Confirm private registry auth is provider-side verified before using private images.",
            "Confirm the RunPod Network Volume is mounted at /workspace.",
            "Confirm planned databases are staged only on the remote volume, not in this repo.",
            "Confirm expected spend remains below the configured scout budget and below $100.",
        ],
    }


def render_setup_script(run_manifest: dict[str, Any]) -> str:
    contract = run_manifest["runpod_contract"]
    remote_workdir = contract["remote_workdir"]
    budget = contract["scout_guardrail"]["configured_budget_usd"]
    return f"""#!/usr/bin/env bash
set -euo pipefail

# BioProspector RunPod readiness setup.
# This script creates directories and records tool checks only. It does not
# install tools, download databases, start workflows, or call the RunPod API.

NETWORK_VOLUME_MOUNT={shlex.quote(NETWORK_VOLUME_MOUNT)}
REMOTE_WORKDIR={shlex.quote(remote_workdir)}
SCOUT_BUDGET_USD={shlex.quote(f"{budget:.2f}")}

if [[ "${{1:-}}" == "--help" ]]; then
  cat <<'HELP'
Usage: bash setup-runpod-readiness.sh

Creates the BioProspector remote workdir layout and writes readiness tool
checks under provenance/. It does not install packages or download data.
HELP
  exit 0
fi

if [[ ! -d "$NETWORK_VOLUME_MOUNT" ]]; then
  echo "FAIL: expected RunPod Network Volume mounted at $NETWORK_VOLUME_MOUNT" >&2
  exit 2
fi

mkdir -p \\
  "$REMOTE_WORKDIR/inputs" \\
  "$REMOTE_WORKDIR/db" \\
  "$REMOTE_WORKDIR/work" \\
  "$REMOTE_WORKDIR/outputs" \\
  "$REMOTE_WORKDIR/provenance"

TOOLCHECK="$REMOTE_WORKDIR/provenance/readiness-toolcheck.tsv"
POLICY="$REMOTE_WORKDIR/provenance/readiness-policy.txt"

printf "tool\\tstatus\\tpath_or_note\\n" > "$TOOLCHECK"

check_bin() {{
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf "%s\\tpresent\\t%s\\n" "$name" "$(command -v "$name")" >> "$TOOLCHECK"
  else
    printf "%s\\tmissing\\trequired or planned for full readiness\\n" "$name" >> "$TOOLCHECK"
  fi
}}

check_any() {{
  local label="$1"
  shift
  local candidate
  for candidate in "$@"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      printf "%s\\tpresent\\t%s\\n" "$label" "$(command -v "$candidate")" >> "$TOOLCHECK"
      return 0
    fi
  done
  printf "%s\\tmissing\\tone of: %s\\n" "$label" "$*" >> "$TOOLCHECK"
}}

check_py_mod() {{
  local module="$1"
  local label="${{2:-$module}}"
  local location
  if location="$(python3 - "$module" 2>/dev/null <<'PY'
import importlib.util
import sys

module = sys.argv[1]
spec = importlib.util.find_spec(module)
if spec is None:
    raise SystemExit(1)
print(spec.origin or "built-in")
PY
)"; then
    printf "%s\\tpresent\\t%s\\n" "$label" "$location" >> "$TOOLCHECK"
  else
    printf "%s\\tmissing\\tpython module not importable\\n" "$label" >> "$TOOLCHECK"
  fi
}}

check_bin python3
check_bin mmseqs
check_bin diamond
check_bin blastp
check_any hmmer_or_pyhmmer hmmscan hmmsearch
check_bin seqkit
check_bin datasets
check_any workflow_runner nextflow snakemake
check_any duckdb_cli duckdb
check_py_mod duckdb duckdb_python
check_py_mod polars polars_python
check_py_mod pandas pandas_python
check_py_mod rdkit rdkit_python
check_py_mod cobra cobrapy
check_py_mod pyhmmer pyhmmer_python

cat > "$POLICY" <<POLICY
BioProspector RunPod readiness policy
Remote workdir: $REMOTE_WORKDIR
Network volume mount: $NETWORK_VOLUME_MOUNT
Scout budget: less than $SCOUT_BUDGET_USD USD, and always less than 100 USD

This readiness script is review-only:
- no RunPod API calls
- no package installation
- no database downloads
- no private, proprietary, collaborator-restricted, or unpublished sequences
- public/open-first data only unless a separate approval exists
POLICY

echo "Readiness directories prepared at $REMOTE_WORKDIR"
echo "Tool check written to $TOOLCHECK"
echo "Policy note written to $POLICY"
"""


def render_mock_plan(run_manifest: dict[str, Any]) -> str:
    campaign = run_manifest["campaign"]
    contract = run_manifest["runpod_contract"]
    campaign_path = run_manifest["source_campaign"]["path"]
    remote_workdir = contract["remote_workdir"]
    return f"""# Mock Runner Command Plan

This plan is intentionally mock-only. It gives an operator reviewable commands
for a manual RunPod Pod, but it does not launch RunPod, install tools, download
databases, or run biological searches.

## Local Review

Run from the repo root before any pod work:

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \\
  --campaign {campaign_path}

python3 -m json.tool {run_manifest["local_output"]["path"]}/runpod-run-manifest.json
```

## Manual Pod Setup

Use the RunPod UI, not an API script:

- Pod type: manual Pod, not Serverless.
- Network Volume mount: `{NETWORK_VOLUME_MOUNT}`.
- Remote workdir: `{remote_workdir}`.
- Scout guardrail: stop before `$100`; this bundle is configured for `${contract["scout_guardrail"]["configured_budget_usd"]:.2f}`.
- Data policy: public/open-first only.

After copying this bundle to the pod, run only the readiness script from the
bundle directory. The script creates `{remote_workdir}` if needed:

```bash
bash setup-runpod-readiness.sh
```

## Mock Runner Summary

The following command writes a small mock summary only. It is useful for testing
artifact paths before implementing or approving a real runner.

```bash
cd {remote_workdir}
python3 - <<'PY'
import json
from pathlib import Path

remote_workdir = Path({remote_workdir!r})
summary = {{
    "campaign_id": {campaign["campaign_id"]!r},
    "target_molecule": {campaign.get("target_molecule", "")!r},
    "host": {campaign.get("host", "")!r},
    "mode": "mock_readiness_only",
    "dry_run": True,
    "mock_tools": True,
    "real_execution_performed": False,
    "ran_searches": False,
    "downloaded_databases": False,
    "runpod_api_calls": False,
    "notes": [
        "This is a mock readiness summary.",
        "Replace only after a reviewed live-run issue approves execution."
    ],
}}
out = remote_workdir / "outputs" / "mock-run-summary.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=2) + "\\n", encoding="utf-8")
print(out)
PY
```

## Live Execution Boundary

Do not add live search, package installation, database staging, or RunPod API
launch commands to this plan. Those require a separate reviewed execution issue.
"""


def render_readme(run_manifest: dict[str, Any]) -> str:
    campaign = run_manifest["campaign"]
    contract = run_manifest["runpod_contract"]
    tools = "\n".join(f"- {tool['name']}: {tool['purpose']}" for tool in PLANNED_TOOLS)
    databases = "\n".join(f"- {db['name']}: {db['policy']}" for db in PLANNED_DATABASES)
    deferred = "\n".join(
        f"- {item['resource']}: {item['reason']}" for item in DEFERRED_RESTRICTED_RESOURCES
    )
    return f"""# RunPod Readiness Bundle

Campaign: `{campaign["campaign_id"]}`

This bundle is prep-only. The generator did not launch RunPod, install tools, or
download databases. Review these files before creating any manual RunPod Pod.

## Files

- `runpod-run-manifest.json`: complete readiness contract and source hashes.
- `setup-runpod-readiness.sh`: pod-side directory and tool-check script.
- `mock-runner-command-plan.md`: mock-only command plan for artifact-path testing.
- `provider-launch-preflight.tsv`: launch blockers for image pull, registry auth, volume, budget, branch/snapshot, payload, secrets, and stage contracts.
- `README.md`: this guide.

## RunPod Contract

- Launch mode: manual Pod plus scripts.
- RunPod API: not used by this bundle.
- Network Volume mount: `{NETWORK_VOLUME_MOUNT}`.
- Remote workdir: `{contract["remote_workdir"]}`.
- Scout guardrail: less than `$100`; configured budget `${contract["scout_guardrail"]["configured_budget_usd"]:.2f}`.
- Data policy: public/open-first only.
- Local output policy: keep generated bundles under `.runtime/`, which is ignored by git.
- Candidate package policy: return graph edges, candidate AA-sequence pointers,
  compact domain maps, diversity selections, literature-search summaries,
  versions, hashes, and licenses; keep raw all-hit outputs and large databases
  on provider storage.

## Planned Tools

{tools}

## Planned Databases

{databases}

## Deferred Or Restricted Resources

{deferred}

## Review Sequence

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \\
  --campaign {run_manifest["source_campaign"]["path"]}

python3 -m json.tool {run_manifest["local_output"]["path"]}/runpod-run-manifest.json
```

If the campaign and readiness contract are approved, create a manual RunPod Pod
with a Network Volume mounted at `/workspace`, copy this bundle to the pod, then
run this from the bundle directory:

```bash
bash setup-runpod-readiness.sh
```

Do not stage heavy databases or run searches from this bundle alone.
"""


def render_provider_launch_preflight(run_manifest: dict[str, Any]) -> str:
    contract = run_manifest["runpod_contract"]
    image_contract = contract["image_pull_contract"]
    digest_status = "pass" if image_contract["digest_pinned"] else "review_required"
    auth_status = "pass"
    if image_contract["image_access"] == "unknown":
        auth_status = "review_required"
    if image_contract["image_access"] == "private_auth_required":
        auth_status = "blocked"

    rows = [
        {
            "check_id": "RPP001",
            "provider_id": "runpod_manual_pod",
            "check_type": "image_digest_pin",
            "expected": "image reference includes @sha256 digest before live execution",
            "observed": image_contract["image"],
            "status": digest_status,
            "blocking_before_launch": "true",
            "notes": "Digest-pinned images beat install-at-boot; unpinned images are readiness/dev only.",
        },
        {
            "check_id": "RPP002",
            "provider_id": "runpod_manual_pod",
            "check_type": "registry_auth",
            "expected": "public image or provider-side private registry auth verified",
            "observed": f"{image_contract['registry']} image_access={image_contract['image_access']}",
            "status": auth_status,
            "blocking_before_launch": "true",
            "notes": "Private GHCR images will not pull on RunPod unless registry credentials are configured provider-side.",
        },
        {
            "check_id": "RPP003",
            "provider_id": "runpod_manual_pod",
            "check_type": "network_volume",
            "expected": "/workspace network volume mounted",
            "observed": contract["network_volume_mount"],
            "status": "planned",
            "blocking_before_launch": "true",
            "notes": "Must be verified on the actual pod before heavy work.",
        },
        {
            "check_id": "RPP004",
            "provider_id": "runpod_manual_pod",
            "check_type": "cost_guardrail",
            "expected": "scout budget under 100 USD",
            "observed": f"{contract['scout_guardrail']['configured_budget_usd']:.2f}",
            "status": "pass",
            "blocking_before_launch": "true",
            "notes": "Budget alerts are not proof of progress; stage progress is still required.",
        },
        {
            "check_id": "RPP005",
            "provider_id": "runpod_manual_pod",
            "check_type": "branch_snapshot",
            "expected": "exact branch/snapshot contains the bundle the worker will clone",
            "observed": run_manifest["local_output"]["path"],
            "status": "review_required",
            "blocking_before_launch": "true",
            "notes": "Validate orchestration plumbing before launch.",
        },
        {
            "check_id": "RPP006",
            "provider_id": "runpod_manual_pod",
            "check_type": "stage_contract",
            "expected": "stage contracts and progress emission defined for long runs",
            "observed": "stage-contract-ledger.tsv and stage-progress-ledger.tsv required for live run",
            "status": "review_required",
            "blocking_before_launch": "true",
            "notes": "Provider desiredStatus/RUNNING does not prove container or workflow progress.",
        },
        {
            "check_id": "RPP007",
            "provider_id": "runpod_manual_pod",
            "check_type": "secrets_boundary",
            "expected": "no credentials in repo, Linear, or bundle files",
            "observed": "manual review required",
            "status": "review_required",
            "blocking_before_launch": "true",
            "notes": "Use provider-side secrets only; never paste registry tokens or API keys into tracked files.",
        },
    ]
    headers = [
        "check_id",
        "provider_id",
        "check_type",
        "expected",
        "observed",
        "status",
        "blocking_before_launch",
        "notes",
    ]
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(row[header] for header in headers))
    return "\n".join(lines) + "\n"


def write_bundle(run_manifest: dict[str, Any], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "runpod-run-manifest.json": json.dumps(run_manifest, indent=2, sort_keys=False) + "\n",
        "setup-runpod-readiness.sh": render_setup_script(run_manifest),
        "mock-runner-command-plan.md": render_mock_plan(run_manifest),
        "provider-launch-preflight.tsv": render_provider_launch_preflight(run_manifest),
        "README.md": render_readme(run_manifest),
    }

    written: list[Path] = []
    for name, content in files.items():
        path = out_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
        if name.endswith(".sh"):
            os.chmod(path, 0o755)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument(
        "--out",
        type=Path,
        help="Output directory under .runtime/; defaults to .runtime/runpod-readiness/<campaign_id>",
    )
    parser.add_argument(
        "--image",
        default="TODO:digest-pinned-bioprospector-image",
        help="RunPod image reference to record. Use a digest-pinned image before live execution.",
    )
    parser.add_argument(
        "--image-access",
        choices=sorted(IMAGE_ACCESS_VALUES),
        default="unknown",
        help=(
            "Image pull posture for launch preflight. Use private_auth_required for private images "
            "until provider-side registry auth is verified."
        ),
    )
    parser.add_argument(
        "--scout-budget-usd",
        default=DEFAULT_BUDGET_USD,
        type=float,
        help="Scout budget guardrail. Must be greater than 0 and less than 100.",
    )
    args = parser.parse_args()

    campaign_path = args.campaign.resolve()
    if not campaign_path.exists():
        print(f"FAIL campaign not found: {campaign_path}")
        return 1
    if args.scout_budget_usd <= 0 or args.scout_budget_usd >= 100:
        print("FAIL --scout-budget-usd must be greater than 0 and less than 100")
        return 1

    campaign = load_json(campaign_path)
    campaign_id = campaign.get("campaign_id")
    if not isinstance(campaign_id, str) or not campaign_id:
        print("FAIL campaign manifest must include a non-empty campaign_id")
        return 1

    try:
        out_dir = resolve_output_dir(args.out, campaign_id)
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1

    run_manifest = build_manifest(
        campaign_path=campaign_path,
        campaign=campaign,
        out_dir=out_dir,
        image=args.image,
        image_access=args.image_access,
        scout_budget_usd=args.scout_budget_usd,
    )
    written = write_bundle(run_manifest, out_dir)

    print(f"Wrote RunPod readiness bundle to {out_dir}")
    for path in written:
        print(f"- {repo_relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
