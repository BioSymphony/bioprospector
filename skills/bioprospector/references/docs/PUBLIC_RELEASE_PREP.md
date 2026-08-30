# Public release checks

Use this gate for every public release candidate. It checks the repository and
ignored synthetic runtime output; it does not run biological searches, call
providers, mutate trackers, or publish anything.

## Local checks

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
- Public audit scans the current tree, Git-tracked file paths, and generated
  `.runtime/` output for runtime directories, logs, raw biological artifacts,
  and private data.
- Runtime audit scans generated sidecars for private paths, provider identifiers, raw artifacts, and secret-looking literals.
- Public audits report `PASS`.

## Secret and history scan

Run this before publishing when `gitleaks` is installed:

```bash
gitleaks detect --source . --no-banner --redact --verbose
gitleaks dir . --no-banner --redact --verbose
```

`detect` checks committed history. `dir` checks the current working tree. If
`gitleaks` is unavailable, record the missing scan in the release notes and
complete the manual review.

## Repository boundary

Do not publish:

- private workstation paths or non-public local history
- `.env`, credentials, tokens, signed URLs, registry auth, or SSH keys
- private Linear issue text, internal run logs, cost records, raw pod logs, pod IDs, or network volume IDs
- unpublished biological data, private sequences, raw reads, large database snapshots, raw BLAST outputs, model weights, or restricted datasets
- cloud account IDs, private bucket names, or billing details

## Result boundary

- Generates planning ledgers, issue drafts, and readiness bundles.
- Includes a local-only GeneCluster atlas lane for source scouting, route ceilings, and cluster/function jury contracts.
- Includes opportunity lanes for route rules, thermodynamics, host modeling, supply chain, active-site risk, context evidence, and review surfaces.
- Does not launch RunPod, submit ElasticBLAST, create cloud resources, seed Linear, or download databases by default.
- Treats outputs as design intelligence and prioritization, not biological validation.
- Keeps public examples compact and claim-bounded.
