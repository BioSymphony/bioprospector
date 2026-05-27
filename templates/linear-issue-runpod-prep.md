# RunPod Readiness Prep

## Goal

Prepare reviewable RunPod launch artifacts without creating pods, pulling
images, installing packages, downloading databases, or running searches.

## Required Artifacts

- provider readiness bundle under ignored `.runtime/`
- `compute-provider-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`
- `stage-contract-ledger.tsv`
- `tool-execution-proof-ledger.tsv` when exact commands block launch

## Acceptance Criteria

- Bundle rows include image digest, registry/auth, workdir, volume, cost, secrets, branch snapshot, and stage-contract gates.
- Private registry auth, missing image digest, missing volume, missing stage contract, or unresolved payload size remains a launch blocker.
- Provider desired state, image existence, or setup-script generation does not count as tool execution or biological evidence.
- No credentials, private data, raw reads, database mirrors, or model weights are copied into repo files or issue bodies.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-real-execution
```
