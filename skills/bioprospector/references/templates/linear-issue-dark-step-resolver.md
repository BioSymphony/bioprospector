# <Campaign>: Dark Step Resolver

## Agent Role

Unknown-gene discovery worker.

## Scientific Goal

Reason through an ambiguous pathway step without assuming the answer is a single
top homolog.

## Artifact Contract

- Update `pathway-inference-ledger.tsv`.
- Update `unknown-gene-hypothesis-ledger.tsv`.
- Add `enzyme-family-sweep.tsv` rows when chemistry-first reasoning creates a search lane.
- Preserve counterevidence in `rejected-candidates.tsv`.

## Claim Boundary

Hypotheses are planning intelligence only. Do not claim pathway completion,
validated activity, or production.

<!-- symphony:schema
complexity: high
touched_areas:
  - pathway-inference-ledger
  - unknown-gene-hypothesis-ledger
  - enzyme-family-sweep
  - rejected-candidates
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
