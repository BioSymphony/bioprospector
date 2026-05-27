---
name: bioprospector
description: Use when planning or executing BioSymphony BioProspector campaigns for agentic biosynthetic pathway discovery, enzyme/gene candidate mining, pathway stitching, host-fit review, construct hypotheses, and evidence-led candidate compression.
---

# BioSymphony BioProspector

BioProspector is a local-first agentic harness for turning target molecules
and host constraints into biosynthetic route families, enzyme/gene mining
lanes, pathway-stitching review, construct hypotheses, and compact review
packages.

## Default Agent Flow

1. Read every Markdown note under `.bioprospector-memory/` if the folder exists. These are durable lessons captured by past agents on this user's machine. Treat them as agent-process guidance for this campaign, not as biology evidence or claim closeout.
2. Read `README.md`, `docs/QUICKSTART.md`, and `docs/AGENT_PLAYBOOK.md`.
3. Run `python3 skills/bioprospector/scripts/bioprospector_doctor.py`.
4. Choose a public example or scaffold a new campaign under `.runtime/`.
5. Run preflight and input audit before asking operator questions.
6. Generate local issue drafts with `--include-profile full-frontier` when a broad review graph is useful.
7. Build review artifacts: campaign graph, candidate package, route-frontier ranking, or review package.
8. Close out with claim level, blockers, generated paths, and confirmation that no provider launch, raw-data materialization, credential storage, or public publish occurred.

## Operating Model

Treat Symphony, Linear, RunPod, HPC, and AWS ElasticBLAST as optional
integrations. The public repo is a portable local skill kit; it should work for
new users without a private daemon, cloud account, issue tracker, or external
provider.

Use BioProspector as a local-first skill kit:

1. define target contract
2. audit declared inputs before asking operator questions
3. run a short operator-intake loop only for true gaps or confirmations
4. enumerate route universe
5. normalize reaction steps
6. create local issue-style drafts for route, step, candidate mining, controls, integration, and red-team lanes
7. use Dark Step Resolver lanes when genes, modules, or substeps are ambiguous
8. run heavy search only in approved local/remote workdirs
9. join inputs, execution artifacts, target evidence, controls, and claims
10. distill candidate intelligence from sequence pointers, public accessions, literature, and close canonical matches
11. build candidate package indexes, campaign graph edges, rankings, and Pareto route frontiers
12. run the metadata-only GeneCluster atlas planner when source, route, and genome-context ceilings matter
13. write structured dossier outputs that index real genes, candidates, clusters, evidence, packages, rejected rows, and route decisions
14. require claim levels and route-stitching review before recommending designs

## Required Check

Before accepting a campaign prep artifact, run:

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py

python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json

python3 skills/bioprospector/scripts/bioprospector_stage_contract.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
```

To prepare local issue-style planning drafts without dispatching workers or
touching an issue tracker:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/vanillin-yeast-v0/campaign-manifest.json \
  --prefix VANILLIN \
  --out .runtime/vanillin-linear-issues
```

To include wide/frontier evidence-lane children, RunPod prep drafts, and AWS ElasticBLAST prep drafts:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/nootkatone-linear-issues \
  --include-evidence-lanes \
  --include-runpod-prep \
  --include-elasticblast-prep \
  --include-literature-lanes \
  --include-ambiguity-lanes \
  --include-enzyme-family-sweeps \
  --include-genome-mining-lanes \
  --include-structure-risk-lanes \
  --include-host-comparison-lanes \
  --include-assay-handoff-lanes \
  --include-monitoring-lanes \
  --include-stage-contract-lanes \
  --include-input-audit-lanes \
  --include-operator-intake-lanes \
  --include-maturity-lanes \
  --include-target-evidence-lanes \
  --include-decoy-control-lanes \
  --include-self-check-lanes \
  --include-provider-lanes \
  --include-provider-preflight-lanes \
  --include-framework-lanes \
  --include-sequence-search-lanes \
  --include-candidate-package-lanes \
  --include-candidate-intelligence-lanes \
  --include-genecluster-atlas-lanes \
  --include-self-learning-lanes
```

To validate the public Huperzine A dark-step/source-context frontier demo:

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json
```

To create a new compact reviewed campaign scaffold:

```bash
python3 skills/bioprospector/scripts/bioprospector_new_campaign.py \
  --target-contract templates/target-contract.example.json \
  --out .runtime/scaffolds/example-target-v0 \
  --campaign-id example-target-v0
```

To export a compact dossier:

```bash
python3 skills/bioprospector/scripts/bioprospector_dossier_export.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/dossiers/huperzine-frontier-public-v0.md
```

To compile the campaign graph, package candidate indexes, run Pareto ranking,
and export a sidecar-aware dossier:

```bash
python3 skills/bioprospector/scripts/bioprospector_campaign_status.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/campaign-status/huperzine-frontier-public-v0.md \
  --format markdown

python3 skills/bioprospector/scripts/bioprospector_handoff_packet.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/handoffs/huperzine-frontier-public-v0 \
  --prefix HUPERZINE \
  --profile public-demo

python3 skills/bioprospector/scripts/bioprospector_agent_brief.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/agent-briefs/huperzine-frontier-public-v0 \
  --prefix HUPERZINE \
  --profile public-demo \
  --mode goal \
  --agent codex

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

python3 skills/bioprospector/scripts/bioprospector_pareto_rank.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/rankings/nootkatone-yeast-v0

python3 skills/bioprospector/scripts/bioprospector_dossier_export.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --sidecar-dir .runtime/candidate-packages/huperzine-frontier-public-v0 \
  --out .runtime/dossiers/huperzine-frontier-public-v0.md
```

To smoke-test public sidecars without launching anything:

```bash
python3 skills/bioprospector/scripts/bioprospector_public_demo_smoke.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/public-demo-smoke/nootkatone \
  --skip-provider-bundles
```

After an operator-owned run has copied compact after-run artifacts into an
ignored local runtime folder, build a redacted retrospective ledger:

```bash
python3 skills/bioprospector/scripts/bioprospector_retrospective.py \
  --root .runtime \
  --out .runtime/retrospective-ledger.tsv
```

Before worker questions, audit declared inputs:

```bash
python3 skills/bioprospector/scripts/bioprospector_input_audit.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
```

Then ask only the minimum necessary operator questions. If the operator says
`skip and go`, continue planning with explicit assumptions in
`operator-intake-ledger.tsv`; do not treat skipped assumptions as approval for
live execution or final claim closeout.

Before declaring any live campaign successful, run the joined contract self-check:

```bash
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py \
  --campaign path/to/live/campaign-manifest.json \
  --require-real-execution \
  --require-target-evidence \
  --require-decoy-controls \
  --require-maturity L5
```

To prepare a review-only RunPod readiness bundle without launching compute:

```bash
python3 skills/bioprospector/scripts/bioprospector_runpod_bundle.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0
```

To prepare a review-only AWS ElasticBLAST wide-search bundle without touching AWS:

