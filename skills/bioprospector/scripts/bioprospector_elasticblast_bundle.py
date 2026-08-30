#!/usr/bin/env python3
"""Create a prep-only AWS ElasticBLAST wide-search bundle.

This generator does not call AWS, submit ElasticBLAST jobs, upload queries, or
download databases. It writes reviewable configs and ledgers under `.runtime/`
so an operator can inspect cost, cleanup, and data-policy gates before any
cloud resources are created.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_ROOT = REPO_ROOT / ".runtime"
HEAVY_SEARCH_WIDTHS = {"wide", "frontier"}
DEFAULT_BUCKET_URI = "s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast"
DEFAULT_REGION = "us-east-1"
DEFAULT_BUDGET_USD = 25.0
DEFAULT_NUM_NODES = 1
DEFAULT_MAX_TARGET_SEQS = 500
DEFAULT_EVALUE = "1e-10"


def database_notes(database: str) -> list[str]:
    db = database.strip().lower()
    notes = {
        "refseq_select_prot": [
            "`refseq_select_prot` is the preferred compact RefSeq-family scout before broader NCBI-wide runs.",
            "Verify provider metadata names in the ElasticBLAST environment before submit; database aliases can differ by release.",
            "Escalate to full `refseq_protein`/`nr` only after memory and cost behavior are observed on a small search.",
        ],
        "refseq_protein": [
            "`refseq_protein` is a broad RefSeq protein lane that may require high-memory instances for practical runtimes.",
            "Run a tiny query and inspect scheduler shape before promising a cheap run.",
            "Prefer `refseq_select_prot` or Swiss-Prot first when the campaign only needs a scout lane.",
        ],
        "nr": [
            "`nr` is the broadest default escalation lane and should be treated as budget-sensitive.",
            "Run compact scouts first; use full `refseq_protein`/`nr` only after memory, quota, and cleanup are verified.",
            "Do not submit private or unpublished query sequences without a separate data-policy approval.",
        ],
        "swissprot": [
            "`swissprot` is a curated scout database and is usually the lowest-risk first ElasticBLAST smoke target.",
            "Use it to validate query packaging, AWS setup, cleanup, and result egress before broader databases.",
        ],
    }
    if db in notes:
        return notes[db]
    return [
        f"`{database}` has no project-specific profile yet; verify the exact provider database name before submit.",
        "Run a tiny query first and record memory, runtime, cost, and cleanup behavior before scaling.",
    ]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


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
        return "REPLACE_ME_EXTERNAL_PATH"


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


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def reject_symlink_components(path: Path) -> None:
    candidate = path.expanduser()
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    current = Path(candidate.anchor)
    for name in candidate.parts[1:]:
        current = current / name
        if not current.is_symlink():
            continue
        if current.parent == Path("/") and current.name in {"tmp", "var"}:
            current = current.resolve()
            continue
        raise ValueError("output path contains a symlink; choose a path without symlinks")


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


def resolve_output_dir(out_arg: Path | None, campaign_id: str) -> Path:
    if out_arg is None:
        out = RUNTIME_ROOT / "elasticblast-readiness" / slug(campaign_id)
    else:
        out = out_arg.expanduser()
        if not out.is_absolute():
            out = REPO_ROOT / out
    reject_symlink_components(out)
    out = out.resolve()
    if not path_is_under(out, RUNTIME_ROOT):
        raise ValueError("output directory must be under .runtime")
    return out


def campaign_file_hashes(campaign_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    base = campaign_path.parent
    files: list[Path] = [campaign_path]
    target_contract = manifest.get("target_contract")
    target_path = declared_path(base, target_contract)
    if target_path is not None:
        files.append(target_path)
    ledgers = manifest.get("ledgers")
    if isinstance(ledgers, dict):
        for rel in ledgers.values():
            path = declared_path(base, rel)
            if path is not None:
                files.append(path)

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


def heavy_steps(campaign_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    ledgers = manifest.get("ledgers")
    if not isinstance(ledgers, dict):
        return []
    rel = ledgers.get("reaction_step_ledger")
    if not isinstance(rel, str) or not rel:
        return []
    path = declared_path(campaign_path.parent, rel)
    if path is None or not path.exists():
        return []
    return [
        step
        for step in read_tsv(path)
        if step.get("candidate_search_width", "").strip() in HEAVY_SEARCH_WIDTHS
    ]


def search_rows(
    *,
    campaign_id: str,
    steps: list[dict[str, str]],
    bucket_uri: str,
    region: str,
    database: str,
    program: str,
    num_nodes: int,
    use_preemptible: bool,
    max_target_seqs: int,
    evalue: str,
    budget_usd: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    preemptible = "true" if use_preemptible else "false"
    for step in steps:
        step_id = step.get("step_id", "")
        search_id = f"ELB-{step_id}"
        query_set = f"{bucket_uri}/queries/{campaign_id}/{step_id}_queries.faa"
        result_uri = f"{bucket_uri}/results/{campaign_id}/{step_id}-{database}"
        rows.append(
            {
                "search_id": search_id,
                "step_id": step_id,
                "query_set": query_set,
                "program": program,
                "database": database,
                "cloud_provider": "aws",
                "region": region,
                "result_uri": result_uri,
                "num_nodes": num_nodes,
                "use_preemptible": preemptible,
                "thresholds": f"evalue={evalue};max_target_seqs={max_target_seqs};task={program}-fast",
                "max_hits": max_target_seqs,
                "budget_usd": f"{budget_usd:.2f}",
                "approval_status": "operator_review_required",
                "notes": (
                    "Prep-only AWS ElasticBLAST lane. Upload query FASTA and verify AWS safety controls "
                    "before submit; run elastic-blast delete and cleanup verification after completion."
                ),
            }
        )
    return rows


def run_rows(search_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in search_plan:
        rows.append(
            {
                "run_id": f"RUN-{row['search_id']}",
                "search_id": row["search_id"],
                "status": "planned",
                "submitted_at": "",
                "completed_at": "",
                "cloud_provider": row["cloud_provider"],
                "region": row["region"],
                "result_uri": row["result_uri"],
                "cleanup_status": "not_started",
                "estimated_cost_usd": "0.00",
                "output_summary": "",
                "notes": "No AWS job has been submitted by this bundle.",
            }
        )
    return rows


def safety_rows(bucket_uri: str, region: str, budget_usd: float) -> list[dict[str, str]]:
    return [
        {
            "control_id": "AWS-001",
            "control_type": "account",
            "control_name": "Dedicated AWS sandbox account",
            "required_status": "required",
            "verification_mode": "human",
            "verification_command": "aws sts get-caller-identity",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Prefer a dedicated account or isolated project account before ElasticBLAST execution.",
        },
        {
            "control_id": "AWS-002",
            "control_type": "budget",
            "control_name": f"Monthly budget at or below ${budget_usd:.2f} for first tests",
            "required_status": "required",
            "verification_mode": "aws_cli_or_console",
            "verification_command": "aws budgets describe-budgets --account-id <account-id>",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Budgets are delayed alerts/actions, not a real-time hard cap.",
        },
        {
            "control_id": "AWS-003",
            "control_type": "cost_anomaly",
            "control_name": "Cost Anomaly Detection alert",
            "required_status": "required",
            "verification_mode": "aws_cli_or_console",
            "verification_command": "aws ce get-anomaly-monitors",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Use a low alert threshold for first BioProspector ElasticBLAST tests.",
        },
        {
            "control_id": "AWS-004",
            "control_type": "service_quota",
            "control_name": f"Low EC2 vCPU quota in {region}",
            "required_status": "required",
            "verification_mode": "aws_cli_or_console",
            "verification_command": "aws service-quotas list-service-quotas --service-code ec2",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Keep first run at one node; do not request large quota increases before smoke tests.",
        },
        {
            "control_id": "AWS-005",
            "control_type": "s3",
            "control_name": "Private encrypted S3 bucket with lifecycle cleanup",
            "required_status": "required",
            "verification_mode": "aws_cli_or_console",
            "verification_command": f"aws s3api get-public-access-block --bucket {bucket_uri.removeprefix('s3://')}",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Block public access and expire scratch prefixes after review.",
        },
        {
            "control_id": "AWS-006",
            "control_type": "elasticblast",
            "control_name": "ElasticBLAST janitor role or explicit cleanup procedure",
            "required_status": "required",
            "verification_mode": "aws_cli_or_console",
            "verification_command": "aws-describe-elastic-blast-janitor-role.sh",
            "blocking_before_submit": "true",
            "last_verified": "",
            "owner": "operator",
            "notes": "Use elastic-blast==1.5.0 or newer and verify cleanup after every run.",
        },
    ]


def render_ini(row: dict[str, Any]) -> str:
    return f"""[cloud-provider]
