#!/usr/bin/env python3
"""Tests for read-only ElasticBLAST probe helpers."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = REPO_ROOT / "skills/bioprospector/scripts/bioprospector_elasticblast_probe.py"

spec = importlib.util.spec_from_file_location("bioprospector_elasticblast_probe", PROBE_PATH)
assert spec and spec.loader
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class ElasticBlastProbeHelperTests(unittest.TestCase):
    def test_us_east_1_bucket_location_is_null(self) -> None:
        self.assertEqual(probe.bucket_region_name(None), "us-east-1")
        self.assertEqual(probe.bucket_region_name(""), "us-east-1")

    def test_non_default_bucket_location_is_preserved(self) -> None:
        self.assertEqual(probe.bucket_region_name("us-west-2"), "us-west-2")

    def test_redacts_account_and_iam_ids(self) -> None:
        user_id = "AI" + "DAEXAMPLEUSERID123456"
        account_id = "".join(["123", "456", "789", "012"])
        text = f"arn:aws:iam::{account_id}:user/example-operator {user_id} {account_id}"

        redacted = probe.redact_aws_text(text)

        self.assertNotIn(account_id, redacted)
        self.assertNotIn(user_id, redacted)
        self.assertIn("<redacted-account>", redacted)
        self.assertIn("<redacted-user-id>", redacted)

    def test_provider_identifiers_redact_unless_explicitly_shown(self) -> None:
        self.assertEqual(probe.provider_identifier("real-bucket"), "<redacted-provider-identifier>")
        self.assertEqual(probe.provider_identifier("real-bucket", show=True), "real-bucket")

    def test_existing_infra_names_are_redacted_by_default(self) -> None:
        original = probe.aws_json

        def fake_aws_json(profile, region, service_args):
            if service_args[:2] == ["batch", "describe-compute-environments"]:
                return probe.CommandResult(0, "{}", ""), {
                    "computeEnvironments": [{"computeEnvironmentName": "private-compute-env"}]
                }
            return probe.CommandResult(0, "{}", ""), {"StackSummaries": [{"StackName": "private-stack"}]}

        probe.aws_json = fake_aws_json
        try:
            checks = probe.existing_infra_checks(None, "us-east-1")
        finally:
            probe.aws_json = original

        serialized = json.dumps(checks)
        self.assertNotIn("private-compute-env", serialized)
        self.assertNotIn("private-stack", serialized)
        self.assertIn('"names_redacted": true', serialized)

    def test_guardrail_document_requires_region_and_ec2_denies(self) -> None:
        document = {
            "Statement": [
                {
                    "Sid": "DenyOutsideUsEast1",
                    "Effect": "Deny",
                    "Condition": {"StringNotEquals": {"aws:RequestedRegion": "us-east-1"}},
                },
                {"Sid": "DenyHugeOrSpecialtyEC2Direct", "Effect": "Deny"},
            ]
        }

        self.assertTrue(probe.guardrail_document_ok(document, "us-east-1"))
        self.assertFalse(probe.guardrail_document_ok(document, "us-west-2"))

    def test_emergency_document_requires_key_denies(self) -> None:
        document = {
            "Statement": [
                {
                    "Sid": "DenyNewExpensiveResources",
                    "Effect": "Deny",
                    "Action": ["ec2:RunInstances", "batch:SubmitJob", "cloudformation:CreateStack"],
                }
            ]
        }

        self.assertTrue(
            probe.statement_denies_actions(
                document,
                "DenyNewExpensiveResources",
                {"ec2:RunInstances", "batch:SubmitJob", "cloudformation:CreateStack"},
            )
        )

    def test_template_check_accepts_cost_capped_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "template.ini"
            path.write_text(
                "\n".join(
                    [
                        "[cloud-provider]",
                        "aws-region = us-east-1",
                        "[cluster]",
                        "num-nodes = 1",
                        "use-preemptible = true",
                        "machine-type = m5.4xlarge",
                        "[blast]",
                        "results = s3://example-public-elasticblast-bucket/results/test",
                    ]
                ),
                encoding="utf-8",
            )

            check = probe.elasticblast_template_check(path, "us-east-1", "example-public-elasticblast-bucket")

        self.assertEqual(check["status"], "pass")


if __name__ == "__main__":
    unittest.main()
