---
tracker:
  kind: linear
  api_key: $TRACKER_AUTH_ENV
  project_slug: "replace-with-linear-project-slug"
  issue_filters:
    labels:
      - "sym:bioprospector-nootkatone-frontier"
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Done
    - Closed
    - Cancelled
    - Canceled
    - Duplicate

campaign:
  mode: direct-done
  routing_label: "sym:bioprospector-nootkatone-frontier"
  trust: trusted-local
  integration_owner: worker

workspace:
  root: $SYMPHONY_WORKSPACES_ROOT

hooks:
  after_create: |
    # Portable sidecar setup:
    #   export BIOPROSPECTOR_REPO_URL=git@github.com:your-org/bioprospector.git
    #   export BIOPROSPECTOR_BRANCH=main
    #
    # The clone pattern mirrors the shared Symphony template but keeps closeout
    # direct-done and avoids after_run promotion or GitHub handoff mutation.
    rm -rf ./* ./.[!.]* 2>/dev/null || true
    git clone --depth 1 --branch "${BIOPROSPECTOR_BRANCH:-main}" "${BIOPROSPECTOR_REPO_URL:?set BIOPROSPECTOR_REPO_URL}" . || {
      git clone --depth 1 --branch "${BIOPROSPECTOR_BRANCH:-main}" "${BIOPROSPECTOR_REPO_URL:?set BIOPROSPECTOR_REPO_URL}" repo
      shopt -s dotglob && mv repo/* repo/.git . 2>/dev/null; rm -rf repo
    }
    rm -f .symphony-promote-ready .symphony-promoted .symphony-promote-result .symphony-github-handoff .symphony-github-handoff-result
  # after_run intentionally disabled for this sidecar. Workers use direct-done
  # closeout after self-review and validation; operators perform any repo
  # integration manually.

agent:
  max_concurrent_agents: 1
  overlap_aware: true
  max_turns: 20
  auto_stop_when_idle: true
  idle_grace_checks: 3

codex:
  command: 'CODEX_HOME="$SYMPHONY_CODEX_HOME" codex --model gpt-5.4 --config ''shell_environment_policy.include_only=["TRACKER_AUTH_ENV","BIOPROSPECTOR_REPO_URL","BIOPROSPECTOR_BRANCH"]'' --config model_reasoning_effort=medium app-server'
  approval_policy: never
  thread_sandbox: workspace-write
---

You are working on Linear issue {{ issue.identifier }}.

Title: {{ issue.title }}

Body:
{{ issue.description }}

{% if attempt > 1 %}
This is retry attempt {{ attempt }}. A previous worker ran out of turns on this issue.
Check the existing workspace state and Linear comments to understand what was already completed.
Focus on the remaining work rather than starting over.
{% endif %}

## Required Behavior

This workflow is a portable BioProspector sidecar. It is intentionally strict:
`campaign.mode` is `direct-done`, `agent.max_concurrent_agents` is `1`, and
`after_run` is disabled. Do not create promotion markers, GitHub handoff markers,
or automatic snapshot mutations.

- Read the repository `AGENTS.md` chain before making changes.
- Use repo-local `.codex/skills` and `skills/bioprospector/SKILL.md` when relevant.
- Use the local tracker integration, such as `$symphony-linear`, only if the
  operator stack already provides it.
- Keep changes bounded to the issue and its declared `## Touched Areas`.
- Treat `## Search Budget`, `## Continuation Criteria`, `## Kill Criteria`, `## Review Gate`, and `## Claim Boundary` as hard gates.
- Read declared inputs before asking operator questions; escalate only explicit `missing_operator_items`.
- Treat runner flags, issue status, and mock summaries as intent, not proof.
- Do not close a live success/closeout issue unless `bioprospector_contract_self_check.py` passes with the issue's required flags.
- Keep target organism/sample evidence separate from public/reference database context.
- Wide/frontier candidate promotion requires decoy or negative-control gates when the issue declares them.
- Treat RunPod as one reviewed optional provider pattern, and keep
  local/cloud/neocloud/HPC work provider-neutral through the same ledgers and
  final self-check.
- Do not add framework-specific shortcuts; shell, Python, Nextflow, Snakemake, CWL, WDL, and managed workflows must all emit the declared artifacts.
- Do not copy API keys, tokens, private sequence data, unpublished constructs, raw reads, large database snapshots, model weights, or restricted database content into the repo.
- Do not copy AWS access keys, secret keys, session tokens, MFA codes, root credentials, or SSO verification codes into Linear, repo files, or comments.
- Treat BioProspector outputs as design intelligence and prioritization, not biological validation.
- If the issue body contains `## Acceptance Criteria`, do not close the issue until every item passes.
- If the issue body contains `## Validation Commands`, run those commands exactly as written.
- Before closing, perform a skeptical self-review against the acceptance criteria, touched areas, data policy, and claim boundary.
- For completed work, post a concise final Linear comment with files touched, validation run, residual risks, and then move the issue directly to `Done`.
- If blocked, move the issue to an appropriate non-terminal blocked or backlog state with a comment explaining the blocker and remaining work. Do not leave it in `In Progress` without a recent comment.
- Do not move issues to `In Review` for this workflow unless an operator has explicitly changed the workflow closeout mode.
- Do not run RunPod, HPC, or heavy public-data searches from a prep-only issue. Prep issues may write query contracts, budget limits, resource ledgers, and compact output policies only.
- Do not submit AWS ElasticBLAST jobs, create buckets, upload query FASTA, or download BLAST results from prep-only issues. ElasticBLAST prep issues may write configs, safety ledgers, and cleanup plans only.

Before moving an issue to a terminal state, post a final Linear comment containing
this structured outcome block:

<!-- symphony-outcome
outcome_version: 1
status: success
files_touched: path/to/file.md
tests_added: 0
validation_summary: python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign ... passed
suggested_action: none
-->

For non-success outcomes, include:

<!-- symphony-outcome
outcome_version: 1
status: failed
reason: external_blocker
progress_pct: 60
remaining: Describe the remaining evidence lane, ledger update, or RunPod prep gap.
files_touched: path/to/file.md
tests_added: 0
validation_summary: Validation not run because ...
suggested_action: human_review
-->

Reason codes: scope_too_broad | validation_flaky | overlap_conflict |
missing_repo_guidance | environment_restriction | exhausted_turn_budget |
external_blocker | architecture_drift

Suggested actions: none | split_ticket | increase_turns | add_guidance | human_review
