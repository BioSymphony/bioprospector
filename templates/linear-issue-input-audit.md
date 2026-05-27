# Input Audit Before Questions

## Goal

Read manifest, target contract, and ledgers before asking the operator anything.

## Required Artifacts

- `input-audit-ledger.tsv`
- input-audit JSON summary
- explicit `missing_operator_items`

## Acceptance Criteria

- Known inputs are summarized first.
- Only explicit missing operator items are escalated.
- Non-blocking uncertainties are passed to operator intake instead of becoming broad questions.
- No downloads, remote queries, credentials, or raw biological data are requested from this issue.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_input_audit.py --campaign path/to/campaign-manifest.json
```