aws-region = {row["region"]}

[cluster]
num-nodes = {row["num_nodes"]}
use-preemptible = {row["use_preemptible"]}
labels = project=biosymphony,campaign=bioprospector,step={row["step_id"]},search={row["search_id"]}

[blast]
program = {row["program"]}
db = {row["database"]}
queries = {row["query_set"]}
results = {row["result_uri"]}
options = -task {row["program"]}-fast -evalue {row["thresholds"].split(";")[0].split("=")[1]} -max_target_seqs {row["max_hits"]} -outfmt "7 std sskingdoms ssciname stitle"
"""


def build_manifest(
    *,
    campaign_path: Path,
    campaign: dict[str, Any],
    out_dir: Path,
    search_plan: list[dict[str, Any]],
    safety: list[dict[str, str]],
    budget_usd: float,
) -> dict[str, Any]:
    return {
        "schema": "biosymphony.bioprospector.elasticblast_readiness_bundle.v1",
        "generated_at": utc_now(),
        "generator": repo_relative(Path(__file__)),
        "source_campaign": {
            "path": repo_relative(campaign_path),
            "sha256": sha256_file(campaign_path),
            "campaign_manifest": campaign,
            "related_file_hashes": campaign_file_hashes(campaign_path, campaign),
        },
        "campaign": {
            "campaign_id": campaign["campaign_id"],
            "campaign_name": campaign.get("campaign_name", ""),
            "target_molecule": campaign.get("target_molecule", ""),
            "host": campaign.get("host", ""),
            "mode": campaign.get("mode", ""),
            "scope": campaign.get("scope", ""),
            "claim_boundary": campaign.get("claim_boundary", ""),
        },
        "elasticblast_contract": {
            "purpose": "wide NCBI BLAST database escalation lane",
            "execution_boundary": "prep_only_no_aws_calls",
            "default_cloud_provider": "aws",
            "default_region": search_plan[0]["region"] if search_plan else DEFAULT_REGION,
            "database_notes": database_notes(search_plan[0]["database"]) if search_plan else [],
            "operator_approval_required": True,
            "scout_budget_usd": budget_usd,
            "cost_policy": "first tests must stay under configured scout budget and always below $100",
            "data_policy": "public_or_approved_query_fasta_only",
            "not_for": [
                "private or unpublished sequence upload without separate security review",
                "unbounded nr searches",
                "long-lived AWS resources",
                "RunPod-local nr mirroring",
            ],
        },
        "search_plan": search_plan,
        "aws_safety_controls": safety,
        "bundle_files": {
            "run_manifest": "elasticblast-run-manifest.json",
            "search_plan": "elasticblast-search-plan.tsv",
            "run_ledger": "elasticblast-run-ledger.tsv",
            "aws_safety_ledger": "aws-safety-ledger.tsv",
            "configs": "configs/*.ini",
            "aws_setup_checklist": "aws-setup-checklist.md",
            "cleanup_checklist": "cleanup-verification.md",
            "readme": "README.md",
        },
        "local_output": {
            "path": repo_relative(out_dir),
            "gitignore_policy": ".runtime/ is ignored; generated bundle output should stay outside git",
        },
    }


def render_setup_checklist(manifest: dict[str, Any]) -> str:
    contract = manifest["elasticblast_contract"]
    region = contract["default_region"]
    budget = contract["scout_budget_usd"]
    return f"""# AWS ElasticBLAST Setup Checklist

