# <Campaign>: Genome Context Mining

## Agent Role

Genome-context mining planner.

## Scientific Goal

Plan anchor, neighborhood, and BGC-context evidence without copying raw genome
artifacts into the repo.

## Artifact Contract

- Update `genome-mining-plan.tsv`.
- Update `genome-hit-ledger.tsv` with accessions, pointers, and compact support.
- Update `resource-ledger.tsv` for source and tool boundaries.

## Claim Boundary

Neighborhood support is evidence, not proof of function.

<!-- symphony:schema
complexity: high
touched_areas:
  - genome-mining-plan
  - genome-hit-ledger
  - resource-ledger
local_friendly: true
requires_private_data: false
requires_heavy_compute: true
-->
