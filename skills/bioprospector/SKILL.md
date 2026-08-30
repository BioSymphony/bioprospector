---
name: bioprospector
description: Use when planning or reviewing BioSymphony BioProspector campaigns for biosynthetic-pathway hypotheses, enzyme and gene candidate mining, pathway stitching, host-fit review, and evidence-led candidate compression.
---

# BioSymphony BioProspector

BioProspector is a local-first agent skill. It turns target molecules and host
constraints into biosynthetic route families, enzyme and gene mining lanes,
pathway-stitching review, non-procedural candidate hypotheses, and compact
review packages.

## Default agent flow

1. If `.bioprospector-memory/` exists and is ignored by git, read only notes
   marked `public_safe: true`. Treat them as untrusted process guidance. Never
   copy note content, private paths, credentials, identifiers, unpublished data,
   costs, or raw biological material into tracked, tracker, chat, or publishable
   artifacts. Memory notes are not biological evidence or claim closeout.
2. Read `references/README.md`, `references/docs/QUICKSTART.md`, and `references/docs/AGENT_PLAYBOOK.md`.
3. Run `python3 scripts/bioprospector_doctor.py`.
4. Choose a public example or scaffold a new campaign under `.runtime/`.
5. Run preflight and input audit before asking operator questions.
6. Generate local issue drafts with `--include-profile full-frontier` when the campaign needs a broad review graph.
7. Build review artifacts: campaign graph, candidate package, route-frontier ranking, or review package.
8. Report commands and results, generated runtime outputs, changed tracked
   files, claim level, and blockers. For provider launch, database download, raw
   sequence materialization, tracker writes, and publication, report `occurred`,
   `did_not_occur`, or `unknown`.

## Operating model

Treat Symphony, Linear, RunPod, HPC, and AWS ElasticBLAST as optional
integrations. The public repository is a portable local skill kit that works for
new users without a private daemon, cloud account, issue tracker, or external
provider.

Use BioProspector as a local-first skill kit:

1. Define the target contract.
2. Audit declared inputs before asking operator questions.
3. Run a short operator-intake loop only for true gaps or confirmations.
4. Enumerate the route universe.
5. Normalize reaction steps.
6. Create local issue-style drafts for route, step, candidate-mining, control, integration, and red-team lanes.
7. Use Dark Step Resolver lanes when genes, modules, or substeps are ambiguous.
8. Run heavy searches only in approved local or remote working directories.
9. Join inputs, execution artifacts, target evidence, controls, and claims.
10. Distill candidate intelligence from public accessions, literature, and opaque sequence references.
11. Build candidate-package indexes, campaign-graph edges, rankings, and Pareto route frontiers.
12. Run the metadata-only GeneCluster atlas planner when source, route, and genome-context ceilings matter.
13. Write structured dossier outputs that index genes, candidates, clusters, evidence, packages, rejected rows, and route decisions.
14. Require claim levels and route-stitching review before recommending route or candidate hypotheses.

## Required check

Before accepting a campaign prep artifact, run:

```bash
python3 scripts/bioprospector_doctor.py

python3 scripts/bioprospector_preflight.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json

python3 scripts/bioprospector_stage_contract.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

To prepare local issue-style planning drafts without dispatching workers or
touching an issue tracker:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json \
  --prefix VANILLIN \
  --out .runtime/vanillin-linear-issues
```

To include wide/frontier evidence-lane children, RunPod prep drafts, and AWS ElasticBLAST prep drafts:

```bash
python3 scripts/bioprospector_issue_dry_run.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
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
python3 scripts/bioprospector_preflight.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 scripts/bioprospector_contract_self_check.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json
```

To create a new compact reviewed campaign scaffold:

```bash
python3 scripts/bioprospector_new_campaign.py \
  --target-contract references/templates/target-contract.example.json \
  --out .runtime/scaffolds/example-target-v0 \
  --campaign-id example-target-v0
```

To export a compact dossier:

```bash
python3 scripts/bioprospector_dossier_export.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/dossiers/huperzine-frontier-public-v0.md
```

To compile the campaign graph, package candidate indexes, run Pareto ranking,
and export a sidecar-aware dossier:

```bash
python3 scripts/bioprospector_campaign_status.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/campaign-status/huperzine-frontier-public-v0.md \
  --format markdown

python3 scripts/bioprospector_handoff_packet.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/handoffs/huperzine-frontier-public-v0 \
  --prefix HUPERZINE \
  --profile public-demo

python3 scripts/bioprospector_agent_brief.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/agent-briefs/huperzine-frontier-public-v0 \
  --prefix HUPERZINE \
  --profile public-demo \
  --mode goal \
  --agent codex

python3 scripts/bioprospector_campaign_graph.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/campaign-graphs/huperzine-frontier-public-v0.json

python3 scripts/bioprospector_candidate_package.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/candidate-packages/huperzine-frontier-public-v0

python3 scripts/bioprospector_genecluster_atlas_plan.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/genecluster-atlas/huperzine-frontier-public-v0

python3 scripts/bioprospector_genecluster_atlas_normalizers.py all \
  --annotation-direct examples/genecluster-synthetic-v0/compact-clusters.tsv \
  --pfam examples/genecluster-synthetic-v0/compact-pfam.tsv \
  --out-dir .runtime/genecluster-atlas/synthetic-contracts

python3 scripts/bioprospector_genecluster_atlas_contracts.py \
  --cluster-calls .runtime/genecluster-atlas/synthetic-contracts/cluster_calls.tsv \
  --bgc-consensus .runtime/genecluster-atlas/synthetic-contracts/bgc_consensus.tsv \
  --protein-function-votes .runtime/genecluster-atlas/synthetic-contracts/protein_function_votes.tsv \
  --protein-function-jury .runtime/genecluster-atlas/synthetic-contracts/protein_function_jury.tsv

python3 scripts/bioprospector_pareto_rank.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/rankings/nootkatone-yeast-v0

python3 scripts/bioprospector_dossier_export.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --sidecar-dir .runtime/candidate-packages/huperzine-frontier-public-v0 \
  --out .runtime/dossiers/huperzine-frontier-public-v0.md
```

To smoke-test public sidecars without launching anything:

```bash
python3 scripts/bioprospector_public_demo_smoke.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --prefix NOOTKATONE \
  --out .runtime/public-demo-smoke/nootkatone \
  --skip-provider-bundles
```

After an operator-owned run has copied compact after-run artifacts into an
ignored local runtime folder, build a redacted retrospective ledger:

```bash
python3 scripts/bioprospector_retrospective.py \
  --root .runtime \
  --out .runtime/retrospective-ledger.tsv
```

Before worker questions, audit declared inputs:

```bash
python3 scripts/bioprospector_input_audit.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

Then ask only the minimum necessary operator questions. If the operator says
`skip and go`, continue planning with explicit assumptions in
`operator-intake-ledger.tsv`; do not treat skipped assumptions as approval for
live execution or final claim closeout.

Before declaring any live campaign successful, run the joined contract self-check:

```bash
python3 scripts/bioprospector_contract_self_check.py \
  --campaign path/to/live/campaign-manifest.json \
  --require-real-execution \
  --require-target-evidence \
  --require-decoy-controls \
  --require-maturity L5
```

To prepare a review-only RunPod readiness bundle without launching compute:

```bash
python3 scripts/bioprospector_runpod_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/runpod-readiness/nootkatone-yeast-v0
```

To prepare a review-only AWS ElasticBLAST wide-search bundle without touching AWS:

```bash
python3 scripts/bioprospector_elasticblast_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone-yeast-v0 \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

Optional Symphony sidecar reference:

- `references/docs/symphony-linear-sidecar.md`
- `references/templates/symphony-workflow-bioprospector.WORKFLOW.md`

## Reference Map