This checklist is for operator review. Do not paste AWS keys, secret keys,
session tokens, MFA codes, or root credentials into chat or repo files.

## Authentication Options

Preferred first smoke test:

1. Sign into AWS Console with MFA.
2. Open AWS CloudShell in `{region}`.
3. Run setup and smoke commands there.

Preferred repeat use:

```bash
aws configure sso --profile bioprospector
aws sso login --profile bioprospector
aws sts get-caller-identity --profile bioprospector
```

## Required Brakes Before Submit

- Dedicated sandbox AWS account or reviewed project account.
- AWS Budget at or below `${budget:.2f}` for first tests, with actual and forecasted alerts.
- Cost Anomaly Detection enabled with a low alert threshold.
- Low EC2 vCPU quotas retained for the first run.
- Private S3 bucket with block-public-access, encryption, and lifecycle cleanup.
- ElasticBLAST janitor role installed or explicit `elastic-blast delete` cleanup procedure.
- ElasticBLAST version checked; use `elastic-blast==1.5.0` or newer.
- Query FASTA is public or separately approved for cloud upload.

## Install ElasticBLAST In CloudShell

```bash
python3 -m venv .elb-venv
source .elb-venv/bin/activate
pip install wheel
pip install elastic-blast==1.5.0
elastic-blast --version
```

