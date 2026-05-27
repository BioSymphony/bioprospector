# BioProspector Opportunity Radar

Refresh date: 2026-05-23.

This is the public expansion backlog for BioProspector. Items here are not
default campaign dependencies. Promote one only after it has a ledger contract,
tool/API/provider preflight, license and data-policy review, and a compact
output story.

## Adoption Filter

- The item maps to a BioProspector ledger, stage contract, or package index.
- Outputs can be represented as IDs, checksums, summaries, citations, graph
  edges, or runtime pointers.
- Raw reads, private sequences, full database mirrors, unrestricted FASTA dumps,
  model weights, full spectra, and full-text articles stay out of the repo.
- Claim boundary is explicit: planning, prioritization, reference context,
  target evidence, control evidence, or execution proof.
- Live execution has tool-command proof and provider/data-policy approval.

## Contract Lanes

- Ledger schema hardening: Frictionless-style schemas and LinkML-ready semantic
  notes for the TSV contract layer.
- Supply-chain preflight: SBOM, vulnerability, signature, and provenance proof
  for provider images.
- Executable proof: exact commands, versions, database/model versions, and dry
  invocation evidence before paid compute.
- Review surface: candidate graph exports plus Quarto, marimo, Evidence.dev, or
  Streamlit dossiers driven by ledgers.

## Candidate Expansion And Compression

- Remote homology and diversity: HH-suite, PLMSearch/PLMAlign,
  ProteinCartography, EFI tools, MGnify, OrthoFinder, OMA, PROSITE, NCBI CDD,
  CATH-Gene3D, and M-CSA.
- Relevant ledgers: `sequence-search-plan-ledger.tsv`,
  `candidate-sequence-ledger.tsv`, `domain-annotation-ledger.tsv`,
  `candidate-diversity-ledger.tsv`, `candidate-graph-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `target-evidence-ledger.tsv`, and
  `claim-ledger.md`.
- Boundary: ranking and evidence compression only until target evidence,
  controls, and self-check gates support stronger language.

## Route, Reaction, And Host Fit

- Route expansion and enzyme ranking: RetroRules, RetroBioCat, SelenzymeRF,
  Pickaxe, novoStoic, and ECREACT-style comparators.
- Feasibility and host context: eQuilibrator, component-contribution, gapseq,
  COBRApy, StrainDesign, ModelSEEDpy, and KBase-style hosted summaries.
- Fallback review: ASKCOS or manual chemoenzymatic rescue ideas for blocked
  steps, recorded as degraded or alternate-route context.
- Relevant ledgers: `route-rule-ledger.tsv`, `thermodynamics-ledger.tsv`,
  `metabolic-model-ledger.tsv`, `strain-design-ledger.tsv`, and
  `chemoenzymatic-fallback-ledger.tsv`.

## Structure And Active Site

- Adopt after candidate compression: M-CSA, PROSITE/ProRule, P2Rank, EnzyMM,
  PyJess, BioLiP2, PLINDER, and PoseBusters.
- Defer to explicit design lanes: docking, free-energy, mutation design, and
  AF3-class consensus checks.
- Relevant ledgers: `structure-risk-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `decoy-control-ledger.tsv`,
  `tool-execution-proof-ledger.tsv`, and `run-output-package-ledger.tsv`.
- Boundary: pocket, motif, pose, and design scores are prioritization
  intelligence, not biological validation.

## Genome, BGC, Metagenome, And Metabolomics Context

- BGC and genome context: plantiSMASH, GECCO, BiG-SLiCE/BiG-FAM, BGCFlow,
  cblaster, clinker, and related cluster/neighborhood summaries.
- Metagenome context: MAG quality, contig pointers, taxonomy summaries, and
  decoy-control joins without raw reads or MAG archives.
- Metabolomics handoff: MZmine, GNPS2, matchms, and MS2Query contracts with
  explicit upload policy before any hosted/private spectra work.
- Source priors: LOTUS and Natural Products Atlas as reference context with
  license boundaries.
- Relevant ledgers: `bgc-context-ledger.tsv`,
  `metagenome-context-ledger.tsv`, `mag-quality-ledger.tsv`,
  `metabolomics-evidence-ledger.tsv`, `compound-source-ledger.tsv`, and
  `eukaryotic-annotation-ledger.tsv`.

## Promotion Rule

Move an item from this radar into a campaign only when the issue generator can
draft a bounded lane and preflight can validate the declared ledgers. If a tool
is useful but cannot yet return compact, joinable artifacts, keep it here.
