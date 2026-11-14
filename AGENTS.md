# BioSymphony BioProspector agent guide

Use the [BioProspector skill](skills/bioprospector/SKILL.md) for campaign
planning, evidence review, and result mapping. The CLI validates ledgers and
generates local planning artifacts.

## Public safety rules

Do not add:

- API keys, provider credentials, signed URLs, SSH keys, or registry auth
- private workstation paths or non-public local history
- pod IDs, network volume IDs, account IDs, or private project identifiers
- private Linear issue text, internal run logs, cost records, or raw pod output
- unpublished biological data, private sequences, raw reads, database mirrors, model weights, or restricted datasets
- wet-lab protocols, construct automation, or claims of biological validation

Use synthetic or explicitly public examples only. Keep public examples compact
and label dry-run or mock artifacts clearly.

## Release Checks

Run `make release-check` before committing release changes. See the
[release checklist](docs/PUBLIC_SWITCH_CHECKLIST.md) for the content review.

## Claim boundaries

Treat outputs as design intelligence and prioritization, not biological
validation. Do not claim production, validation in a host, route completion, or
assay success without direct evidence joined through the declared ledgers.
