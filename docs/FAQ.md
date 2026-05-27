# FAQ

## Do I need Symphony, Linear, RunPod, AWS, or HPC?

No. The public repo runs locally by default. Optional integrations are modeled
as readiness contracts and review-only drafts unless an operator separately
approves real execution outside this repo.

| Thing | Required for quickstart? | Public repo behavior |
| --- | --- | --- |
| Symphony | No | Generates portable local issue-style drafts. |
| Linear | No | Writes Markdown issue bodies under `.runtime/`; it does not create issues. |
| RunPod/HPC | No | Builds preflight/readiness bundles only. |
| AWS ElasticBLAST | No | Builds reviewable config bundles only. |
| BLAST/MMseqs2/HMMER/Foldseek | No | Optional external tools; local examples use compact ledgers. |
| Private sequences or raw reads | No | Keep them outside the repo and pass only secure pointers or summaries. |

## What should I run first?

Run:

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime
make local-demo
```

Then inspect `.runtime/local-demo/huperzine/dossier.md` and continue with
[`QUICKSTART.md`](QUICKSTART.md). Use [`WORKFLOWS.md`](WORKFLOWS.md) when you
want to choose between local planning, tracker mirroring, cloud readiness, and
live-run closeout.

## How does this help a team using Linear?

BioProspector can generate a local Markdown work graph with dependencies,
budgets, kill criteria, validation commands, and claim boundaries. A team can
review those drafts, then copy selected items into Linear or another tracker.
The public repo does not call Linear APIs or create issues by itself.

Start with:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-workgraph \
  --include-profile full-frontier
```

Then read [`symphony-linear-sidecar.md`](symphony-linear-sidecar.md) and the
tracker workflow in [`WORKFLOWS.md`](WORKFLOWS.md#4-linear-or-tracker-mirror).

## Can I use cloud resources?

Yes, but the public repo stops at readiness unless an operator separately runs
approved work outside the repo. RunPod, HPC, cloud VMs, neocloud VMs, and AWS
ElasticBLAST all have to preserve the same ledgers, stage progress,
execution-artifact proof, target-evidence joins, controls, and final self-check.

Cloud readiness bundles answer what would be needed before launch; they do not
launch resources:

```bash
python3 skills/bioprospector/scripts/bioprospector_runpod_bundle.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0
```

See [`WORKFLOWS.md`](WORKFLOWS.md#5-cloud-readiness) and
[`compute-provider-strategy.md`](compute-provider-strategy.md).

## Is this a wet-lab protocol generator?

No. BioProspector produces planning intelligence: route hypotheses, candidate
shortlists, evidence ledgers, provider-readiness checks, and claim-bounded
dossiers. It does not validate biological function, design wet-lab protocols,
or prove production in a host.

## What can safely go in the repo?

Use compact, public-safe material:

- accession IDs, public citation IDs, checksums, and source names
- derived summaries, claim levels, caveats, and review notes
- small synthetic fixtures and expected-output snapshots
- local issue drafts and dossier summaries under ignored `.runtime/`

Do not commit credentials, provider IDs, private paths, private or unpublished
sequences, raw reads, full BLAST output, genome mirrors, large databases, model
weights, or proprietary full text.

## How should an agent use this repo?

Point the agent at the checkout and ask for artifacts, not open-ended prose:

```text
Use the bioprospector skill in this checkout. Run doctor, keep everything local,
and create a public-safe first campaign for <target molecule> in <host>. Do not
store raw sequences, credentials, provider identifiers, or private paths.
```

More prompts are in [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md).

## Why are there so many ledgers?

The ledgers make broad biological search work auditable. They keep route
hypotheses, candidates, evidence events, controls, execution artifacts, and
claim levels joinable instead of burying them in prose. See
[`GLOSSARY.md`](GLOSSARY.md) for the core terms.

## What makes a result stronger?

The maturity ladder is:

- `L0`: plan only
- `L1`: tools selected
- `L2`: inputs declared
- `L3`: execution artifacts captured
- `L4`: evidence joined to declared inputs
- `L5`: claim-audited dossier

Public examples intentionally stay at planning/review levels unless they carry
real, joined execution artifacts and claim review.

## How do I prepare for a future public switch?

Run:

```bash
make release-check
gitleaks dir . --no-banner --redact --verbose
gitleaks detect --source . --no-banner --redact --verbose
```

Then follow [`PUBLIC_SWITCH_CHECKLIST.md`](PUBLIC_SWITCH_CHECKLIST.md). Staying
local is the default; no command in the quickstart publishes the repo.
