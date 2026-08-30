# BioProspector Demo Notes

Demo docs are narrative walkthroughs. Generated artifacts land under ignored
`.runtime/`. Provider launches, tracker writes, database downloads, and
Symphony starts happen only on operator-approved live commands.

- `public-nootkatone-demo.md`: public scaffold walkthrough for the tracked frontier example.
- `public-huperzine-frontier-demo.md`: public dark-step and source-context walkthrough.
- `expected-outputs/`: tiny checked-in output snapshots for users who want to
  inspect the artifact shape before running commands.
- `sample-inputs/`: synthetic BLAST6, DIAMOND, MMseqs, and HMMER inputs that
  feed `bioprospector_evidence_ingest.py` to produce populated candidate,
  sequence, graph, domain, and evidence-event ledgers under `.runtime/`.
- Run `make capabilities` to generate and audit public demo issue drafts,
  dossiers, rankings, and GeneCluster contract artifacts under ignored
  `.runtime/`.