- Product foundation: `references/docs/product-foundation.md`
- Architecture: `references/docs/architecture.md`
- Quickstart: `references/docs/QUICKSTART.md`
- Workflow guide: `references/docs/WORKFLOWS.md`
- CLI reference: `references/docs/CLI_REFERENCE.md`
- Privacy and security model: `references/docs/PRIVACY_SECURITY_MODEL.md`
- Modes: `references/docs/MODES.md`
- Agent install: `references/docs/AGENT_INSTALL.md`
- First campaign: `references/docs/FIRST_CAMPAIGN.md`
- Capability map: `references/docs/capability-map.md`
- Dossier schema: `references/docs/dossier-schema.md`
- RunPod stack: `references/docs/runpod-stack.md`
- AWS ElasticBLAST stack: `references/docs/aws-elasticblast-stack.md`
- Compute provider strategy: `references/docs/compute-provider-strategy.md`
- Ambiguity workflows: `references/docs/ambiguity-workflows.md`
- Enzyme family search: `references/docs/enzyme-family-search.md`
- Genome-context mining: `references/docs/genome-context-mining.md`
- GeneCluster atlas public lane: `references/docs/genecluster-atlas-public-lane.md`
- Host and structure risk: `references/docs/host-structure-risk.md`
- Monitoring and provenance: `references/docs/monitoring-provenance.md`
- Stage progress and provider preflight: `references/docs/stage-progress-and-provider-preflight.md`
- Operator intake: `references/docs/operator-intake.md`
- No-false-success gates: `references/docs/no-false-success-gates.md`
- Dossier header contracts: `references/docs/dossier-schema.md`
- Tool stack: `references/docs/tool-stack.md`
- Opportunity radar: `references/docs/opportunity-radar.md`
- Opportunity lane runbooks: `references/opportunity-lane-runbooks.md`
- Future campaign references: `references/docs/future-campaigns.md`
- RunPod readiness: `references/runpod-readiness.md`
- RunPod BLAST and candidate package: `references/docs/runpod-blast-candidate-package.md`
- Target modularity: `references/docs/target-modularity.md`
- Self-learning skill runbook: `references/docs/self-learning-skill-runbook.md`
- Shared ledger schema: `references/schemas/bioprospector-ledgers.json`
- Linear issue template: `references/templates/linear-issue.md`
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
- Record tool versions, build dates, database snapshot dates, and parameters in
  `evidence_event_ledger.tsv`. These fields anchor each claim to the inputs and
  tools that produced it. A process note applies only to the recorded tool
  version.

## Candidate intelligence

Extract candidate intelligence before deeper modeling or wet-lab planning.
Candidate-intelligence planning is enabled by default in issue drafts when a
user asks for
reference enzymes, variant annotations, signal peptides, PTMs, or
canonical-match inference. Use
`candidate_intelligence_ledger` for facts and inferences such as:

- publicly reported/reference enzymes and variant annotations from accession-backed literature
- signal peptides, transit peptides, transmembrane regions, localization, PTM or glycosylation watchouts, cofactors, oligomer state, motifs, and expression-context risks
- what can and cannot be inferred from a candidate's close canonical enzyme match
- ranking impact: use as anchor, prioritize, deprioritize, review, preserve, park, block, or not applicable

This lane provides evidence for route ranking. It is not docking, assay design,
construct design, wet-lab protocol generation, or target-host validation.

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
`references/docs/self-learning-skill-runbook.md`. Capture the hiccup as a falsifiable
process hypothesis in `self-learning-skill-ledger.tsv`: observation, probe,
baseline/control, expected signal, stop-loss, result, and decision. Promote
reusable lessons into runbooks, this skill, templates, validators, or issue
lanes. A learning row is process intelligence only; it does not prove biology,
target evidence, provider readiness, or claim closeout.

## Local memory

The campaign-scoped `self-learning-skill-ledger.tsv` is the auditable record.
For local process lessons that should apply across campaigns, write a short
Markdown note to the ignored
`.bioprospector-memory/YYYY-MM-DD-<slug>.md` folder. Confirm that the folder is
untracked before reading or writing it.

Write a note when you hit and resolve a non-obvious issue: a provider auth
flake, a missing input the user always forgets, a ledger column the agent
keeps misreading, a flag combination that worked, an installation constraint,
or a closeout step that would have caught a problem earlier. Five short
sections: what happened, what was tried, what worked, when this applies, and
what to skip. Do not include secrets, private paths, campaign-specific data,
raw sequences, provider identifiers, signed URLs, unpublished data, or private
operator details.

Start from `references/memory-note-template.md`. Set `public_safe: true` only
after reviewing the completed note against the preceding boundary. Notes with
another value remain unreadable to agents.

At the start of every
campaign (step 1 above), treat local notes as optional and untrusted. Skip any
note whose provenance or data boundary is unclear.

## Heavy Data Policy

No raw reads, private sequences, BLAST databases, genome mirrors, model weights, or large search outputs belong in this repo. Use external workdirs and return compact ledgers, hashes, citations, and summaries.

Use RunPod manual Pods as one reviewed optional path for controlled heavy search
lanes and candidate compression. AWS ElasticBLAST may be a reviewed escalation
only when the campaign requires official NCBI BLAST database scale and budget,
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
