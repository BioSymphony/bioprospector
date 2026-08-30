# Design principles

BioProspector is a control plane for evidence-aware bioprospecting. These
principles keep campaigns portable, reviewable, and honest about what their
artifacts show.

## Use contracts before compute

- Define the target, route universe, evidence questions, controls, and stop
  conditions before starting an expensive search.
- Represent work as small ledgers with stable identifiers and explicit joins.
- Give every long-running stage an expected artifact, progress signal, timeout,
  resume point, and fail-closed rule.

## Match claims to evidence

- A plan, prediction, similarity hit, or reference example is not evidence that
  a route works in the target host.
- Preserve rejected candidates, counterevidence, unresolved steps, and degraded
  paths instead of flattening them into a single winner.
- Closeout requires declared artifacts, provenance, controls, joined evidence,
  and a claim audit.

## Keep the repository compact

- Track schemas, validators, public fixtures, summaries, citations, public
  accessions, placeholders, and checksums.
- Keep raw reads, private sequences, database mirrors, model weights, provider
  workdirs, credentials, and unpublished material outside the repository.
- Treat ignored local notes and runtime output as untrusted local input. Keep
  exact external locations out of public artifacts.

## Keep execution operator-owned

- Readiness bundles are review packets, not launchers.
- Provider, tracker, and publication actions require explicit operator review.
- Tool outputs remain evidence inputs. They do not establish biological
  validation, production, assay success, or clinical utility by themselves.
