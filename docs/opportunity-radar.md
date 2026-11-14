# BioProspector Tool Review

Reviewed November 13, 2026. Use these external tools and studies to plan
evaluations. See the [integration guide](TOOL_INTEGRATIONS.md) for supported
formats.

## AI annotation, retrieval, and evaluation

| Tool and dated source | Useful output | Decision and limitation |
| --- | --- | --- |
| [ProTrek](https://github.com/westlake-repl/ProTrek); [paper, 2025-10-02](https://doi.org/10.1038/s41587-025-02836-0) | Sequence/structure/text retrieval scores and public reference IDs | Evaluate for candidate graph and diversity summaries. MIT code; review each model and index license. Similarity scores do not establish function. Keep embeddings and search databases external. |
| [GOAnnotator](https://github.com/ZhuLab-Fudan/GOAnnotator); [issue, 2025-07-15](https://doi.org/10.1093/bioinformatics/btaf199) | Retrieved PMIDs, proposed GO terms, and scores | Evaluate for literature-linked function votes. Apache-2.0 code; checkpoint terms need separate review. Require the 2026-07-02 code/checkpoint correction, pin the PubMed index, and retain each supporting citation. |
| [Metagenomic-DeepFRI](https://github.com/Tomasz-Lab/Metagenomic-DeepFRI); [preprint, 2026-04-29](https://doi.org/10.64898/2026.04.27.720983) | GO predictions with structural-template provenance | Evaluate as an additional function-vote source. BSD-3-Clause pipeline; upstream models and databases have separate terms. Annotation coverage does not measure accuracy. Keep template coverage and model scores with each vote. |
| [Conformal Protein Retrieval](https://github.com/ronboger/conformal-protein-retrieval); [paper, 2025-01-02](https://doi.org/10.1038/s41467-024-55676-y) | Retrieval sets with declared statistical error control | Evaluate the calibration contract before predictor expansion. Apache-2.0 repository; conflicting model-card metadata and undeclared model/data rights require review. Record the calibration population, loss, threshold, and distribution assumptions; guarantees may fail under dataset shift. |
| [LAFA](https://github.com/anphan0828/CAFA_forever); [preprint, 2026-04-22](https://arxiv.org/abs/2604.20782) | Timestamped comparisons of function-annotation models | Evaluate for repeatable model review. GPL-3.0 code. Pin annotation and ontology snapshots, evidence codes, and the training cutoff. The initial study covers a small method set; it does not establish universal rankings. |
| [CAFA-evaluator-PK](https://github.com/claradepaolis/CAFA-evaluator-PK); [CAFA5 preprint, 2026](https://doi.org/10.64898/2026.04.27.716980) | Function metrics that account for previously known annotations | Evaluate alongside LAFA for partial-knowledge scoring. GPL-3.0 code; review evaluation-data terms separately. Preserve terms of interest, known annotations, ontology release, and split date. Keep benchmark archives external. |

## Genome context and source metadata

| Tool and dated source | Useful output | Decision and limitation |
| --- | --- | --- |
| [BGC Atlas v2](https://bgc-atlas.cs.uni-tuebingen.de/about); [preprint, 2026-09-18](https://doi.org/10.64898/2026.09.14.751540) | Public cluster IDs, taxonomy, and environmental metadata | Evaluate metadata-only source scouting. Generated annotations are CC BY 4.0; assemblies retain source terms. Caller and assembly errors persist. A cluster marked complete is not proof of biochemical function. |
| [BGC-QUAST](https://github.com/gurevichlab/bgc-quast); [preprint v2, 2026-09-15](https://doi.org/10.64898/2026.05.04.722653) | Caller comparisons and coordinate-overlap summaries | Evaluate for control and benchmark reports. MIT code. Its reference may be another caller's prediction; report agreement separately from experimentally supported accuracy. Pin caller, coordinate conventions, and overlap settings. |
| [DiscERN](https://github.com/MaxMeta/DiscERN); [paper, 2026-07-14](https://doi.org/10.1038/s41467-026-75491-x) | Related cluster-family summaries | Watch until a compact adapter and independent comparison exist. AGPL-3.0 code. Family-level similarity and the study's limited family set do not establish product identity; retain caller and model provenance. |
| [SeqForge](https://github.com/ERBringHorvath/SeqForge); [paper, 2025-11-18](https://doi.org/10.1186/s12859-025-06297-9) | GenBank/JSON source metadata in tables | Evaluate only the metadata extraction component. MIT code. It is a utility, not a BGC caller; missing or inconsistent source records remain missing or uncertain. Keep sequence-bearing inputs external. |

## Literature and Citations

| Tool | Evaluation |
| --- | --- |
| [OpenAlex MCP](https://github.com/ourresearch/openalex-mcp-server) | Compare discovery results with Europe PMC. Retain the exact query and work IDs. |
| [Crossref and Retraction Watch](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) | Track corrections and retractions by notice DOI, relationship, and access date. |
| [Literature Evidence MCP 0.5.1](https://github.com/Furox-Art/literature-evidence-mcp/blob/v0.5.1/README.md) | Compare JATS paragraph locators and text hashes with direct Europe PMC retrieval. Record quote matching and claim support separately. |
| [MinerU 4.2.2](https://github.com/opendatalab/MinerU/releases/tag/mineru-4.2.2-released), [Docling 2.150.0](https://github.com/docling-project/docling/releases/tag/v2.150.0), and [GROBID 0.9.1](https://github.com/grobidOrg/grobid/releases/tag/0.9.1) | Compare source locators, table extraction, and references on the same papers. Record parser versions and per-file status. |
| [Ai2 Scholar QA](https://github.com/allenai/ai2-scholarqa-lib), [OpenScholar](https://www.nature.com/articles/s41586-025-10072-4), and [SemanticCite](https://arxiv.org/abs/2511.16198) | Compare retrieved passages and proposed support judgments with reviewer labels. |

| Preprint | How it informs evaluation |
| --- | --- |
| [Hybrid scientific claim verification, v2, November 12](https://arxiv.org/abs/2611.03093v2) | An agreement rule reduced macro-F1 for all three models tested. Score support, contradiction, and insufficient evidence separately. |
| [PreprintPaperTracker, v3, October 21](https://www.biorxiv.org/content/10.64898/2026.06.30.735556v3) | The authors classified 10.2% of primary abstract claims in 72,644 matched pairs as substantially revised. Recheck the cited claim when the source changes. |
| [TableParseMap, v1, August 10](https://arxiv.org/abs/2608.09842v1) | Include large tables and ambiguous row or column boundaries in parser comparisons. Verify values, units, and headers against the source. |

## Workflow Provenance

| Tool | Evaluation |
| --- | --- |
| [Nextflow 26.10.6](https://github.com/nextflow-io/nextflow/releases/tag/v26.10.6) and [nf-prov 1.8.0](https://github.com/nextflow-io/nf-prov/releases/tag/1.8.0) | Compare run and task records. Check the export profile and trace cached tasks to the producing run. |
| [Snakemake RO-Crate plugin 0.1.0](https://github.com/snakemake/snakemake-report-plugin-rocrate/blob/v0.1.0/README.md) | Evaluate Provenance Run Crate 0.5 metadata on completed, reused, and failed tasks. Check run status and artifact presence alongside profile conformance. |
| [nf-core/provenancereport 1.0.1](https://nf-co.re/provenancereport/1.0.1/docs/output/) | Review report indexes, checksums, and workflow metadata as reference formats. |
| [Flowcept 1.0.3](https://github.com/ORNL/flowcept/releases/tag/v1.0.3) | Evaluate local JSONL task events and artifact metadata. |

Record the exporter and profile versions with validation results. The
[Workflow Run RO-Crate 0.6 release](https://github.com/ResearchObject/workflow-run-crate/releases/tag/0.6.0)
uses RO-Crate 1.3.

## Release Notes for Existing Tools

Retain BLAST/DIAMOND/MMseqs2, HMMER, curated reaction sources, and MIBiG as
comparators. The [tool stack](tool-stack.md) maps these established roles.
The [integration map](TOOL_INTEGRATIONS.md) distinguishes shipped parsers from
operator-owned normalization.

| Release reference | Consequence for an existing contract |
| --- | --- |
| [MMseqs2 18-8cc5c, 2025-07-27](https://github.com/soedinglab/MMseqs2/releases/tag/18-8cc5c) | Record binary and database-build revisions; GPU-compatible database ordering can change results. |
| [DIAMOND 2.2.8](https://github.com/bbuchfink/diamond/releases/tag/v2.2.8) | Changes clustering performance and temporary-file use. Check search and cluster outputs separately. |
| [nf-core/proteinfamilies 2.6.0](https://github.com/nf-core/proteinfamilies/releases/tag/2.6.0) | Changes metadata CSV names and ordering. Check parsers against the new files. |
| [cblaster 1.4.2](https://github.com/gamcil/cblaster/releases/tag/v1.4.2) | Retain remote-search mode, taxonomy fields, and database revision. |
| [BiG-SLiCE 2.0.2](https://github.com/medema-group/bigslice/releases/tag/v2.0.2) | antiSMASH 8 support does not update every underlying model archive; record both releases. |
| [runpodctl 3.1.1](https://github.com/runpod/runpodctl/releases/tag/v3.1.1) | REST commands use API v2. Check command compatibility before updating scripts. |

Keep [ProtNote](https://github.com/microsoft/protnote) and
[BGC-Prophet](https://github.com/HUST-NingKang-Lab/BGC-Prophet) as alternate
predictors pending model/data review and comparisons with the selected
baselines. [VenusX](https://github.com/ai4protein/VenusX), an ICLR 2026
benchmark, has CC BY-NC-ND 4.0 repository terms; resolve intended-use rights
before adapting its assets. [PlantBGC](https://arxiv.org/abs/2607.27258) is a
July 2026 preprint; code and model availability remain unverified. Existing
CatPred-style kinetics, Folddisco motif search, and hosted design backends
remain separate, campaign-specific review options.

## Record an Evaluation

Record a selected tool in `tool_registry_ledger` and its adapter in
`adapter_contract_ledger`. Existing schema fields hold the input policy,
license boundary, supported event types, required columns, failure mode, and
compact output policy. Add both ledger paths to the campaign manifest before
preflight.

Each evaluation needs public or synthetic inputs, a declared baseline,
held-out examples, acceptance criteria, and an abstention or rejection case.
For AI outputs, retain the exact model revision, training or reference-data
cutoff when available, score meaning, and applicable calibration population.
Review code, weights, datasets, and hosted-service terms separately.

Map results to existing contracts:

| Evidence role | Compact record |
| --- | --- |
| Retrieval and annotation | `candidate-graph-ledger.tsv`, `candidate-intelligence-ledger.tsv`, `protein_function_votes.tsv` |
| Genome context | `cluster_calls.tsv`, `bgc_consensus.tsv`, `bgc-context-ledger.tsv` |
| Literature | `literature-search-ledger.tsv`, `literature-ledger.tsv`, `evidence-event-ledger.tsv` |
| Evaluation and provenance | `decoy-control-ledger.tsv`, `tool-execution-proof-ledger.tsv`, `run-output-package-ledger.tsv` |
