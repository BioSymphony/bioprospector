# Privacy And Security Model

BioProspector is designed as a public-safe control plane. The public repo should
contain schemas, validators, templates, compact examples, issue drafts, and
summary indexes. It should not contain sensitive data or heavy biological
artifacts.

This boundary should not block a user's agent from producing useful results.
For real user-owned runs, raw/heavy outputs may live in operator-approved local
workdirs, external volumes, HPC paths, RunPod volumes, or cloud buckets. The
repo-facing return should be compact ledgers, pointers, checksums, summaries,
rankings, and dossiers that tell the user where the full outputs live without
copying private or heavy data into public/repo/tracker/chat surfaces.

## Data Classes

| Class | Public Repo Policy | Examples |
| --- | --- | --- |
| Public-safe control data | Allowed | schemas, validators, templates, compact demo ledgers, public accession-style pointers |
| Public-safe derived summaries | Allowed after review | candidate ranks, claim levels, package indexes, citations, checksums, graph edges |
| Runtime sidecars | Ignored by default | `.runtime/` issue drafts, demo dossiers, generated package ledgers |
| Provider metadata | Summaries only | provider class, planned budget, stage contracts, cleanup policy |
| Sensitive operator data | Never commit | credentials, account IDs, pod IDs, volume IDs, signed URLs, private paths, billing records |
| Restricted biological data | Never commit | unpublished sequences, private raw reads, FASTA dumps, BLAST databases, model weights, private spectra |

## Threat Model

Primary risks:

- leaking private workstation paths, account names, provider IDs, or internal
  run logs
- committing API keys, SSH keys, registry auth, signed URLs, cloud credentials,
  or budget/account identifiers
- storing raw or restricted biological artifacts in a repo intended for public
  use
- letting dry-run, mock, provider-intent, or reference-only evidence read as
  biological validation
- uploading private sequences, raw reads, or private spectra to public web tools
  during future live work

## Controls

- `scripts/public_audit.py` scans working tree content, Git-tracked paths, and
  generated runtime sidecars for private text, forbidden directories, raw/heavy
  biological file extensions, provider identifiers, and secret-looking values.
- `scripts/check_docs_links.py` catches broken local docs links without network
  access.
- `bioprospector_doctor.py` checks schema/script/example health, public audit,
  forbidden tracked directories, and optional tool availability.
- `make release-check` runs tests, doctor checks, docs checks, examples, demo
  generation, root audit, and runtime audit.
- `gitleaks` is recommended before a public switch for current tree and history
  scanning.
- `.runtime/` is ignored and must stay reproducible from tracked inputs.

## Claim Boundary

Public outputs are design intelligence and prioritization. They are not:

- wet-lab protocols
- construct recipes
- production claims
- clinical claims
- target-host validation
- proof that a provider job completed
- proof that a sequence-similarity hit has the claimed biochemical function

Use `run-maturity-ledger.tsv` and
[`no-false-success-gates.md`](no-false-success-gates.md) to separate planning
from execution, joined evidence, and claim-audited closeout.

## Public Switch Checklist

Before changing visibility or pushing a public remote:

```bash
make switch-check
python3 scripts/public_audit.py .
python3 scripts/public_audit.py .runtime
git ls-files .runtime logs internal private
gitleaks dir . --no-banner --redact --verbose
gitleaks detect --source . --no-banner --redact --verbose
```

If any sensitive content ever reaches public history, do not repair it with a
normal follow-up commit. Re-create public history from a clean export and rotate
affected credentials outside the repo.
