# Product Foundation

## Decision

BioSymphony BioProspector is a sibling project to the structural BioSymphony foundation. It focuses on bioprospecting, pathway expansion, enzyme candidate mining, route stitching, and host-fit review.

For v1, BioProspector is a repo-hosted skill kit: schemas, validators,
campaign templates, and provider-readiness layer. The public default is
local Markdown artifacts; optional Symphony or Linear-style operator stacks
can consume those artifacts when a user has that setup.

## Product Unit

The product unit is a campaign:

```text
operator request
  -> target contract
  -> input audit and short operator intake
  -> stage/provider readiness gates
  -> local issue-style draft DAG
  -> optional operator/agent worker waves
  -> bioprospector dossier
  -> ranked route shortlist and validation roadmap
```

## What This Enables

BioProspector makes the expensive part of bioprospecting explicit:

- where the route universe came from
- which steps are known, inferred, or missing
- which unknown genes, hidden substeps, or multi-gene modules could explain ambiguous chemistry
- how many candidates were searched per step
- why candidates survived or failed
- which genome-context, structure-risk, and host-fit evidence changed the ranking
- which provider, stage, and progress gates make a long run real rather than merely launched
- which routes stitch chemically and fit the host
- which claims are evidence-supported versus speculative

## What It Is Not Yet

BioProspector v1 is not:

- a wet-lab protocol generator
- a construct automation system
- a LIMS
- a full DBTL platform
- a public database mirror
- a one-click strain engineering platform

Those may become downstream layers. The foundation should prove the local
contract graph, search funnel, evidence ledger, route stitching, and red-team
review first.

## Naming

Repo:

`biosymphony-bioprospector`

Product:

`BioSymphony BioProspector`

Major modes:

- `Pathway Big Bang`: route explosion from target molecule and host
- `Enzyme Frontier`: broad candidate mining per reaction step
- `Dark Step Resolver`: ambiguity, unknown-gene, hidden-step, and counterevidence reasoning
- `Genome Context`: anchor-neighborhood and BGC-style evidence planning
- `Structure Risk`: active-site, cofactor, membrane, and substrate-access triage
- `Pathway Stitcher`: route integration, missing-link handling, and host fit
- `Chassis Jury`: host compatibility, burden, toxicity, and feasibility review
- `Evidence Ledger`: provenance, claim levels, and red-team audit
