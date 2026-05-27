# Opportunity Lane Runbooks

These runbooks are contracts-first planning guides. They do not authorize live
tool execution, provider launch, data upload, biological validation, or
production claims.

## Ledger Schema

Keep `schemas/bioprospector-ledgers.json`, preflight validators, examples, and
tests aligned. Add new ledger contracts before asking agents to emit new row
types.

## Tool Execution Proof

Record exact command, version, database/model version, dry-run status, mock
status, exit status, and compact evidence pointers in
`tool-execution-proof-ledger.tsv`. Tool proof cannot replace execution-artifact
proof or target evidence.

## Candidate Graph

Build graph rows from manifest-declared ledgers. Edges should connect routes,
steps, candidates, domains, citations, target evidence, controls, packages, and
review surfaces without re-parsing prose.

## Provider Supply Chain

Record SBOM, vulnerability, signature, and provenance checks in
`supply-chain-preflight-ledger.tsv`. Supply-chain rows gate launch readiness;
they do not prove tool execution or biology.

## Active Site Audit

Use curated catalytic-site, motif, pocket, ligand, benchmark, and pose sanity
summaries as risk evidence. Pocket, motif, and pose checks are not validation.

## Route And Host Context

Route-rule, thermodynamic, metabolic-model, strain-design, and fallback rows are
prioritization intelligence unless joined execution artifacts and evidence
support a stronger claim level.

## Metabolomics Handoff

Prefer local or provider-side contracts for spectra processing. Hosted upload,
private spectra, or unpublished samples require explicit upload-policy and
data-policy pass rows before live execution.
