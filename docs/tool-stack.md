# Tool knowledge base

Use this reference to select tools for a research question and identify useful
follow-up calls. The [integration guide](TOOL_INTEGRATIONS.md) lists supported
result formats; the [dated tool review](opportunity-radar.md) covers proposed
additions and evaluation questions.

## Choose the next tool

| You have | You need | Tools to consider |
| --- | --- | --- |
| A reference protein | Related sequences | DIAMOND, MMseqs2, BLAST+ |
| Sequence hits | Family and domain evidence | HMMER with Pfam or another suitable profile database |
| An available structure | Structural neighbors | Foldseek |
| Candidate genome locations | Neighboring-gene context | cblaster, antiSMASH, MIBiG |
| Conflicting annotations | Source records and published evidence | UniProt, Europe PMC, literature search |
| A reaction question | Curated reaction references | Rhea; route-planning references listed in this guide |

Your agent runs tools through its own shell, API, or MCP access. Before a call,
check the installed version, required inputs, database or model, and expected
output. Pass identifiers and source references between calls; retrieve sequences,
structures, or coordinates in the permitted environment when the next tool
requires them. Use the returned evidence to revise the search or compare candidates.

Catalog entries describe research options. Dedicated import support is listed
in the integration guide; other outputs need mapping before local processing.

## Search and clustering

- [MMseqs2 and MMseqs2-GPU](https://github.com/soedinglab/MMseqs2):
  large-scale sequence search and clustering.
- [DIAMOND](https://github.com/bbuchfink/diamond): fast protein and translated
  sequence search, plus clustering workflows that need a separate output
  contract.
- [HMMER](https://www.hmmer.org/): profile HMM and domain-family searches.
- [NCBI BLAST+ documentation](https://blast.ncbi.nlm.nih.gov/doc/blast-help/):
  compatibility and local exact BLAST workflows.
- [nf-core/proteinfamilies](https://github.com/nf-core/proteinfamilies),
  HH-suite, PLMSearch, and PLMAlign: family compression and remote-homology
  exploration when outputs are reduced to compact summaries.
- [NCBI ElasticBLAST](https://blast.ncbi.nlm.nih.gov/doc/elastic-blast/):
  reviewed cloud-near-data escalation for official NCBI BLAST databases.

## Function and structure evidence

- ProTrek, GOAnnotator, and Metagenomic-DeepFRI: optional retrieval and
  annotation candidates. See the [dated review](opportunity-radar.md) for
  sources, license boundaries, and evaluation requirements.
- LAFA, CAFA-evaluator-PK, and Conformal Protein Retrieval: evaluation and
  calibration references. Record time splits, ontology versions, and
  calibration populations before comparing predictors.

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

## Literature and Source Records

| Need | Tools | Record |
| --- | --- | --- |
| Paper metadata, versions, and corrections | [Europe PMC](https://europepmc.org/RestfulWebService), [bioRxiv API](https://api.biorxiv.org/), and [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api) | Source ID, version, access date, and any update notice |
| Text, tables, or bibliographies | Docling, MinerU, and GROBID | Parser version, source locator, and extraction status |
| Entities mentioned in text | PubTator 3.0, Europe PMC Annotations, and SciSpaCy | Entity ID and source locator |
| Public assembly and taxonomy records | [NCBI Datasets](https://github.com/ncbi/datasets/releases/tag/v18.41.1) | Versioned accession and retrieval date |

## Host Models and Workflow Records

- COBRApy, CarveMe, ModelSEEDpy/KBase, cameo, and memote provide host-model
  and model-quality checks. Record model versions and assumptions.
- Nextflow, Snakemake, and Flowcept record workflow and artifact metadata.
  See the [tool review](opportunity-radar.md#workflow-provenance) for exporter
  and profile versions.

## Result mapping

Record tool and model versions, database releases, source IDs, and the meaning
of each score with the results. Similarity hits and predictions contribute
evidence; they do not establish experimental function.

For custom adapters, `tool_registry_ledger` and `adapter_contract_ledger` are
optional schema entries. Add their paths and TSV files to the campaign manifest
before preflight. Normalize compact results into `evidence-event-ledger.tsv`
and retain the command, version, and execution status in
`tool-execution-proof-ledger.tsv`. See the [integration guide](TOOL_INTEGRATIONS.md)
for output mapping.
