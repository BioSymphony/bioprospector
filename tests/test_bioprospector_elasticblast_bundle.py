"""Tests for prep-only ElasticBLAST bundle helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_elasticblast_bundle.py"

spec = importlib.util.spec_from_file_location("bioprospector_elasticblast_bundle", BUNDLE_PATH)
assert spec is not None
bundle = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bundle)


def test_refseq_select_database_notes_name_compact_scout() -> None:
    notes = "\n".join(bundle.database_notes("refseq_select_prot"))
    assert "compact RefSeq-family scout" in notes
    assert "provider metadata names" in notes


def test_refseq_protein_database_notes_warn_about_memory() -> None:
    notes = "\n".join(bundle.database_notes("refseq_protein"))
    assert "high-memory instances" in notes
    assert "before promising a cheap run" in notes


def test_render_readme_includes_database_notes() -> None:
    manifest = {
        "campaign": {"campaign_id": "test-campaign"},
        "source_campaign": {"path": "skills/bioprospector/examples/test/campaign-manifest.json"},
        "local_output": {"path": ".runtime/test"},
        "search_plan": [{"database": "refseq_select_prot"}],
        "elasticblast_contract": {
            "default_region": "us-east-1",
            "scout_budget_usd": 1.0,
            "execution_boundary": "prep_only_no_aws_calls",
            "database_notes": bundle.database_notes("refseq_select_prot"),
        },
    }
    readme = bundle.render_readme(manifest)
    assert "## Database Notes" in readme
    assert "refseq_select_prot" in readme
    assert "full `refseq_protein`/`nr` only after memory" in readme
