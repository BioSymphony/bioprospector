# Optional Tracker Sidecar

This sidecar makes BioProspector campaign planning portable across optional
Symphony/Linear-style operator setups. The default is Markdown issue drafts
under `.runtime/`; the repo does not create tracker issues by default. An
operator decides whether to copy reviewed drafts into an external tracker.
For the user-facing workflow, see
[`WORKFLOWS.md`](WORKFLOWS.md#4-linear-or-tracker-mirror).

## What The Sidecar Provides

- Dry-run issue bodies for target contract, route, step, integration, and red-team work.
- Optional evidence-lane child drafts for every `wide` or `frontier` reaction step.
- Optional RunPod prep drafts for campaign-level and step-level remote search planning.
- Optional AWS ElasticBLAST prep drafts for NCBI-wide BLAST escalation planning.
- Optional operator-intake drafts for short confirmations, `skip and go`
  assumptions, and later execution/claim blockers.
- Optional stage-contract and provider-preflight drafts so long runs have
  checkpoints, progress, image-pull checks, and fail-closed launch gates.
- Optional no-false-success drafts for input audit, maturity, target-evidence joins, decoy controls, and final contract self-check.
- Optional provider/framework drafts so RunPod, local, cloud, neocloud, HPC, and managed workflow paths share one issue contract.
- Optional self-learning skill drafts for converting stalls, fallback, false-success risks, and repeated workflow gaps into durable workflow improvements.
- Default candidate-intelligence drafts for publicly reported/reference enzymes, variant annotations, signal peptides, PTMs, localization, expression watchouts, and close-canonical-match inferences.
- A conservative optional workflow draft at `templates/symphony-workflow-bioprospector.WORKFLOW.md`.

Generated issues include these worker gates:

- `Search Budget`
- `Continuation Criteria`
- `Kill Criteria`
- `Touched Areas`
- `Review Gate`
- `Claim Boundary`
- validation commands that distinguish schema checks from final joined self-checks

## Generate Issue Drafts

Base dry run:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json \
  --prefix VANILLIN \
  --out .runtime/vanillin-linear-issues
```

Recommended full-frontier dry run for agent work graphs:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-profile full-frontier
```

The command writes Markdown files only. It does not call Linear and does not
create, update, or move real issues.

Example sidecar inventory:

| Lane | Why it exists | First-wave default |
| --- | --- | --- |
| target contract and input audit | give the campaign a stable starting packet | active |
| route expansion and reaction steps | split route families into reviewable work | active |
| dark-step resolver | preserve missing-gene and multi-gene hypotheses | active for frontier gaps |
| enzyme-family sweep | compress broad candidate sets before promotion | active for wide steps |
| candidate intelligence | add motifs, variants, localization, PTM, and expression context | backlog until candidate rows exist |
| RunPod/HPC/cloud readiness | define future execution without launching it | blocked until operator review |
| ElasticBLAST escalation | prepare official NCBI-wide search only when needed | blocked until operator review |
| red-team and claim audit | kill weak routes and keep claims bounded | active |
| dossier export | produce the human review packet | final wave |

Tracker mapping:

| Tracker field | Use from BioProspector draft |
| --- | --- |
| title | draft heading |
| labels | campaign prefix, lane type, provider/readiness tag |
| owner | assigned after local review |
| status | `Backlog` except the first validated wave |
| dependency | `Depends On` and `Review Gate` sections |
| acceptance criteria | `Continuation Criteria`, `Kill Criteria`, validation commands |
| closeout comment | changed ledgers, generated artifacts, claim level, blockers |

<details>
<summary>Equivalent explicit flag form</summary>

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-evidence-lanes \
  --include-runpod-prep \
  --include-elasticblast-prep \
  --include-literature-lanes \
  --include-ambiguity-lanes \
  --include-enzyme-family-sweeps \
  --include-genome-mining-lanes \
  --include-structure-risk-lanes \
  --include-host-comparison-lanes \
  --include-assay-handoff-lanes \
  --include-monitoring-lanes \
  --include-stage-contract-lanes \
  --include-input-audit-lanes \
  --include-operator-intake-lanes \
  --include-maturity-lanes \
  --include-target-evidence-lanes \
  --include-decoy-control-lanes \
  --include-self-check-lanes \
  --include-provider-lanes \
  --include-provider-preflight-lanes \
  --include-framework-lanes \
  --include-sequence-search-lanes \
  --include-candidate-package-lanes \
  --include-candidate-intelligence-lanes \
  --include-self-learning-lanes
```

</details>

## Validate Before Handoff

Run campaign preflight:

```bash
python3 scripts/bioprospector_preflight.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json
```

Run the input audit before worker questions:

```bash
python3 scripts/bioprospector_input_audit.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

Then use operator intake only for unresolved decisions. A `skip and go` response
may unlock planning when assumptions are recorded, but it does not unlock live
RunPod/AWS/local execution or final claim closeout.

Run the planning self-check before handoff:

```bash
python3 scripts/bioprospector_contract_self_check.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

Only a live closeout should use the strict flags:

```bash
python3 scripts/bioprospector_contract_self_check.py \
  --campaign path/to/live/campaign-manifest.json \
  --require-real-execution \
  --require-target-evidence \
  --require-decoy-controls \
  --require-maturity L5
```

If you copy the workflow into a local operator stack and replace the
placeholders, run the equivalent repo preflight from that stack:

```bash
${SYMPHONY_HOME}/bin/repo-preflight \
  /path/to/bioprospector \
  bioprospector
```

## Use The Workflow Draft

Copy the workflow into an operator setup only after local review, then edit the
portable placeholders:

```bash
cp templates/symphony-workflow-bioprospector.WORKFLOW.md \
  ${SYMPHONY_HOME}/workflows/bioprospector.WORKFLOW.md
```

Required operator edits:

- Set `tracker.project_slug`.
- Set or export `BIOPROSPECTOR_REPO_URL`.
- Set `BIOPROSPECTOR_BRANCH` if the branch is not `main`.
- Keep the routing label as `sym:bioprospector-nootkatone-frontier` unless the copied Linear issues use a different label.

Execution defaults:

- `campaign.mode: direct-done`
- `agent.max_concurrent_agents: 1`
- `tracker.issue_filters.labels: sym:bioprospector-nootkatone-frontier`
- `after_run` disabled
- no snapshot promotion
- no GitHub handoff
- no RunPod execution from prep-only issues
- no paid provider launch until blocking provider-launch-preflight rows pass
- no long-run closeout without stage progress and done markers
- no genome mining, structure prediction, or host-model execution from prep-only issues

## Operator Pattern

1. Generate dry-run issue drafts.
2. Review and prune drafts before creating real external tracker issues.
3. Add the workflow routing label to every issue intended for this sidecar.
4. Keep most issues in `Backlog`; activate only the first validated wave.
5. Start with one worker until the campaign proves its validation loop.
6. Promote downstream issues only after dependencies, review gates, and claim boundaries are satisfied.

## Data And Claim Boundaries

Do not store API keys, tokens, private sequence data, unpublished constructs,
raw reads, large database snapshots, model weights, or restricted database
content in this repo or in external tracker issue bodies.

Use accessions, checksums, secure path references, compact ledgers, citations,
and derived summaries. BioProspector issue outputs are planning intelligence,
not wet-lab validation or target-host production claims.
