#!/usr/bin/env python3
"""Tests for summary-only GeneCluster Atlas normalizers."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_genecluster_atlas_normalizers.py"
VALIDATOR = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py"
FIXTURE = REPO_ROOT / "skills/bioprospector/examples/genecluster-synthetic-v0"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class GeneClusterAtlasNormalizerTests(unittest.TestCase):
    def test_all_normalizer_outputs_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "atlas"
            result = run(
                str(NORMALIZER),
                "--json",
                "all",
                "--annotation-direct",
                str(FIXTURE / "compact-clusters.tsv"),
                "--pfam",
                str(FIXTURE / "compact-pfam.tsv"),
                "--out-dir",
                str(out),
            )
            summary = json.loads(result.stdout)
            self.assertEqual(summary["row_counts"]["cluster_calls"], 5)
            self.assertEqual(summary["row_counts"]["protein_function_votes"], 10)
            run(
                str(VALIDATOR),
                "--cluster-calls",
                str(out / "cluster_calls.tsv"),
                "--bgc-consensus",
                str(out / "bgc_consensus.tsv"),
                "--protein-function-votes",
                str(out / "protein_function_votes.tsv"),
                "--protein-function-jury",
                str(out / "protein_function_jury.tsv"),
            )
            jury = read_tsv(out / "protein_function_jury.tsv")
            self.assertEqual(
                {row["protein_id"] for row in jury},
                {
                    "protein_alpha",
                    "protein_beta",
                    "protein_gamma",
                    "protein_delta",
                    "protein_epsilon",
                    "protein_zeta",
                    "protein_eta",
                    "protein_theta",
                    "protein_iota",
                    "protein_kappa",
                },
            )


if __name__ == "__main__":
    unittest.main()
