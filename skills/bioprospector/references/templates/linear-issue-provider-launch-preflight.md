# Provider Launch Preflight

## Goal

Fail before paid compute starts if provider launch prerequisites are not
verified.

## Required Artifacts

- `provider-launch-preflight-ledger.tsv`
- provider readiness bundle path
- image pull/auth status
- branch or snapshot reference
- stage contract references

## Acceptance Criteria

- Every `blocking_before_launch=true` row has `status=pass` before live launch.
- Private GHCR or other private registry images are blocked until provider-side registry auth is verified outside repo/Linear.
- Image digest, network volume, workdir, budget, payload size, issue body, secrets boundary, data policy, and stage contracts are reviewed.
- No provider API call, pod creation, AWS submit, credential test, or database download is performed from this issue.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-real-execution
```
