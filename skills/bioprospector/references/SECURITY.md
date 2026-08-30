# Security

Report sensitive disclosure issues privately to the repository maintainers. When
the project is hosted on GitHub, use GitHub private vulnerability reporting if
it is enabled for the repository. Do not open a public issue for secrets,
private data, provider identifiers, or unpublished biological material.

## Supported versions

Security maintenance covers the `main` branch and the tagged release with the
highest semantic version.
Release notes document any narrower support window.

## Public repository boundaries

See [`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md) for the
full data-class and threat model.

This repository must not contain:

- API keys, cloud credentials, SSH keys, tokens, signed URLs, or registry auth
- private workstation paths, private issue-tracker content, or internal run logs
- pod IDs, network volume IDs, account IDs, or billing records
- unpublished biological data, private sequences, raw reads, large database snapshots, model weights, or restricted datasets

If sensitive content appears in the tree or history, stop the release and report
it privately. Rotate affected credentials outside this repository. Re-create
public history from a reviewed clean export before publishing again.

## Response handling

Maintainers must acknowledge private security reports, triage whether the
issue affects current tree content or history, rotate any affected credentials
outside this repository, and prepare a clean public export when history contains
sensitive content. Public advisories must not repeat leaked values.

## Release gate

Before each public release, run:

```bash
make release-check
python3 scripts/check_docs_links.py .
python3 scripts/public_audit.py .
python3 scripts/public_audit.py .runtime
```

The audit checks working-tree content, generated runtime sidecars, and
Git-tracked paths for private runtime folders, raw biological artifacts,
provider identifiers, private paths, and secret-looking literals.
