# Tool Stack Reference

This is a planning reference. These tools are not installed or executed by the
repo scaffold.

When a tool is used, represent it through `tool-registry-ledger.tsv` and
`adapter-contract-ledger.tsv`, then normalize compact output into
`evidence-event-ledger.tsv`. Tool execution proof belongs in
`tool-execution-proof-ledger.tsv` and cannot replace execution artifacts or
claim-audit gates.

## Search And Clustering

- MMseqs2: large-scale sequence search and clustering.
- DIAMOND: fast protein and translated sequence search.
- HMMER: profile HMM and domain-family searches.
- BLAST+: compatibility and local exact BLAST workflows.
- NCBI ElasticBLAST: reviewed cloud-near-data BLAST escalation for official NCBI database scale.

## Function And Structure Evidence

- CLEAN and CLEAN-Contact: EC/function evidence for enzyme candidates.
- EasIFA: active-site evidence.
- ESM/ProtT5/ProGen-style protein language models: embeddings or exploratory scoring with license/version caveats.
- Foldseek: structure-neighborhood evidence when structures or public predicted structures are available.

## Route And Reaction Knowledge

- Rhea: curated biochemical reaction knowledge.
- RetroPath2, RP2Paths, and RetroRules: retrobiosynthesis and route enumeration.
- Selenzyme: enzyme selection for target reactions.
- Galaxy-SynBioCAD: pathway-design workflow environment.

## Genome Context

- antiSMASH and plantiSMASH.
- cblaster.
- GECCO and DeepBGC.
- BiG-SCAPE, BiG-SLiCE, and MIBiG.

## Host And Provenance

- COBRApy, CarveMe, ModelSEEDpy/KBase, cameo, and memote-style QA for host feasibility after route candidates exist.
- Nextflow, nf-core, nf-prov, Workflow Run RO-Crate, and Snakemake for future live execution/provenance.

All tool outputs are evidence inputs. BioProspector claim levels, provenance,
and red-team review decide how the evidence can be used.
