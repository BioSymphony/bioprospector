"""Tests for destructive-output and public-path guards."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "skills/bioprospector/scripts"


def load_module(name: str, filename: str):
    path = SCRIPT_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


new_campaign = load_module("bioprospector_new_campaign_path_tests", "bioprospector_new_campaign.py")
demo_smoke = load_module("bioprospector_public_demo_smoke_path_tests", "bioprospector_public_demo_smoke.py")
self_learning = load_module("bioprospector_self_learning_path_tests", "bioprospector_self_learning.py")
runpod_bundle = load_module("bioprospector_runpod_bundle_path_tests", "bioprospector_runpod_bundle.py")
elasticblast_bundle = load_module(
    "bioprospector_elasticblast_bundle_path_tests", "bioprospector_elasticblast_bundle.py"
)


class BioProspectorPathSafetyTests(unittest.TestCase):
    def test_replace_guards_reject_broad_directories(self) -> None:
        for module in (new_campaign, demo_smoke):
            for path in (Path("/"), Path.home(), REPO_ROOT, REPO_ROOT.parent):
                with self.subTest(module=module.__name__, path=path):
                    with self.assertRaises(ValueError):
                        module.safe_replace_target(path)

    def test_replace_guards_accept_scoped_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "campaign" / "output"
            for module in (new_campaign, demo_smoke):
                self.assertEqual(target.resolve(), module.safe_replace_target(target))

    def test_replace_guards_reject_symlink_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "generated" / "output"
            target.mkdir(parents=True)
            link = Path(tmpdir) / "campaign-output"
            link.symlink_to(target, target_is_directory=True)

            for module in (new_campaign, demo_smoke):
                with self.subTest(module=module.__name__):
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        module.safe_replace_target(link)

            self.assertTrue(target.exists())

    def test_replace_guards_reject_symlink_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_parent = Path(tmpdir) / "generated"
            target_parent.mkdir()
            link_parent = Path(tmpdir) / "linked-parent"
            link_parent.symlink_to(target_parent, target_is_directory=True)
            output = link_parent / "output"

            for module in (new_campaign, demo_smoke):
                with self.subTest(module=module.__name__):
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        module.safe_replace_target(output)

            self.assertFalse((target_parent / "output").exists())

    def test_campaign_scaffold_rejects_dangling_output_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            link = Path(tmpdir) / "campaign-output"
            link.symlink_to(Path(tmpdir) / "missing-target", target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symlink"):
                new_campaign.scaffold_campaign(Path(tmpdir) / "missing-contract.json", link)

    def test_provider_bundles_reject_runtime_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temporary_repo = Path(tmpdir) / "repository"
            external_runtime = Path(tmpdir) / "external-runtime"
            temporary_repo.mkdir()
            external_runtime.mkdir()
            runtime_link = temporary_repo / ".runtime"
            runtime_link.symlink_to(external_runtime, target_is_directory=True)

            for module in (runpod_bundle, elasticblast_bundle):
                with self.subTest(module=module.__name__):
                    with mock.patch.object(module, "REPO_ROOT", temporary_repo), mock.patch.object(
                        module, "RUNTIME_ROOT", runtime_link
                    ):
                        with self.assertRaisesRegex(ValueError, "symlink"):
                            module.resolve_output_dir(None, "path-test")

            self.assertEqual([], list(external_runtime.iterdir()))

    def test_demo_smoke_refuses_unmarked_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "documents" / "output"
            target.mkdir(parents=True)
            sentinel = target / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                demo_smoke.prepare_output(target)

            self.assertTrue(sentinel.exists())

    def test_demo_smoke_refuses_unmarked_directory_under_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temporary_repo = Path(tmpdir) / "repository"
            target = temporary_repo / ".runtime" / "other-demo"
            target.mkdir(parents=True)
            sentinel = target / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with mock.patch.object(demo_smoke, "REPO_ROOT", temporary_repo):
                with self.assertRaisesRegex(ValueError, "marker"):
                    demo_smoke.prepare_output(target)
                with self.assertRaisesRegex(ValueError, "broad"):
                    demo_smoke.safe_replace_target(temporary_repo / ".runtime")

            self.assertTrue(sentinel.exists())

    def test_demo_smoke_refuses_forged_or_symlink_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temporary_repo = Path(tmpdir) / "repository"
            target = temporary_repo / ".runtime" / "demo"
            target.mkdir(parents=True)
            marker = target / demo_smoke.SMOKE_MARKER
            marker.write_text("unreviewed marker\n", encoding="utf-8")

            with mock.patch.object(demo_smoke, "REPO_ROOT", temporary_repo):
                with self.assertRaisesRegex(ValueError, "marker"):
                    demo_smoke.prepare_output(target)

                marker.unlink()
                marker_target = temporary_repo / ".runtime" / "marker-target"
                marker_target.write_text(demo_smoke.SMOKE_MARKER_CONTENT, encoding="utf-8")
                marker.symlink_to(marker_target)
                with self.assertRaisesRegex(ValueError, "marker"):
                    demo_smoke.prepare_output(target)

    def test_campaign_force_refuses_unrecognized_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "documents" / "campaign"
            target.mkdir(parents=True)
            sentinel = target / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                new_campaign.remove_existing_campaign(target)

            self.assertTrue(sentinel.exists())

    def test_self_learning_manifest_path_cannot_escape_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign = Path(tmpdir) / "campaign-manifest.json"
            campaign.write_text(
                '{"campaign_id":"path-test","ledgers":{"self_learning_skill_ledger":"../learning.tsv"}}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "inside the campaign directory"):
                self_learning.resolve_ledger(campaign, None)

    def test_self_learning_external_output_is_not_printable_as_a_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "learning.tsv"
            self.assertEqual("REPLACE_ME_EXTERNAL_PATH", self_learning.display_path(path))


if __name__ == "__main__":
    unittest.main()
