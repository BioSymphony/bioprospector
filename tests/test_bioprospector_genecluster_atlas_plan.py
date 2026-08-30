#!/usr/bin/env python3
"""Tests for the public-safe GeneCluster atlas planner."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.write_text(
        "\t".join(headers) + "\n" + "\n".join("\t".join(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_minimal_atlas_campaign(root: Path, *, source_pointer: str = "public-accession:ABC123") -> Path:
    write_tsv(
        root / "organism-sample-ledger.tsv",
        [
            "organism_id",
            "taxon_name",
            "strain_or_accession",
            "sample_id",
            "role",
            "evidence_type",
            "data_status",
            "source_pointer",
            "license_boundary",
            "notes",
        ],
        [["ORG001", "public_target", "public_reference", "no_sample", "target_organism", "planning", "declared", "target-dataset-ledger.tsv", "open_summary_only", "test"]],
    )
    write_tsv(
        root / "target-dataset-ledger.tsv",
        [
            "dataset_id",
            "organism_id",
            "dataset_type",
            "dataset_label",
            "source_pointer",
            "materialized_status",
            "checksum_or_version",
            "target_evidence_role",
            "license_boundary",
            "notes",
        ],
        [
            ["DS001", "ORG001", "genome", "public genome pointer", source_pointer, "available", "review_before_run", "target_context", "open_summary_only", "test"],
            ["DS002", "ORG001", "annotation", "public annotation pointer", "public-accession:ANN123", "available", "review_before_run", "target_context", "open_summary_only", "test"],
        ],
    )
    write_tsv(
        root / "query-set-ledger.tsv",
        [
            "query_id",
            "step_id",
            "query_type",
            "query_label",
            "source_organism",
            "source_pointer",
            "materialized_status",
            "checksum_or_version",
            "license_boundary",
            "notes",
        ],
        [["Q001", "S001", "protein", "public seed", "public_source", "public-accession:Q123", "declared", "review_before_run", "accession_summary_only", "test"]],
    )
    write_tsv(
        root / "decoy-control-ledger.tsv",
        [
            "control_id",
            "step_id",
            "control_type",
            "query_or_dataset",
            "expected_result",
            "observed_result",
            "status",
            "blocks_promotion",
            "notes",
        ],
        [["DC001", "S001", "shuffled_sequence", "Q001_shuffle", "low_or_no_hit", "not_run", "planned", "true", "test"]],
    )
    manifest = {
        "campaign_id": "genecluster-public-test",
        "campaign_name": "GeneCluster Public Test",
        "target_contract": "target-contract.json",
        "host": "public_host",
        "target_molecule": "public_product",
        "mode": "pathway_big_bang",
        "scope": "planning_only",
        "claim_boundary": "planning only",
        "ledgers": {
            "organism_sample_ledger": "organism-sample-ledger.tsv",
            "target_dataset_ledger": "target-dataset-ledger.tsv",
            "query_set_ledger": "query-set-ledger.tsv",
            "decoy_control_ledger": "decoy-control-ledger.tsv",
        },
    }
    path = root / "campaign-manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


class GeneClusterAtlasPlanTests(unittest.TestCase):
    def test_public_demo_generates_l0_plan(self) -> None:
        campaign = REPO_ROOT / "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "atlas"
            result = run("--campaign", str(campaign), "--out", str(out), "--json")

            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["route_summary"]["selected_route"], "next_experiment_design")
            self.assertTrue((out / "genecluster-source-scout-ledger.tsv").exists())
            self.assertTrue((out / "genecluster-route-decision-ledger.tsv").exists())
            self.assertTrue((out / "genecluster-atlas-contract-ledger.tsv").exists())
            self.assertNotIn(str(out), result.stdout)
            contract_text = (out / "genecluster-atlas-contract-ledger.tsv").read_text(encoding="utf-8")
            self.assertNotIn(str(out), contract_text)
            self.assertIn("REPLACE_ME_EXTERNAL_PATH", contract_text)

    def test_ready_annotation_context_gets_l3_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            campaign = write_minimal_atlas_campaign(root)
            out = root / "atlas"
            run("--campaign", str(campaign), "--out", str(out))

            routes = read_tsv(out / "genecluster-route-decision-ledger.tsv")
            self.assertEqual(routes[0]["recommended_route"], "annotation_direct_then_context")
            self.assertEqual(routes[0]["claim_ceiling"], "L3_annotation_neighborhood_ready")

    def test_local_raw_pointer_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_pointer = str(root / "local-target.fasta")
            campaign = write_minimal_atlas_campaign(root, source_pointer=private_pointer)
            out = root / "atlas"
            result = run("--campaign", str(campaign), "--out", str(out), "--json", check=False)

            self.assertNotEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])
            self.assertIn("local raw/heavy pointer", "\n".join(data["errors"]))
            self.assertNotIn(private_pointer, result.stdout)
            for generated in out.iterdir():
                self.assertNotIn(private_pointer, generated.read_text(encoding="utf-8"))
            self.assertIn(
                "REPLACE_ME_EXTERNAL_PATH",
                (out / "genecluster-source-scout-ledger.tsv").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
