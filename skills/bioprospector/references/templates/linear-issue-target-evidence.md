# Target Evidence Join Gate

## Goal

Prevent public/reference hits from being treated as target organism or sample evidence.

## Required Artifacts

- `organism-sample-ledger.tsv`
- `target-dataset-ledger.tsv`
- `target-evidence-ledger.tsv`
- candidate downgrades where target evidence is absent

## Acceptance Criteria

- Candidate, step, organism/sample, and dataset IDs join.
- Reference-only rows remain reference context.
- Promoted candidates have joined target evidence or are downgraded.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-target-evidence
```
