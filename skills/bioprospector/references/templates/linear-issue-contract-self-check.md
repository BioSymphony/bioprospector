# Final Contract Self-Check

## Goal

Join inputs, materialized data, execution artifacts, evidence, controls, and claims before declaring success.

## Required Artifacts

- `input-audit-ledger.tsv`
- `operator-intake-ledger.tsv`
- `run-maturity-ledger.tsv`
- `stage-contract-ledger.tsv`
- `stage-progress-ledger.tsv`
- `execution-artifact-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`
- `target-evidence-ledger.tsv`
- `decoy-control-ledger.tsv`
- `claim-ledger.md`
- contract self-check JSON

## Acceptance Criteria

- Runner flags are not treated as proof.
- Dry-run and mock artifacts cannot satisfy real evidence requirements.
- Claims are bounded by joined artifacts and target evidence.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py \
  --campaign path/to/campaign-manifest.json \
  --require-real-execution \
  --require-target-evidence \
  --require-decoy-controls \
  --require-maturity L5
```
