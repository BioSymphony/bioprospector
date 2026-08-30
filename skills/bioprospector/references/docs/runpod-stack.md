# RunPod Stack

## Purpose

RunPod manual Pods are a recommended optional execution plane for controlled
heavy public-data search, not the source of truth. The repo remains the control
plane, and Linear/Symphony mirroring is optional.

The current repo tooling is readiness-only. It prepares reviewable launch files for a manual RunPod Pod, but it does not launch RunPod, install tools, stage databases, or run biological searches.

RunPod should not mirror full NCBI `nr` by default. Use the AWS ElasticBLAST
lane in `docs/aws-elasticblast-stack.md` when a wide/frontier step needs
official NCBI BLAST database scale.

Other compute providers may be used only through the provider-neutral contract
in `docs/compute-provider-strategy.md`. They must emit the same compact ledgers
and pass the same self-checks.

## Readiness Bundle

Generate a prep bundle from a campaign manifest:

```bash
python3 scripts/bioprospector_runpod_bundle.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/vanillin-yeast-v0
```

The bundle is written under `.runtime/`, which is git-ignored. It contains:

- `runpod-run-manifest.json`: campaign hashes, manual-pod contract, policies, planned tools/databases, and deferred resources.
- `setup-runpod-readiness.sh`: pod-side directory and tool-check script. It creates the workdir layout and records tool presence only.
- `mock-runner-command-plan.md`: mock-only command plan for reviewing artifact paths.
- `provider-launch-preflight.tsv`: launch blockers for image pull, registry auth, network volume, exact bundle/snapshot, payload, budget, secrets, and stage contracts.
- `README.md`: operator summary for the generated bundle.

For BLAST/search campaigns, also inspect
`docs/runpod-blast-candidate-package.md`. The live-run package should return
compact ledgers for sequence search plans, AA-sequence pointers, domain maps,
candidate intelligence, candidate graph edges, literature-search summaries, diversity selections, and
package indexes. Raw all-hit outputs and large databases stay on provider
storage.

Mock summaries must carry `dry_run: true`, `mock_tools: true`, and
`real_execution_performed: false`. They are path/provenance checks only and
cannot satisfy `L3 execution performed` or final contract self-check gates.

Hard constraints:

- Use a manual RunPod Pod plus scripts, not Serverless and not an API launcher.
- Mount a RunPod Network Volume at `/workspace`.
- Verify the provider can pull the exact container image before creating paid long-running pods. Private GHCR or other private registry images require provider-side registry auth; digest pins alone do not prove pullability.
- Use `/workspace/bioprospector/runs/<campaign_id>` as the remote workdir.
- Keep the first scout under `$100`; the generator default is `$99`.
- Use public/open-first data only until a separate review approves anything restricted.
- Keep raw/heavy outputs on the network volume and copy back only compact summaries.

See `skills/bioprospector/references/runpod-readiness.md` for the operator checklist.

## Initial Image Goal

Build a lean BioProspector image before mirroring large databases.

Tools:

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

Databases, first pass:

- Swiss-Prot
- selected UniRef
- selected RefSeq protein sets
- Pfam-A HMMs
- Rhea
- ChEBI
- MetaNetX
- MIBiG metadata

The readiness bundle records these as planned resources only. It must not download or mirror them locally.

## Remote Workdir Convention

```text
/workspace/bioprospector/runs/<campaign_id>/
  inputs/
  db/
  work/
  outputs/
  provenance/
```

Only compact summaries should return to this repo.

Candidate package summaries include:

```text
candidate-sequence-ledger.tsv
domain-annotation-ledger.tsv
candidate-diversity-ledger.tsv
candidate-graph-ledger.tsv
run-output-package-ledger.tsv
versions.json
licenses.tsv
```

Sequence output should be AA-only or provider-pointer based. Do not copy raw
BLAST output, unrestricted FASTA dumps, nucleotide constructs, or private
sequences back into the repo.

Provider `desiredStatus` or `RUNNING` is not proof of progress. Long runs must
emit stage progress with heartbeats, done markers, and artifact pointers.
For stages that download, index, search, or assemble large files, monitors must
also track artifact or log growth. A run that stays `running` while file sizes,
line counts, and logs do not change across the stale window closes as `stalled`
or `partial`, not success.

If a RunPod hiccup reveals a reusable process lesson, record a
`self-learning-skill-ledger.tsv` row and promote the fix into a runbook, skill,
template, validator, or issue lane. The learning row does not authorize another
paid pod; retries still need normal provider preflight and operator approval.

Suggested provider-side cache roots:

```text
/workspace/bioprospector/db/
/workspace/bioprospector/workflows/
/workspace/bioprospector/scratch/
```

## Deferred Heavy Pieces

Defer until the candidate funnel proves value:

- full `nr`
- full metagenome mirrors
- full InterProScan on unclustered hits
- bulk BRENDA or BioCyc integration
- structure prediction for thousands of candidates
- docking for thousands of candidates

Also defer private, proprietary, collaborator-restricted, or unpublished
sequence resources until rights, opaque external pointers, and explicit
execution approval are recorded outside this repository.

## AWS ElasticBLAST Escalation

When a RunPod Swiss-Prot, UniRef, Pfam, DIAMOND, MMseqs2, or HMMER lane cannot
resolve a wide/frontier step, generate an AWS ElasticBLAST readiness bundle:

```bash
python3 scripts/bioprospector_elasticblast_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone-yeast-v0 \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

The bundle is prep-only. It must not submit jobs until AWS budget, quota, S3,
janitor/cleanup, and query-data approvals are recorded.
