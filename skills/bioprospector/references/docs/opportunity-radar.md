# BioProspector opportunity radar

Reviewed: 2026-08-30.

This page tracks external tools that may strengthen BioProspector campaigns.
It is a dated discovery index, not a compatibility promise or installation
list. None of these projects becomes a default dependency until it has a
ledger contract, a tool or provider preflight, a license and data-policy
review, and a compact output path.

## Changes verified in this review

| Project | Verified upstream change | BioProspector treatment |
| --- | --- | --- |
| [MMseqs2 18-8cc5c](https://github.com/soedinglab/MMseqs2/releases/tag/18-8cc5c) | July 2025 release with a new aligner, GPU and ARM64 improvements, and a GPU-database ordering change | Keep optional. Record the exact binary and database-build version; do not assume indices from older versions are interchangeable. |
| [DIAMOND 2.2.4](https://github.com/bbuchfink/diamond/releases/tag/v2.2.4) | July 2026 release with clustering, FASTA-processing, and distributed-workflow improvements | Keep optional. Search and clustering remain separate adapter contracts. |
| [nf-core/proteinfamilies 2.5.0](https://github.com/nf-core/proteinfamilies/releases/tag/2.5.0) | August 2026 release adds iterative family-generation work | Keep on the family-workflow lane. Normalize only compact family, HMM, and membership summaries. |
| [runpodctl 2.12.0](https://github.com/runpod/runpodctl/releases/tag/v2.12.0) | August 2026 release removes two automatic stop and terminate flags introduced by earlier versions | Keep provider commands out of tracked examples. Follow the current [runpodctl documentation](https://docs.runpod.io/runpodctl/overview) during an operator-reviewed run. |
| [cblaster 1.4.2](https://github.com/gamcil/cblaster/releases/tag/v1.4.2) | August 2026 release stores taxonomy information in remote-search results and reduces the search batch size | Record the search mode, database, and tool version before normalizing neighborhood summaries. |
| [BiG-SLiCE 2.0.2](https://github.com/medema-group/bigslice/releases/tag/v2.0.2) | August 2025 release adds antiSMASH 8 support | Record the caller, input format, database, and tool version before normalizing cluster summaries. |
| [Folddisco](https://github.com/steineggerlab/folddisco) | Public discontinuous structural-motif search project and 2026 publication | Radar only. Adoption needs a compact motif-hit adapter, control design, and a clear claim ceiling. |

## Adoption filter

- The item maps to a BioProspector ledger, stage contract, or package index.
- Tracked outputs can use IDs, checksums, summaries, citations, graph edges,
  public accessions, or placeholders. Exact runtime locations remain ignored.
- Raw reads, private sequences, full database mirrors, unrestricted FASTA dumps,
  model weights, full spectra, and full-text articles stay out of the repository.
- Claim boundary is explicit: planning, prioritization, reference context,
  target evidence, control evidence, or execution proof.
- Live execution has tool-command proof and provider/data-policy approval.

## Contract lanes

- Ledger schema hardening: Frictionless-style schemas and LinkML-ready semantic
  notes for the TSV contract layer.
- Supply-chain preflight: SBOM, vulnerability, signature, and provenance proof
  for provider images.
- Executable proof: exact commands, versions, database/model versions, and dry
  invocation evidence before paid compute.
- Review surface: candidate graph exports plus Quarto, marimo, Evidence.dev, or
  Streamlit reports driven by ledgers.

## Hosted design and tool backends

- Proto / Evo Design: `proto-tools` standardizes input, configuration, and output
  schemas for structure prediction, inverse folding, PLM scoring, alignment,
  annotation, retrieval, and sequence scoring. `proto-language` models design
  work as sequences, segments, constructs, generators, constraints, optimizers,
  and programs. Proto Bio MCP provides a hosted tool interface.
- BioProspector fit: map Proto tool schemas, runs, metrics, assets, and exports
  into `tool-execution-proof-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `structure-risk-ledger.tsv`,
  `sequence-search-plan-ledger.tsv`, and `run-output-package-ledger.tsv`.
- Primary sources: [Proto about](https://proto.evodesign.org/about),
  [proto-tools](https://github.com/evo-design/proto-tools),
  [proto-language](https://github.com/evo-design/proto-language), and
  [Proto Bio MCP](https://proto.evodesign.org/docs/mcp/introduction).

## Candidate expansion and compression

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

## Route, reaction, and host fit

- Route expansion and enzyme ranking: RetroRules, RetroBioCat, SelenzymeRF,
  Pickaxe, novoStoic, ChemEnzyRetroPlanner, BioNavi, EnzRetro, and
  ECREACT-style comparators.
- Reference-only route history: [RP2Paths 1.5.1](https://pypi.org/project/rp2paths/)
  was released on October 7, 2020. Use it to interpret older RetroPath2 outputs,
  not as a default. Do not conflate it with the separate
  [TraceLD RetroPath](https://github.com/TraceLD/retropath) project.
- Feasibility and host context: eQuilibrator, component-contribution, gapseq,
  COBRApy, StrainDesign, ModelSEEDpy, and KBase-style hosted summaries.
- Fallback review: ASKCOS or manual chemoenzymatic rescue ideas for blocked
  steps, recorded as degraded or alternate-route context.
- Relevant ledgers: `route-rule-ledger.tsv`, `thermodynamics-ledger.tsv`,
  `metabolic-model-ledger.tsv`, `strain-design-ledger.tsv`, and
  `chemoenzymatic-fallback-ledger.tsv`.

## Structure and active site

- Candidate-stage references after candidate compression: M-CSA,
  PROSITE/ProRule, P2Rank, EnzyMM, PyJess, BioLiP2, PLINDER, and PoseBusters.
- Keep Folddisco on the radar until it has a compact hit adapter and control
  contract.
- Defer to explicit design lanes: docking, free-energy, mutation design, and
  AF3-class consensus checks.
- Relevant ledgers: `structure-risk-ledger.tsv`,
  `candidate-intelligence-ledger.tsv`, `decoy-control-ledger.tsv`,
  `tool-execution-proof-ledger.tsv`, and `run-output-package-ledger.tsv`.
- Boundary: pocket, motif, pose, and design scores are prioritization
  intelligence, not biological validation.

## Genome, BGC, metagenome, and metabolomics context

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

## Literature and evidence extraction

- Candidate tools: PubTator 3.0 for biomedical entity and relation extraction;
  SciSpaCy and GROBID for local extraction; and Semantic Scholar, Europe PMC,
  and Crossref for citation metadata. Use PaperQA2-style citation-grounded
  summarization only after an operator approves source access.
- Relevant ledgers: `literature-search-ledger.tsv`,
  `literature-ledger.tsv`, `candidate-intelligence-ledger.tsv`,
  `evidence-event-ledger.tsv`, and `claim-ledger.md`.
- Boundary: store public source identifiers, citations, extracted entities,
  and short findings only. Do not store publisher PDFs, full-text dumps, or
  uncited summaries.

## Promotion rule

Move an item from this radar into a campaign only when the issue generator can
draft a bounded lane and preflight can validate the declared ledgers. If a tool
is useful but cannot yet return compact, joinable artifacts, keep it here.
