# BioProspector Capability Map

## Core Claim

BioSymphony BioProspector helps agents build a claim-bounded research graph for a molecule, plan public/provider-approved enzyme and route searches, and audit candidate-compression workflows into ranked planning outputs.

## Capabilities At A Glance

| Capability | Why it matters | Primary outputs |
| --- | --- | --- |
| Route explosion | Prevents the agent from anchoring on the first plausible pathway. | `route-universe.tsv`, `route-ledger.tsv`, `reaction-step-ledger.tsv` |
| Enzyme frontier | Turns each step into a ranked candidate-mining problem instead of a one-off literature guess. | `candidate-funnels.tsv`, `enzyme-draft-board.tsv`, `candidate-sequence-ledger.tsv` |
| Dark-step resolver | Keeps unknown chemistry, missing genes, multi-gene modules, and counterevidence visible. | `unknown-step-ledger.tsv`, `unknown-gene-hypothesis-ledger.tsv`, `pathway-inference-ledger.tsv` |
| Candidate package engine | Converts noisy search output into a portable package an agent can review, rank, and cite. | `run-output-package-ledger.tsv`, `candidate-graph-ledger.tsv`, `domain-annotation-ledger.tsv` |
| Pathway stitcher | Scores whether individually promising enzymes can actually form a coherent route. | `route-stitching-scorecard.tsv`, `candidate-ranking-ledger.tsv` |
| Pareto frontier | Returns several useful winners instead of pretending one route is the answer. | `pareto-frontier-ledger.tsv` |
| Agent work graph | Splits broad campaigns into bounded lanes with budgets, dependencies, kill criteria, and closeouts. | Linear-style Markdown drafts under `.runtime/` |
| Agent kickoff brief | Gives Codex, Claude Code, Symphony/Linear, or `/goal` workflows a campaign-specific starting prompt and command set. | `agent-brief.md`, `agent-goal-prompt.txt`, `agent-brief.json` |
| Cloud handoff | Converts a future heavy search into stage contracts, expected outputs, returned ledgers, and proof rows. | RunPod/HPC/cloud/ElasticBLAST readiness bundles |
| Dossier export | Gives humans a compact review package with claims, blockers, evidence summaries, and next lanes. | `dossier.md`, `claim-ledger.md`, `red-team-report.md` |

## 1. Pathway Big Bang

Start with one target and host. Expand into:

- known natural routes
- engineered routes
- fed-substrate routes
- de novo routes
- degradation routes run backward
- analog routes
- speculative missing-step routes

Output:

- `route-universe.tsv`
- `unknown-step-ledger.tsv`

Future review surface:

- `route-atlas.html`

## 2. Enzyme Frontier

Every reaction step gets its own candidate universe. Wide steps can plan reviewed searches over large candidate sets; narrow steps can go deeper on active-site and literature review.

Output:

- `candidate-sequence-ledger.tsv`
- `candidate-funnels.tsv`
- `enzyme-draft-board.tsv`
- `candidate-diversity-ledger.tsv`
- `candidate-graph-ledger.tsv`
- `rejected-candidates.tsv`

## 3. Dark Step Resolver

Missing chemistry becomes a first-class frontier:

- chemistry-first enzyme-class inference
- single-gene versus multi-gene hypotheses
- hidden substep decomposition
- reverse catabolism search
- analog substrate search
- promiscuous enzyme family search
- BGC neighborhood search
- host-native bypass search
- counterevidence and cheapest discriminating next-step planning

Output:

- `unknown-step-ledger.tsv`
- `pathway-inference-ledger.tsv`
- `unknown-gene-hypothesis-ledger.tsv`
- `assay-handoff-ledger.tsv`

## 4. Pathway Stitcher

Routes only survive if their selected enzymes connect chemically and fit the host.

Checks:

- intermediate compatibility
- stereochemistry
- cofactors
- compartment
- toxicity
- transport
- host-native side reactions
- missing protection steps

Output:

