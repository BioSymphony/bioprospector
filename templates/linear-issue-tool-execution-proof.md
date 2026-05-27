# Exact Executable Proof

## Goal

Prove the exact tool commands used by live stages are callable before paid
compute, live closeout, or scientific success language.

## Required Artifacts

- `tool-execution-proof-ledger.tsv`
- `stage-contract-ledger.tsv`
- observed version or dry-invocation evidence pointer
- provider-launch-preflight row when command proof blocks launch

## Acceptance Criteria

- Package installation, image build, or tool presence alone is not proof.
- Every materialized proof row records `tool_id`, `adapter_id`, `provider_id`, command/workflow, versions, exit status, output pointers, and checksum or summary.
- Every live L3/L4/L5 fail-closed stage has a `status=materialized` proof row with `dry_run=false` and `mock_tools=false`.
- Placeholder, fixture, mock, reference-only, and generic command paths are rejected.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-real-execution
```
