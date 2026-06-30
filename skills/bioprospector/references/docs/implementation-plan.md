# Implementation Plan

## Phase 0: Foundation

Status: initial scaffold.

Deliverables:

- repo guide
- BioProspector skill
- campaign references
- dossier schema docs
- starter campaign
- preflight validator

Exit criteria:

- starter campaign validates
- docs explain scope and non-scope
- no heavy biological artifacts are present

## Phase 1: Contract And Ledger Hardening

Status: public foundation implemented, with shared schema and helper CLIs.

Build:

- stricter TSV schema checks
- Linear issue dry-run generator
- candidate funnel validator
- claim-level validator
- resource/license ledger checks
- optional `unknown_step_ledger`, `rejected_candidates`, `provenance_log`, and `runpod_run_manifest` manifest support
- optional ambiguity, literature, family-sweep, genome-context, structure-risk, host-comparison, assay-handoff, and monitoring ledger support
- opt-in local artifact scan through `bioprospector_preflight.py --repo-root PATH --scan-local-artifacts`
- shared `schemas/bioprospector-ledgers.json` contract
- compact campaign scaffold generation
- public-safe dossier export
- compact evidence ingest from tabular search summaries
- self-learning row helper
- public demo smoke checks for issue drafts and provider readiness bundles

Exit criteria:

- a campaign manifest can generate route, step, candidate-mining, integration, and red-team issue bodies
- each issue body passes a contract preflight
- campaign preflight validates route statuses, claim levels, candidate search widths, optional unknown-step/rejected-candidate headers, and absence of heavy biological artifacts when the scan flag is used

## Phase 2: Enzyme Frontier Prototype

Run one broad and one narrow enzyme-step prototype.

Suggested pair:

- broad: valencene oxidase/P450-like step
- narrow: valencene synthase-like step

Exit criteria:

- candidate funnels show raw to shortlist compression
- rejected candidates are preserved
- final shortlist rows include claim levels and evidence classes

## Phase 2B: Ambiguity And Unknown-Gene Readiness

Build:

- `pathway_inference_ledger`
- `unknown_gene_hypothesis_ledger`
- Dark Step Resolver issue generation
- enzyme-family sweep and genome-context planning lanes

Exit criteria:

- ambiguous steps preserve hypotheses and counterevidence
- multi-gene and hidden-step explanations can be represented without overclaiming
- generated issues include stop points before heavy search

## Phase 3: Pathway Stitcher Prototype

Combine shortlists into route designs.

Exit criteria:

- `route-stitching-scorecard.tsv` exists
- route-level bottlenecks are explicit
- Pareto route winners are generated

## Phase 4: RunPod Search Image

Prepare a lean remote execution environment.

First tools:

- MMseqs2
- DIAMOND
- BLAST+
- HMMER or pyhmmer
- seqkit
- NCBI Datasets CLI
- DuckDB
- RDKit
- COBRApy
- Nextflow or Snakemake

Defer:

- full `nr`
- full genome mirrors
- full InterProScan on unclustered hits
- structure prediction for every candidate
- deep licensed database integration

## Phase 4B: AWS ElasticBLAST Wide Search

Prepare a cloud-near-data escalation lane for official NCBI BLAST databases.

Build:

- `elasticblast_search_plan`, `elasticblast_run_ledger`, and `aws_safety_ledger`
- prep-only ElasticBLAST bundle generator
- AWS setup checklist with no-secret authentication boundary
- budget, quota, S3, janitor, and cleanup gates
- per-step config templates for wide/frontier searches

Exit criteria:

- nootkatone campaign preflight validates the ElasticBLAST ledgers
- generated bundle contains configs for all wide/frontier steps
- no AWS credentials, S3 uploads, ElasticBLAST submissions, or cloud resources are created
- generated configs require operator approval before live submit

## Phase 5: BioProspector Campaign Demo

Run a complete dry-run campaign from target contract to route shortlist.

Exit criteria:

- route universe
- step ledger
- candidate funnels
- enzyme draft board
- stitching scorecard
- claim ledger
- red-team report
- validation roadmap

## Phase 6: Complex Workflow Prep

Prepare references for taxane route resolution, post-branch MIA expansion,
complex saponin stitching, cryptic microbial BGC dereplication, fungal/endophyte
mining, and triterpene analog workflows without adding full target examples.
