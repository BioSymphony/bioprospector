# <Campaign>: Self-Learning Skill After Hiccup

## Agent Role

BioProspector learning reviewer.

## Scientific Goal

Convert a campaign hiccup into reusable process intelligence without treating
the learning as biological evidence.

## Inputs

- campaign manifest
- relevant `logs/YYYY-MM-DD-*.md` note or closeout
- `stage-progress-ledger.tsv`, `execution-artifact-ledger.tsv`, or provider
  status summary when applicable
- `self-learning-skill-ledger.tsv` if present
- failed command, validator output, or compact artifact pointer

## Artifact Contract

- Add or update one `self-learning-skill-ledger.tsv` row.
- State observation, hypothesis, probe, baseline/control, expected signal, and
  stop-loss before any retry.
- Record result and decision: update runbook, update skill, update template, add
  validator, retry, park, stop, escalate, or no change.
- Link the durable change if one is made.

## Acceptance Criteria

- The row distinguishes process learning from biological validation.
- No secrets, private sequences, raw outputs, full FASTA dumps, database mirrors,
  or full-text literature enter the repo.
- Paid or remote retries remain blocked unless a separate execution issue has
  provider preflight, budget guardrail, stage contract, and operator approval.
- A repeated hiccup becomes a reusable guardrail when it can be enforced by a
  template, validator, skill instruction, or runbook update.

## Claim Boundary

Self-learning entries improve future execution quality. They do not prove route
chemistry, enzyme activity, host production, or candidate validity.

<!-- symphony:schema
complexity: low
touched_areas:
  - self-learning-skill-ledger
  - logs
  - docs
  - templates
  - validators
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
