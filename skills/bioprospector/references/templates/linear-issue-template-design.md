# Curated Template Design

## Goal

Compress raw sequence/domain/literature hits into a dry-lab template set that a
pathway stitcher can inspect without reading raw BLAST output.

## Required Artifacts

- `template-design-ledger.tsv`
- `candidate-sequence-ledger.tsv`
- `domain-annotation-ledger.tsv`
- `candidate-diversity-ledger.tsv`
- literature citation pointers for optimization notes

## Acceptance Criteria

- Template rows join to `enzyme-draft-board.tsv` candidates and pathway steps.
- Each pathway step has no more than 50 curated template rows.
- Conservative, middle-ground, out-there, and frontier-planning bins are kept distinct.
- Rows record AA-sequence pointers, source accession, signal peptide/localization calls, multimer state, host PTM watchouts, fusion/minimization potential, and literature optimizations.
- Planning-only rows do not claim yeast expression, product chemistry, or wet-lab validation.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json
```
