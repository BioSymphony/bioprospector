# Use Cases

BioProspector is a skill repo for agentic bioprospecting: route expansion,
enzyme mining, dark-step resolution, candidate compression, source-context
planning, tracker work graphs, cloud-run handoffs, and review dossiers. These
use cases are designed to be useful before any provider execution exists. For a
path-based chooser, see
[`WORKFLOWS.md`](WORKFLOWS.md).

## When To Reach For This

| You want to... | Recipe |
| --- | --- |
| Plan a route from a target molecule in a microbial host | [First Target Campaign](#1-first-target-campaign) |
| Resolve a dark step or unknown gene in a candidate route | [Route And Unknown-Step Review](#2-route-and-unknown-step-review) |
| Compress a noisy enzyme search into a ranked Pareto shortlist | [Candidate Compression](#3-candidate-compression) |
| Mine biosynthetic gene clusters for a natural product | [Metadata-Only GeneCluster Atlas Planning](#7-metadata-only-genecluster-atlas-planning) |
| Split a long-horizon campaign into tracker-ready lanes | [Linear Or Tracker Work Graph](#5-linear-or-tracker-work-graph) |
| Prepare a cloud-scale search for review before launch | [Cloud Readiness And Live Handoff](#6-cloud-readiness-and-live-handoff) |

Each row links to a workflow recipe below with its prompt, command path, and
expected outputs.

Out of scope for this skill: one-shot BLAST lookups, plasmid or strain design,
and routes you already have and just need a vendor to make. The scaffolding here
pays back when a campaign is large enough to need ledgers, lanes, and a claim
audit.

## Workflow Recipes

### 1. First Target Campaign

Start here when you have a target molecule and a host but no campaign packet
yet.

What you get:

- target contract and manifest
- required ledger skeletons
- input audit
- planning-level claim ledger
- preflight report

Prompt:

```text
Use the bioprospector skill. Create a first campaign for <target> in <host>,
keep outputs under .runtime/, run preflight and input audit, then summarize the
route families, missing evidence, and smallest set of operator decisions needed
before expansion.
```

Command path:

```bash
python3 scripts/bioprospector_new_campaign.py \
  --target-contract templates/target-contract.example.json \
  --out .runtime/scaffolds/example-target-v0 \
  --campaign-id example-target-v0

python3 scripts/bioprospector_preflight.py \
  --campaign .runtime/scaffolds/example-target-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 scripts/bioprospector_input_audit.py \
  --campaign .runtime/scaffolds/example-target-v0/campaign-manifest.json
```

### 2. Route And Unknown-Step Review

Use this when a biosynthetic route is plausible but one or more steps are
uncertain.

What you get:

- route hypotheses
- reaction-step ledger
- unknown-step and unknown-gene hypotheses
- route-stitching scorecard
- red-team rows for weak links

Good closeout:

- which routes are still planning-only
- which steps need evidence
- what would block candidate promotion

Claim ceiling: route plausibility and unresolved-gap review, not pathway
completion or production.

### 3. Candidate Compression

Use this after a search or fixture has compact hit summaries, not raw sequence
archives.

What you get:

- candidate funnels
- candidate sequence pointers
- domain annotation rows
- candidate graph edges
- candidate rankings
- Pareto route fronts

Command path:

```bash
python3 scripts/bioprospector_candidate_package.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/candidate-packages/huperzine-frontier-public-v0

python3 scripts/bioprospector_pareto_rank.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/rankings/nootkatone-yeast-v0
```

Expected outputs:

- `.runtime/candidate-packages/huperzine-frontier-public-v0/`
- `.runtime/rankings/nootkatone-yeast-v0/pareto-frontier-ledger.tsv`

Claim ceiling: ranked planning candidates and evidence gaps, not enzyme
validation.

### 4. Long-Run Readiness

Use this when a promising route or enzyme frontier is ready to become a
resumable local, RunPod, HPC, cloud VM, neocloud, managed workflow, or
ElasticBLAST run.

What you get:

- stage contract validation
- heartbeat and stale-progress gates
- provider launch preflight rows
- execution-artifact proof requirements
- no-silent-fallback policy
- resume commands, expected outputs, budgets, and compact returned-ledger
  contracts

Prompt:

```text
Use BioProspector to prepare review-only long-run readiness for the nootkatone
example. Validate stage contracts, generate provider readiness files under
.runtime/, and report launch blockers. Do not launch providers.
```

Command path:

```bash
python3 scripts/bioprospector_stage_contract.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json

python3 scripts/bioprospector_runpod_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0
```

The bundle is a launch packet, not a launch action. It tells an operator what a
future run should produce and what still blocks execution.

### 5. Linear Or Tracker Work Graph

Use this when a team wants a campaign split into reviewable work lanes before
copying selected tasks into Linear or another tracker.

What you get:

- local Markdown issue-style drafts
- dependencies and touched areas
- search budgets and kill criteria
- provider-preflight and stage-contract lanes
- validation commands and claim boundaries

Command path:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-workgraph \
  --include-profile full-frontier
```

Why it is useful: Linear or another tracker can hold owners, dependencies,
blocked lanes, route-review decisions, provider-readiness tasks, and closeout
comments while the campaign contract remains the local source of truth.

### 6. Cloud Readiness And Live Handoff

Use this when a future search might need RunPod, HPC, cloud VMs, neocloud VMs,
or AWS ElasticBLAST.

What you get:

- provider readiness bundles
- provider-launch blocker rows
- stage contracts and progress expectations
- compact-output policies
- strict live closeout command

Command path:

```bash
python3 scripts/bioprospector_runpod_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0

python3 scripts/bioprospector_elasticblast_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone-yeast-v0 \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

Good closeout: the returned package joins execution artifacts, target evidence,
decoy controls, maturity, and claim audit back to the original campaign
contract.

### 7. Metadata-Only GeneCluster Atlas Planning

Use this when source context, gene clusters, or route ceilings matter but raw
data should stay out of the public repo.

What you get:

- source scout ledgers
- route decision ledgers
- Atlas contract ledgers
- cluster-call and function-jury contract validation

Prompt:

```text
Use BioProspector to build the Huperzine A metadata-only GeneCluster atlas
plan. Do not download raw data. Summarize route decisions, source-context
boundaries, and the claim ceiling.
```

Command path:

```bash
python3 scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0
```

## Operational Recipes

### 8. Demo Or Teaching Artifact

Use this when you want to show the full route-to-dossier workflow on compact
example data.

What you get:

- issue drafts
- compact dossier
- candidate package sidecars
- expected-output snapshots
- public audit pass/fail status

Command path:

```bash
make local-demo
python3 scripts/public_audit.py .runtime
```

### 9. Public Switch Readiness

Use this before any future public release.

What you get:

- syntax and unit tests
- wheel smoke test
- doctor report
- docs link and docs index checks
- release metadata checks
- root and runtime audits
- example preflights

Command path:

```bash
make switch-check
gitleaks dir . --redact --verbose
gitleaks detect --source . --redact --verbose
```

Keep the release local until the audit output, git status, and promoted files
are reviewed as one coherent public change.
