# BioProspector RunPod Readiness

Status: readiness contract v1
Last reviewed: 2026-08-30

This reference defines the prep-only RunPod handoff for BioProspector campaigns. It is for bundle review and pod readiness, not live execution.

RunPod manual Pods are one reviewed optional v0 heavy-search path. Other local, cloud,
neocloud, HPC, or managed workflow paths must use the same compute-provider,
workflow-framework, execution-artifact, and self-check ledgers.

## Generate A Bundle

```bash
python3 skills/bioprospector/scripts/bioprospector_runpod_bundle.py \
  --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/vanillin-yeast-v0
```

The generator writes only to `.runtime/` and does not launch RunPod, install packages, download databases, or run searches.

## Bundle Files

- `runpod-run-manifest.json`: review contract with source hashes, campaign summary, planned tools/databases, public/open-first data policy, and deferred resources.
- `setup-runpod-readiness.sh`: pod-side directory and tool-check script. It creates the standard folder layout and records missing/present tools.
- `mock-runner-command-plan.md`: mock-only commands for testing artifact paths and summary writing.
- `provider-launch-preflight.tsv`: blocking launch checks for image digest, registry auth, image pull, network volume, exact bundle/snapshot, stage contracts, payload, budget, and secrets.
- `README.md`: short operator guide for the generated bundle.

Mock summaries must explicitly include `dry_run: true`, `mock_tools: true`, and
`real_execution_performed: false`. They cannot satisfy live evidence or maturity
requirements.

## Manual RunPod Contract

- Use a manual RunPod Pod, not Serverless.
- Do not use a generated API launcher for v0.
- Mount the RunPod Network Volume at `/workspace`.
- Use `/workspace/bioprospector/runs/<campaign_id>` as the remote workdir.
- Keep the first scout below `$100`; stop before the configured budget is reached.
- Use a digest-pinned image before live execution. Placeholder image names are readiness-only.
- Verify provider-side image pull before launch. Private GHCR or other private registry images require provider-side registry auth outside repo, generated bundles, and Linear.
- Treat RunPod desired status or `RUNNING` as intent only; require stage progress and artifact proof.
- Require a no-progress stop-loss for long stages: monitor declared file sizes,
  line counts, log growth, and per-command timeouts; a heartbeat with no artifact
  growth is `stalled`, not progress.
- Keep heavy data and intermediate outputs on the network volume.
- Copy back only compact summaries, provenance, versions, license rows, and reviewed ledger updates.

## Public/Open-First Data Policy

Allowed first:

- public accessions
- open or openly documented reference databases
- derived summaries with citations
- checksums and opaque external pointers managed outside this repository

Not allowed without separate approval:

- private sequences
- unpublished constructs
- proprietary datasets
- collaborator-restricted data
- tokens, API keys, or credentials in repo files, `.env`, `env.sh`, generated bundles, or Linear issue bodies

## Planned Tool Stack

- MMseqs2
- DIAMOND
- BLAST+
- HMMER or pyhmmer
- seqkit
- NCBI Datasets CLI
- DuckDB
- Polars or pandas
- RDKit
- COBRApy
- Nextflow or Snakemake

The readiness setup script checks for these tools but does not install them.

## Planned Database Stack

First-pass public/open resources:

- Swiss-Prot
- selected UniRef
- selected RefSeq protein sets
- Pfam-A HMMs
- Rhea
- ChEBI
- MetaNetX
- MIBiG metadata

The bundle may name cache paths under `/workspace/bioprospector/db/`, but database staging is a separate reviewed action.

## Deferred Or Restricted Resources

Defer these until candidate funnels prove value and an execution issue explicitly approves the cost/license boundary:

- full `nr`
- full metagenome mirrors
- full InterProScan on unclustered hits
- bulk BRENDA or BioCyc integration
- structure prediction or docking for thousands of candidates
- private, proprietary, collaborator-restricted, or unpublished sequence resources

## Readiness Review

Before any live run:

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json

python3 -m json.tool .runtime/runpod-readiness/vanillin-yeast-v0/runpod-run-manifest.json
```

Then inspect the generated README, provider-launch preflight, and mock command
plan. If a manual pod is created, copy the bundle to the pod and run this from
the bundle directory:

```bash
bash setup-runpod-readiness.sh
```

Do not stage databases or run candidate searches from the readiness bundle alone.
