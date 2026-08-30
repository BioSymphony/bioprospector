# Tool stack reference

This planning index maps external tools to BioProspector evidence roles. The
repository does not install or execute them.

This is a discovery index, not a supported-version matrix. Before operator-run
use, verify the primary source and record the tool version, database, model, or
rule-set release, access date, operating mode, and output schema in the campaign
ledgers. See the [`opportunity radar`](opportunity-radar.md) for dated upstream
reviews and integration candidates.

`tool_registry_ledger` and `adapter_contract_ledger` are optional schema
contracts. A campaign that uses them must add both paths to the manifest's
`ledgers` object and provide the TSV files before preflight. The campaign then
normalizes compact output into `evidence-event-ledger.tsv`. Tool execution proof belongs in
`tool-execution-proof-ledger.tsv` and cannot replace execution artifacts or
claim-audit gates.

## Search and clustering

- [MMseqs2 and MMseqs2-GPU](https://github.com/soedinglab/MMseqs2):
  large-scale sequence search and clustering.
- [DIAMOND](https://github.com/bbuchfink/diamond): fast protein and translated
  sequence search, plus clustering workflows that need a separate output
  contract.
- [HMMER](http://hmmer.org/): profile HMM and domain-family searches.
- [NCBI BLAST+ documentation](https://blast.ncbi.nlm.nih.gov/doc/blast-help/):
  compatibility and local exact BLAST workflows.
- [nf-core/proteinfamilies](https://github.com/nf-core/proteinfamilies),
  HH-suite, PLMSearch, and PLMAlign: family compression and remote-homology
  exploration when outputs are reduced to compact summaries.
- [NCBI ElasticBLAST](https://blast.ncbi.nlm.nih.gov/doc/elastic-blast/):
  reviewed cloud-near-data escalation for official NCBI BLAST databases.

## Function and structure evidence

- CLEAN, CLEAN-Contact, ProtDETR, TopEC, and related EC predictors:
  function-evidence votes for enzyme candidates.
- EasIFA: active-site evidence.
- CatPred, CataPro, ProKcat, and related kinetic-parameter predictors:
  ranking context after substrate and sequence scope are explicit.
- ESM/ProtT5/ProGen-style protein language models: embeddings or exploratory scoring with license/version caveats.
- Foldseek: structure-neighborhood evidence when structures or public predicted
  structures are available.
- [Folddisco](https://github.com/steineggerlab/folddisco): discontinuous
  structural-motif search candidate for active-site review. Keep it on the
  opportunity radar until a compact output adapter and control contract exist.

## Route and reaction knowledge

- [Rhea](https://www.rhea-db.org/): curated biochemical reaction knowledge.
  Rhea updates every eight weeks. Record the Rhea release and access date.
- [RetroPath2](https://github.com/brsynth/RetroPath2-wrapper) and
  [RP2Paths](https://pypi.org/project/rp2paths/): reference-only
  route-enumeration tools. Capture the executable, rule-set snapshot, and
  output schema before operator-run use.
- [RetroRules](https://retrorules.org/): reaction-rule reference for route
  enumeration. Record the selected rule set, source reaction identifiers, and
  query date.
- Selenzyme: enzyme selection for target reactions.
- RetroBioCat, ChemEnzyRetroPlanner, BioNavi, and EnzRetro: biocatalytic or
  hybrid route-planning references that need route-rule and enzyme evidence
  contracts before campaign use.
- [Galaxy-SynBioCAD](https://galaxy-synbiocad.org/static/welcome.html): route
  and pathway-analysis reference only. Genetic-design, plasmid, assembly, and
  automation workflows are outside this public repository's scope.

## Genome context

- antiSMASH, antiSMASH DB, plantiSMASH, and MIBiG. Record caller and reference
  database releases together.
- [cblaster](https://github.com/gamcil/cblaster).
- GATOR-GC, BGCFlow, lsaBGC, and FunBGCeX for targeted or comparative BGC lanes.
- GECCO and DeepBGC.
- BiG-SCAPE and BiG-SLiCE: cluster-family summaries. Record the tool version,
  input caller and version, and reference release before normalizing compact
  outputs.

## Host and provenance

- COBRApy, CarveMe, ModelSEEDpy/KBase, cameo, and memote-style QA for host feasibility after route candidates exist.
- PubTator 3.0, SciSpaCy, GROBID, Semantic Scholar, Europe PMC, and PaperQA2
  for citation and entity extraction when source access and full-text boundaries
  are explicit.
- Nextflow, nf-core, nf-prov, Workflow Run RO-Crate, and Snakemake: workflow and
  provenance references. This repository does not ship runner integrations for them.

All tool outputs are evidence inputs. The claim ledger, provenance records, and
claim-audit gates determine the language used for each result.
