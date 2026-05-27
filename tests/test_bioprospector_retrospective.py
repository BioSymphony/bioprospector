"""Tests for public-safe BioProspector retrospective ledger generation."""

from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_retrospective.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


retrospective = load_module("bioprospector_retrospective", SCRIPT_PATH)


class BioProspectorRetrospectiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="public-retrospective-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_provider_rows_redact_resource_identifiers(self) -> None:
        run_dir = self.temp_dir / "demo-after-run-20260513T000000Z"
        run_dir.mkdir()
        (run_dir / "runpod_resource_record.json").write_text(
            json.dumps(
                {
                    "preview": {
                        "contract": {"run_id": "demo-run"},
                        "plan": {
                            "compute": {
                                "profile": "cpu-tiny-blast-runpod-smoke",
                                "max_estimated_cost_usd": 2,
                                "max_runtime_minutes": 30,
                            },
                            "execution": {"artifact_egress": {"mode": "workspace_archive"}},
                        },
                    },
                    "duplicate_check": {"active_matches": [{"id": "example-resource-match"}]},
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "trusted_after_run_summary.json").write_text(
            json.dumps(
                {
                    "issue_identifier": "PUBLIC-TEST",
                    "final_status": "success",
                    "steps": [
                        {
                            "started_at": "2026-05-13T00:00:00Z",
                            "ended_at": "2026-05-13T00:01:00Z",
                            "returncode": 0,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "create_pod_response.json").write_text(
            json.dumps({"pod_id": "example-resource-created"}),
            encoding="utf-8",
        )
        (run_dir / "runpod-execution").mkdir()

        row = retrospective.parse_provider_after_run(run_dir)
        self.assertEqual("succeeded", row["final_status"])
        self.assertEqual("yes", row["provider_resource_seen"])
        self.assertEqual("redacted", row["provider_resource_ref"])
        self.assertNotIn("example-resource", "\t".join(str(value) for value in row.values()))

    def test_cli_writes_retrospective_tsv_for_provider_and_elasticblast_runs(self) -> None:
        provider_run = self.temp_dir / "provider-after-run-20260513T000000Z"
        provider_run.mkdir()
        (provider_run / "trusted_after_run_summary.json").write_text(
            json.dumps({"run_id": "provider-run", "final_status": "failed", "error": "tool exited"}),
            encoding="utf-8",
        )
        elastic_run = self.temp_dir / "elasticblast-smoke-20260513-001"
        elastic_run.mkdir()
        (elastic_run / "status.log").write_text("SEARCH SUCCEEDED\n", encoding="utf-8")
        (elastic_run / "results.tsv").write_text("query\thit\nq1\th1\n", encoding="utf-8")
        out = self.temp_dir / "retrospective-ledger.tsv"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--root",
                str(self.temp_dir),
                "--out",
                str(out),
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )

        with out.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(2, len(rows))
        self.assertEqual({"elasticblast", "runpod"}, {row["provider"] for row in rows})
        self.assertIn("provider resources redacted", result.stderr)


if __name__ == "__main__":
    unittest.main()
