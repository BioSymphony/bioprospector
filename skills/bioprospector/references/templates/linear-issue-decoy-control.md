# Decoy And Negative-Control Gate

## Goal

Require controls before wide/frontier search results can promote candidates.

## Required Artifacts

- `decoy-control-ledger.tsv`
- control summaries or provider-side pointers
- candidate downgrades for failed controls

## Acceptance Criteria

- Every wide/frontier step has a passed blocking control before promotion.
- Failed controls block candidate promotion.
- Control artifacts are compact summaries, not raw search dumps.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-decoy-controls
```
