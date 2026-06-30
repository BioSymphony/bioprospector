# <Campaign>: Monitoring And Provenance

## Agent Role

Campaign monitoring reviewer.

## Scientific Goal

Track expected artifacts, blockers, heartbeat states, review checkpoints, and
closeout proof without adding a daemon.

## Artifact Contract

- Update `monitoring-ledger.tsv`.
- Record expected compact artifacts for active lanes.
- Declare no-progress probes for long active stages: artifact byte growth,
  ledger row growth, log growth, or a command timeout shorter than the campaign
  budget.
- Preserve validation commands and provenance notes.

## Acceptance Criteria

- Provider `RUNNING`, job id, or process id is not treated as progress.
- A stage with heartbeats but no declared artifact/log growth across the stale
  window records `heartbeat_status=stalled` or an explicit blocker.
- Partial completed inputs or shards are preserved in compact ledgers before a
  later stalled input can stop the run.
- Repeated or costly hiccups create a `self-learning-skill-ledger.tsv` row rather
  than another unstructured post-mortem.

## Claim Boundary

Monitoring proves process state, not scientific validity.

<!-- symphony:schema
complexity: low
touched_areas:
  - monitoring-ledger
  - provenance
  - workflow
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
