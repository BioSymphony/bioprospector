# Agent playbook

BioProspector uses the repository as a local control plane. Read the skill, run
the checks, generate compact artifacts under `.runtime/`, and record pathway
decisions, non-procedural candidate hypotheses, and claim boundaries.

## Campaign planning prompt

```text
Use the bioprospector skill in this checkout. Turn <target molecule> in <host>
into a biosynthetic-pathway planning campaign: route families, enzyme and gene
mining lanes, pathway-stitching review, non-procedural candidate hypotheses, and a
Linear-ready issue graph under .runtime/. Keep this planning pass local and do
not write raw sequences, credentials, provider identifiers, signed URLs,
private paths, or large databases into the repository.
```

## First check prompt

```text
Use the bioprospector skill in this checkout. Run the local doctor and public
audit first. Then tell me which local examples and commands are ready to use.
Keep generated artifacts under .runtime/.
```

## New campaign prompt

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

## Example review prompt

```text
Inspect the nootkatone public example. Generate full-frontier issue drafts under
.runtime/nootkatone-linear-issues, run the stage-contract validator, export a
review package, and summarize the route families, enzyme-frontier bottlenecks,
construct-hypothesis implications, and next best work lanes.
```

Useful commands:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-profile full-frontier

python3 skills/bioprospector/scripts/bioprospector_stage_contract.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
```

## What a generated Linear issue looks like

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

`python3 skills/bioprospector/scripts/bioprospector_input_audit.py \
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
drafts under .runtime/nootkatone-workgraph, summarize the first approved,
contract-checked wave, and
list the lanes that should stay blocked until provider or data approvals exist.
```

Command:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-workgraph \
  --include-profile full-frontier
```

## Generate a campaign agent brief

Use this when the operator has a capable agent, Symphony + Linear setup, or
`/goal` workflow and needs a campaign-specific prompt, command list, lane counts,
and boundaries.

```bash
python3 skills/bioprospector/scripts/bioprospector_agent_brief.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
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

## Public artifact boundary

Keep raw, heavy, or private outputs in an operator-approved external location.
Return compact ledgers, opaque pointers, checksums, summaries, rankings,
dossiers, citations, and accessions to the campaign. Planning, dry-run,
readiness, and mock rows do not prove execution or biological validity.

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
python3 skills/bioprospector/scripts/bioprospector_runpod_bundle.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0

python3 skills/bioprospector/scripts/bioprospector_elasticblast_bundle.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
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
python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_normalizers.py all \
  --annotation-direct skills/bioprospector/examples/genecluster-synthetic-v0/compact-clusters.tsv \
  --pfam skills/bioprospector/examples/genecluster-synthetic-v0/compact-pfam.tsv \
  --out-dir .runtime/genecluster-atlas/synthetic-contracts
```

## Release-Readiness Prompt

```text
Do a local public-release readiness pass. Run make release-check, public audit,
runtime audit, docs checks, and gitleaks if available. Do not stage, commit,
push, or publish. Report any tracked forbidden files, docs gaps, or repository
boundary risks.
```

## Agent closeout

Ask the agent to close with:

- commands run and pass/fail status
- generated `.runtime/` paths
- changed tracked files, if any
- claim level and remaining blockers
- provider launch, database download, raw sequence materialization, tracker
  writes, and publication, each marked `occurred`, `did_not_occur`, or `unknown`