```bash
python3 skills/bioprospector/scripts/bioprospector_elasticblast_bundle.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone-yeast-v0 \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

Optional Symphony sidecar reference:

- `../../docs/symphony-linear-sidecar.md`
- `../../templates/symphony-workflow-bioprospector.WORKFLOW.md`

## Reference Map

- Product foundation: `../../docs/product-foundation.md`
- Architecture: `../../docs/architecture.md`
- Quickstart: `../../docs/QUICKSTART.md`
- Workflow guide: `../../docs/WORKFLOWS.md`
- CLI reference: `../../docs/CLI_REFERENCE.md`
- Privacy and security model: `../../docs/PRIVACY_SECURITY_MODEL.md`
- Modes: `../../docs/MODES.md`
- Agent install: `../../docs/AGENT_INSTALL.md`
- First campaign: `../../docs/FIRST_CAMPAIGN.md`
- Capability map: `../../docs/capability-map.md`
- Dossier schema: `../../docs/dossier-schema.md`
- RunPod stack: `../../docs/runpod-stack.md`
- AWS ElasticBLAST stack: `../../docs/aws-elasticblast-stack.md`
- Compute provider strategy: `../../docs/compute-provider-strategy.md`
- Ambiguity workflows: `../../docs/ambiguity-workflows.md`
- Enzyme family search: `../../docs/enzyme-family-search.md`
- Genome-context mining: `../../docs/genome-context-mining.md`
- GeneCluster atlas public lane: `../../docs/genecluster-atlas-public-lane.md`
- Host and structure risk: `../../docs/host-structure-risk.md`
- Monitoring and provenance: `../../docs/monitoring-provenance.md`
- Stage progress and provider preflight: `../../docs/stage-progress-and-provider-preflight.md`
- Operator intake: `../../docs/operator-intake.md`
- No-false-success gates: `../../docs/no-false-success-gates.md`
- Dossier header contracts: `../../docs/dossier-schema.md`
- Tool stack: `../../docs/tool-stack.md`
- Opportunity radar: `../../docs/opportunity-radar.md`
- Opportunity lane runbooks: `references/opportunity-lane-runbooks.md`
- Future campaign references: `../../docs/future-campaigns.md`
- RunPod readiness: `references/runpod-readiness.md`
- RunPod BLAST and candidate package: `../../docs/runpod-blast-candidate-package.md`
- Target modularity: `../../docs/target-modularity.md`
- Self-learning skill runbook: `../../docs/self-learning-skill-runbook.md`
- Shared ledger schema: `../../schemas/bioprospector-ledgers.json`
- Linear issue template: `../../templates/linear-issue.md`
- Full frontier readiness: `references/campaigns/full-frontier-readiness.md`
- Campaign: `references/campaigns/pathway-big-bang.md`
- Campaign: `references/campaigns/enzyme-frontier.md`
- Campaign: `references/campaigns/pathway-stitcher.md`
- Public demo: `examples/huperzine-frontier-public-v0`

## Campaign Modes

- `pathway_big_bang`: route explosion and unknown-step discovery
- `enzyme_frontier`: broad candidate mining per step
- `dark_step_resolver`: unknown-gene, multi-gene, hidden-step, and counterevidence reasoning
- `genome_context`: anchor, neighborhood, and BGC-context evidence planning
- `pathway_stitcher`: route assembly and host-fit review
- `red_team`: claim audit and kill criteria
- `dossier_export`: structured final package

## Claim Policy

Do not write "produces", "completes", or "validated in host" unless direct evidence supports that exact claim.

Runner flags such as `--search`, `--analyze`, `--full-run`, or generated issue
status are intent only. Success requires artifacts joined back to declared
inputs. Mock and dry-run outputs must carry `mock_tools: true` or
`dry_run: true` and cannot satisfy real execution gates.

Prefer:

- candidate
- hypothesized
- domain-supported
- ortholog-supported
- characterized elsewhere
- validated elsewhere

Promotion gates:

- reference hits and public database matches are not target organism/sample evidence
- wide/frontier searches need decoy or negative-control gates before promotion
- use the maturity ladder: L0 plan, L1 tools, L2 inputs, L3 execution, L4 evidence joined, L5 claim-audited review package
- use stage contracts and progress ledgers for long runs; provider `RUNNING` or desired state is intent only
- tool proof cannot replace execution artifact proof, and mock/dry-run proof cannot satisfy L3
- L5 needs materialized provider package indexes, sequence checksums, cluster membership, joined evidence events, and Pareto/ranking joins
- fail before paid compute if image pull, private registry auth, network volume, payload, snapshot, budget, secrets, or stage contracts are not ready
- record tool versions, build dates, database snapshot dates, and the parameters used in `evidence_event_ledger.tsv` so claims are version-anchored; a BLAST `nr` hit from six months ago is not the same claim as one from today, and a memory note about a tool quirk is only useful if the version it bit you on is captured

## Useful Sequence Intelligence

BioProspector should extract ranking-useful candidate intelligence before it asks
for deeper modeling or wet-lab planning. Candidate-intelligence planning is
default-on in issue drafts so agents do not forget it when a user asks for
reference enzymes, variant annotations, signal peptides, PTMs, or
canonical-match inference. Use
`candidate_intelligence_ledger` for facts and inferences such as:

- publicly reported/reference enzymes and variant annotations from accession-backed literature
- signal peptides, transit peptides, transmembrane regions, localization, PTM or glycosylation watchouts, cofactors, oligomer state, motifs, and expression-context risks
- what can and cannot be inferred from a candidate's close canonical enzyme match
- ranking impact: use as anchor, prioritize, deprioritize, review, preserve, park, block, or not applicable

This lane is deliberately flexible. It should make candidates more useful to a
route designer, but it is not docking, assay design, construct design, wet-lab
protocol generation, or target-host validation.

If the operator explicitly asks for it, or if the campaign scope requires those
answers for ranking, the lane may run lightweight candidate intelligence tools
or public accession/literature lookups: SignalP/TMHMM-style
signal/transmembrane predictors, localization/PTM/cofactor/motif annotators, or
operator-approved reference-variant extraction. Treat tool/API execution as
preflight-gated, not silently automatic. Before running on RunPod,
neocloud, HPC, cloud VM, or local-full, require provider preflight rows for
`candidate_intelligence_tools`, `public_api_access`, `provider_egress_policy`,
`tool_execution_proof`, `data_policy`, `workdir`, and `stage_contract` when
applicable. Return only `candidate_intelligence_ledger`,
`literature_search_ledger`, citations/accessions, checksums, tool versions, and
compact summaries.

## Self-Learning Skill

When a BioProspector run stalls, falls back, fails a gate, burns unexpected
budget, produces ambiguous rankings, or reveals a repeated workflow gap, use
`../../docs/self-learning-skill-runbook.md`. Capture the hiccup as a falsifiable
process hypothesis in `self-learning-skill-ledger.tsv`: observation, probe,
baseline/control, expected signal, stop-loss, result, and decision. Promote
reusable lessons into runbooks, this skill, templates, validators, or issue
lanes. A learning row is process intelligence only; it does not prove biology,
target evidence, provider readiness, or claim closeout.

## Local Memory

The campaign-scoped `self-learning-skill-ledger.tsv` is for audit. For lessons
that should change agent behavior on the user's machine across campaigns,
write a short Markdown note to `.bioprospector-memory/YYYY-MM-DD-<slug>.md`.
That folder is gitignored, so notes stay on the user's machine and never
leak back to the public repo.

Write a note when you hit and resolve a non-obvious issue: a provider auth
flake, a missing input the user always forgets, a ledger column the agent
keeps misreading, a flag combination that actually worked, an install gotcha,
or a closeout step that would have caught a problem earlier. Five short
sections: what happened, what was tried, what worked, when this applies,
what to skip. No secrets, no private paths, no campaign-specific data, no
raw sequences, no provider identifiers, no signed URLs.

See `references/memory-note-template.md` for the shape. At the start of every
campaign (step 1 above), read all notes under `.bioprospector-memory/` so
the next campaign starts smarter than the last.

## Heavy Data Policy

No raw reads, private sequences, BLAST databases, genome mirrors, model weights, or large search outputs belong in this repo. Use external workdirs and return compact ledgers, hashes, citations, and summaries.

Use RunPod manual Pods as one reviewed optional path for controlled heavy search
lanes and candidate compression. AWS ElasticBLAST may be a reviewed escalation
only when official NCBI BLAST database scale is actually needed and budget,
quota, S3, cleanup, and query-data approvals are recorded outside this repo.
Local compute, SSH/HPC, generic cloud VMs, neocloud VMs, and managed workflow
services may be approved for a specific compatible role only if they preserve the
same input audit, execution-artifact, target-evidence, decoy-control, maturity,
stage-progress, and self-check contracts. Never submit ElasticBLAST jobs until
approvals are recorded.
Private registry images must not be treated as launch-ready until provider-side
pull auth is verified outside this repo and Linear. Any fallback from RunPod to
local, real data to mock, target evidence to reference-only evidence, or full
route to rescue route must close as partial/degraded unless a new claim boundary
is explicitly approved.

For RunPod BLAST/search package runs, require first-class rows for
`tool_registry_ledger`, `adapter_contract_ledger`, `evidence_event_ledger`,
`tool_execution_proof_ledger`, `sequence_search_plan_ledger`, `candidate_sequence_ledger`,
`domain_annotation_ledger`, `candidate_intelligence_ledger`, `literature_search_ledger`,
`candidate_diversity_ledger`, `candidate_graph_ledger`,
`candidate_ranking_ledger`, `pareto_frontier_ledger`, and
`run_output_package_ledger`. Return graph edges, AA-sequence pointers,
checksums, cluster membership, domain maps, citations, and compact summaries. Do not return raw
all-hit outputs, unrestricted FASTA dumps, database mirrors, full-text
literature, or private sequences to the repo.
