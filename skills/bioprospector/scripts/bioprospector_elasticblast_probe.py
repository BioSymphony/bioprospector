#!/usr/bin/env python3
"""Read-only AWS ElasticBLAST readiness probe.

This script checks local tooling, AWS identity, region, S3 bucket safety,
budget visibility, and absence/presence of existing Batch/CloudFormation
resources. It never submits ElasticBLAST, creates AWS resources, uploads query
FASTA, downloads BLAST output, or prints AWS secrets.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REGION = "us-east-1"
DEFAULT_MAX_BUDGET_USD = 25.0
DEFAULT_IAM_USER: str | None = None
DEFAULT_GUARDRAIL_POLICY = "ElasticBlastGuardrails"
DEFAULT_EMERGENCY_POLICY = "EmergencyDenyExpensive"
DEFAULT_BUDGET_ACTION_ID: str | None = None
DEFAULT_CONFIG_TEMPLATE: Path | None = None
REDACTED_PROVIDER_IDENTIFIER = "<redacted-provider-identifier>"
S3_SCHEME = "s3" + "://"


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def run_command(args: list[str], timeout: int = 30) -> CommandResult:
    proc = subprocess.run(args, check=False, capture_output=True, text=True, timeout=timeout)
    return CommandResult(proc.returncode, proc.stdout.strip(), proc.stderr.strip())


def aws_base(profile: str | None, region: str | None = None) -> list[str]:
    args = ["aws"]
    if profile:
        args.extend(["--profile", profile])
    if region:
        args.extend(["--region", region])
    return args


def parse_json(text: str) -> Any:
    return json.loads(text or "{}")


def redact_aws_text(text: str) -> str:
    text = re.sub(r"\b[0-9]{12}\b", "<redacted-account>", text)
    text = re.sub(r"AIDA[0-9A-Z]+", "<redacted-user-id>", text)
    text = re.sub(r"AROA[0-9A-Z]+", "<redacted-role-id>", text)
    text = re.sub(r"arn:aws:iam::<redacted-account>:", "arn:aws:iam::<redacted-account>:", text)
    text = re.sub(r"arn:aws:iam::[0-9]{12}:", "arn:aws:iam::<redacted-account>:", text)
    return text


def provider_identifier(value: Any, *, show: bool = False, placeholder: str = REDACTED_PROVIDER_IDENTIFIER) -> Any:
    if value is None or value == "":
        return value
    return value if show else placeholder


def redact_provider_text(text: str, identifiers: list[str | None], *, show: bool = False) -> str:
    text = redact_aws_text(text)
    if show:
        return text
    for identifier in identifiers:
        if identifier:
            text = text.replace(identifier, REDACTED_PROVIDER_IDENTIFIER)
    return text


def redact_policy_arn(arn: str) -> str:
    return redact_aws_text(arn)


def ok_check(name: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"name": name, "status": "pass", "detail": detail, **extra}


def warn_check(name: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"name": name, "status": "warn", "detail": detail, **extra}


def fail_check(name: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"name": name, "status": "fail", "detail": redact_aws_text(detail), **extra}


def command_version(binary: str, version_args: list[str]) -> dict[str, Any]:
    path = shutil.which(binary)
    if not path:
        return fail_check(f"{binary}_on_path", f"{binary} not found on PATH")
    result = run_command([path, *version_args])
    output = result.stdout or result.stderr
    if result.returncode != 0:
        return fail_check(f"{binary}_version", output or f"{binary} version probe failed", path=path)
    return ok_check(f"{binary}_version", output.splitlines()[0], path=path)


def aws_json(profile: str | None, region: str, service_args: list[str]) -> tuple[CommandResult, Any | None]:
    result = run_command([*aws_base(profile, region), *service_args, "--output", "json"])
    if result.returncode != 0:
        return result, None
    try:
        return result, parse_json(result.stdout)
    except json.JSONDecodeError:
        return CommandResult(1, result.stdout, "AWS returned non-JSON output"), None


def aws_global_json(profile: str | None, service_args: list[str]) -> tuple[CommandResult, Any | None]:
    result = run_command([*aws_base(profile), *service_args, "--output", "json"])
    if result.returncode != 0:
        return result, None
    try:
        return result, parse_json(result.stdout)
    except json.JSONDecodeError:
        return CommandResult(1, result.stdout, "AWS returned non-JSON output"), None


def configured_region(profile: str | None) -> dict[str, Any]:
    args = ["aws", "configure", "get", "region"]
    if profile:
        args.extend(["--profile", profile])
    result = run_command(args)
    if result.returncode != 0 or not result.stdout.strip():
        return warn_check("aws_config_region", result.stderr or "No configured AWS region found")
    return ok_check("aws_config_region", result.stdout.strip())


def identity_check(profile: str | None, region: str) -> tuple[dict[str, Any], str | None]:
    result, data = aws_json(profile, region, ["sts", "get-caller-identity"])
    if result.returncode != 0 or data is None:
        return fail_check("aws_identity", result.stderr or result.stdout or "identity probe failed"), None
    account = str(data.get("Account", "")).strip() or None
    arn = redact_aws_text(str(data.get("Arn", "")))
    user_id = redact_aws_text(str(data.get("UserId", "")))
    return ok_check("aws_identity", "AWS identity resolved", arn=arn, user_id=user_id), account


def infer_iam_user_from_identity(profile: str | None, region: str) -> str | None:
    result, data = aws_json(profile, region, ["sts", "get-caller-identity"])
    if result.returncode != 0 or data is None:
        return None
    arn = str(data.get("Arn", ""))
    match = re.search(r":user/(.+)$", arn)
    return match.group(1) if match else None


def bucket_region_name(location_constraint: Any) -> str:
    return DEFAULT_REGION if location_constraint in (None, "") else str(location_constraint)


def bucket_checks(
    profile: str | None,
    region: str,
    bucket: str,
    *,
    show_provider_identifiers: bool = False,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    bucket_display = provider_identifier(bucket, show=show_provider_identifiers)
    result, data = aws_json(profile, region, ["s3api", "get-bucket-location", "--bucket", bucket])
    if result.returncode != 0 or data is None:
        detail = redact_provider_text(
            result.stderr or result.stdout or "bucket location probe failed",
            [bucket],
            show=show_provider_identifiers,
        )
        return [fail_check("s3_bucket_location", detail)]
    bucket_region = bucket_region_name(data.get("LocationConstraint"))
    if bucket_region == region:
        checks.append(ok_check("s3_bucket_location", bucket_region, bucket=bucket_display))
    else:
        checks.append(
            fail_check("s3_bucket_location", f"bucket is in {bucket_region}, expected {region}", bucket=bucket_display)
        )

    result, data = aws_json(profile, region, ["s3api", "get-public-access-block", "--bucket", bucket])
    if result.returncode != 0 or data is None:
        detail = redact_provider_text(
            result.stderr or result.stdout or "public access probe failed",
            [bucket],
            show=show_provider_identifiers,
        )
        checks.append(fail_check("s3_public_access_block", detail))
    else:
        block = data.get("PublicAccessBlockConfiguration", {})
        required = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        if all(block.get(key) is True for key in required):
            checks.append(ok_check("s3_public_access_block", "all public access block flags are true"))
        else:
            checks.append(fail_check("s3_public_access_block", f"not all public access block flags are true: {block}"))

    result, data = aws_json(profile, region, ["s3api", "get-bucket-encryption", "--bucket", bucket])
    if result.returncode != 0 or data is None:
        detail = redact_provider_text(
            result.stderr or result.stdout or "encryption probe failed",
            [bucket],
            show=show_provider_identifiers,
        )
        checks.append(fail_check("s3_bucket_encryption", detail))
    else:
        rules = data.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
        algorithms = [
            rule.get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm")
            for rule in rules
        ]
        if any(algo in {"AES256", "aws:kms"} for algo in algorithms):
            checks.append(ok_check("s3_bucket_encryption", ",".join(str(algo) for algo in algorithms if algo)))
        else:
            checks.append(fail_check("s3_bucket_encryption", "no AES256 or aws:kms default encryption rule found"))
    return checks


def budget_check(
    profile: str | None,
    region: str,
    account_id: str | None,
    budget_name: str | None,
    max_budget_usd: float,
    *,
    show_provider_identifiers: bool = False,
) -> dict[str, Any]:
    if not account_id:
        return fail_check("aws_budget", "account id unavailable from identity probe")
    result, data = aws_json(profile, region, ["budgets", "describe-budgets", "--account-id", account_id])
    if result.returncode != 0 or data is None:
        return fail_check("aws_budget", result.stderr or result.stdout or "budget probe failed")
    budgets = data.get("Budgets", [])
    if budget_name:
        budgets = [budget for budget in budgets if budget.get("BudgetName") == budget_name]
        if not budgets:
            display_name = provider_identifier(budget_name, show=show_provider_identifiers)
            return fail_check("aws_budget", f"budget {display_name!r} not found")
    affordable = []
    for budget in budgets:
        limit = budget.get("BudgetLimit", {})
        try:
            amount = float(limit.get("Amount", "nan"))
        except ValueError:
            amount = float("nan")
        if budget.get("BudgetType") == "COST" and budget.get("TimeUnit") == "MONTHLY" and amount <= max_budget_usd:
            affordable.append(
                {
                    "name": provider_identifier(budget.get("BudgetName"), show=show_provider_identifiers),
                    "amount": amount,
                    "unit": limit.get("Unit"),
                }
            )
    if affordable:
        return ok_check("aws_budget", f"{len(affordable)} monthly cost budget(s) <= ${max_budget_usd:.2f}", budgets=affordable)
    return fail_check("aws_budget", f"no monthly COST budget <= ${max_budget_usd:.2f} found")


def policy_arn(account_id: str, policy_name: str) -> str:
    return f"arn:aws:iam::{account_id}:policy/{policy_name}"


def get_policy_document(profile: str | None, policy_arn_value: str) -> tuple[dict[str, Any] | None, str | None]:
    result, data = aws_global_json(profile, ["iam", "get-policy", "--policy-arn", policy_arn_value])
    if result.returncode != 0 or data is None:
        return None, result.stderr or result.stdout or "get-policy failed"
    version_id = data.get("Policy", {}).get("DefaultVersionId")
    if not version_id:
        return None, "policy default version missing"
    result, data = aws_global_json(
        profile,
        ["iam", "get-policy-version", "--policy-arn", policy_arn_value, "--version-id", str(version_id)],
    )
    if result.returncode != 0 or data is None:
        return None, result.stderr or result.stdout or "get-policy-version failed"
    return data.get("PolicyVersion", {}).get("Document"), None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def statement_has_sid(document: dict[str, Any], sid: str) -> bool:
    return any(stmt.get("Sid") == sid for stmt in as_list(document.get("Statement")))


def statement_denies_actions(document: dict[str, Any], sid: str, required_actions: set[str]) -> bool:
    for stmt in as_list(document.get("Statement")):
        if stmt.get("Sid") != sid or stmt.get("Effect") != "Deny":
            continue
        actions = {str(action) for action in as_list(stmt.get("Action"))}
        return required_actions.issubset(actions)
    return False


def guardrail_document_ok(document: dict[str, Any], region: str) -> bool:
    if not statement_has_sid(document, "DenyOutsideUsEast1"):
        return False
    if not statement_has_sid(document, "DenyHugeOrSpecialtyEC2Direct"):
        return False
    region_statement = next(
        (stmt for stmt in as_list(document.get("Statement")) if stmt.get("Sid") == "DenyOutsideUsEast1"),
        {},
    )
    requested_region = region_statement.get("Condition", {}).get("StringNotEquals", {}).get("aws:RequestedRegion")
    return requested_region == region


def iam_guardrail_checks(
    profile: str | None,
    region: str,
    account_id: str | None,
    iam_user: str | None,
    guardrail_policy_name: str,
    emergency_policy_name: str,
    *,
    show_provider_identifiers: bool = False,
) -> list[dict[str, Any]]:
    if not account_id:
        return [fail_check("iam_guardrails", "account id unavailable from identity probe")]
    if not iam_user:
        return [
            warn_check(
                "iam_guardrails",
                "IAM user was not resolved from the current identity; pass --iam-user to inspect user-attached guardrails",
            )
        ]
    checks: list[dict[str, Any]] = []
    iam_user_display = provider_identifier(iam_user, show=show_provider_identifiers)
    result, data = aws_global_json(profile, ["iam", "list-attached-user-policies", "--user-name", iam_user])
    if result.returncode != 0 or data is None:
        detail = redact_provider_text(
            result.stderr or result.stdout or "list-attached-user-policies failed",
            [iam_user],
            show=show_provider_identifiers,
        )
        return [fail_check("iam_user_policies", detail)]
    attached = data.get("AttachedPolicies", [])
    attached_names = {policy.get("PolicyName") for policy in attached}
    redacted_attached = [
        {"PolicyName": policy.get("PolicyName"), "PolicyArn": redact_policy_arn(str(policy.get("PolicyArn", "")))}
        for policy in attached
    ]
    if guardrail_policy_name in attached_names:
        checks.append(
            ok_check(
                "iam_guardrail_attached",
                f"{guardrail_policy_name} attached to {iam_user_display}",
                policies=redacted_attached,
            )
        )
    else:
        checks.append(
            fail_check(
                "iam_guardrail_attached",
                f"{guardrail_policy_name} is not attached to {iam_user_display}",
                policies=redacted_attached,
            )
        )
    if "AdministratorAccess" in attached_names:
        checks.append(warn_check("iam_admin_access_attached", "AdministratorAccess is attached; explicit Deny guardrails still take precedence"))
    if emergency_policy_name in attached_names:
        checks.append(fail_check("iam_emergency_policy_attached", f"{emergency_policy_name} is already attached; live submits are likely blocked"))
    else:
        checks.append(
            ok_check(
                "iam_emergency_policy_standby",
                f"{emergency_policy_name} is not currently attached to {iam_user_display}",
            )
        )

    guardrail_doc, error = get_policy_document(profile, policy_arn(account_id, guardrail_policy_name))
    if guardrail_doc is None:
        checks.append(fail_check("iam_guardrail_policy_document", error or "guardrail policy unreadable"))
    elif guardrail_document_ok(guardrail_doc, region):
        checks.append(ok_check("iam_guardrail_policy_document", f"{guardrail_policy_name} has region and EC2 size denies"))
    else:
        checks.append(fail_check("iam_guardrail_policy_document", f"{guardrail_policy_name} lacks expected region or EC2 deny statements"))

    emergency_doc, error = get_policy_document(profile, policy_arn(account_id, emergency_policy_name))
    required_emergency_actions = {"ec2:RunInstances", "batch:SubmitJob", "cloudformation:CreateStack"}
    if emergency_doc is None:
        checks.append(fail_check("iam_emergency_policy_document", error or "emergency policy unreadable"))
    elif statement_denies_actions(emergency_doc, "DenyNewExpensiveResources", required_emergency_actions):
        checks.append(ok_check("iam_emergency_policy_document", f"{emergency_policy_name} denies key expensive actions"))
    else:
        checks.append(fail_check("iam_emergency_policy_document", f"{emergency_policy_name} lacks expected deny actions"))
    return checks


def budget_action_check(
    profile: str | None,
    region: str,
    account_id: str | None,
    budget_name: str | None,
    budget_action_id: str | None,
    iam_user: str | None,
    emergency_policy_name: str,
    expected_threshold_usd: float,
    *,
    show_provider_identifiers: bool = False,
) -> dict[str, Any]:
    if not account_id:
        return fail_check("aws_budget_action", "account id unavailable from identity probe")
    if not budget_name:
        return warn_check("aws_budget_action", "No --budget-name supplied; budget action not checked")
    if not iam_user:
        return warn_check(
            "aws_budget_action",
            "IAM user was not resolved; pass --iam-user to verify budget action user targets",
        )
    args = ["budgets", "describe-budget-action", "--account-id", account_id, "--budget-name", budget_name]
    if budget_action_id:
        args.extend(["--action-id", budget_action_id])
        result, data = aws_json(profile, region, args)
    else:
        result, data = aws_json(
            profile,
            region,
            ["budgets", "describe-budget-actions-for-budget", "--account-id", account_id, "--budget-name", budget_name],
        )
    if result.returncode != 0 or data is None:
        detail = redact_provider_text(
            result.stderr or result.stdout or "budget action probe failed",
            [budget_name, budget_action_id, iam_user],
            show=show_provider_identifiers,
        )
        return fail_check("aws_budget_action", detail)
    actions = [data.get("Action")] if data.get("Action") else data.get("Actions", [])
    if not actions:
        return fail_check("aws_budget_action", "no budget action found")
    expected_policy_suffix = f":policy/{emergency_policy_name}"
    for action in actions:
        iam_def = action.get("Definition", {}).get("IamActionDefinition", {})
        threshold = action.get("ActionThreshold", {})
        users = set(iam_def.get("Users", []))
        policy = str(iam_def.get("PolicyArn", ""))
        try:
            threshold_value = float(threshold.get("ActionThresholdValue", "nan"))
        except ValueError:
            threshold_value = float("nan")
        if (
            action.get("ActionType") == "APPLY_IAM_POLICY"
            and action.get("ApprovalModel") == "AUTOMATIC"
            and action.get("Status") == "STANDBY"
            and iam_user in users
            and policy.endswith(expected_policy_suffix)
            and threshold.get("ActionThresholdType") == "ABSOLUTE_VALUE"
            and threshold_value <= expected_threshold_usd
        ):
            return ok_check(
                "aws_budget_action",
                f"automatic standby action applies {emergency_policy_name} at ${threshold_value:.2f} actual spend",
                action_id=provider_identifier(action.get("ActionId"), show=show_provider_identifiers),
                action_status=action.get("Status"),
            )
    return fail_check("aws_budget_action", "no matching standby automatic emergency policy action found")


def elasticblast_template_check(
    path: Path,
    region: str,
    bucket: str | None,
    *,
    show_provider_identifiers: bool = False,
) -> dict[str, Any]:
    path_display = str(path) if show_provider_identifiers else path.name
    if not path.exists():
        return warn_check("elasticblast_template", f"template not found: {path_display}")
    parser = configparser.ConfigParser()
    parser.read(path)
    errors: list[str] = []
    template_region = parser.get("cloud-provider", "aws-region", fallback="")
    if template_region != region:
        errors.append(f"aws-region={template_region!r}")
    num_nodes = parser.getint("cluster", "num-nodes", fallback=0)
    if num_nodes > 1:
        errors.append(f"num-nodes={num_nodes}")
    use_preemptible = parser.getboolean("cluster", "use-preemptible", fallback=False)
    if not use_preemptible:
        errors.append("use-preemptible is not true")
    machine_type = parser.get("cluster", "machine-type", fallback="")
    denied_patterns = ("p", "g", "dl", "trn", "inf", "x1", "x2", "u-")
    if machine_type.startswith(denied_patterns) or ".24xlarge" in machine_type or ".32xlarge" in machine_type:
        errors.append(f"machine-type={machine_type!r}")
    results = parser.get("blast", "results", fallback="")
    if bucket and not results.startswith(f"{S3_SCHEME}{bucket}/"):
        errors.append("results bucket mismatch")
    if errors:
        return fail_check("elasticblast_template", "; ".join(errors), path=path_display)
    return ok_check(
        "elasticblast_template",
        f"template caps num-nodes={num_nodes}, spot={use_preemptible}, machine-type={machine_type}",
        path=path_display,
    )


def existing_infra_checks(
    profile: str | None,
    region: str,
    *,
    show_provider_identifiers: bool = False,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    result, data = aws_json(profile, region, ["batch", "describe-compute-environments"])
    if result.returncode != 0 or data is None:
        checks.append(warn_check("aws_batch_compute_environments", result.stderr or result.stdout or "Batch probe failed"))
    else:
        envs = data.get("computeEnvironments", [])
        status = "pass" if not envs else "warn"
        check = {
            "name": "aws_batch_compute_environments",
            "status": status,
            "detail": f"{len(envs)} compute environment(s) visible",
            "visible_count": len(envs),
        }
        if show_provider_identifiers:
            check["names"] = [env.get("computeEnvironmentName") for env in envs[:10]]
        elif envs:
            check["names_redacted"] = True
        checks.append(check)

    result, data = aws_json(
        profile,
        region,
        [
            "cloudformation",
            "list-stacks",
            "--stack-status-filter",
            "CREATE_COMPLETE",
            "UPDATE_COMPLETE",
            "CREATE_IN_PROGRESS",
            "UPDATE_IN_PROGRESS",
        ],
    )
    if result.returncode != 0 or data is None:
        checks.append(warn_check("aws_cloudformation_active_stacks", result.stderr or result.stdout or "CloudFormation probe failed"))
    else:
        stacks = data.get("StackSummaries", [])
        status = "pass" if not stacks else "warn"
        check = {
            "name": "aws_cloudformation_active_stacks",
            "status": status,
            "detail": f"{len(stacks)} active stack(s) visible",
            "visible_count": len(stacks),
        }
        if show_provider_identifiers:
            check["names"] = [stack.get("StackName") for stack in stacks[:10]]
        elif stacks:
            check["names_redacted"] = True
        checks.append(check)
    return checks


def probe(args: argparse.Namespace) -> dict[str, Any]:
    profile = args.profile or os.environ.get("AWS_PROFILE")
    region = args.region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or DEFAULT_REGION
    bucket = args.bucket or os.environ.get("BIOPROSPECTOR_ELASTICBLAST_BUCKET")
    show_provider_identifiers = bool(args.show_provider_identifiers)

    checks: list[dict[str, Any]] = [
        command_version("aws", ["--version"]),
        command_version("elastic-blast", ["--version"]),
        configured_region(profile),
    ]
    identity, account_id = identity_check(profile, region)
    checks.append(identity)
    if bucket:
        checks.extend(bucket_checks(profile, region, bucket, show_provider_identifiers=show_provider_identifiers))
    else:
        checks.append(warn_check("s3_bucket", "No bucket provided; set --bucket or BIOPROSPECTOR_ELASTICBLAST_BUCKET"))
    if not args.skip_budget:
        checks.append(
            budget_check(
                profile,
                region,
                account_id,
                args.budget_name,
                args.max_budget_usd,
                show_provider_identifiers=show_provider_identifiers,
            )
        )
    iam_user = args.iam_user or infer_iam_user_from_identity(profile, region) or DEFAULT_IAM_USER
    if not args.skip_iam_guardrails:
        checks.extend(
            iam_guardrail_checks(
                profile,
                region,
                account_id,
                iam_user,
                args.guardrail_policy_name,
                args.emergency_policy_name,
                show_provider_identifiers=show_provider_identifiers,
            )
        )
    if not args.skip_budget_action:
        checks.append(
            budget_action_check(
                profile,
                region,
                account_id,
                args.budget_name,
                args.budget_action_id,
                iam_user,
                args.emergency_policy_name,
                args.budget_action_threshold_usd,
                show_provider_identifiers=show_provider_identifiers,
            )
        )
    if args.config_template:
        checks.append(
            elasticblast_template_check(
                args.config_template.expanduser(),
                region,
                bucket,
                show_provider_identifiers=show_provider_identifiers,
            )
        )
    checks.extend(existing_infra_checks(profile, region, show_provider_identifiers=show_provider_identifiers))

    fail_count = sum(check["status"] == "fail" for check in checks)
    warn_count = sum(check["status"] == "warn" for check in checks)
    profile_display = profile or "default"
    return {
        "ok": fail_count == 0,
        "profile": provider_identifier(profile_display, show=show_provider_identifiers) if profile else profile_display,
        "region": region,
        "bucket": provider_identifier(bucket, show=show_provider_identifiers),
        "iam_user": provider_identifier(iam_user, show=show_provider_identifiers),
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks": checks,
        "boundary": "read_only_no_submit_no_upload_no_download_no_resource_creation",
        "provider_identifiers_redacted": not show_provider_identifiers,
    }


def print_human(report: dict[str, Any]) -> None:
    print(f"BioProspector ElasticBLAST probe: {'PASS' if report['ok'] else 'FAIL'}")
    print(f"profile: {report['profile']}")
    print(f"region: {report['region']}")
    print(f"iam_user: {report['iam_user'] or '<not resolved>'}")
    if report.get("bucket"):
        print(f"bucket: {report['bucket']}")
    print(f"boundary: {report['boundary']}")
    for check in report["checks"]:
        print(f"[{check['status'].upper()}] {check['name']}: {check['detail']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", help="AWS profile to use. Defaults to AWS_PROFILE or the AWS default profile.")
    parser.add_argument("--region", default=DEFAULT_REGION, help=f"AWS region to probe. Defaults to {DEFAULT_REGION}.")
    parser.add_argument("--bucket", help="S3 bucket for ElasticBLAST queries/results, or BIOPROSPECTOR_ELASTICBLAST_BUCKET.")
    parser.add_argument("--budget-name", help="Optional exact AWS Budget name to require.")
    parser.add_argument("--max-budget-usd", type=float, default=DEFAULT_MAX_BUDGET_USD)
    parser.add_argument("--iam-user", help="IAM user to inspect. Defaults to the identity ARN user when STS returns a user ARN.")
    parser.add_argument("--guardrail-policy-name", default=DEFAULT_GUARDRAIL_POLICY)
    parser.add_argument("--emergency-policy-name", default=DEFAULT_EMERGENCY_POLICY)
    parser.add_argument("--budget-action-id", default=DEFAULT_BUDGET_ACTION_ID)
    parser.add_argument("--budget-action-threshold-usd", type=float, default=30.0)
    parser.add_argument("--config-template", type=Path, default=DEFAULT_CONFIG_TEMPLATE, help="Optional ElasticBLAST config template to inspect.")
    parser.add_argument("--skip-budget", action="store_true", help="Skip AWS Budgets check.")
    parser.add_argument("--skip-iam-guardrails", action="store_true", help="Skip IAM guardrail policy checks.")
    parser.add_argument("--skip-budget-action", action="store_true", help="Skip AWS Budgets action check.")
    parser.add_argument(
        "--show-provider-identifiers",
        action="store_true",
        help="Print AWS profile, S3 bucket, IAM user, stack, and compute environment names. Default redacts them.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = probe(args)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
