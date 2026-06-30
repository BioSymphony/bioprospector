# Enzyme Family Search Backbone

The default search backbone is layered. BioProspector should compress candidate
families before promoting individual enzymes.

## Default Order

1. Literature and accession seeds.
2. Curated databases such as Swiss-Prot or reviewed pathway resources.
3. MMseqs2, DIAMOND, BLAST+, and HMMER searches on approved public or local datasets.
4. Family-level clustering and motif/domain filtering.
5. Evidence review with claim levels and rejected classes preserved.
6. Structure-risk and host-fit lanes only for survivors.

## Family Sweep Ledger

`enzyme-family-sweep.tsv` records:

- seed accessions and family scope
- domain model and required motifs
- raw hit, cluster, and representative counts
- known activity references
- family-level risk and next lane

This keeps `enzyme-draft-board.tsv` focused on reviewed candidates rather than
thousands of raw hits.

## Predictor Role

CLEAN, CLEAN-Contact, EasIFA, protein language models, and structure-search
tools are evidence generators. They do not replace accession, motif, substrate,
host-fit, and red-team review.
