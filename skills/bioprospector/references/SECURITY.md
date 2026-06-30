# Security

Report sensitive disclosure issues privately to the repository maintainers. When
the project is hosted on GitHub, use GitHub private vulnerability reporting if
it is enabled for the repository. Do not open a public issue for secrets,
private data, provider identifiers, or unpublished biological material.

## Supported Versions

Until the first public release is tagged, only the current `main` branch is
maintained. After tagging begins, supported versions will be documented in the
release notes.

## Public Repo Boundaries

See [`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md) for the
full data-class and threat model.

This repository must not contain:

- API keys, cloud credentials, SSH keys, tokens, signed URLs, or registry auth
- private workstation paths, private issue-tracker content, or internal run logs
- pod IDs, network volume IDs, account IDs, or billing records
- unpublished biological data, private sequences, raw reads, large database snapshots, model weights, or restricted datasets

If sensitive content appears in the tree, remove it before publishing and
re-create public history from a clean export. Do not push a repaired commit on
top of a leaked public history without maintainer review.

## Response Handling

Maintainers should acknowledge private security reports, triage whether the
issue affects current tree content or history, rotate any affected credentials
outside this repository, and prepare a clean public export when history contains
sensitive content. Public advisories should avoid repeating leaked values.

## Release Gate

Before publishing, run:

```bash
make release-check
python3 scripts/check_docs_links.py .
python3 scripts/public_audit.py .
python3 scripts/public_audit.py .runtime
```

The audit checks working-tree content, generated runtime sidecars, and
Git-tracked paths for private runtime folders, raw biological artifacts,
provider identifiers, private paths, and secret-looking literals.
