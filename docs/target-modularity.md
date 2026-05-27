# Target Modularity

BioProspector campaigns should be target-swappable. Nootkatone and vanillin are
public examples, not special product modes. Local-only stress fixtures may live
under ignored `local-examples/`.

## Stable Campaign Interface

Every target should provide:

- `campaign-manifest.json`: campaign id, mode, execution policy, and ledger paths
- `target-contract.json`: target molecule, host, allowed route classes, optimization goals, and hard boundaries
- `route-ledger.tsv`: route hypotheses and route status
- `reaction-step-ledger.tsv`: normalized transformations and search-width budgets
- `candidate-funnels.tsv`: raw-to-shortlist compression counts
- `enzyme-draft-board.tsv`: candidate enzyme scorecard
- `route-stitching-scorecard.tsv`: integrated route feasibility review
- `claim-ledger.md`: explicit claims, evidence level, and caveats

Frontier campaigns should also provide:

- `unknown-step-ledger.tsv`: missing or uncertain chemistry
- `rejected-candidates.tsv`: negative knowledge memory
- `provenance.jsonl`: command, database, and review provenance
- `runpod-run-manifest.json`: reviewable remote execution plan, not a live launch record
- `elasticblast-search-plan.tsv`: reviewable AWS ElasticBLAST escalation plan for wide/frontier steps
- `elasticblast-run-ledger.tsv`: submitted run and cleanup record, empty/planned before execution
- `aws-safety-ledger.tsv`: budget, quota, S3, IAM, and cleanup controls before submit
- `literature-ledger.tsv`: citation, evidence class, and license/fulltext boundary
- `pathway-inference-ledger.tsv`: route hypotheses, assumptions, counterevidence, and decisions
- `unknown-gene-hypothesis-ledger.tsv`: single-gene, multi-gene, and non-obvious unknown-step hypotheses
- `enzyme-family-sweep.tsv`: family-level search compression before candidate promotion
- `genome-mining-plan.tsv` and `genome-hit-ledger.tsv`: compact genome-context evidence
- `structure-risk-ledger.tsv`: active-site, cofactor, membrane, and substrate-access risks
- `host-comparison-ledger.tsv`: host/chassis fit and route burden comparison
- `assay-handoff-ledger.tsv`: non-protocol validation priorities and controls needed
- `monitoring-ledger.tsv`: expected artifacts, heartbeat state, blockers, and review checkpoints
- `input-audit-ledger.tsv`: known inputs and explicit missing operator items
- `operator-intake-ledger.tsv`: confirmations, reversible assumptions, skip policy, and later blockers
- `run-maturity-ledger.tsv`: L0 through L5 readiness and success gates
- `stage-contract-ledger.tsv` and `stage-progress-ledger.tsv`: long-run stage outputs, timeouts, checkpoints, heartbeats, fallbacks, and resume paths
- `organism-sample-ledger.tsv`, `query-set-ledger.tsv`, and `target-dataset-ledger.tsv`: target/source/query provenance
- `target-evidence-ledger.tsv`: candidate-to-step-to-organism/sample-to-dataset evidence joins
- `decoy-control-ledger.tsv`: negative-control and decoy gates for broad searches
- `execution-artifact-ledger.tsv`: real versus mock/dry-run artifact proof
- `compute-provider-ledger.tsv`: provider choices and boundaries, with RunPod as one reviewed optional path and role-specific AWS/neocloud/HPC/cloud escalation paths
- `provider-launch-preflight-ledger.tsv`: launch blockers for image pull, registry auth, volume, branch/snapshot, payload, budget, secrets, and stage contracts
- `workflow-framework-ledger.tsv`: runner framework compatibility without changing claim gates

## Target Swap Rule

A new target should be created by copying an example campaign directory and
changing only:

- target molecule and host fields
- route rows
- reaction-step rows
- claim-boundary notes
- resource rows

Scripts should discover ledger paths from `campaign-manifest.json` and should
not special-case nootkatone, vanillin, yeast, or any single enzyme family.

If a target has ambiguous biology, add the ambiguity ledgers instead of forcing
the uncertainty into `notes` fields or premature candidate rows.

If a target starts from a loose operator prompt, add `operator-intake-ledger.tsv`
early. Planning may proceed on reversible assumptions, but execution and final
claims need confirmed rows for their required gates.

If a target will move beyond planning, add the no-false-success ledgers before
execution. Reference hits, issue status, and runner flags are not target evidence
or execution proof by themselves.

If a target may run outside RunPod, add provider/framework rows rather than
forking the workflow. The provider can change; the ledger contract and final
self-check cannot.

If a target has long-running stages, add stage contracts before launch. A
provider status field, billing state, or command intent is not a done marker.

## Search Width Budgets

Use search width to control expansion:

- `tiny`: manual/literature review only
- `narrow`: hundreds of candidates or fewer
- `medium`: thousands of candidates with clustering
- `wide`: tens of thousands of raw hits with strict compression
- `frontier`: explicit RunPod/HPC-ready search with budget, kill criteria, and review gate

`frontier` does not mean "run immediately." It means the issue needs a remote
readiness bundle and an operator review before any compute starts.

For NCBI-wide BLAST searches, `frontier` should prefer an ElasticBLAST readiness
bundle over staging full `nr` on RunPod.

## Sidecar Boundary

BioProspector should be portable as a Symphony sidecar:

- repo-local skill material teaches workers the protocol
- dry-run issue generation emits reviewable Linear issue bodies
- workflow drafts can be copied into a local Symphony-compatible operator stack
- RunPod bundles can be reviewed before any paid compute or database download
