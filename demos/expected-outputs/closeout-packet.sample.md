# Closeout Packet Sample

A real closeout joins provider output back to the campaign contract. This sample
shows the shape of the review packet, not biological validation.

## Promoted Candidates

| Candidate | Step | Why promoted | Remaining blocker |
| --- | --- | --- | --- |
| `CAND-DEMO-001` | `S003` | best compact evidence summary plus domain support | target-evidence join |
| `CAND-DEMO-004` | `S005` | diversity representative with useful motif context | decoy-control review |

## Parked Candidates

| Candidate | Reason parked | Next useful lane |
| --- | --- | --- |
| `CAND-DEMO-007` | promising family but weak substrate evidence | candidate-intelligence review |
| `CAND-DEMO-009` | host-fit uncertainty | structure-risk and host-comparison lane |

## Killed Claims

| Claim | Reason killed | Evidence row |
| --- | --- | --- |
| route completion in target host | no joined target-host evidence | `target-evidence-ledger.tsv` |
| single-enzyme dark-step answer | multi-gene hypothesis remains plausible | `unknown-step-ledger.tsv` |

## Returned Artifacts

- `execution-artifact-ledger.tsv`
- `tool-execution-proof-ledger.tsv`
- `candidate-sequence-ledger.tsv`
- `domain-annotation-ledger.tsv`
- `candidate-graph-ledger.tsv`
- `pareto-frontier-ledger.tsv`
- `dossier.md`

## Next Wave

- run the candidate-intelligence lane on parked diversity candidates
- promote the strongest evidence route to red-team review
- keep provider escalation blocked until the first package joins cleanly
