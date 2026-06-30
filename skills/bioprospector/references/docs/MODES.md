# BioProspector Modes

BioProspector is local-first. The same ledgers can describe future provider
work, but this public repo ships only planning, review, validation, and
readiness helpers.

For a task-oriented chooser across local, agent, tracker, cloud-readiness, and
live-closeout paths, see [`WORKFLOWS.md`](WORKFLOWS.md).

## Local Planning

Use this mode for new campaigns, examples, issue drafts, graph exports,
candidate packages, Pareto ranking, and dossiers.

```bash
python3 scripts/bioprospector_doctor.py
python3 scripts/bioprospector_preflight.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json
```

This mode does not call providers, download biological databases, or write
outside the checkout except ignored `.runtime/` artifacts you request.

## Local Demo

Use this when evaluating the repo quickly.

```bash
make local-demo
```

It produces a campaign graph, metadata-only GeneCluster atlas plan, synthetic
atlas checks, candidate package, Pareto frontier, and compact dossier under
`.runtime/`. Compare the shape with
[`../demos/expected-outputs`](../demos/expected-outputs).

## Agent Skill Mode

Use this mode when installing the BioProspector skill into another local agent
environment. The skill points agents to the same scripts, schemas, examples,
and safety rules in this checkout. See [`AGENT_INSTALL.md`](AGENT_INSTALL.md).

## Provider Readiness Review

RunPod, HPC, and AWS ElasticBLAST docs and bundles are review-only. They create
plans, manifests, and preflight rows. They do not create pods, submit jobs,
upload queries, download raw results, or handle credentials.

```bash
python3 scripts/bioprospector_elasticblast_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

Provider probe reports redact profile, bucket, IAM user, stack, and compute
environment names by default. Use explicit opt-in only for local private review.

## Public Switch Mode

Before publishing, run the release gate and inspect the switch checklist.

```bash
make switch-check
sed -n '1,220p' docs/PUBLIC_SWITCH_CHECKLIST.md
```

The public switch gate is about repository hygiene. It is not evidence that a
biological campaign succeeded.
