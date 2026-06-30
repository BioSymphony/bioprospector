# <Issue Title>

## Agent Role

Define the worker role and narrow scope.

## Scientific Goal

State the exact route, reaction step, candidate family, host-fit question, or review gate this issue handles.

## Inputs

- Campaign:
- Target:
- Host:
- Route or step IDs:
- Required ledgers:
- External resources:

## Artifact Contract

The worker must write structured outputs only:

- updated ledger rows:
- evidence records:
- rejected candidates:
- provenance notes:
- validation summary:
- input audit or self-check summary when this issue claims readiness, execution, evidence join, or success:

## Acceptance Criteria

- Required columns are present.
- Candidate claims use approved claim levels.
- Rejected routes or candidates include a reason.
- Host-fit or route-stitching issues are captured when relevant.
- Reference hits are not treated as target organism/sample evidence.
- Mock and dry-run artifacts are labeled and not used as real proof.
- No private or large biological data is copied into this repo.

## Validation Commands

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign path/to/campaign-manifest.json
```

## Dependencies

- Blocks:
- Blocked by:

## Review Gate

The orchestrator should verify evidence level, search budget, continuation criteria, and claim boundary before unlocking downstream issues.

## Claim Boundary

Allowed language:

- candidate
- hypothesized
- evidence-supported
- characterized elsewhere
- validated elsewhere

Forbidden language unless directly supported:

- produces
- completes
- catalyzes in target host
- validated in target host

<!-- symphony:schema
complexity: medium
touched_areas:
  - ledgers
  - dossier
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
