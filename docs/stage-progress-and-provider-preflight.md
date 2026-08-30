# Stage progress and provider preflight

Provider status is intent, not evidence. A RunPod pod with desired status
`RUNNING`, an AWS job submission, or a local process id does not prove that the
container pulled, the command started, the stage progressed, or the requested
artifact exists.

## Stage Contracts

Use `stage-contract-ledger.tsv` before any long run, especially anything that
can burn cloud spend or run for more than an hour.

Each stage records:

- stage id and provider id
- expected artifact
- checkpoint marker
- done marker
- timeout
- resume command
- fail-closed behavior
- maturity level it can support
- current status

If a stage is `fail_closed=true`, missing progress or a failed/blocked status
prevents real execution closeout.

Validate the contract before treating a campaign as live-ready:

```bash
python3 skills/bioprospector/scripts/bioprospector_stage_contract.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
```

For real closeout, add `--require-terminal --require-real-execution` and set a
heartbeat ceiling with `--max-heartbeat-age-minutes`.

## Progress Ledgers

Use `stage-progress-ledger.tsv` or a provider-side `stage-progress.jsonl` with
the same fields. Events should distinguish:

- `started`
- `heartbeat`
- `completed`
- `failed`
- `partial`
- `fallback`
- `skipped`
- `resumed`

Fallbacks are first-class events. A worker that switches from RunPod to local,
from target data to reference data, from real data to mock data, or from the full
route to a rescue route must record `fallback` or a non-`none`
`degraded_status`. Strict closeout fails until the claim boundary is narrowed.

## No-Progress Stop-Loss

Long provider stages need a no-progress detector in addition to heartbeats. A
stage can be alive but stuck inside a blocking download, solver, model, or tool
process that emits no new stage event.

For every active long stage, declare at least one observable progress probe:

- byte growth for expected large files such as `.faa`, `.fasta`, `.fastq`,
  `.sra`, `.dmnd`, `.hmmpress` outputs, archives, or model outputs
- row or line-count growth for ledgers, logs, shard outputs, or JSONL progress
  streams
- updated mtime plus process/log tail for commands that write in bursts
- active command timeout that is shorter than the whole campaign budget

If none of the declared probes changes across the configured stale window, emit
`event_status=stalled`, set `degraded_status=stalled`, write a partial summary,
and stop paid compute unless an operator explicitly extends the run. A `running`
heartbeat without artifact or log growth is not progress proof.

For multi-input materialization stages, write partial ledgers after each input
finishes. One completed dataset, query shard, or candidate batch should remain a
salvageable partial result even when a later input stalls.

When a stall reveals a reusable process lesson, add a
`self-learning-skill-ledger.tsv` row and follow
`docs/self-learning-skill-runbook.md`. The learning row can recommend a future
retry or guardrail, but it does not override provider preflight, stage contracts,
or strict closeout gates.

## Provider Launch Preflight

Use `provider-launch-preflight-ledger.tsv` before paid compute starts.

Blocking checks should cover:

- image digest pin
- private registry auth
- image pull readiness
- network volume mount
- workdir
- cost guardrail
- no-progress stop-loss
- secrets boundary
- exact branch or snapshot
- provider payload size
- rendered issue body
- data policy
- stage contract

Private GHCR or other private registry images are launch blockers until the
provider can pull the exact image with provider-side credentials. Do not put
registry tokens in this repo, Linear, chat, or generated bundles.

## Closeout Rule

Readiness bundles, provider intent, mock summaries, and fallback progress are
not success. Real closeout requires execution artifacts, target evidence,
controls, completed stage progress, provider launch preflight passes, and claim
audit under the final self-check.
