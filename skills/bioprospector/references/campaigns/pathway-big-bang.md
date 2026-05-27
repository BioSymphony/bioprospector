# Pathway Big Bang Campaign

Status: draft v0

Use this campaign when the operator starts with a target molecule and host and wants BioProspector to expand all plausible biochemical routes.

## Goal

Generate a route universe that includes known, engineered, fed-substrate, de novo, degradation-derived, analog, and speculative routes.

## Required Outputs

- `target-contract.json`
- `route-ledger.tsv`
- `reaction-step-ledger.tsv`
- `unknown-step-ledger.tsv`
- `route-kill-list.md`

## Waves

1. Target and host contract
2. Known route harvest
3. Engineered route harvest
4. Reverse catabolism route scan
5. Analog chemistry route scan
6. Host-native precursor review
7. Route normalization into reaction steps
8. Missing-step ledger and route triage

## Review Gate

Routes advance only if they have:

- explicit substrates and products
- reaction-step decomposition
- evidence level
- route status
- primary risk
- next issue recommendations
