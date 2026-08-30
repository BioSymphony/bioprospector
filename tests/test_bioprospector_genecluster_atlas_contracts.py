#!/usr/bin/env python3
"""Tests for public GeneCluster Atlas contract validation."""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py"
FIXTURE = REPO_ROOT / "skills/bioprospector/examples/genecluster-synthetic-v0"

spec = importlib.util.spec_from_file_location("genecluster_contracts_tests", SCRIPT)
assert spec and spec.loader
contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contracts)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_rows(path: Path, rows_: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows_[0]))
        writer.writeheader()
        writer.writerows(rows_)


class GeneClusterAtlasContractTests(unittest.TestCase):
    def test_synthetic_fixture_validates(self) -> None:
        result = run(
            "--cluster-calls",
            str(FIXTURE / "cluster_calls.tsv"),
            "--bgc-consensus",
            str(FIXTURE / "bgc_consensus.tsv"),
            "--protein-function-votes",
            str(FIXTURE / "protein_function_votes.tsv"),
            "--protein-function-jury",
            str(FIXTURE / "protein_function_jury.tsv"),
            "--json",
        )

        data = json.loads(result.stdout)
        self.assertTrue(data["ok"], data)

    def test_raw_heavy_pointer_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cluster_calls.tsv"
            fixture_rows = rows(FIXTURE / "cluster_calls.tsv")
            private_pointer = str(Path(tmp) / "local_contigs.fasta")
            fixture_rows[0]["contig"] = private_pointer
            write_rows(path, fixture_rows)

            result = run("--cluster-calls", str(path), "--json", check=False)

        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertFalse(data["ok"])
        self.assertIn("raw/heavy", "\n".join(data["errors"]))
        self.assertNotIn(private_pointer, result.stdout)

    def test_consensus_cannot_hide_caller_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls = rows(FIXTURE / "cluster_calls.tsv")
            calls[1]["end"] = "4300"
            write_rows(root / "cluster_calls.tsv", calls)
            consensus = rows(FIXTURE / "bgc_consensus.tsv")
            consensus[0]["disagreement_status"] = "none"
            write_rows(root / "bgc_consensus.tsv", consensus)

            result = run(
                "--cluster-calls",
                str(root / "cluster_calls.tsv"),
                "--bgc-consensus",
                str(root / "bgc_consensus.tsv"),
                "--json",
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("collapses caller disagreement", "\n".join(data["errors"]))

    def test_secret_manager_uri_is_rejected_without_echoing_value(self) -> None:
        private_reference = "secret://private-project/provider-token"
        errors = contracts.find_raw_or_secret_values(
            {"api_key": private_reference},
            "provider manifest",
        )

        rendered = "\n".join(errors)
        self.assertIn("must be an env name", rendered)
        self.assertNotIn(private_reference, rendered)

    def test_provider_handoff_accepts_symphony_neocloud_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "provider_handoff_manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "genecluster_provider_handoff.v1",
                        "provider": {"adapter": "symphony-neocloud-bridge", "class": "neocloud_vm"},
                        "workload": {"mode": "review_only"},
                        "artifact_egress": {
                            "summary_only": True,
                            "hash_algorithm": "sha256",
                            "expected_artifacts": ["summary.json"],
                        },
                        "safety": {"launches_provider": False},
                        "cleanup": {"verify_artifacts_fetched": True},
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            result = run("--provider-handoff-manifest", str(manifest), "--json")

        data = json.loads(result.stdout)
        self.assertTrue(data["ok"], data)


if __name__ == "__main__":
    unittest.main()
