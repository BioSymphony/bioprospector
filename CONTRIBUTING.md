# Contributing

Keep contributions public-safe, compact, and claim-bounded. The skill
should remain useful from a laptop and across multi-agent harnesses.

## Before Opening A PR

```bash
make release-check
```

`release-check` runs the test suite, doctor, docs link checks, docs index
check, release metadata check, example preflights, capability demo, public
audit on the tree, and public audit on `.runtime/`. For public-switch work,
also review [`docs/PUBLIC_SWITCH_CHECKLIST.md`](docs/PUBLIC_SWITCH_CHECKLIST.md).

If you have `pre-commit` installed, `pre-commit install` enables a local
hook that runs the audit and docs link checks before each commit. See
`.pre-commit-config.yaml`.

## How To Extend The Skill

### Add A Public Example Campaign

1. Copy `templates/target-contract.example.json` and adapt for the target
   molecule and host.
2. Generate a scaffold:

   ```bash
   python3 skills/bioprospector/scripts/bioprospector_new_campaign.py \
     --target-contract path/to/target-contract.json \
     --out skills/bioprospector/examples/<example-id> \
     --campaign-id <example-id>
   ```
3. Add a short `README.md` in the new example folder describing what it
   exercises and a claim ceiling line.
4. Run preflight and the contract self-check:

   ```bash
   python3 skills/bioprospector/scripts/bioprospector_preflight.py \
     --campaign skills/bioprospector/examples/<example-id>/campaign-manifest.json
   python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py \
     --campaign skills/bioprospector/examples/<example-id>/campaign-manifest.json
   ```
5. Add the example to `docs/README.md` under "Examples" and to the example
   table in the top-level `README.md`.

### Extend The Schema

The shared schema lives in `schemas/bioprospector-ledgers.json`. Adding a
new ledger type or column:

1. Edit the schema and update any affected ledger templates under
   `skills/bioprospector/examples/`.
2. Update validators in `skills/bioprospector/scripts/` that consume the
   ledger.
3. Add a test in `tests/` that covers the new field shape.
4. Run `python3 -m pytest -q` and `make release-check`.

### Add A New CLI Subcommand

1. Implement the script under `skills/bioprospector/scripts/` with a
   `main()` entry point.
2. Register it in `src/biosymphony_bioprospector/cli.py` so it shows up as
   a `bioprospector <subcommand>`.
3. Add an entry in `pyproject.toml` under `[project.scripts]`.
4. Add a unit test in `tests/`.
5. Update `docs/CLI_REFERENCE.md` and `docs/CLI` references in the README
   as needed.
6. Run `make wheel-smoke` to confirm the installed CLI works.

## Public-Safe Examples

- Use synthetic or explicitly public-source examples.
- Keep raw or heavy data outside the repo.
- Store accessions, checksums, public URLs, and compact summaries instead
  of sequence dumps or database mirrors.
- Mark dry-run and mock artifacts as `dry_run: true` or `mock_tools: true`.
- Preserve rejected candidates and counterevidence.

## Out Of Scope For The Public Repo

- credentials, tokens, `.env` files, signed URLs, or private registry auth
- private workstation paths, private issue text, or internal run logs
- pod IDs, network volume IDs, cloud account IDs, or billing records
- unpublished biological data, private sequences, raw reads, raw BLAST
  outputs, model weights, or restricted datasets

See [`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md) for
the full data-class policy.

## Claim Language

Prefer "candidate", "hypothesized", "domain-supported", "ortholog-supported",
"characterized elsewhere", or "validated elsewhere" when that is the
evidence level. Reserve "produces" or "validated in host" for cases where
direct evidence supports that exact claim.
