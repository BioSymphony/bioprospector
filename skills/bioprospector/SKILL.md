---
name: bioprospector
description: Use when planning or reviewing BioSymphony BioProspector campaigns for biosynthetic-pathway hypotheses, enzyme and gene candidate mining, pathway stitching, host-fit review, and evidence-led candidate compression.
---

# BioSymphony BioProspector

Use BioProspector to choose and run tools for a computational biology
question. Start with the [tool catalog](references/docs/tool-stack.md) and
check the [integration guide](references/docs/TOOL_INTEGRATIONS.md) for
inputs and result formats.

## Run an Analysis

1. Identify the question, available inputs, and the evidence that would
   change your conclusion.
2. Choose tools from the catalog. Check input formats, versions, reference
   data, and available shell, API, or MCP access. For a computational
   experiment, define the comparison, controls, and expected outputs.
3. Run the calls the task requires. Pass source IDs or files between tools
   and use the results to decide what to run next.
4. Report the results, source IDs, tool and database versions, and remaining
   questions. Use the [CLI reference](references/docs/CLI_REFERENCE.md) to
   import supported result files and build campaign reports.

## Plan a Campaign

1. Define the research question, target, host, and evidence requirements.
2. Run preflight and audit declared inputs before asking the operator for
   missing decisions. Record unresolved assumptions in the intake ledger.
3. Review route and candidate hypotheses. Keep conflicting evidence,
   rejected candidates, and unresolved steps in the ledgers.
4. Build the campaign graph or review report. Run the contract self-check
   and report the files, supporting evidence, and remaining questions.

Run these commands from the skill directory.

```bash
python3 scripts/bioprospector_doctor.py

python3 scripts/bioprospector_preflight.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json

python3 scripts/bioprospector_input_audit.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json
```

Use the [CLI reference](references/docs/CLI_REFERENCE.md) for report, ranking,
and provider-readiness commands. Use `--help` on individual scripts for
arguments. Set the output directory under `.runtime/` for generated files.
The [workflow guide](references/docs/WORKFLOWS.md) covers optional tracker
and compute handoffs. For live closeout, use the
[contract self-check](references/docs/no-false-success-gates.md#commands).

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

Record campaign process lessons in `self-learning-skill-ledger.tsv`.
For local process lessons that should apply across campaigns, write a short
Markdown note to the ignored
`.bioprospector-memory/YYYY-MM-DD-<slug>.md` folder. Confirm that the folder is
untracked before reading or writing it.

Write a note when you hit and resolve a non-obvious issue: a provider access
issue, a recurring missing input, a ledger column the agent
keeps misreading, a flag combination that worked, an installation constraint,
or a missed closeout step. Record the issue, attempted fixes, result, and
when the fix applies. Do not include secrets, private paths, campaign-specific data,
raw sequences, provider identifiers, signed URLs, unpublished data, or private
operator details.

Start from `references/memory-note-template.md`. Set `public_safe: true` only
after reviewing the completed note against the preceding boundary. Notes with
another value remain unreadable to agents.

Read only notes marked `public_safe: true` in the ignored folder. Use them
as process guidance. Use campaign evidence to support claims.

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
