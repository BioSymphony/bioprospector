# Public Porting Notes

Reviewed: 2026-05-23

This note records public-safe capabilities promoted into this BioProspector
release. It intentionally avoids workstation paths, provider traces, campaign
run output, account identifiers, source-specific defaults, and private issue
text.

## Public Design Lessons

- Scientific work should be represented as reviewable contracts, not loose task
  prose.
- Stage 0 preflight is valuable: data readiness, query seeds, relevance,
  novelty, and claim importance should be checked before compute.
- Gene discovery needs route ceilings. Transcript-only, genome-only,
  annotation-rich, and literature-only inputs do not justify the same claims.
- Long provider runs need stage contracts, progress events, stale-output
  guards, and artifact pull policies before launch.
- Successful closeout means declared artifacts were fetched or indexed,
  validated, hashed where applicable, joined back to inputs, and claim-audited.
- The strongest public artifact is a dossier or review surface backed by
  ledgers, not raw search output.

## Ported In This Release

- Metadata-only GeneCluster atlas planning for source scout, route decision,
  cluster/function jury, and dossier contracts.
- Summary-only GeneCluster atlas contract validation for cluster calls, BGC
  consensus, function votes, function jury rows, and review/provider handoff
  manifests.
- Ledger schema entries for scale controls, supply-chain preflight, route
  rules, thermodynamics, metabolic modeling, host-fit model hypotheses,
  chemoenzymatic fallback, BGC/metagenome/metabolomics context, compound-source
  priors, MAG quality, and eukaryotic annotation.
- Full-frontier issue lanes for executable proof, template design, schema
  hardening, supply chain, active-site audit, route rules, thermodynamics,
  metabolic modeling, host-fit model review, fallback, context evidence, compound
  priors, and review surfaces.
- Release-check coverage through unit tests, package smoke checks, public
  audit, and runtime artifact audit.
- Public documentation for opportunity lanes and claim ceilings.

## Keep Out Of Public Releases

- Generated atlas folders, rendered reports, provider logs, local workdirs, and
  ignored runtime output.
- Raw or heavy biological artifacts and local database/index material.
- Operator-specific cloud dispatch scripts and provider identifiers.
- Source-specific campaign aliases, one-off runbooks, and private issue text.
- Any unpublished sequence, collaborator-restricted data, credentials, account
  identifiers, signed URLs, or private paths.

## Next Public Ports

- Compact normalizers for user-supplied summary tables, without tool execution.
- Optional tool-inventory docs for MMseqs, Foldseek, BGC callers, synteny, and
  report rendering, marked as user-installed external tools.
- History-safe release audit with redacted secret scanning before the public
  switch.
