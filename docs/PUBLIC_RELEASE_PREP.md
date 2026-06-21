# Public Release Prep

Clean, no-history public-prep workspace for BioSymphony BioProspector.

## Status

- [x] Public-safe BioProspector skill and repo-local Codex shim.
- [x] Public foundation docs, templates, validators, and tests.
- [x] Compact public vanillin starter scaffold.
- [x] Compact public nootkatone frontier demo.
- [x] Compact public Huperzine A dark-step/source-context demo.
- [x] RunPod readiness generator that writes review-only bundles under `.runtime/`.
- [x] AWS ElasticBLAST readiness generator that writes review-only bundles under `.runtime/`.
- [x] Self-learning skill ledger and issue template.
- [x] Shared schema contract, scaffold generator, dossier exporter, evidence ingest skeleton, self-learning helper, and public demo smoke runner.
- [x] Metadata-only GeneCluster atlas planner, summary normalizer, contract validator, schema ledgers, issue lane, docs, and tests.
- [x] Public package metadata, citation metadata, notice file, CI workflow, and public-switch checklist.
- [x] Public opportunity radar, opportunity issue lanes, and extended ledger schema contracts.
- [x] Public quickstart, CLI reference, privacy/security model, and local docs-link checker.
- [x] Canonical `NON_CLAIMS.md`.
- [x] Canonical `BIOSAFETY.md`.
- [x] Local validation gate (`make release-check`).
- [ ] Decide public remote, repository visibility, and release tag.
- [ ] Re-run tree, tracked-file, history, and optional secret scans immediately before first push.

## Local Release Checks

```bash
make release-check
```

Expected outcomes:

- Unit tests pass.
- Package smoke, doctor, and docs-link checks pass.
- Vanillin, nootkatone, and Huperzine A campaign preflights pass.
- Nootkatone and Huperzine A planning self-checks pass.
- Public demo smoke generates issue drafts and dossiers under `.runtime/` without provider bundle sidecars.
- GeneCluster atlas smoke generates metadata-only source, route, contract, normalized cluster/function, and plan ledgers under `.runtime/`.
- Public audit scans the current tree, Git-tracked file paths, and generated `.runtime/` output for forbidden runtime/log/raw/private artifacts.
- Runtime audit scans generated sidecars for private paths, provider identifiers, raw artifacts, and secret-looking literals.
- Public audits report `PASS`.

## Secret And History Scan

Before the first public push, run this when `gitleaks` is installed:

```bash
gitleaks detect --source . --no-banner --redact --verbose
gitleaks dir . --no-banner --redact --verbose
```

`detect` checks committed history. `dir` checks the current working tree. If
the binary is unavailable, record that exception in the release notes and keep
manual review mandatory.

## Repository Boundary Rules

Do not publish:

- private workstation paths or non-public local history
- `.env`, credentials, tokens, signed URLs, registry auth, or SSH keys
- private Linear issue text, internal run logs, cost records, raw pod logs, pod IDs, or network volume IDs
- unpublished biological data, private sequences, raw reads, large database snapshots, raw BLAST outputs, model weights, or restricted datasets
- cloud account IDs, private bucket names, or billing details

## Public Positioning

- Generates planning ledgers, issue drafts, and readiness bundles.
- Includes a local-only GeneCluster atlas lane for source scouting, route ceilings, and cluster/function jury contracts.
- Includes opportunity lanes for route rules, thermodynamics, host modeling, supply chain, active-site risk, context evidence, and review surfaces.
- Does not launch RunPod, submit ElasticBLAST, create cloud resources, seed Linear, or download databases by default.
- Treats outputs as design intelligence and prioritization, not biological validation.
- Keeps public examples compact and claim-bounded.
