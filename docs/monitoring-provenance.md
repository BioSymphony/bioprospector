# Monitoring and provenance

BioProspector monitoring is ledger- and Linear-first. Do not add a daemon,
dashboard, queue runner, or background service for this phase.

## Monitoring Ledger

`monitoring-ledger.tsv` records:

- run id
- issue id
- lane
- expected compact artifact
- heartbeat status
- blocker
- next review point
- owner

Use it to define checkpoints before widening searches, increasing agent
concurrency, launching RunPod, or submitting ElasticBLAST.

## Stage Progress

For long runs, `monitoring-ledger.tsv` is not enough. Use
`stage-contract-ledger.tsv` and `stage-progress-ledger.tsv` to record expected
artifacts, timeouts, heartbeats, checkpoint markers, done markers, resume
commands, partial/fallback state, and timestamps.

Provider `RUNNING` or desired state is only intent. It cannot satisfy stage
completion, L3 execution, or claim closeout without artifact proof.

## Self-Learning Loop

When monitoring finds a stale stage, provider failure, fallback, repeated
operator-question gap, or false-success risk, open the self-learning skill loop in
`docs/self-learning-skill-runbook.md`.

Use `self-learning-skill-ledger.tsv` only for reusable process lessons:
observation, hypothesis, smallest safe probe, baseline/control, expected signal,
stop-loss, result, and durable decision. Link any runbook, skill, template,
validator, or issue-generator update that prevents the same hiccup from
recurring.

Learning rows are not success evidence. They do not satisfy execution,
target-evidence, control, provider-preflight, or claim-closeout gates.

## No-False-Success Provenance

Use `execution-artifact-ledger.tsv` for artifact proof. Each row must mark
whether it is `dry_run` or `mock_tools`; those rows can prove path wiring but
cannot prove biological execution. Use `run-maturity-ledger.tsv` to keep L0-L5
status separate.

Before asking the operator questions, run `bioprospector_input_audit.py` and
record only explicit missing operator items. Then use
`operator-intake-ledger.tsv` for a short confirmation loop: zero questions when
the prompt and manifest are sufficient, otherwise at most three grouped
questions. Before live closeout, run `bioprospector_contract_self_check.py` with
the required evidence flags.

## Provenance

Campaigns should preserve:

- command lines and validation commands
- database/tool/model names and versions
- external workdir or cloud result pointers
- checksums when available
- claim-boundary decisions

For future live workflows, prefer Nextflow or Snakemake execution with
Workflow Run RO-Crate or nf-prov style provenance, then copy back only compact
BioProspector ledgers and summaries.
