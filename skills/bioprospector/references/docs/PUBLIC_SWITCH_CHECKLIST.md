# Public Switch Checklist

This repository is intended to be publishable only after this checklist passes
from a clean local checkout.

## Required Gates

```bash
python3 scripts/bioprospector_doctor.py --include-runtime
make release-check
python3 scripts/public_audit.py .
python3 scripts/public_audit.py .runtime
git status --short
git ls-files .runtime logs internal private
git ls-files --error-unmatch pyproject.toml src/biosymphony_bioprospector/cli.py scripts/check_docs_links.py docs/QUICKSTART.md CITATION.cff
```

Expected result:

- `make release-check` passes.
- `bioprospector_doctor.py --include-runtime` reports `BioProspector doctor: ok`.
- `scripts/public_audit.py .` prints `PASS public audit`.
- `scripts/public_audit.py .runtime` prints `PASS public audit` after generated demos exist.
- `git status --short` contains only intentional release changes.
- `git ls-files .runtime logs internal private` prints nothing.
- The `git ls-files --error-unmatch ...` command confirms release-critical
  packaging, CLI, docs-check, quickstart, and citation files are tracked.
- [`PRIVACY_SECURITY_MODEL.md`](PRIVACY_SECURITY_MODEL.md) still matches the intended public boundary.

## Secret And History Scans

Run these before the first public push when `gitleaks` is available:

```bash
gitleaks detect --source . --no-banner --redact --verbose
gitleaks dir . --no-banner --redact --verbose
```

Use `detect` for history and `dir` for the current tree. If the binary is not
available, record that exception in the release notes and do not treat it as a
substitute for manual review.

## Manual Review

Review every public release for:

- private workstation paths, non-public repo names, private issue text, or internal run logs
- API keys, tokens, signed URLs, SSH keys, registry auth, provider IDs, pod IDs, volume IDs, account IDs, or billing records
- raw or heavy biological files, search databases, model weights, provider workdirs, or rendered restricted reports
- source-specific campaign aliases that present a private run as a public default
- claim language that implies biological validation, route completion, production, assay success, or clinical utility

## Publish Boundary

The public switch should publish schemas, validators, examples, templates,
docs, and small planning/dossier outputs only. Runtime sidecars remain ignored
and reproducible; they are not release artifacts.
