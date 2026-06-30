# Agent Playbook

BioProspector works best when an agent treats the repo as a local control plane:
read the skill, run checks first, generate compact artifacts under `.runtime/`,
and keep pathway decisions, construct hypotheses, and claim boundaries
explicit.

## Power Prompt

```text
Use the bioprospector skill in this checkout. Turn <target molecule> in <host>
into a biosynthetic pathway discovery campaign: route families, enzyme/gene
mining lanes, pathway-stitching review, construct hypotheses, and a
Linear-ready issue graph under .runtime/. Keep everything local for now and do
not write raw sequences, credentials, provider identifiers, signed URLs,
private paths, or large databases into the repo.
```

## First Check Prompt

```text
Use the bioprospector skill in this checkout. Run the local doctor and public
audit first. Then tell me which local examples and commands are ready to use.
Keep generated artifacts under .runtime/.
```

## New Campaign Prompt

```text
Create a BioProspector campaign for <target molecule> in <host>. Start from
templates/target-contract.example.json, generate a scaffold under
.runtime/first-campaign/, run preflight and input audit, then tell me the route
families, likely dark steps, candidate-mining lanes, and smallest set of
operator decisions still needed before expansion.
```

Expected agent behavior:

- edit only ignored `.runtime/` campaign files unless asked to promote a compact
  reviewed example
- run `bioprospector_preflight.py`
- run `bioprospector_input_audit.py`
- keep claims at planning level until evidence and controls exist

## Example Review Prompt

```text
Inspect the nootkatone public example. Generate full-frontier issue drafts under
.runtime/nootkatone-linear-issues, run the stage-contract validator, export a
review package, and summarize the route families, enzyme-frontier bottlenecks,
construct-hypothesis implications, and next best work lanes.
```

Useful commands:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-profile full-frontier

python3 scripts/bioprospector_stage_contract.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

## What A Generated Linear Issue Looks Like

`bioprospector_issue_dry_run.py` produces tracker-ready Markdown drafts.
The shape is short, scannable, and ledger-bound. Example draft for the
input-audit lane:

```markdown
# Input Audit Before Questions

## Goal

Read manifest, target contract, and ledgers before asking the operator anything.

## Required Artifacts

- `input-audit-ledger.tsv`
- input-audit JSON summary
- explicit `missing_operator_items`

## Acceptance Criteria

- Known inputs are summarized first.
- Only explicit missing operator items are escalated.
- Non-blocking uncertainties are passed to operator intake instead of
  becoming broad questions.

## Validation

`python3 scripts/bioprospector_input_audit.py \
  --campaign path/to/campaign-manifest.json`
```

Forty-plus lane templates ship under `templates/`; the dry-run script
populates each with campaign-specific dependencies, kill criteria, and
validation commands. See [`../templates/README.md`](../templates/README.md)
for the full index.

## Tracker Work-Graph Prompt

```text
Use BioProspector to create a Linear-ready work graph for the nootkatone public
example, but do not call Linear or any tracker API. Generate Markdown issue
drafts under .runtime/nootkatone-workgraph, summarize the first useful wave, and
list the lanes that should stay blocked until provider or data approvals exist.
```

Useful command:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-workgraph \
  --include-profile full-frontier
```

## Generate A Campaign Agent Brief

Use this when the operator has a capable agent, Symphony + Linear setup, or
`/goal` workflow and needs a better starting packet rather than more machinery
inside the repo.

```bash
python3 scripts/bioprospector_agent_brief.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/huperzine-agent-brief \
  --prefix HUPERZINE \
  --profile public-demo \
  --mode goal \
  --agent codex
```

The brief writes `agent-goal-prompt.txt`, `agent-brief.md`, `agent-brief.json`,
and `commands.sh`. It tells the agent that BioProspector supplies contracts,
ledgers, validators, and local work graphs while the agent or external
orchestrator owns sequencing, tracker mutation, provider execution, and final
judgment.

## Public Skill Safety Audit Prompt

Use this prompt to check another public BioSymphony-style skill repo for the
same boundary:

```text
Audit this public BioSymphony-style skill repo for result-return and data-boundary clarity.

The repo should not imply that a user's capable agent is forbidden from getting real results back to the user. It should only forbid writing raw/private/heavy biological data into the repo, tracked examples, public artifacts, tracker issues, chat logs, or publishable docs.

Check README, quickstart, agent playbooks, CLI help, generated prompts, handoff packets, issue templates, and tests for ambiguous phrases like "do not materialize raw data" or "no raw data output." Replace them with language that says:
- raw/heavy/private outputs belong in user-approved external workdirs, volumes, HPC paths, RunPod volumes, or cloud buckets;
- the repo-facing return should be compact ledgers, pointers, checksums, summaries, rankings, dossiers, citations/accessions, and validation logs;
- generated planning/readiness artifacts do not launch providers, mutate trackers, download databases, or prove execution;
- mock, dry-run, planned, or readiness rows are not evidence;
- a public checkout is reusable control-plane code for the user's own campaign, with private data kept outside repo, tracker, chat, and publishable artifacts.

After edits, add or update tests so generated agent prompts and handoff packets include both halves of the boundary: "do not write raw/private data into repo/tracker/chat/publishable artifacts" and "return results through user-approved external locations plus compact ledgers/pointers/hashes/summaries/dossiers." Run the repo's local release or docs checks and report exactly what changed.
```

## Cloud Readiness Prompt

```text
Use BioProspector to prepare cloud-readiness review artifacts for the
nootkatone public example. Generate RunPod and AWS ElasticBLAST readiness
bundles under .runtime/, do not launch anything, and report expected outputs,
resume points, returned ledgers, budget, data, credential, cleanup, and
stage-contract blockers before any live run.
```

Useful commands:

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

## GeneCluster Atlas Prompt

```text
Use BioProspector to build the Huperzine A metadata-only GeneCluster atlas plan.
Do not download raw data. Generate local outputs under .runtime/genecluster-atlas/,
run the Atlas contract validator on the synthetic fixture, and summarize the
route decisions and claim ceiling.
```

Useful commands:

```bash
python3 scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0

python3 scripts/bioprospector_genecluster_atlas_normalizers.py all \
  --annotation-direct examples/genecluster-synthetic-v0/compact-clusters.tsv \
  --pfam examples/genecluster-synthetic-v0/compact-pfam.tsv \
  --out-dir .runtime/genecluster-atlas/synthetic-contracts
```

## Release-Readiness Prompt

```text
Do a local public-release readiness pass. Run make release-check, public audit,
runtime audit, docs checks, and gitleaks if available. Do not stage, commit,
push, or publish. Report any tracked forbidden files, docs gaps, or repository
boundary risks.
```

## Good Agent Closeout

Ask the agent to close with:

- commands run and pass/fail status
- generated `.runtime/` paths
- changed tracked files, if any
- claim level and remaining blockers
- explicit confirmation that no provider launch, database download, raw sequence
  materialization, Linear write, or public publish occurred