## Submit Boundary

Generated configs are not approval to submit. A human operator must review:

- `elasticblast-search-plan.tsv`
- `aws-safety-ledger.tsv`
- query FASTA sensitivity
- budget and quota state
- cleanup procedure
"""


def render_cleanup_checklist(manifest: dict[str, Any]) -> str:
    region = manifest["elasticblast_contract"]["default_region"]
    return f"""# ElasticBLAST Cleanup Verification

After any real run, execute cleanup first:

```bash
elastic-blast delete --cfg configs/<search-id>.ini
```

Then verify in `{region}`:

```bash
aws ec2 describe-instances \\
  --region {region} \\
  --filters "Name=tag:project,Values=biosymphony" "Name=instance-state-name,Values=pending,running,stopping,stopped" \\
  --query 'Reservations[].Instances[].{{InstanceId:InstanceId,State:State.Name,Tags:Tags}}'

aws batch describe-compute-environments --region {region}
aws batch describe-job-queues --region {region}
aws cloudformation list-stacks --region {region} --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
```

Record cleanup status in `elasticblast-run-ledger.tsv`.
"""


def render_readme(manifest: dict[str, Any]) -> str:
    campaign = manifest["campaign"]
    contract = manifest["elasticblast_contract"]
    count = len(manifest["search_plan"])
    databases = sorted({row.get("database", "") for row in manifest["search_plan"] if row.get("database", "")})
    notes = contract.get("database_notes")
    if not isinstance(notes, list):
        notes = []
    note_lines = "\n".join(f"- {note}" for note in notes)
    if not note_lines:
        note_lines = "\n".join(
            f"- {note}"
            for database in databases
            for note in database_notes(database)
        )
    return f"""# AWS ElasticBLAST Readiness Bundle

Campaign: `{campaign["campaign_id"]}`

This bundle prepares the wide-search lane for NCBI-hosted BLAST databases. It
does not authenticate to AWS, create buckets, upload queries, submit jobs, or
download results.

## Why This Exists

RunPod remains the BioProspector backbone for controlled local datasets,
Swiss-Prot, UniRef, Pfam, DIAMOND, MMseqs2, HMMER, scoring, and route stitching.
AWS ElasticBLAST is the escalation lane for official NCBI BLAST database scale
such as `nr`, `refseq_protein`, and `swissprot`.

## Files

- `elasticblast-run-manifest.json`: source hashes, policy, search plan, safety controls.
- `elasticblast-search-plan.tsv`: one planned wide-search row per selected step.
- `elasticblast-run-ledger.tsv`: planned run records; update only after real runs.
- `aws-safety-ledger.tsv`: cost, IAM, S3, quota, and cleanup controls.
- `configs/*.ini`: ElasticBLAST config templates.
- `aws-setup-checklist.md`: safe AWS setup path.
- `cleanup-verification.md`: post-run cleanup checks.

## Search Plan

- Planned searches: `{count}`
- Cloud provider: AWS
- Region: `{contract["default_region"]}`
- Scout budget: `${contract["scout_budget_usd"]:.2f}`
- Execution boundary: `{contract["execution_boundary"]}`
- Database(s): `{", ".join(databases) if databases else "not declared"}`

## Database Notes

{note_lines}

## Review Sequence

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \\
  --campaign {manifest["source_campaign"]["path"]}

