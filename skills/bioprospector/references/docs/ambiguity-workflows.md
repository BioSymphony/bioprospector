# Ambiguity and dark-step workflows

BioProspector must handle steps where the enzyme, gene, module, or even the
true reaction decomposition is unknown. The Dark Step Resolver lane is for these
cases.

## When to use

- A pathway step is chemically plausible but no gene is known.
- Several enzyme classes could perform the transformation.
- A single apparent step may hide multiple transformations.
- Transport, cofactors, host-native promiscuity, or spontaneous chemistry may explain the observation.
- Source-organism genome, transcriptome, metabolite, or tissue clues exist but do not directly name a gene.

## Required Outputs

Use compact ledgers, not freeform speculation:

- `pathway-inference-ledger.tsv`: hypothesis tree, assumptions, counterevidence, claim level, and decision.
- `unknown-gene-hypothesis-ledger.tsv`: single-gene and multi-gene hypotheses, evidence for/against, next discriminating step.
- `enzyme-family-sweep.tsv`: candidate enzyme-class searches created from chemistry-first reasoning.
- `assay-handoff-ledger.tsv`: non-protocol next evidence needed when computation cannot decide.

## Agent pattern

1. Decompose the transformation into possible hidden substeps.
2. Infer plausible enzyme classes from chemistry before widening homology search.
3. Compare single-gene, multi-gene, transport, cofactor, and host-native explanations.
4. Preserve unusual candidates separately from standard homolog hits.
5. Record counterevidence and the cheapest discriminating next step.

Dark Step Resolver outputs are hypotheses. They do not validate production,
activity, or pathway completion.