- `route-stitching-scorecard.tsv`
- `candidate-ranking-ledger.tsv`

Future review surface:

- `bottleneck-map.md`

## 5. Pareto Route Frontier

Always return multiple winners:

- minimal-gene route
- highest-evidence route
- clearest validation handoff route
- best host-fit route
- ambitious de novo route
- diversity-library route

Output:

- `pareto-frontier-ledger.tsv`

Future review surface:

- `minimal-designs.md`

## 5A. Candidate Package Engine

The final useful output is a package index that carries the campaign's
structured evidence. A campaign should return genes, candidate proteins,
accession and source, claim level, evidence class, sequence pointers,
cluster membership, domain maps, graph edges, rankings, rejected rows, and
package provenance.

Output:

- `tool-registry-ledger.tsv`
- `adapter-contract-ledger.tsv`
- `evidence-event-ledger.tsv`
- `tool-execution-proof-ledger.tsv`
- `run-output-package-ledger.tsv`
- provider-side approved protein AA sequence package
- final dossier that indexes the package

## 6. Negative Knowledge Memory

Rejected candidates matter. The system should preserve why a gene, route, or claim failed so future agents do not rediscover the same weak options.

Output:

- `rejected-candidates.tsv`
- `red-team-report.md`

Future review surface:

- `route-kill-list.md`

## 7. NCBI Wide Search Escalation

Use AWS ElasticBLAST only when cheaper RunPod lanes cannot resolve a wide or
frontier step. The output is not raw BLAST archives; it is compressed evidence
that feeds candidate funnels and route stitching.

Output:

- `elasticblast-search-plan.tsv`
- `elasticblast-run-ledger.tsv`
- `aws-safety-ledger.tsv`

## 8. Genome And Structure Context

Use genome neighborhoods, BGC tools, structure-risk triage, and host comparison
only after they change candidate ranking or uncertainty. These lanes create
compact evidence; they do not import raw genomes, model caches, or validation
claims.

Output:

- `genome-mining-plan.tsv`
- `genome-hit-ledger.tsv`
- `structure-risk-ledger.tsv`
- `host-comparison-ledger.tsv`

## 8A. GeneCluster Atlas Control Plane

When a campaign needs source-species to target-species genome context, the
public release now has a metadata-only GeneCluster lane. It chooses a route
ceiling from declared organism, dataset, query, and decoy ledgers, then creates
contracts for sequence search, cluster/function jury review, and a claim-bounded
dossier. The lane is local-only until a separate provider preflight is approved.

Output:

- `genecluster-source-scout-ledger.tsv`
- `genecluster-route-decision-ledger.tsv`
- `genecluster-atlas-contract-ledger.tsv`
- `cluster_calls.tsv`
- `bgc_consensus.tsv`
- `protein_function_votes.tsv`
- `protein_function_jury.tsv`
- `genecluster-atlas-plan.json`

## 8B. Opportunity Lane Radar

The public release can draft contract lanes for capabilities that are powerful
but not safe as defaults: route-rule expansion, thermodynamics, host modeling,
host-fit model hypotheses, chemoenzymatic fallback, active-site risk, BGC and
metagenome context, metabolomics handoff, compound/source priors, supply-chain
preflight, and review surfaces.

Output:

- `docs/opportunity-radar.md`
- `supply-chain-preflight-ledger.tsv`
- `route-rule-ledger.tsv`
- `thermodynamics-ledger.tsv`
- `metabolic-model-ledger.tsv`
- `strain-design-ledger.tsv`
- `chemoenzymatic-fallback-ledger.tsv`
- `bgc-context-ledger.tsv`
- `metagenome-context-ledger.tsv`
- `metabolomics-evidence-ledger.tsv`
- `compound-source-ledger.tsv`

## 9. Campaign Monitoring

Large Symphony + Linear campaigns need explicit stop points before widening
search, launching compute, or increasing concurrency.

Output:

- `monitoring-ledger.tsv`
- provenance summaries
- Symphony closeout blocks
