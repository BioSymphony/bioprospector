# Enzyme family search backbone

Use a layered search order. Compress candidate families before reviewing
individual enzymes.

## Default order

1. Literature and accession seeds.
2. Curated databases such as Swiss-Prot or reviewed pathway resources.
3. MMseqs2, DIAMOND, BLAST+, and HMMER searches on approved public or local datasets.
4. Family-level clustering and motif/domain filtering.
5. Evidence review with claim levels and rejected classes preserved.
6. Structure-risk and host-fit lanes only for survivors.

## Family sweep ledger

`enzyme-family-sweep.tsv` records:

- seed accessions and family scope
- domain model and required motifs
- raw hit, cluster, and representative counts
- known activity references
- family-level risk and next lane

This keeps `enzyme-draft-board.tsv` focused on reviewed candidates rather than
thousands of raw hits.

## Predictor role

CLEAN, CLEAN-Contact, EasIFA, protein language models, and structure-search
tools provide ranking signals. Combine their outputs with accession, motif,
substrate, host-fit, and red-team review.
