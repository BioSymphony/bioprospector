# Sequence Search Contract

## Goal

Define BLAST, DIAMOND, MMseqs2, HMMER, or profile-search work as a resumable
ledger-producing stage instead of a raw hit dump.

## Required Artifacts

- `sequence-search-plan-ledger.tsv`
- `query-set-ledger.tsv`
- `candidate-sequence-ledger.tsv`
- `domain-annotation-ledger.tsv`
- `execution-artifact-ledger.tsv` for real runs

## Acceptance Criteria

- Query scope, database scope, max hits, budget, approval status, and output expectations are explicit.
- Sequence pointers, checksums, accession IDs, and compact domain summaries are retained; raw FASTA dumps and database mirrors are not.
- Mock or dry-run rows carry `mock_tools=true` or `dry_run=true` and cannot satisfy real evidence gates.
- Candidate claims remain hypothesis/reference/context until target evidence, decoy controls, execution artifacts, and L5 audit apply.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-real-execution
```
