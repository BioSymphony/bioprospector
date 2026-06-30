# BioProspector Opportunity Radar

Refresh date: 2026-06-28.

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
  Streamlit reports driven by ledgers.

## Hosted Design And Tool Backends

- Proto / Evo Design: `proto-tools` standardizes Input / Config / Output
  schemas for structure prediction, inverse folding, PLM scoring, alignment,
  annotation, retrieval, and sequence scoring. `proto-language` models design
  work as sequences, segments, constructs, generators, constraints, optimizers,
  and programs. `proto-client` and Proto Bio MCP provide a hosted tool and
  optimization interface.
- BioProspector fit: map Proto tool schemas, runs, metrics, assets, and exports
  into `tool-execution-proof-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `structure-risk-ledger.tsv`,
  `sequence-search-plan-ledger.tsv`, and `run-output-package-ledger.tsv`.
- Primary sources: [Proto about](https://proto.evodesign.org/about),
  [proto-tools](https://github.com/evo-design/proto-tools),
  [proto-language](https://github.com/evo-design/proto-language),
  [proto-client](https://github.com/evo-design/proto-client), and
  [Proto Bio MCP](https://proto.evodesign.org/docs/mcp/introduction).

## Candidate Expansion And Compression

- Remote homology and diversity: HH-suite, PLMSearch/PLMAlign,
  ProteinCartography, EFI tools, MGnify, OrthoFinder, OMA, PROSITE, NCBI CDD,
  CATH-Gene3D, and M-CSA.
- Recent sequence and family candidates: MMseqs2-GPU for approved GPU search,
  nf-core/proteinfamilies for reproducible family/HMM workflows, and
  PLMSearch/PLMAlign for remote-homology ranking. Keep model caches and raw
  sequence stores outside the repo.
- Enzyme-function and kinetics candidates: CatPred, CataPro, ProKcat, ProtDETR,
  TopEC, EasIFA, CLEAN, and CLEAN-Contact. Treat outputs as votes for ranking
  and review, not target evidence by themselves.
- Relevant ledgers: `sequence-search-plan-ledger.tsv`,
  `candidate-sequence-ledger.tsv`, `domain-annotation-ledger.tsv`,
  `candidate-diversity-ledger.tsv`, `candidate-graph-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `target-evidence-ledger.tsv`, and
  `claim-ledger.md`.
- Boundary: ranking and evidence compression only until target evidence,
  controls, and self-check gates support stronger language.

## Route, Reaction, And Host Fit

- Route expansion and enzyme ranking: RetroRules, RetroBioCat, SelenzymeRF,
  Pickaxe, novoStoic, ChemEnzyRetroPlanner, BioNavi, EnzRetro, and
  ECREACT-style comparators.
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

- BGC and genome context: antiSMASH 8, antiSMASH DB, plantiSMASH 2, GECCO,
  BiG-SCAPE/BiG-SLiCE/BiG-FAM, MIBiG 4, GATOR-GC, BGCFlow, lsaBGC, FunBGCeX,
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

## Literature And Evidence Extraction

- Candidate tools: PubTator 3.0 for biomedical entity/relation extraction,
  SciSpaCy and GROBID for local extraction, Semantic Scholar / Europe PMC /
  Crossref for citation metadata, and PaperQA2-style citation-grounded
  summarization when source access is operator-approved.
- Relevant ledgers: `literature-search-ledger.tsv`,
  `literature-ledger.tsv`, `candidate-intelligence-ledger.tsv`,
  `evidence-event-ledger.tsv`, and `claim-ledger.md`.
- Boundary: store identifiers, citations, extracted entities, short findings,
  and source pointers only. Do not store publisher PDFs, full-text dumps, or
  generated answer text without source-linked evidence rows.

## Promotion Rule

Move an item from this radar into a campaign only when the issue generator can
draft a bounded lane and preflight can validate the declared ledgers. If a tool
is useful but cannot yet return compact, joinable artifacts, keep it here.
