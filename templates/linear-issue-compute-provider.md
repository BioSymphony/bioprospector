# Compute Provider Strategy

## Goal

Keep RunPod as one reviewed optional heavy-search pattern while preserving one
BioProspector contract for local, cloud, neocloud, SSH/HPC, and managed workflow
users.

## Required Artifacts

- `compute-provider-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`
- `stage-contract-ledger.tsv`
- provider-specific stop gates
- cost, secrets, storage, and workdir boundaries

## Acceptance Criteria

- RunPod manual Pod remains a reviewed optional pattern for controlled heavy search lanes.
- Other providers are compatible only through the same ledger and self-check contracts.
- No provider path bypasses input audit, execution artifacts, target evidence, controls, maturity, or claim audit.
- Private registry auth, image pull, payload, snapshot, volume, budget, and stage-contract checks block launch until they pass.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
```
