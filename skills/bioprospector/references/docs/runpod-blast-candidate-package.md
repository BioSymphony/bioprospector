# RunPod BLAST and candidate package

This is one supported shape for a real BioProspector heavy-search run: an
operator-managed RunPod workspace can do local BLAST/DIAMOND/MMseqs2/HMMER
work, and the repo receives compact ledgers, graph edges, hashes, versions, and
package indexes.

No pod is launched by the tracked examples. No database, FASTA, GFF, BLAST
output, model weight, private sequence, or full-text literature is stored here.

## RunPod search plane

RunPod is a reviewed optional heavy-search path when an operator wants
controlled remote compute without burning the laptop. The first live run should
use an operator-managed manual Pod with a Network Volume mounted at
`/workspace`.

Default remote layout:

```text
/workspace/bioprospector/runs/<campaign_id>/
  inputs/
  db/
  work/
  outputs/
  provenance/
```

The repo stores the contract in:

- `compute-provider-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`
- `stage-contract-ledger.tsv`
- `stage-progress-ledger.tsv`
- `sequence-search-plan-ledger.tsv`
- `execution-artifact-ledger.tsv`

Before live launch, every blocking provider preflight row must pass. A pod in
`RUNNING` or desired status is not proof that the image pulled or that the
workflow progressed.

## BLAST and search contract

Each planned search is a row in `sequence-search-plan-ledger.tsv`.

Required fields include:

- step id
- query id
- search tool
- database
- provider id
- remote workdir
- sequence scope
- max hits
- thresholds
- budget
- approval status
- output contract

RunPod-local lanes should prefer staged public/open resources first:

- Swiss-Prot or curated seed sets
- selected UniRef or RefSeq protein sets
- Pfam-A HMMs
- DIAMOND/MMseqs2 for wide protein search
- BLAST+ for compatibility and spot checks
- HMMER or pyhmmer for domain/family gates

AWS ElasticBLAST remains a separate reviewed escalation when official NCBI BLAST
database scale is needed.

## Candidate package

The high-detail output package should be intricate but compact.

Default sequence policy is provider-side full candidate pack. The external run
package stores all approved protein AA candidate sequences for the campaign
universe, representative sequences, cluster memberships, checksums, database
versions, and license boundaries. The public repo stores only compact indexes,
accession IDs, graph edges, checksums, and external pointers.

Expected tracked indexes:

- `candidate-sequence-ledger.tsv`: candidate id, step id, AA-sequence pointer,
  length/checksum when materialized, source database, license boundary, domain
  map status.
- `domain-annotation-ledger.tsv`: domain source, accession, name, span,
  active-site or motif summary, confidence.
- `candidate-intelligence-ledger.tsv`: publicly reported/reference enzyme, mutant/engineered
  variant, signal/transit peptide, transmembrane, PTM, localization, cofactor,
  oligomer, motif, expression-context, and close-canonical-match inferences.
- `candidate-diversity-ledger.tsv`: canonical, close homolog, diverse homolog,
  remote homolog, and unusual selections.
- `candidate-graph-ledger.tsv`: route -> step -> candidate -> domain ->
  literature -> package edges.
- `run-output-package-ledger.tsv`: package index, graph artifact pointer,
  sequence policy, location/pointer, status.
- `tool-registry-ledger.tsv`, `adapter-contract-ledger.tsv`,
  `evidence-event-ledger.tsv`, and `tool-execution-proof-ledger.tsv`: adapter
  registry, normalized compact events, and tool proof rows for the run.
- `candidate-ranking-ledger.tsv` and `pareto-frontier-ledger.tsv`: per-step
  candidate ranks and route-level rankings by gene count, evidence, host fit,
  ambition, and diversity.

Sequence policy: protein AA only or provider-side pointer. Do not copy
nucleotide constructs, raw all-hit dumps, unrestricted FASTA bundles, or private
sequence data into the repo.

The helper command below builds the public-safe package indexes only:

```bash
python3 scripts/bioprospector_candidate_package.py \
  --campaign examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/candidate-packages/huperzine-frontier-public-v0
```

It does not run BLAST, download databases, copy FASTA, or launch RunPod. Live
closeout remains blocked until provider-side artifacts are fetched, checksummed,
joined to the ledgers, and strict self-check passes.

## Candidate intelligence lane

This lane adds sequence and public-evidence context without starting a heavier
modeling campaign. Candidate-intelligence planning is
default-on because these questions are easy for agents to forget and often
materially change ranking. It should answer questions like:

- which publicly reported enzymes can serve as reference anchors
- whether public variant annotations affect ranking context
- whether a candidate has signal peptide, transit peptide, transmembrane,
  localization, PTM/glycosylation, cofactor, oligomer, motif, or expression
  watchouts
- what can be inferred from close canonical enzymes, and what remains only a
  close-match caveat

The lane can use accession records, compact citation summaries, domain maps,
AA-sequence pointers, and campaign-specific design notes. It must not require
docking, wet-lab assays, construct recipes, full-text literature mirrors, raw
FASTA dumps, or target-host validation claims.

If an operator asks to run tools, or if the campaign scope requires those
answers for ranking, it can execute lightweight predictors or public lookups on
RunPod, neocloud, HPC, cloud VM, or local-full. Examples include
SignalP/TMHMM-style signal/transmembrane predictors, localization/PTM annotators,
motif/cofactor checks, and operator-approved mutant or engineered variant
extraction. Before launch, add provider preflight rows for
`candidate_intelligence_tools`, `public_api_access`, `provider_egress_policy`,
`tool_execution_proof`, `data_policy`, `workdir`, and `stage_contract` as
applicable. Return tool versions, citation/accession identifiers, compact
summaries, and `candidate-intelligence-ledger.tsv` rows only.

## Literature lane

Time-bounded literature work is represented through `literature-search-ledger.tsv`.
Rows capture source list, query terms, recency window, result cap, status, and
output contract. The output is compact citation identifiers, claim summaries,
and license boundaries, not article bodies or large supplements.

## Ranking views

The final package should support several Pareto views:

- minimal genes
- highest evidence
- clearest validation handoff
- best yeast host fit
- ambitious de novo route
- diversity library
- unusual candidates parked separately from standard homolog hits

Similarity hits alone must not become activity or production claims. Promotion
requires domain/motif support, literature or accession provenance, controls,
host-fit review, route stitching, and final contract self-checks.
