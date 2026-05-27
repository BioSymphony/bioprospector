# Sample Tool Inputs

Tiny synthetic input files for the `bioprospector_evidence_ingest` round trip.
They show the file shapes BioProspector accepts as compact tool output, so an
agent (or operator) can run the ingest and produce populated candidate,
sequence, graph, domain, and evidence-event ledgers without a live search.

All accessions and query IDs in these files are synthetic. They look like real
sequence database hits to demonstrate the shape; treat them as illustrations,
not biological evidence.

## Files

| File | Format | What it shows |
| --- | --- | --- |
| `example.blast6.tsv` | `blast6` | 12-column NCBI BLAST tabular output for one query against an LDC/ODC-like family |
| `example.diamond.tsv` | `diamond` | Same 12-column shape as DIAMOND would emit, for an oxidoreductase-like family |
| `example.mmseqs.tsv` | `mmseqs` | Same 12-column shape as MMseqs would emit, for a mixed-module dark step |
| `example.hmmer.domtblout` | `hmmer-domtbl` | HMMER `--domtblout` lines for Pfam-style domain hits |

## Run The Ingest

From the repository root:

```bash
python3 skills/bioprospector/scripts/bioprospector_evidence_ingest.py \
  --hits demos/sample-inputs/example.blast6.tsv \
  --out .runtime/sample-ingest/blast6 \
  --step-id S001 \
  --format blast6

python3 skills/bioprospector/scripts/bioprospector_evidence_ingest.py \
  --hits demos/sample-inputs/example.diamond.tsv \
  --out .runtime/sample-ingest/diamond \
  --step-id S002 \
  --format diamond

python3 skills/bioprospector/scripts/bioprospector_evidence_ingest.py \
  --hits demos/sample-inputs/example.mmseqs.tsv \
  --out .runtime/sample-ingest/mmseqs \
  --step-id S005 \
  --format mmseqs

python3 skills/bioprospector/scripts/bioprospector_evidence_ingest.py \
  --hits demos/sample-inputs/example.hmmer.domtblout \
  --out .runtime/sample-ingest/hmmer \
  --step-id S001 \
  --format hmmer-domtbl
```

## What You Get

The BLAST6, DIAMOND, and MMseqs inputs each produce:

- `candidate-funnels.tsv`
- `enzyme-draft-board.tsv`
- `candidate-sequence-ledger.tsv`
- `candidate-graph-ledger.tsv`
- `evidence-event-ledger.tsv`
- `target-evidence-ledger.tsv`

The HMMER domtblout input produces:

- `domain-annotation-ledger.tsv`
- `evidence-event-ledger.tsv`

These are the populated ledgers an agent would join into a candidate
package, Pareto ranking, and dossier. The same ingest accepts real tool
output from a RunPod or HPC search; the file shape is the contract.

## Claim Ceiling

These ledgers carry sequence-similarity and domain-membership evidence at
the ingest level. They are planning evidence, not biological validation.
Promotion past `hypothesis` requires the target-evidence, decoy-control,
and execution-artifact gates documented in
[`../../docs/no-false-success-gates.md`](../../docs/no-false-success-gates.md).
