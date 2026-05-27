# Enzyme Frontier Campaign

Status: draft v0

Use this campaign when one reaction step needs broad candidate mining and evidence-led compression.

## Goal

Expand from a reaction step into a candidate enzyme universe, then compress raw hits into a defensible shortlist.

## Required Outputs

- `candidate-universe/<step_id>.tsv`
- `candidate-funnels.tsv`
- `enzyme-draft-board.tsv`
- `candidate-sequence-ledger.tsv`
- `domain-annotation-ledger.tsv`
- `candidate-diversity-ledger.tsv`
- `candidate-graph-ledger.tsv`
- `evidence-event-ledger.tsv`
- `rejected-candidates.tsv`
- `candidate-ranking-ledger.tsv`
- `claim-ledger.md`

## Funnel

```text
raw hits
  -> quality-filtered hits
  -> domain-valid hits
  -> clustered representatives
  -> evidence-reviewed candidates
  -> shortlist
  -> final picks
```

## Evidence Lanes

- literature
- accession
- sequence similarity
- domain
- motif
- phylogeny
- structure
- substrate
- kinetics
- host fit
- red team

## Review Gate

No candidate advances to route stitching without:

- source organism
- accession or source pointer
- evidence class
- claim level
- rejection risk
- host-fit note
