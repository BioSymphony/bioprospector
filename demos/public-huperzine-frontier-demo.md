# Public Huperzine A Frontier Demo Walkthrough

## What This Proves

- BioProspector can keep a useful campaign open when the route is not fully
  resolved.
- Dark-step lanes can track unknown chemistry, possible multi-gene modules,
  hidden substeps, and source-context ambiguity without pretending the pathway
  is complete.
- Candidate-family sweeps can stay useful for ranking and follow-up planning
  without storing raw sequences, BLAST dumps, private paths, or provider
  artifacts.
- Claim ceilings can be tested on a target where users naturally expect a
  complete answer, which makes it a good public stress case.

## Claim Ceiling

The demo establishes dark-step hypotheses, source-context lanes, candidate
families, metadata-only atlas planning, and a claim-bounded dossier at
planning maturity. Production claims, complete-pathway claims, final enzyme
identification, constructs, protocols, assays, and live tool runs (BLAST,
MMseqs2, HMMER, Foldseek, RunPod, AWS, public APIs, Symphony) require
operator evidence joined through the live closeout path and institutional
review. See [`BIOSAFETY.md`](../BIOSAFETY.md) and
[`NON_CLAIMS.md`](../NON_CLAIMS.md).

## Walkthrough

```mermaid
flowchart LR
  A["unresolved step"] --> B["dark-step hypotheses"]
  B --> C["source context"]
  C --> D["candidate-family sweeps"]
  D --> E["metadata-only atlas plan"]
  E --> F["claim ceiling"]
```

1. Inspect `skills/bioprospector/examples/huperzine-frontier-public-v0/target-contract.json`.
2. Review `unknown-step-ledger.tsv` and `unknown-gene-hypothesis-ledger.tsv`
   before looking at candidate families.
3. Review `pathway-inference-ledger.tsv` and `organism-sample-ledger.tsv` for
   source-context and comparator boundaries.
4. Run campaign preflight with local artifact scanning.
5. Run the planning-friendly contract self-check.
6. Verify `claim-ledger.md` still blocks production, complete-pathway, and
   host-validation claims.

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0

python3 skills/bioprospector/scripts/bioprospector_candidate_package.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/candidate-packages/huperzine-frontier-public-v0

python3 skills/bioprospector/scripts/bioprospector_dossier_export.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --sidecar-dir .runtime/candidate-packages/huperzine-frontier-public-v0 \
  --out .runtime/dossiers/huperzine-frontier-public-v0.md
```

## Expected Outputs

- Validated public planning ledgers.
- A useful unresolved-route example for dark-step, source-context, and
  candidate-family planning.
- Metadata-only atlas and candidate-package sidecars under ignored `.runtime/`.
- A compact dossier under `.runtime/dossiers/huperzine-frontier-public-v0.md`.
- All artifacts land under ignored `.runtime/`. Live execution, raw sequence
  storage, and biological validation claims remain with the operator's
  live closeout path.
