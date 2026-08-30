# GeneCluster Atlas Public Lane

This lane uses metadata-only contracts and compact summaries to plan
genome-context work while keeping raw biological artifacts and provider
execution state outside the repository.

## Purpose

GeneCluster Atlas is the genome-context extension of BioProspector. It answers:

- which public source records are available
- which route is scientifically defensible before compute
- which controls block candidate promotion
- what claim ceiling applies to transcript, genome, annotation, and literature evidence
- what compact artifacts a worker must return

BioProspector treats this as a control-plane lane. It does not fetch
sequence data, build databases, run BLAST, call provider APIs, or write raw
FASTA/GFF/FASTQ-style artifacts into the repo.

## Local Command

```bash
python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0
```

Expected outputs:

- `genecluster-source-scout-ledger.tsv`
- `genecluster-route-decision-ledger.tsv`
- `genecluster-atlas-contract-ledger.tsv`
- `genecluster-atlas-plan.json`

Normalize and validate synthetic summary tables:

```bash
python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_normalizers.py all \
  --annotation-direct skills/bioprospector/examples/genecluster-synthetic-v0/compact-clusters.tsv \
  --pfam skills/bioprospector/examples/genecluster-synthetic-v0/compact-pfam.tsv \
  --out-dir .runtime/genecluster-atlas/synthetic-contracts

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py \
  --cluster-calls .runtime/genecluster-atlas/synthetic-contracts/cluster_calls.tsv \
  --bgc-consensus .runtime/genecluster-atlas/synthetic-contracts/bgc_consensus.tsv \
  --protein-function-votes .runtime/genecluster-atlas/synthetic-contracts/protein_function_votes.tsv \
  --protein-function-jury .runtime/genecluster-atlas/synthetic-contracts/protein_function_jury.tsv
```

These helpers accept compact summary/fixture rows and emit:

- `cluster_calls.tsv`
- `bgc_consensus.tsv`
- `protein_function_votes.tsv`
- `protein_function_jury.tsv`

## Route Ceilings

- `L0_plan_only`: no usable target dataset is declared; write the next experiment or intake plan.
- `L1_sequence_candidate_ready`: proteome/query evidence can support candidate search only.
- `L2_transcript_candidate_ready`: transcript evidence can support candidate genes, not physical cluster claims.
- `L2_coordinate_context_ready`: genome evidence can support coordinate-context planning.
- `L3_annotation_neighborhood_ready`: annotation plus genome/proteome context can support neighborhood review.
- `L1_controls_or_queries_pending`: otherwise strong route, but missing query seeds or decoy controls block promotion.

## Public Boundary

Keep these out of the public repo:

- raw reads, assemblies, annotations, alignments, sequence FASTA, BLAST/MMseqs/HMMER databases, model weights, and provider workdirs
- provider IDs, volume IDs, signed URLs, credential names with values, and private issue text
- campaign logs and generated atlas outputs
- source-specific defaults that do not generalize across campaigns

Use these patterns:

- source scout before execution
- route decision before dispatch
- summary-only provider return contract
- negative-control gates
- stage-progress and stale-output guards
- cluster/function jury with explicit claim ceilings
- final dossier as index plus caveats, not raw data
