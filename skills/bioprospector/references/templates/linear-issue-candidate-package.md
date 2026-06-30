# Candidate Package

## Goal

Package reviewed candidates into graph, sequence, diversity, domain, structure
risk, and dossier-ready summaries without upgrading claims.

## Required Artifacts

- `candidate-sequence-ledger.tsv`
- `domain-annotation-ledger.tsv`
- `candidate-diversity-ledger.tsv`
- `candidate-graph-ledger.tsv`
- `run-output-package-ledger.tsv`

## Acceptance Criteria

- Every package row joins back to a campaign step, candidate, source pointer, checksum/version, and claim level.
- Graph edges distinguish evidence class, reference context, controls, and target evidence.
- Package summaries include rejected or parked candidates where they affect route decisions.
- Candidate packages support review and prioritization only; they do not prove enzyme function, host production, or pathway completion.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json
```
