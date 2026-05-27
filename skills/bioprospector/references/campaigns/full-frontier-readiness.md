# Full Frontier Readiness Campaign

Status: draft v0

Use this campaign mode when a target should be prepared all the way up to a
reviewable RunPod/HPC execution bundle without actually launching compute.

## Goal

Prepare a complete control-plane package:

- target contract
- route universe
- reaction-step ledger
- candidate frontier budgets
- dry-run Linear issues
- Symphony workflow draft
- RunPod readiness bundle
- validation and red-team gates
- input audit, operator intake, stage/progress contracts, provider launch preflight, maturity ladder, target-evidence, decoy-control, and final self-check gates

## Non-Goals

- no pod creation
- no database download
- no public-webserver upload
- no real Linear mutation unless explicitly requested later
- no Symphony worker launch unless the operator separately asks
- no claim of target-host production

## Required Outputs

- `campaign-manifest.json`
- `target-contract.json`
- `route-ledger.tsv`
- `reaction-step-ledger.tsv`
- `candidate-funnels.tsv`
- `enzyme-draft-board.tsv`
- `unknown-step-ledger.tsv`
- `rejected-candidates.tsv`
- `route-stitching-scorecard.tsv`
- `resource-ledger.tsv`
- `claim-ledger.md`
- `input-audit-ledger.tsv`
- `operator-intake-ledger.tsv`
- `run-maturity-ledger.tsv`
- `stage-contract-ledger.tsv`
- `stage-progress-ledger.tsv`
- `organism-sample-ledger.tsv`
- `query-set-ledger.tsv`
- `target-dataset-ledger.tsv`
- `target-evidence-ledger.tsv`
- `decoy-control-ledger.tsv`
- `execution-artifact-ledger.tsv`
- `compute-provider-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`
- `workflow-framework-ledger.tsv`
- `runpod-run-manifest.json`
- dry-run Linear issue pack under `.runtime/`
- RunPod readiness bundle under `.runtime/`

## Review Gates

1. Campaign preflight passes.
2. No-heavy-artifact scan passes.
3. Dry-run issue pack includes search budgets, continuation criteria, kill criteria, touched areas, and validation commands.
4. RunPod bundle is reviewable and contains no secrets.
5. Restricted resources are marked deferred or manual-review.
6. Frontier issues do not move from planning to execution without an operator decision.
7. Input audit has no blocking `missing_operator_items`.
8. Operator intake has no `planning` blockers, and `execution` or `claim_closeout` assumptions are not treated as approval.
9. Stage contracts exist for long runs, with progress events, done markers, timeouts, and resume commands.
10. Provider launch preflight blocks private image pull failures, missing registry auth, missing volumes, payload issues, and wrong branch/snapshot before paid compute starts.
11. Any fallback is recorded as partial/degraded and cannot satisfy strict closeout without a narrowed claim boundary.
12. Any live success claim passes the joined contract self-check with real-execution, target-evidence, decoy-control, and L5 maturity flags.
13. Provider and workflow framework choices preserve the same ledger, artifact, and self-check contracts; RunPod remains one reviewed optional heavy-search pattern.
