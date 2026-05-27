# Candidate Intelligence

## Goal

Capture ranking-useful public evidence and sequence interpretation for
candidates without turning the lane into docking, assay design, construct
design, or biological validation.

## Required Artifacts

- `candidate-intelligence-ledger.tsv`
- `literature-search-ledger.tsv`
- `literature-ledger.tsv`
- `candidate-sequence-ledger.tsv` and `domain-annotation-ledger.tsv` when sequence-derived calls are used
- `provider-launch-preflight-ledger.tsv` and `tool-execution-proof-ledger.tsv` before live predictors or APIs

## Acceptance Criteria

- Publicly reported reference enzymes, variant annotations, motifs, cofactors, oligomer state, localization, PTM/glycosylation, and signal/transit/TM watchouts are captured with source scope and confidence.
- PubMed, Europe PMC, Semantic Scholar, PubTator/SciSpaCy, approved GROBID extraction, and optional PaperQA2 summaries store identifiers and compact findings only.
- Public literature, predictors, and close-canonical-match inferences remain prioritization intelligence unless joined to target evidence and audited.
- No full-text dumps, private sequences, raw search outputs, docking archives, assay protocols, or construct recipes are stored in the repo.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json
```
