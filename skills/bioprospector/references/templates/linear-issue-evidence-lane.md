# Evidence Lane

## Goal

Turn a wide or frontier search need into bounded evidence-collection work with
explicit inputs, controls, budgets, and claim boundaries.

## Required Artifacts

- `sequence-search-plan-ledger.tsv` or lane-specific search plan rows
- `candidate-funnels.tsv`
- `enzyme-draft-board.tsv`
- `rejected-candidates.tsv`
- `decoy-control-ledger.tsv` when promotion could follow a wide/frontier search

## Acceptance Criteria

- The lane records search width, query scope, expected outputs, and stop/continue criteria.
- Raw all-hit output stays outside the repo; only compact summaries, IDs, checksums, and pointers are retained.
- Candidate promotion is blocked until target evidence, decoy controls, execution artifacts, and self-check gates apply.
- Reference database hits remain reference context unless joined to declared target organism or sample evidence.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-decoy-controls
```
