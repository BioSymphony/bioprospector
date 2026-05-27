# <Campaign>: Literature Evidence Ledger

## Agent Role

Literature evidence reviewer.

## Scientific Goal

Map claims to citations, accessions, evidence classes, license boundaries, and
claim levels. Include preprint scans (biorxiv, chemrxiv, and any field-specific
preprint server) when the target sits in a fast-moving area such as
natural-product biosynthesis or enzyme engineering; recency matters more than
total volume. Record the preprint server, deposit date, and version when a
preprint is the source of a claim.

## Artifact Contract

- Update `literature-ledger.tsv`.
- Update `resource-ledger.tsv` only with compact source metadata.
- Update `claim-ledger.md` when evidence changes claim language.

## Claim Boundary

Do not copy article bodies, restricted database content, or large supplements
into the repo.

<!-- symphony:schema
complexity: medium
touched_areas:
  - literature-ledger
  - resource-ledger
  - claim-ledger
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
