# Stage Contract And Progress Ledger

## Goal

Define fail-closed stage contracts and progress events before any long-running
local, RunPod, cloud, HPC, or ElasticBLAST work.

## Required Artifacts

- `stage-contract-ledger.tsv`
- `stage-progress-ledger.tsv` or provider-side `stage-progress.jsonl`
- resume command for every long-running stage
- checkpoint and done markers

## Acceptance Criteria

- Every long stage has an expected artifact, timeout, checkpoint marker, done marker, and resume command.
- Provider desired state or RUNNING status is not treated as progress proof.
- Every long stage declares at least one no-progress probe such as file-size
  growth, ledger row growth, log growth, or an active command timeout.
- Fallback, partial, failed, skipped, or degraded progress is recorded explicitly.
- Stalled stages emit `event_status=stalled`, preserve partial artifacts, and
  fail closed unless the claim boundary is downgraded.
- If the stall exposes a reusable process lesson, record the hypothesis and
  stop-loss in `self-learning-skill-ledger.tsv`.
- Strict closeout fails unless required execution stages complete and join to execution artifacts.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-real-execution
```
