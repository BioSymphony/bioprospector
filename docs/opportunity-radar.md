# BioProspector opportunity radar

Reviewed: 2026-09-22. Dates identify the cited publication or release; they
are separate from this review date.

Prioritize source-linked tools and references that
return compact evidence records. These selections are research
recommendations, not tested integrations. **Evaluate** means prepare a bounded
comparison; **watch** means resolve the stated gap first. BioProspector adds no
runtime dependency for a catalog entry.

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

## Literature, citation review, and provenance

| Tool and dated source | Useful output | Decision and limitation |
| --- | --- | --- |
| [Ai2 Scholar QA](https://github.com/allenai/ai2-scholarqa-lib); [preprint, 2025-04-15](https://arxiv.org/abs/2504.10861) | Paper IDs, retrieved passages, and claim-linked citations | Evaluate a literature adapter. Apache-2.0 code; corpus and model-provider terms are separate. Queries and passages can reach external services. Retain source locators, retrieval settings, model revision, and reviewer status. |
| [OpenScholar](https://github.com/akariasai/OpenScholar); [paper, 2026-02-04](https://www.nature.com/articles/s41586-025-10072-4) | Citation-aware literature synthesis and retrieval evaluation | Watch as an architecture/evaluation reference. Apache-2.0 code; verify model and corpus rights separately. The full index is too large for this kit. Source-linked synthesis still requires claim-by-claim review. |
| [MinerU 4.0.6](https://github.com/opendatalab/MinerU/releases/tag/mineru-4.0.6-released), 2026-09-22 | Page/block locators and extracted text, table, and formula fields | Evaluate operator-side document extraction. Custom license includes commercial and service-use conditions. Keep public-paper PDFs and raw extraction external; return short findings with parser revision, locator, and checksum. Confirm local versus remote processing. |
| [SemanticCite](https://github.com/sebhaan/semanticcite); [preprint, 2025-11-20](https://arxiv.org/abs/2511.16198) | Citation-support classes and supporting evidence locators | Watch until packaging and model/data terms are verified. MIT code. A verifier's confidence does not prove support; retain uncertain and unsupported outcomes for a reviewer. |
| [Flowcept 1.0.3](https://github.com/ORNL/flowcept/releases/tag/v1.0.3), 2026-07-20 | Offline JSONL task and artifact provenance | Evaluate metadata-only event capture. MIT code. The local JSONL mode needs no broker; distributed modes have additional services. Disable prompt/response capture and normalize only reviewed events into execution and package ledgers. |

[PaperTrail](https://arxiv.org/abs/2602.21045), submitted 2026-02-24 and
accepted at CHI 2026, is a useful review-interface study. Its 26-participant
study found that clearer claim/evidence links reduced trust without changing
reliance on generated edits. Require an explicit review decision; a citation
interface alone does not establish that review happened.

## Retained baselines and deferred tools

Retain BLAST/DIAMOND/MMseqs2, HMMER, curated reaction sources, and MIBiG as
comparators. The [tool stack](tool-stack.md) maps these established roles.
The [integration map](TOOL_INTEGRATIONS.md) distinguishes shipped parsers from
operator-owned normalization.

| Release reference | Consequence for an existing contract |
| --- | --- |
| [MMseqs2 18-8cc5c, 2025-07-27](https://github.com/soedinglab/MMseqs2/releases/tag/18-8cc5c) | Record binary and database-build revisions; GPU-compatible database ordering can change results. |
| [DIAMOND 2.2.4](https://github.com/bbuchfink/diamond/releases/tag/v2.2.4) | Keep search and clustering output contracts separate. |
| [nf-core/proteinfamilies 2.5.0](https://github.com/nf-core/proteinfamilies/releases/tag/2.5.0) | Iterative family generation changes workflow and membership provenance. |
| [cblaster 1.4.2](https://github.com/gamcil/cblaster/releases/tag/v1.4.2) | Retain remote-search mode, taxonomy fields, and database revision. |
| [BiG-SLiCE 2.0.2](https://github.com/medema-group/bigslice/releases/tag/v2.0.2) | antiSMASH 8 support does not update every underlying model archive; record both releases. |
| [runpodctl 2.14.0, 2026-09-10](https://github.com/runpod/runpodctl/releases/tag/v2.14.0) | Release adds serverless environment management and model-reference fixes. Review command compatibility separately from manual-Pod readiness. |

Keep [ProtNote](https://github.com/microsoft/protnote) and
[BGC-Prophet](https://github.com/HUST-NingKang-Lab/BGC-Prophet) as alternate
predictors pending model/data review and comparisons with the selected
baselines. [VenusX](https://github.com/ai4protein/VenusX), an ICLR 2026
benchmark, has CC BY-NC-ND 4.0 repository terms; resolve intended-use rights
before adapting its assets. [PlantBGC](https://arxiv.org/abs/2607.27258) is a
July 2026 preprint; code and model availability remain unverified. Existing
CatPred-style kinetics, Folddisco motif search, and hosted design backends
remain separate, campaign-specific review options.

## Admission contract

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

Execution requires the campaign's tool, provider, budget, and data-policy
checks. Keep weights, databases, full-text articles, raw sequences, and exact
runtime locations outside tracked artifacts. A citation supports only the
claim a reviewer verifies in that source; an AI score remains a prediction.
