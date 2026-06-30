# Tool Stack Reference

This is a planning reference. These tools are not installed or executed by the
repo scaffold.

When a tool is used, represent it through `tool-registry-ledger.tsv` and
`adapter-contract-ledger.tsv`, then normalize compact output into
`evidence-event-ledger.tsv`. Tool execution proof belongs in
`tool-execution-proof-ledger.tsv` and cannot replace execution artifacts or
claim-audit gates.

## Search And Clustering

- MMseqs2 and MMseqs2-GPU: large-scale sequence search and clustering.
- DIAMOND: fast protein and translated sequence search.
- HMMER: profile HMM and domain-family searches.
- BLAST+: compatibility and local exact BLAST workflows.
- nf-core/proteinfamilies, HH-suite, PLMSearch, and PLMAlign: family compression
  and remote homology exploration when outputs are reduced to compact summaries.
- NCBI ElasticBLAST: reviewed cloud-near-data BLAST escalation for official NCBI database scale.

## Function And Structure Evidence

- CLEAN, CLEAN-Contact, ProtDETR, TopEC, and related EC predictors:
  function-evidence votes for enzyme candidates.
- EasIFA: active-site evidence.
- CatPred, CataPro, ProKcat, and related kinetic-parameter predictors:
  ranking context after substrate and sequence scope are explicit.
- ESM/ProtT5/ProGen-style protein language models: embeddings or exploratory scoring with license/version caveats.
- Foldseek: structure-neighborhood evidence when structures or public predicted structures are available.

## Route And Reaction Knowledge

- Rhea: curated biochemical reaction knowledge.
- RetroPath2, RP2Paths, and RetroRules: retrobiosynthesis and route enumeration.
- Selenzyme: enzyme selection for target reactions.
- RetroBioCat, ChemEnzyRetroPlanner, BioNavi, and EnzRetro: biocatalytic or
  hybrid route-planning references that need route-rule and enzyme evidence
  contracts before campaign use.
- Galaxy-SynBioCAD: pathway-design workflow environment.

## Genome Context

- antiSMASH, antiSMASH DB, plantiSMASH, and MIBiG.
- cblaster.
- GATOR-GC, BGCFlow, lsaBGC, and FunBGCeX for targeted or comparative BGC lanes.
- GECCO and DeepBGC.
- BiG-SCAPE and BiG-SLiCE.

## Host And Provenance

- COBRApy, CarveMe, ModelSEEDpy/KBase, cameo, and memote-style QA for host feasibility after route candidates exist.
- PubTator 3.0, SciSpaCy, GROBID, Semantic Scholar, Europe PMC, and PaperQA2
  for citation and entity extraction when source access and full-text boundaries
  are explicit.
- Nextflow, nf-core, nf-prov, Workflow Run RO-Crate, and Snakemake for future live execution/provenance.

All tool outputs are evidence inputs. BioProspector claim levels, provenance,
and red-team review decide how the evidence can be used.
