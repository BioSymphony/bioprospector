# Glossary

## Campaign

A bounded planning workspace for one target molecule, host, scope, claim
boundary, and set of ledgers. The campaign manifest is the index that tells
scripts where each ledger lives.

## Target contract

The compact JSON statement of the target molecule, host, optimization goals,
hard boundaries, and public/private data limits. Start here before widening a
campaign.

## Ledger

A structured TSV or Markdown artifact with stable columns. Ledgers keep broad
agent work reviewable by making routes, candidates, evidence, controls,
execution artifacts, and claims joinable.

## Route

A proposed path from substrate/source context toward the target molecule. A
route is a hypothesis until every step has evidence and a stitching review.

## Reaction step

One normalized transformation inside a route. Steps can point to candidate
enzymes, unknown-gene hypotheses, multi-gene module hypotheses, or parked
ambiguities.

## Dark step

A route step where the responsible gene, module, transport event, cofactor
explanation, spontaneous chemistry, or hidden substep is unclear. Dark steps
need explicit ambiguity lanes instead of forced one-gene answers.

## Candidate

An enzyme, protein, cluster, route component, or reference anchor being
considered for a step. Candidates need source scope, claim level, evidence
context, and review status.

## Candidate package

A compact index of candidate sequences or sequence pointers, domain spans,
motifs, diversity classes, citations, checksums, graph edges, and caveats. It is
not a raw FASTA dump or full search archive.

## GeneCluster Atlas

A metadata-only planning lane for cluster/neighborhood context. The public
fixture uses synthetic compact cluster rows and contract validators rather than
raw genomes.

## Provider readiness

Review artifacts that describe what would be needed before using RunPod, HPC,
AWS ElasticBLAST, public APIs, or other external providers. Readiness is not
execution proof.

## Stage contract

The expected output, timeout, checkpoint, done marker, resume command,
fail-closed behavior, and progress events for a long-running stage.

## Execution artifact

Proof that a tool or stage ran: command, checksum, output pointer,
status, retained/raw-data boundary, and join back to declared inputs.

## Claim level

The strength of a statement. Public examples should use planning-safe levels
such as hypothesis, review-required, reference-only, or not-observed unless
direct evidence supports a stronger claim.

## Route stitching

The review that asks whether the route works as a connected pathway,
beyond whether each individual step has a plausible candidate.

## Pareto frontier

A shortlist that preserves route options for different criteria, such as minimal genes,
highest evidence, best host fit, clearest validation handoff, ambitious route,
and diversity-library options.

## Public release review

A check before publishing a version of the repository. The release gate tests
the package, documentation, examples, generated artifacts, and public-safety rules.
