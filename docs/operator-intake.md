# Operator Intake

Operator intake is the small interview loop that sits between input audit and
worker dispatch. It prevents false starts without turning BioProspector into a
questionnaire.

## Default Pattern

1. Read `campaign-manifest.json`, `target-contract.json`, and declared ledgers.
2. Run `bioprospector_input_audit.py`.
3. Summarize known inputs and explicit `missing_operator_items`.
4. Ask zero questions when the operator already gave enough information or says
   "skip and go".
5. If questions are needed, ask at most three grouped prompts.
6. Record every assumption, answer, skip, blocker, and later gate in
   `operator-intake-ledger.tsv`.

The interview should clarify only decisions that materially change the work:
target, host, scope, inputs, data policy, provider path, budget, success
criteria, claim boundary, or unresolved ambiguity.

## Skip and go

`skip and go` is allowed for planning when assumptions are reversible and
`planning_can_proceed=true`. It does not unlock live execution or final claim
closeout.

Use `required_before` to keep gates explicit:

- `planning`: must be answered before route or issue planning proceeds.
- `execution`: can be assumed for planning, but blocks RunPod, AWS, local
  search, downloads, and live workflow runs.
- `claim_closeout`: can be assumed for planning, but blocks stronger final
  language and L5 closeout.
- `never`: optional context only.

## Smart Questions

Good intake questions are grouped and decision-oriented:

- "Confirm target, host, and planning scope."
- "Confirm public/open data only, no raw sequence uploads, and no live cloud
  spend."
- "Confirm success criteria: ranked candidate intelligence, not production or
  validation."

Bad intake questions ask the operator to restate information already in the
manifest, request secrets, request private sequence content in chat, or block
planning on optional preferences.

## Ledger Contract

`operator_intake_ledger` uses:

```text
intake_id	input_area	prompt	default_assumption	operator_answer	confirmation_status	required_before	planning_can_proceed	skip_allowed	notes
```

Allowed `input_area` values:

- `target`
- `host`
- `scope`
- `inputs`
- `data_policy`
- `provider`
- `budget`
- `success_criteria`
- `claim_boundary`
- `unknowns`

Allowed `confirmation_status` values:

- `unasked`
- `assumed`
- `confirmed`
- `skipped`
- `needs_operator`
- `blocked`

Allowed `required_before` values:

- `planning`
- `execution`
- `claim_closeout`
- `never`

`planning_can_proceed` and `skip_allowed` must be `true` or `false`.

## Safety Rule

Never ask for AWS keys, RunPod API tokens, private sequences, unpublished
constructs, raw biological files, or collaborator-restricted data in chat,
Linear, or tracked repo files. Ask for a secure path, accession, bucket prefix,
or operator-side confirmation instead.
