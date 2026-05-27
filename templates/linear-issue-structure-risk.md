# <Campaign>: Structure Risk Triage

## Agent Role

Structure-risk reviewer.

## Scientific Goal

Identify active-site, cofactor, membrane, substrate-access, and oligomerization
risks for a small candidate shortlist.

## Artifact Contract

- Update `structure-risk-ledger.tsv`.
- Update `enzyme-draft-board.tsv` only when risk changes a verdict.
- Update `claim-ledger.md` with structure caveats.

## Claim Boundary

Structure support is not enzymatic validation.

<!-- symphony:schema
complexity: medium
touched_areas:
  - structure-risk-ledger
  - enzyme-draft-board
  - claim-ledger
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
