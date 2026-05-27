#!/usr/bin/env python3
"""Generate and audit public-safe demo sidecars without launching anything."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def count_files(path: Path, suffix: str | None = None) -> int:
    if not path.exists():
        return 0
    files = [item for item in path.rglob("*") if item.is_file()]
    if suffix:
        files = [item for item in files if item.name.endswith(suffix)]
    return len(files)


def smoke(campaign: Path, prefix: str, out: Path, include_provider_bundles: bool) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    issue_out = out / "issues"
    run(
        [
            sys.executable,
            "skills/bioprospector/scripts/bioprospector_issue_dry_run.py",
            "--campaign",
            str(campaign),
            "--prefix",
            prefix,
            "--out",
            str(issue_out),
            "--include-profile",
            "full-frontier",
        ]
    )
    if count_files(issue_out, ".md") == 0:
        raise RuntimeError("issue dry-run produced no markdown files")

    dossier_out = out / "dossier.md"
    run(
        [
            sys.executable,
            "skills/bioprospector/scripts/bioprospector_dossier_export.py",
            "--campaign",
            str(campaign),
            "--out",
            str(dossier_out),
        ]
    )
    if not dossier_out.exists():
        raise RuntimeError("dossier export did not produce output")

    if include_provider_bundles:
        runpod_out = out / "runpod-readiness"
        run(
            [
                sys.executable,
                "skills/bioprospector/scripts/bioprospector_runpod_bundle.py",
                "--campaign",
                str(campaign),
                "--out",
                str(runpod_out),
            ]
        )
        if count_files(runpod_out) == 0:
            raise RuntimeError("RunPod readiness bundle produced no files")

        elastic_out = out / "elasticblast-readiness"
        run(
            [
                sys.executable,
                "skills/bioprospector/scripts/bioprospector_elasticblast_bundle.py",
                "--campaign",
                str(campaign),
                "--out",
                str(elastic_out),
                "--bucket-uri",
                "s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast",
                "--budget-usd",
                "25",
            ]
        )
        if count_files(elastic_out) == 0:
            raise RuntimeError("ElasticBLAST readiness bundle produced no files")

    run([sys.executable, "scripts/public_audit.py", str(out)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--skip-provider-bundles", action="store_true")
    args = parser.parse_args()

    try:
        smoke(
            args.campaign,
            args.prefix,
            args.out,
            include_provider_bundles=not args.skip_provider_bundles,
        )
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL public demo smoke: {exc}")
        return 1
    print(f"PASS public demo smoke: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
