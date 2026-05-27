"""Smoke tests for BioProspector capability helper CLIs."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


class CapabilityToolTests(unittest.TestCase):
    def test_schema_file_contains_required_headers(self) -> None:
        schema = json.loads((REPO_ROOT / "schemas/bioprospector-ledgers.json").read_text(encoding="utf-8"))
        self.assertIn("route_ledger", schema["ledger_headers"])
        self.assertIn("claim_levels", schema["enums"])
        self.assertIn("hypothesis", schema["enums"]["claim_levels"])

    def test_doctor_reports_public_safe_checkout(self) -> None:
        result = run("skills/bioprospector/scripts/bioprospector_doctor.py", "--json")
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["repo"], ".")
        self.assertEqual(report["mode"], "local_no_network_no_provider_mutation")
        self.assertTrue(report["checks"]["public_audit"]["ok"])
        self.assertNotIn("/" + "Users" + "/", result.stdout)

    def test_expected_output_snapshots_are_compact_and_machine_readable(self) -> None:
        snapshot_dir = REPO_ROOT / "demos" / "expected-outputs"
        campaign = json.loads((snapshot_dir / "campaign-plan.summary.json").read_text(encoding="utf-8"))
        atlas = json.loads((snapshot_dir / "genecluster-atlas-plan.summary.json").read_text(encoding="utf-8"))
        self.assertEqual(campaign["public_data_policy"], "compact_ledgers_pointers_checksums_only")
        self.assertEqual(atlas["schema_version"], "bioprospector_genecluster_atlas_plan.v1")
        self.assertLess((snapshot_dir / "dossier-excerpt.md").stat().st_size, 10_000)

    def test_new_campaign_scaffold_preflights_and_exports_dossier(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "campaign"
            run(
                "skills/bioprospector/scripts/bioprospector_new_campaign.py",
                "--target-contract",
                "templates/target-contract.example.json",
                "--out",
                str(out),
                "--campaign-id",
                "scaffold-test-v0",
            )
            run(
                "skills/bioprospector/scripts/bioprospector_preflight.py",
                "--campaign",
                str(out / "campaign-manifest.json"),
                "--repo-root",
                str(out),
                "--scan-local-artifacts",
            )
            dossier = Path(tmpdir) / "dossier.md"
            run(
                "skills/bioprospector/scripts/bioprospector_dossier_export.py",
                "--campaign",
                str(out / "campaign-manifest.json"),
                "--out",
                str(dossier),
            )
            text = dossier.read_text(encoding="utf-8")
            self.assertIn("BioProspector Dossier", text)
            self.assertIn("not biological validation", text)

    def test_evidence_ingest_rejects_fasta_and_writes_compact_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            hits = tmp / "hits.tsv"
            hits.write_text(
                "q1\tsubjectA\t55.0\t300\t0\t0\t1\t300\t5\t305\t1e-40\t220\n"
                "q1\tsubjectB\t20.0\t200\t0\t0\t1\t200\t1\t200\t1e-2\t50\n",
                encoding="utf-8",
            )
            out = tmp / "out"
            run(
                "skills/bioprospector/scripts/bioprospector_evidence_ingest.py",
                "--hits",
                str(hits),
                "--out",
                str(out),
                "--step-id",
                "S001",
                "--run-id",
                "TEST",
            )
            with (out / "enzyme-draft-board.tsv").open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["claim_level"], "hypothesis")

            fasta = tmp / "raw.faa"
            fasta.write_text(">seq\nMPEPTIDE\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "skills/bioprospector/scripts/bioprospector_evidence_ingest.py",
                    "--hits",
                    str(fasta),
                    "--out",
                    str(tmp / "bad"),
                    "--step-id",
                    "S001",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FASTA/raw sequence input is not allowed", result.stdout)

    def test_self_learning_helper_appends_valid_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Path(tmpdir) / "self-learning-skill-ledger.tsv"
            run(
                "skills/bioprospector/scripts/bioprospector_self_learning.py",
                "--ledger",
                str(ledger),
                "--trigger",
                "smoke",
                "--hiccup-type",
                "stale_progress",
                "--observation",
                "stage progress stalled",
                "--hypothesis",
                "heartbeat without artifacts predicts join failure",
                "--probe",
                "dry-run validator fixture",
                "--baseline",
                "known-good completed stage",
                "--expected-signal",
                "validator flags stale progress",
                "--stop-loss",
                "one fixture",
                "--decision",
                "add_validator",
            )
            with ledger.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(rows[0]["hiccup_type"], "stale_progress")
            self.assertEqual(rows[0]["decision"], "add_validator")

    def test_public_demo_smoke_generates_public_safe_issue_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "smoke"
            run(
                "skills/bioprospector/scripts/bioprospector_public_demo_smoke.py",
                "--campaign",
                "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json",
                "--prefix",
                "HUPERZINE",
                "--out",
                str(out),
                "--skip-provider-bundles",
            )
            self.assertTrue((out / "dossier.md").exists())
            self.assertGreater(len(list((out / "issues").glob("*.md"))), 0)


if __name__ == "__main__":
    unittest.main()
