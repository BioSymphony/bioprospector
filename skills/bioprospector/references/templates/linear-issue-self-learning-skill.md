# <Campaign>: Self-Learning Skill After Hiccup

## Agent Role

BioProspector learning reviewer.

## Scientific Goal

Convert a campaign hiccup into reusable process intelligence without treating
the learning as biological evidence.

## Inputs

- campaign manifest
- relevant ignored `.runtime/learning-notes/YYYY-MM-DD-*.md` note or
  operator-owned closeout
- `stage-progress-ledger.tsv`, `execution-artifact-ledger.tsv`, or provider
  status summary when applicable
- `self-learning-skill-ledger.tsv` if present
- public-safe failure summary, validator status, or reviewed placeholder

## Artifact Contract

- Add or update one `self-learning-skill-ledger.tsv` row.
- State observation, hypothesis, probe, baseline/control, expected signal, and
  stop-loss before any retry.
- Record result and decision: update runbook, update skill, update template, add
  validator, retry, park, stop, escalate, or no change.
- Link the durable change if one is made.

## Acceptance Criteria

- The row distinguishes process learning from biological validation.
- No secrets, private paths, provider or account IDs, internal logs, cost or
  timing records, private sequences, raw outputs, full FASTA dumps, database
  mirrors, or full-text literature enter the repository.
- Paid or remote retries remain blocked unless a separate execution issue has
  provider preflight, budget guardrail, stage contract, and operator approval.
- A repeated hiccup becomes a reusable guardrail when it can be enforced by a
  template, validator, skill instruction, or runbook update.

## Claim Boundary

Self-learning entries record process changes. They do not prove route
chemistry, enzyme activity, host production, or candidate validity.

<!-- symphony:schema
complexity: low
touched_areas:
  - self-learning-skill-ledger
  - self-learning
  - docs
  - templates
  - validators
local_friendly: true
requires_private_data: false
requires_heavy_compute: false
-->
