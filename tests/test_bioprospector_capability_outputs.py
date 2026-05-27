"""Golden and negative tests for BioProspector capability outputs."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas/bioprospector-ledgers.json"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, headers: list[str], row: list[str]) -> None:
    path.write_text("\t".join(headers) + "\n" + "\t".join(row) + "\n", encoding="utf-8")


def write_minimal_campaign(root: Path, *, raw_event_retained: str = "false") -> Path:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    headers = schema["ledger_headers"]
    rows = {
        "route_ledger": [
            "R001",
            "demo-route",
            "demo-product",
            "demo-host",
            "fed",
            "seed_route",
            "hypothesis",
            "seed",
            "unknown",
            "planning",
        ],
        "reaction_step_ledger": [
            "S001",
            "R001",
            "1",
            "demo transformation",
            "substrate",
            "product",
            "enzyme",
            "evidence",
            "wide",
            "enzyme_draft_board",
            "planning",
        ],
        "candidate_funnels": ["S001", "1", "1", "0", "1", "0", "0", "0", "planned", "planning"],
        "enzyme_draft_board": [
            "E001",
            "S001",
            "candidate",
            "organism",
            "accession",
            "family",
            "domain",
            "sequence_similarity",
            "hypothesis",
            "unknown",
            "unknown",
            "medium",
            "review",
            "planning",
        ],
        "route_stitching_scorecard": [
            "R001",
            "seed",
            "unknown",
            "unknown",
            "unknown",
            "unknown",
            "unknown",
            "S001",
            "not_reviewed",
            "planning",
        ],
        "resource_ledger": [
            "resource",
            "database",
            "review_before_run",
            "open",
            "citation_only",
            "no-large-content-copy",
            "https://example.org",
            "planning",
        ],
        "tool_registry_ledger": [
            "mmseqs",
            "MMseqs2",
            "sequence_search",
            "compact_sequence_adapter",
            "v1",
            "sequence_hit",
            "compact_tsv_only",
            "evidence_event_ledger",
            "no_private_data",
            "tool_license_review_required",
            "local_full;runpod_manual_pod",
            "active",
            "planning",
        ],
        "adapter_contract_ledger": [
            "compact_sequence_adapter",
            "mmseqs",
            "1.0",
            "blast6;diamond;mmseqs",
            "evidence_event_ledger",
            "qseqid;sseqid;pident;evalue;bitscore",
            "fasta;fastq;raw_reads",
            "reject_raw_sequences",
            "stable_sha1_event_ids",
            "fail_closed",
            "active",
            "planning",
        ],
        "evidence_event_ledger": [
            "EV001",
            "sequence_hit",
            "demo",
            "RUN001",
            "S001",
            "E001",
            "",
            "mmseqs",
            "compact_sequence_adapter",
            "public_summary",
            "sequence_similarity",
            "homolog_hit",
            "compact_table:hits.tsv#1",
            "{\"bitscore\":100}",
            "hypothesis",
            "pending",
            "summary_only",
            "compact_input",
            raw_event_retained,
            "none",
            "planning",
        ],
        "tool_execution_proof_ledger": [
            "TP001",
            "RUN001",
            "mmseqs",
            "compact_sequence_adapter",
            "review_before_run",
            "mmseqs easy-search --help",
            "review_before_run",
            "review_before_run",
            "",
            "",
            "planned",
            ".runtime/proof/mmseqs-help.txt",
            "",
            "",
            "true",
            "false",
            "planned",
            "pending_live_command_output",
            "planning",
        ],
    }
    ledgers: dict[str, str] = {}
    for key, row in rows.items():
        filename = key.replace("_", "-") + ".tsv"
        write_tsv(root / filename, headers[key], row)
        ledgers[key] = filename
    (root / "claim-ledger.md").write_text(
        "| Claim | Level | Evidence | Caveat |\n| --- | --- | --- | --- |\n| demo | hypothesis | seed | planning only |\n",
        encoding="utf-8",
    )
    ledgers["claim_ledger"] = "claim-ledger.md"
    (root / "target-contract.json").write_text(
        json.dumps(
            {
                "target_molecule": "demo",
                "host": "demo-host",
                "campaign_goal": "demo",
                "optimization_goals": ["highest_evidence"],
                "hard_boundaries": ["planning_only"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest = {
        "campaign_id": "demo",
        "campaign_name": "Demo",
        "target_contract": "target-contract.json",
        "host": "demo-host",
        "target_molecule": "demo",
        "mode": "pathway_big_bang",
        "scope": "planning_only",
        "claim_boundary": "planning only",
        "ledgers": ledgers,
    }
    path = root / "campaign-manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


class BioProspectorCapabilityOutputTests(unittest.TestCase):
    def test_schema_declares_candidate_package_contracts(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["schema_version"], "1.2.0")
        for key in [
            "tool_registry_ledger",
            "adapter_contract_ledger",
            "evidence_event_ledger",
            "tool_execution_proof_ledger",
            "candidate_ranking_ledger",
            "pareto_frontier_ledger",
            "genecluster_source_scout_ledger",
            "genecluster_route_decision_ledger",
            "genecluster_atlas_contract_ledger",
            "genecluster_cluster_calls",
            "genecluster_bgc_consensus",
            "genecluster_protein_function_votes",
            "genecluster_protein_function_jury",
        ]:
            self.assertIn(key, schema["ledger_headers"])
            self.assertIn(key, schema["optional_ledger_keys"])
        self.assertIn("sequence_pack", schema["enums"]["run_package_types"])

    def test_preflight_validates_adapter_event_contract_and_rejects_raw_retained(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign = write_minimal_campaign(Path(tmpdir), raw_event_retained="false")
            run("skills/bioprospector/scripts/bioprospector_preflight.py", "--campaign", str(campaign))

        with tempfile.TemporaryDirectory() as tmpdir:
            campaign = write_minimal_campaign(Path(tmpdir), raw_event_retained="true")
            result = run("skills/bioprospector/scripts/bioprospector_preflight.py", "--campaign", str(campaign), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evidence_event_ledger raw data retained in repo", result.stdout)

    def test_compact_ingest_writes_events_sequences_and_graph_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            hits = tmp / "hits.tsv"
            hits.write_text("q1\tsubjectA\t55.0\t300\t0\t0\t1\t300\t5\t305\t1e-40\t220\n", encoding="utf-8")
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
                "--campaign-id",
                "demo",
                "--source-tool-id",
                "diamond",
                "--adapter-id",
                "compact_sequence_adapter",
                "--format",
                "diamond",
            )
            events = read_tsv(out / "evidence-event-ledger.tsv")
            sequences = read_tsv(out / "candidate-sequence-ledger.tsv")
            graph = read_tsv(out / "candidate-graph-ledger.tsv")
            self.assertEqual(events[0]["event_type"], "sequence_hit")
            self.assertEqual(events[0]["raw_data_retained"], "false")
            self.assertEqual(sequences[0]["sequence_type"], "provider_pointer")
            self.assertEqual(graph[0]["edge_type"], "step_candidate")

    def test_campaign_graph_package_ranker_and_dossier_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            campaign = "skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json"
            graph = tmp / "campaign-plan.json"
            package = tmp / "candidate-package"
            dossier = tmp / "dossier.md"
            run("skills/bioprospector/scripts/bioprospector_campaign_graph.py", "--campaign", campaign, "--out", str(graph))
            run("skills/bioprospector/scripts/bioprospector_candidate_package.py", "--campaign", campaign, "--out", str(package))
            run(
                "skills/bioprospector/scripts/bioprospector_dossier_export.py",
                "--campaign",
                campaign,
                "--sidecar-dir",
                str(package),
                "--out",
                str(dossier),
            )
            graph_json = json.loads(graph.read_text(encoding="utf-8"))
            self.assertTrue(any(node["node_id"] == "final_dossier" for node in graph_json["nodes"]))
            self.assertTrue((package / "candidate-sequence-ledger.tsv").exists())
            self.assertTrue((package / "candidate-ranking-ledger.tsv").exists())
            self.assertTrue((package / "pareto-frontier-ledger.tsv").exists())
            self.assertFalse(list(package.glob("*.faa")))
            text = dossier.read_text(encoding="utf-8")
            self.assertIn("Provider-Side Candidate Sequence Package", text)
            self.assertIn("Pareto Frontier", text)

    def test_strict_closeout_fails_pending_provider_sequence_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = REPO_ROOT / "skills/bioprospector/examples/huperzine-frontier-public-v0"
            campaign_dir = tmp / "campaign"
            shutil.copytree(source, campaign_dir)
            package = tmp / "package"
            run(
                "skills/bioprospector/scripts/bioprospector_candidate_package.py",
                "--campaign",
                str(campaign_dir / "campaign-manifest.json"),
                "--out",
                str(package),
            )
            manifest_path = campaign_dir / "campaign-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for filename in [
                "candidate-sequence-ledger.tsv",
                "candidate-diversity-ledger.tsv",
                "candidate-graph-ledger.tsv",
                "candidate-ranking-ledger.tsv",
                "pareto-frontier-ledger.tsv",
                "run-output-package-ledger.tsv",
            ]:
                shutil.copy2(package / filename, campaign_dir / filename)
            manifest["ledgers"].update(
                {
                    "candidate_sequence_ledger": "candidate-sequence-ledger.tsv",
                    "candidate_diversity_ledger": "candidate-diversity-ledger.tsv",
                    "candidate_graph_ledger": "candidate-graph-ledger.tsv",
                    "candidate_ranking_ledger": "candidate-ranking-ledger.tsv",
                    "pareto_frontier_ledger": "pareto-frontier-ledger.tsv",
                    "run_output_package_ledger": "run-output-package-ledger.tsv",
                }
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            result = run(
                "skills/bioprospector/scripts/bioprospector_contract_self_check.py",
                "--campaign",
                str(manifest_path),
                "--require-real-execution",
                "--require-target-evidence",
                "--require-decoy-controls",
                "--require-maturity",
                "L5",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate_sequence_package_checksums", result.stdout)


if __name__ == "__main__":
    unittest.main()
