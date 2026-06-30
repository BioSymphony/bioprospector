# <Campaign>: Host Comparison

## Agent Role

Host-fit reviewer.

## Scientific Goal

Compare host/chassis options by burden, precursor fit, compartment fit,
toxicity, and analytics readiness.

## Artifact Contract

- Update `host-comparison-ledger.tsv`.
- Update `route-stitching-scorecard.tsv` if host fit changes route ranking.
- Update `claim-ledger.md` with host assumptions.

## Claim Boundary

Host-fit scoring is not a production claim.

<!-- symphony:schema
complexity: medium
touched_areas:
  - host-comparison-ledger
  - route-stitching-scorecard
  - claim-ledger
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
