# {{PREFIX}}: Scale Control And Partial Closeout

## Agent Role

BioProspector scale-control reviewer.

## Goal

Separate primary evidence from context lanes, estimate fanout before expensive annotation, and require partial summaries plus stale-output guards for resumable provider runs.

## Inputs

- `campaign-manifest.json`
- `lane-status-ledger.tsv`
- `fanout-estimate-ledger.tsv`
- `partial-summary-ledger.tsv`
- `stale-output-guard-ledger.tsv`
- `stage-contract-ledger.tsv`
- `execution-artifact-ledger.tsv`

## Artifact Contract

- Update `lane-status-ledger.tsv` with primary/context/control/summary lane status.
- Update `fanout-estimate-ledger.tsv` with expected expansion and decision.
- Update `partial-summary-ledger.tsv` for failed, partial, deferred, blocked, fallback, or skipped lanes.
- Update `stale-output-guard-ledger.tsv` so done markers join input/code/output hashes.

## Acceptance Criteria

- Context annotation partials are visible and do not masquerade as primary evidence.
- High fanout uses downsample, shard, annotate-once-join-many, defer, block, or operator review.
- Raw tool output is normalized into ledgers before downstream consumption.
- Native/control hits are labeled separately from discovery candidates.
- Persistent-volume outputs cannot close out as live evidence with stale or unknown guards.

## Validation Commands

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign {{CAMPAIGN}}
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign {{CAMPAIGN}}
```

## Claim Boundary

Planning and readiness only unless real execution, target evidence, controls, stale-output guards, and claim audit pass.

<!-- symphony:schema
complexity: medium
touched_areas:
  - lane-status-ledger
  - fanout-estimate-ledger
  - partial-summary-ledger
  - stale-output-guard-ledger
  - stage-contract-ledger
  - execution-artifact-ledger
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
