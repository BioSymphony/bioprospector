# Tool Integrations

BioProspector itself ships zero third-party dependencies. It integrates with
sequence search, domain, structure, BGC, and cloud tools through compact,
tabular contracts at the boundary. The agent (or operator) runs the tool;
BioProspector ingests the compact output.

This page is the consolidated map of what the skill talks to and where.
For install hints, see [`OPTIONAL_TOOLS.md`](OPTIONAL_TOOLS.md).

## Sequence Search

| Tool | Output format | How BioProspector consumes it |
| --- | --- | --- |
| NCBI BLAST+ (`blastp`, `blastn`) | `-outfmt 6` 12-column TSV | `bioprospector_evidence_ingest.py --format blast6` |
| DIAMOND | 12-column TSV in BLAST6 layout | `--format diamond` |
| MMseqs2 / MMseqs2-GPU | 12-column TSV in BLAST6 layout | `--format mmseqs` |

The ingest produces `candidate-funnels.tsv`, `enzyme-draft-board.tsv`,
`candidate-sequence-ledger.tsv`, `candidate-graph-ledger.tsv`,
`evidence-event-ledger.tsv`, and `target-evidence-ledger.tsv`. See
[`../demos/sample-inputs/`](../demos/sample-inputs/) for runnable samples.

## Domain And Family Search

| Tool | Output format | How BioProspector consumes it |
| --- | --- | --- |
| HMMER `hmmscan` / `hmmsearch` | `--domtblout` (Pfam-style) | `--format hmmer-domtbl` |
| Domain summary tables | normalized TSV | `--format domain-tsv` |
| nf-core/proteinfamilies / HH-suite-style family workflows | compact family, HMM, and membership summaries | Normalize to `domain-annotation-ledger.tsv`, `candidate-diversity-ledger.tsv`, and `candidate-graph-ledger.tsv` |
| PLMSearch / PLMAlign-style remote homology | hit tables, embedding-neighbor summaries, and alignment pointers | Normalize to candidate graph and diversity ledgers; keep model caches outside the repo |

The ingest produces `domain-annotation-ledger.tsv` and
`evidence-event-ledger.tsv`.

## Structure And Fold Neighbors

| Tool | Role | Integration |
| --- | --- | --- |
| Foldseek | Structure neighbor searches | Optional; doctor reports availability. Outputs join through `candidate-graph-ledger.tsv` and `structure-risk-ledger.tsv` when an operator wires them in. |
| EasIFA / TopEC / ProtDETR-style function or active-site predictors | Enzyme-function and active-site evidence | Record compact function votes in `protein_function_votes.tsv`, `candidate-intelligence-ledger.tsv`, and `structure-risk-ledger.tsv`; treat predictions as ranking evidence only. |

See [`host-structure-risk.md`](host-structure-risk.md) for the
structure-risk evidence path.

## BGC, Genome Context, And Metabolomics

| Surface | Where it lives in BioProspector |
| --- | --- |
| antiSMASH / plantiSMASH cluster calls | `cluster_calls.tsv`, validated by `bioprospector_genecluster_atlas_contracts.py` |
| antiSMASH DB / MIBiG curated BGC references | `bgc-context-ledger.tsv`, `compound-source-ledger.tsv`, and citation/accession rows |
| GATOR-GC targeted cluster windows | `cluster_calls.tsv`, `bgc_consensus.tsv`, and compact neighborhood summaries |
| BGCFlow / lsaBGC / BiG-SCAPE / BiG-SLiCE summaries | `bgc-context-ledger.tsv`, `candidate-graph-ledger.tsv`, and cluster-family summaries |
| cblaster / clinker neighborhood evidence | `cluster_calls.tsv`, `bgc_consensus.tsv` |
| Pfam / UniProt / EC predictor function votes | `protein_function_votes.tsv`, `protein_function_jury.tsv` |
| Metagenome and MAG context | `metagenome-context-ledger.tsv`, `mag-quality-ledger.tsv` |
| Metabolomics evidence | `metabolomics-evidence-ledger.tsv` |
| Compound source priors | `compound-source-ledger.tsv` |

The GeneCluster atlas planner and normalizers turn metadata-only inputs
into the cluster-call, consensus, function-vote, and function-jury
contracts. See [`genecluster-atlas-public-lane.md`](genecluster-atlas-public-lane.md)
and the synthetic fixture under
[`../../examples/genecluster-synthetic-v0/`](../../examples/genecluster-synthetic-v0/).

## Literature Search

`literature-search-ledger.tsv` and `literature-ledger.tsv` carry compact
citation evidence: search terms, sources, recency windows, result caps,
and citation pointers. The skill stays publisher-neutral; an agent can
populate these from PubMed, EuropePMC, Crossref, or another source under
operator-approved access rules.

PubTator 3.0, SciSpaCy, GROBID, and PaperQA2-style summarizers are useful
adjacent tools when they return identifiers, citations, extracted entities, and
short source-linked findings. They should not copy full-text articles, publisher
PDFs, or unrestricted literature dumps into the repo.

## Cloud Search Providers

| Provider | Role | Generator |
| --- | --- | --- |
| RunPod manual Pod | Controlled heavy search lane (BLAST, DIAMOND, MMseqs, HMMER, Foldseek) | `bioprospector_runpod_bundle.py` |
| AWS ElasticBLAST | Wide search against official NCBI BLAST databases | `bioprospector_elasticblast_bundle.py` |
| HPC / SSH | Site-local searches with the same ledger contracts | `bioprospector_runpod_bundle.py` outputs are portable; site-specific wiring is operator-owned |
| Cloud or neocloud VMs | Generic VM execution | Reviewed approval through the compute-provider ledger |
| Managed workflow services | Nextflow, Snakemake, CWL/WDL | `workflow-framework-ledger.tsv` records compatibility |

Provider bundles are launch packets for operator review. They do not
create cloud resources or submit jobs. See
[`runpod-stack.md`](runpod-stack.md),
[`aws-elasticblast-stack.md`](aws-elasticblast-stack.md), and
[`compute-provider-strategy.md`](compute-provider-strategy.md) for each
provider's contract.

## Tracker And Orchestrator Integrations

| Surface | Role | How BioProspector hands off |
| --- | --- | --- |
| Linear (or any tracker) | Owns issue dependencies, owners, blockers, closeout comments | `bioprospector_issue_dry_run.py` writes Markdown issue drafts; the operator copies into the tracker |
| Symphony workers | Drive autonomous swarms over the work graph | `bioprospector_agent_brief.py` writes a Symphony-compatible kickoff packet |
| Codex / Claude Code skill | Operates the skill on the user's behalf | `bioprospector_agent_brief.py` writes the agent prompt and command list |
| `/goal`-style flows | Single-goal kickoff with command list | `bioprospector_agent_brief.py --mode goal` |

See [`symphony-linear-sidecar.md`](symphony-linear-sidecar.md) for the
sidecar workflow and [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md) for prompts.

## The Boundary

All tool integrations follow the same rule: BioProspector receives
compact, tabular summaries (or pointers and checksums) and produces
compact, tabular ledgers. Raw sequence files, database mirrors, model
weights, and full provider workdirs live outside the repo, in
operator-chosen storage. The evidence-ingest CLI explicitly rejects FASTA
and raw sequence input; provide compact tool output.
