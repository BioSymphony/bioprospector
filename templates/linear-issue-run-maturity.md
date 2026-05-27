# Run Maturity Ladder

## Goal

Separate planning, tool readiness, materialized inputs, execution, joined evidence, and claim-audited dossier status.

## Required Artifacts

- `run-maturity-ledger.tsv`
- `execution-artifact-ledger.tsv`
- `target-evidence-ledger.tsv`
- `claim-ledger.md`

## Acceptance Criteria

- L0 through L5 are not collapsed into one success state.
- L3 requires non-mock execution artifacts.
- L4 requires joined evidence.
- L5 requires final claim audit and contract self-check.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-maturity L5
```
