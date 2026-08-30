# Operator Intake And Assumption Confirmation

## Goal

Convert the input audit into a short operator interview only where decisions are
missing.

## Required Artifacts

- `operator-intake-ledger.tsv`
- input audit JSON summary
- explicit execution and claim-closeout blockers

## Acceptance Criteria

- Manifest, target contract, and ledgers are read before any question is asked.
- The worker asks zero questions when information is sufficient or the operator
  says "skip and go".
- If questions are needed, they are grouped into at most three prompts.
- Skipped and assumed answers record `planning_can_proceed`, `skip_allowed`, and
  `required_before`.
- No secrets, private sequence content, raw biological files, credentials, or
  unpublished constructs are requested in chat, Linear, or tracked files.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_input_audit.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
```
