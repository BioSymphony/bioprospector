# Tool integrations

BioProspector itself ships zero third-party dependencies. It integrates with
sequence search, domain, structure, BGC, and cloud tools through compact,
tabular contracts at the boundary. The agent or operator runs the tool;
BioProspector ingests the compact output.

This page is the consolidated integration map. It does not promise compatibility
with every current release. For install hints, see
the [`optional tools`](OPTIONAL_TOOLS.md); for dated upstream reviews, see the
[`opportunity radar`](opportunity-radar.md).

## Sequence search

| Tool | Output format | How BioProspector consumes it |
| --- | --- | --- |
| NCBI BLAST+ (`blastp`, `blastn`) | `-outfmt 6` 12-column TSV | `bioprospector_evidence_ingest.py --format blast6` |
| [DIAMOND](https://github.com/bbuchfink/diamond) | 12-column TSV in BLAST6 layout | `--format diamond` |
| [MMseqs2 and MMseqs2-GPU](https://github.com/soedinglab/MMseqs2) | 12-column TSV in BLAST6 layout | `--format mmseqs` |

The ingest produces `candidate-funnels.tsv`, `enzyme-draft-board.tsv`,
`candidate-sequence-ledger.tsv`, `candidate-graph-ledger.tsv`,
`evidence-event-ledger.tsv`, and `target-evidence-ledger.tsv`. See
the [`sample input files`](../demos/sample-inputs/) for runnable samples.

## Domain and family search

| Tool | Output format | How BioProspector consumes it |
| --- | --- | --- |
| HMMER `hmmscan` or `hmmsearch` | `--domtblout` (Pfam-style) | `--format hmmer-domtbl` |
| Domain summary tables | normalized TSV | `--format domain-tsv` |
| nf-core/proteinfamilies and HH-suite-style family workflows | compact family, HMM, and membership summaries | Normalize to `domain-annotation-ledger.tsv`, `candidate-diversity-ledger.tsv`, and `candidate-graph-ledger.tsv` |
| PLMSearch and PLMAlign-style remote homology | hit tables, embedding-neighbor summaries, and alignment pointers | Normalize to candidate graph and diversity ledgers; keep model caches outside the repository |

The ingest produces `domain-annotation-ledger.tsv` and
`evidence-event-ledger.tsv`.

## Structure and fold neighbors

| Tool | Role | Integration |
| --- | --- | --- |
| Foldseek | Structure neighbor searches | Optional; doctor reports availability. An operator can map the output to `candidate-graph-ledger.tsv` and `structure-risk-ledger.tsv`. |
| Folddisco | Discontinuous structural-motif searches | Radar only; require a compact hit adapter and control contract before campaign use. |
| EasIFA, TopEC, and ProtDETR-style function or active-site predictors | Enzyme-function and active-site evidence | Record compact function votes in `protein_function_votes.tsv`, `candidate-intelligence-ledger.tsv`, and `structure-risk-ledger.tsv`; treat predictions as ranking evidence only. |

See the [`structure-risk evidence path`](host-structure-risk.md) for details.

## BGC, genome context, and metabolomics

| Surface | Where it lives in BioProspector |
| --- | --- |
| antiSMASH and plantiSMASH cluster calls | `cluster_calls.tsv`, validated by `bioprospector_genecluster_atlas_contracts.py` |
| antiSMASH DB and MIBiG curated BGC references | `bgc-context-ledger.tsv`, `compound-source-ledger.tsv`, and citation and accession rows |
| GATOR-GC targeted cluster windows | `cluster_calls.tsv`, `bgc_consensus.tsv`, and compact neighborhood summaries |
| BGCFlow, lsaBGC, BiG-SCAPE, and BiG-SLiCE summaries | `bgc-context-ledger.tsv`, `candidate-graph-ledger.tsv`, and cluster-family summaries |
| cblaster and clinker neighborhood evidence | `cluster_calls.tsv`, `bgc_consensus.tsv` |
| Pfam, UniProt, and EC predictor function votes | `protein_function_votes.tsv`, `protein_function_jury.tsv` |
| Metagenome and MAG context | `metagenome-context-ledger.tsv`, `mag-quality-ledger.tsv` |
| Metabolomics evidence | `metabolomics-evidence-ledger.tsv` |
| Compound source priors | `compound-source-ledger.tsv` |

The GeneCluster atlas planner and normalizers turn metadata-only inputs
into the cluster-call, consensus, function-vote, and function-jury
contracts. See the [`GeneCluster atlas public lane`](genecluster-atlas-public-lane.md)
and the [`synthetic GeneCluster fixture`](../skills/bioprospector/examples/genecluster-synthetic-v0/).

## Literature search

`literature-search-ledger.tsv` and `literature-ledger.tsv` carry compact
citation evidence: search terms, sources, recency windows, result caps,
and citation pointers. The skill stays publisher-neutral; an agent can
populate these from PubMed, Europe PMC, Crossref, or another source under
operator-approved access rules.

PubTator 3.0, SciSpaCy, GROBID, and PaperQA2-style summarizers can supply
identifiers, citations, extracted entities, and
short source-linked findings. Do not copy full-text articles, publisher PDFs,
or unrestricted literature dumps into the repository.

## Compute and workflow backends

| Provider | Role | Generator |
| --- | --- | --- |
| RunPod manual Pod | Controlled heavy search lane (BLAST, DIAMOND, MMseqs, HMMER, Foldseek) | `bioprospector_runpod_bundle.py` |
| AWS ElasticBLAST | Wide search against official NCBI BLAST databases | `bioprospector_elasticblast_bundle.py` |
| HPC or SSH | Site-local searches with the same ledger contracts | `bioprospector_runpod_bundle.py` outputs are portable; site-specific wiring is operator-owned |
| Cloud or neocloud VMs | Generic VM execution | Reviewed approval through the compute-provider ledger |
| Workflow frameworks | Nextflow, Snakemake, CWL, and WDL | `workflow-framework-ledger.tsv` records compatibility |

Provider bundles are launch packets for operator review. They do not
create cloud resources or submit jobs. See
the [`RunPod stack`](runpod-stack.md),
the [`AWS ElasticBLAST stack`](aws-elasticblast-stack.md), and the
[`compute-provider strategy`](compute-provider-strategy.md) for each
provider's contract.

## Tracker and orchestrator integrations

| Surface | Role | How BioProspector hands off |
| --- | --- | --- |
| Linear (or any tracker) | Owns issue dependencies, owners, blockers, closeout comments | `bioprospector_issue_dry_run.py` writes Markdown issue drafts; the operator copies into the tracker |
| Symphony workers | Run bounded tasks from the work graph | `bioprospector_agent_brief.py` writes a Symphony-compatible kickoff packet |
| Codex and Claude Code skill | Run BioProspector from the supplied campaign contract | `bioprospector_agent_brief.py` writes the agent prompt and command list |
| Goal-oriented flows | Start one bounded goal with a command list | `bioprospector_agent_brief.py --mode goal` |

See the [`Symphony and Linear sidecar`](symphony-linear-sidecar.md) for the
sidecar workflow and the [`agent playbook`](AGENT_PLAYBOOK.md) for prompts.

## The boundary

BioProspector receives compact tabular summaries and produces compact tabular
ledgers. Tracked outputs can contain public accessions, placeholders, and
checksums. Keep exact external locations in ignored operator state. Raw sequence
files, database mirrors, model weights, and full provider working directories
remain in operator-chosen storage. The evidence-ingest CLI rejects FASTA and raw
sequence input; provide compact tool output.