python3 -m json.tool {manifest["local_output"]["path"]}/elasticblast-run-manifest.json
```

Do not run `elastic-blast submit` until the safety ledger is verified and the
operator explicitly approves a specific config.
"""


def write_bundle(
    out_dir: Path,
    manifest: dict[str, Any],
    search_plan: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    safety: list[dict[str, str]],
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    json_path = out_dir / "elasticblast-run-manifest.json"
    json_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    written.append(json_path)

    search_headers = [
        "search_id",
        "step_id",
        "query_set",
        "program",
        "database",
        "cloud_provider",
        "region",
        "result_uri",
        "num_nodes",
        "use_preemptible",
        "thresholds",
        "max_hits",
        "budget_usd",
        "approval_status",
        "notes",
    ]
    run_headers = [
        "run_id",
        "search_id",
        "status",
        "submitted_at",
        "completed_at",
        "cloud_provider",
        "region",
        "result_uri",
        "cleanup_status",
        "estimated_cost_usd",
        "output_summary",
        "notes",
    ]
    safety_headers = [
        "control_id",
        "control_type",
        "control_name",
        "required_status",
        "verification_mode",
        "verification_command",
        "blocking_before_submit",
        "last_verified",
        "owner",
        "notes",
    ]
    tsv_specs = [
        ("elasticblast-search-plan.tsv", search_headers, search_plan),
        ("elasticblast-run-ledger.tsv", run_headers, runs),
        ("aws-safety-ledger.tsv", safety_headers, safety),
    ]
    for filename, headers, rows in tsv_specs:
        path = out_dir / filename
        write_tsv(path, headers, rows)
        written.append(path)

    for row in search_plan:
        path = config_dir / f"{slug(row['search_id'])}.ini"
        path.write_text(render_ini(row), encoding="utf-8")
        written.append(path)

    docs = {
        "aws-setup-checklist.md": render_setup_checklist(manifest),
        "cleanup-verification.md": render_cleanup_checklist(manifest),
        "README.md": render_readme(manifest),
    }
    for filename, content in docs.items():
        path = out_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Path to campaign-manifest.json")
    parser.add_argument("--out", type=Path, help="Output directory under .runtime/")
    parser.add_argument("--bucket-uri", default=DEFAULT_BUCKET_URI, help="S3 bucket/prefix for query and result URIs")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--database", default="nr", help="ElasticBLAST database name, for example nr or refseq_protein")
    parser.add_argument("--program", default="blastp", help="BLAST program")
    parser.add_argument("--num-nodes", default=DEFAULT_NUM_NODES, type=int, help="ElasticBLAST node count")
    parser.add_argument("--use-preemptible", action="store_true", default=True, help="Use preemptible/spot nodes")
    parser.add_argument("--no-preemptible", action="store_false", dest="use_preemptible", help="Disable preemptible/spot nodes")
    parser.add_argument("--max-target-seqs", default=DEFAULT_MAX_TARGET_SEQS, type=int)
    parser.add_argument("--evalue", default=DEFAULT_EVALUE)
    parser.add_argument("--budget-usd", default=DEFAULT_BUDGET_USD, type=float)
    args = parser.parse_args()

    campaign_path = args.campaign.resolve()
    if not campaign_path.exists():
        print(f"FAIL campaign not found: {repo_relative(campaign_path)}")
        return 1
    if args.budget_usd <= 0 or args.budget_usd >= 100:
        print("FAIL --budget-usd must be greater than 0 and less than 100")
        return 1
    if args.num_nodes < 1 or args.num_nodes > 16:
        print("FAIL --num-nodes must be between 1 and 16")
        return 1
    if args.max_target_seqs < 1:
        print("FAIL --max-target-seqs must be greater than 0")
        return 1
    if not args.bucket_uri.startswith("s3://"):
        print("FAIL --bucket-uri must be an s3:// URI for the AWS ElasticBLAST lane")
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

    steps = heavy_steps(campaign_path, campaign)
    if not steps:
        print("FAIL campaign has no wide/frontier reaction steps for ElasticBLAST planning")
        return 1

    searches = search_rows(
        campaign_id=campaign_id,
        steps=steps,
        bucket_uri=args.bucket_uri.rstrip("/"),
        region=args.region,
        database=args.database,
        program=args.program,
        num_nodes=args.num_nodes,
        use_preemptible=args.use_preemptible,
        max_target_seqs=args.max_target_seqs,
        evalue=args.evalue,
        budget_usd=args.budget_usd,
    )
    safety = safety_rows(args.bucket_uri.rstrip("/"), args.region, args.budget_usd)
    runs = run_rows(searches)
    manifest = build_manifest(
        campaign_path=campaign_path,
        campaign=campaign,
        out_dir=out_dir,
        search_plan=searches,
        safety=safety,
        budget_usd=args.budget_usd,
    )
    written = write_bundle(out_dir, manifest, searches, runs, safety)

    print(f"Wrote AWS ElasticBLAST readiness bundle to {repo_relative(out_dir)}")
    for path in written:
        print(f"- {repo_relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
