# <Campaign>: Enzyme Family Sweep

## Agent Role

Enzyme family sweep worker.

## Scientific Goal

Compress broad enzyme-family search space into representative classes before
individual candidate review.

## Artifact Contract

- Update `enzyme-family-sweep.tsv`.
- Update `candidate-funnels.tsv`.
- Preserve killed families in `rejected-candidates.tsv`.

## Claim Boundary

Family support is not activity validation.

<!-- symphony:schema
complexity: medium
touched_areas:
  - enzyme-family-sweep
  - candidate-funnels
  - rejected-candidates
local_friendly: true
requires_private_data: false
requires_heavy_compute: true
-->
