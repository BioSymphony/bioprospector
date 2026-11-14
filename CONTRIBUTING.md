# Contributing

Use synthetic or explicitly public data in examples.

## Before Opening a Pull Request

```bash
python3 -m pip install -e '.[dev]'
make release-check
```

See the [release checklist](docs/PUBLIC_SWITCH_CHECKLIST.md) before publishing.

If you have `pre-commit` installed, `pre-commit install` enables a local
hook that runs the audit and docs link checks before each commit. See
`.pre-commit-config.yaml`.

## Extend the skill

### Add a public example campaign

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
5. Add the example under "Examples" in `docs/README.md`.

### Extend the schema

The shared schema lives in `schemas/bioprospector-ledgers.json`. To add a ledger
type or column, do the following:

1. Edit the schema and update any affected ledger templates under
   `skills/bioprospector/examples/`.
2. Update validators in `skills/bioprospector/scripts/` that consume the
   ledger.
3. Add a test in `tests/` that covers the new field contract.
4. Run `python3 -m pytest -q` and `make release-check`.

### Add a CLI subcommand

1. Implement the script under `skills/bioprospector/scripts/` with a
   `main()` entry point.
2. Register it in `src/biosymphony_bioprospector/cli.py` so it shows up as
   a `bioprospector <subcommand>`.
3. Add an entry in `pyproject.toml` under `[project.scripts]`.
4. Add a unit test in `tests/`.
5. Update `docs/CLI_REFERENCE.md` and the README's CLI reference link as needed.
6. Run `make wheel-smoke` to confirm the installed CLI works.

## Public-safe examples

- Use synthetic or explicitly public-source examples.
- Keep raw or heavy data outside the repository.
- Store accessions, checksums, public URLs, and compact summaries instead
  of sequence dumps or database mirrors.
- Mark dry-run and mock artifacts as `dry_run: true` or `mock_tools: true`.
- Preserve rejected candidates and counterevidence.

## Content excluded from the public repository

- credentials, tokens, `.env` files, signed URLs, or private registry auth
- private workstation paths, private issue text, or internal run logs
- pod IDs, network volume IDs, cloud account IDs, or billing records
- unpublished biological data, private sequences, raw reads, raw BLAST
  outputs, model weights, or restricted datasets

See [`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md) for
the full data-class policy.

## Claim language

Prefer "candidate", "hypothesized", "domain-supported", "ortholog-supported",
"characterized elsewhere", or "validated elsewhere" when that is the
evidence level. Reserve "produces" or "validated in host" for cases where
direct evidence supports that exact claim.
