# Host Fit And Structure Risk

Host and structure lanes keep BioProspector from recommending routes that look
good only as isolated enzyme lists.

## Host Comparison

`host-comparison-ledger.tsv` compares host options by:

- expression burden
- precursor fit
- compartment fit
- toxicity
- analytics and product recovery fit
- verdict

Yeast can remain the default public demo host, but future campaigns may compare
plant transient expression, bacteria, cell-free systems, or other chassis when
that changes route feasibility.

## Structure Risk

`structure-risk-ledger.tsv` records:

- structure source and confidence
- active-site residue support
- cofactor or membrane risk
- substrate-access risk
- oligomerization risk
- claim boundary and verdict

This lane is triage only. Do not bulk-predict structures, run docking at scale,
or copy AlphaFold caches, PDB bundles, model weights, or docking archives into
the repo.
