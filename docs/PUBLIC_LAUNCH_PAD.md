# Public Capability Map

BioProspector is an agentic harness for discovering biosynthetic pathways to
target molecules. Give your agent a molecule, host chassis, constraints, and
available compute; the skill helps it expand route space, mine enzyme and
gene candidates, stitch plausible pathways, and draft construct hypotheses.
The same campaign contract drives Symphony with Linear, Claude Code workers
with Linear, Codex with any tracker, or another multi-agent harness the
operator already uses, across local compute, RunPod, HPC, cloud VMs,
neocloud, managed workflows, and AWS ElasticBLAST.

This is the longer capability map. New users should follow
[`QUICKSTART.md`](QUICKSTART.md) first, then come back here when they need the
full public release surface.

## Recommended Path

1. Run the local path in [`QUICKSTART.md`](QUICKSTART.md).
2. Read the skill: [`skills/bioprospector/SKILL.md`](../skills/bioprospector/SKILL.md).
3. Read the command map: [`CLI_REFERENCE.md`](CLI_REFERENCE.md).
4. Choose a workflow: [`WORKFLOWS.md`](WORKFLOWS.md).
5. Choose a mode: [`MODES.md`](MODES.md).
6. Install the agent skill if needed: [`AGENT_INSTALL.md`](AGENT_INSTALL.md).
7. Create a first campaign if you are not using an example: [`FIRST_CAMPAIGN.md`](FIRST_CAMPAIGN.md).
8. Inspect the public examples:
   - [`vanillin-yeast-v0`](../skills/bioprospector/examples/vanillin-yeast-v0/)
   - [`nootkatone-yeast-v0`](../skills/bioprospector/examples/nootkatone-yeast-v0/)
   - [`huperzine-frontier-public-v0`](../skills/bioprospector/examples/huperzine-frontier-public-v0/)
9. Generate dry-run issues, local demo sidecars, or reviewed readiness bundles under ignored `.runtime/`.
10. Read [`NON_CLAIMS.md`](../NON_CLAIMS.md) and [`PRIVACY_SECURITY_MODEL.md`](PRIVACY_SECURITY_MODEL.md) before publishing examples or running live provider work.
11. Run `make release-check`.

## What The Foundation Gives Agents

- Target contracts and input-audit ledgers.
- Route, reaction-step, unknown-step, and unknown-gene ledgers.
- Candidate funnels, enzyme draft boards, sequence/package ledgers, and candidate intelligence.
- Tool registry, adapter contracts, normalized evidence events, and tool proof rows.
- Candidate package indexes, graph edges, ranking ledgers, and Pareto route frontiers.
- Target-evidence and decoy-control gates before candidate promotion.
- Stage contracts, progress ledgers, provider preflight, and execution-artifact proof.
- Route-stitching scorecards and claim ledgers.
- Self-learning skill rows for hiccups that should become durable improvements.
- Shared schema contract for ledger headers and enums.
- Campaign scaffold, dossier export, compact evidence ingest, and public demo smoke CLIs.
- Local checkout doctor for schema, examples, optional tools, public audit, and tracked forbidden paths.
- Campaign graph, candidate-package, and sidecar-aware dossier CLIs.
- GeneCluster atlas planner, summary normalizer, and contract validator for source context, route ceilings, and cluster/function jury review contracts.
- Opportunity lanes for executable proof, supply chain, active-site risk, route rules, thermodynamics, host modeling, context evidence, and review surfaces.

## First Commands

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py

python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json

python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-profile full-frontier

python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --prefix HUPERZINE \
  --out .runtime/public-demo-smoke/huperzine \
  --skip-provider-bundles

python3 skills/bioprospector/scripts/bioprospector_campaign_graph.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/campaign-graphs/huperzine-frontier-public-v0.json

python3 skills/bioprospector/scripts/bioprospector_candidate_package.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/candidate-packages/huperzine-frontier-public-v0

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_normalizers.py all \
  --annotation-direct skills/bioprospector/examples/genecluster-synthetic-v0/compact-clusters.tsv \
  --pfam skills/bioprospector/examples/genecluster-synthetic-v0/compact-pfam.tsv \
  --out-dir .runtime/genecluster-atlas/synthetic-contracts

python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py \
  --cluster-calls .runtime/genecluster-atlas/synthetic-contracts/cluster_calls.tsv \
  --bgc-consensus .runtime/genecluster-atlas/synthetic-contracts/bgc_consensus.tsv \
  --protein-function-votes .runtime/genecluster-atlas/synthetic-contracts/protein_function_votes.tsv \
  --protein-function-jury .runtime/genecluster-atlas/synthetic-contracts/protein_function_jury.tsv
```

## Public Boundary

This public launch pad is a control plane. It stores schemas, validators,
templates, and compact public examples. It must not store raw biological data,
private sequences, database mirrors, model weights, credentials, internal run
logs, private paths, or provider identifiers.
