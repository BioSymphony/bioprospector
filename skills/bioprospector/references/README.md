# BioSymphony BioProspector

BioProspector is an agent skill for planning biosynthetic pathways and
reviewing the evidence for candidate enzymes and genes. Give your agent a
target molecule, host, constraints, and compute budget. The skill defines how
to record route options, candidate rankings, source evidence, and unresolved
questions in a review package.

Use it with Codex, Claude Code, or Symphony with Linear. The repository includes
the skill, command-line tools, schemas, validators, and compact planning
examples for vanillin, nootkatone, and Huperzine A. The examples demonstrate
planning outputs; they do not establish biological validation.

![BioProspector biosynthetic-pathway planning banner](docs/assets/bioprospector-banner-woodblock-2to1.jpg)

## Start here

To use BioProspector with your agent, follow the
[skill installation guide](docs/AGENT_INSTALL.md), then the
[first campaign guide](docs/FIRST_CAMPAIGN.md).

To inspect the local demo, run this command from the repository root with
Python 3.11+, Git, and Make available:

```bash
make first-look
```

The command checks the checkout and generates local planning artifacts without
launching cloud jobs. Open `.runtime/local-demo/huperzine/dossier.md` to review
the output. See the [quickstart](docs/QUICKSTART.md) for individual commands and
prerequisites, or the [workflow guide](docs/WORKFLOWS.md) for tracker and compute
handoffs.

## Campaign overview

```mermaid
%%{init:{'theme':'base','flowchart':{'htmlLabels':false,'padding':16,'subGraphTitleMargin':{'top':10,'bottom':18}},'themeVariables':{'fontFamily':'Menlo, Consolas, monospace','lineColor':'#7a7a7a','clusterBkg':'#0c0c0c','clusterBorder':'#3a3a3a','titleColor':'#dcdcdc'}}}%%
flowchart LR
  classDef io fill:#0c0c0c,stroke:#5a5a5a,color:#ededed,stroke-width:1.5px
  classDef accent fill:#0c0c0c,stroke:#bdf0a0,color:#bdf0a0,stroke-width:1.5px
  A("TARGET MOLECULE<br/>+ HOST"):::io
  B("EXPAND THE<br/>ROUTE SPACE"):::io
  C("MINE ENZYME +<br/>GENE CANDIDATES"):::io
  D("RESOLVE DARK STEPS<br/>STITCH · HOST-FIT"):::io
  E("CONSTRUCT<br/>HYPOTHESES"):::accent
  F("COMPUTE-READY<br/>WORK GRAPH"):::accent
  A --> B --> C --> D --> E
  D --> F
```

## What agents get

A campaign records:

- Alternative route hypotheses, including the evidence and gaps for each.
- Candidate genes for each reaction, with source references, domain summaries,
  rejected candidates, and counterevidence.
- Route comparisons by gene count, evidence strength, host fit, and unresolved
  steps.
- Separate records for plans, execution, controls, and claims, so reviewers can
  check what each result supports.

<details>
<summary>Route comparison diagram</summary>

```mermaid
%%{init:{'theme':'base','flowchart':{'htmlLabels':false,'padding':16,'subGraphTitleMargin':{'top':10,'bottom':18}},'themeVariables':{'fontFamily':'Menlo, Consolas, monospace','lineColor':'#7a7a7a','clusterBkg':'#0c0c0c','clusterBorder':'#3a3a3a','titleColor':'#dcdcdc'}}}%%
flowchart TD
  classDef wide fill:#0c0c0c,stroke:#5a5a5a,color:#ededed,stroke-width:1.5px
  classDef mid fill:#0c0c0c,stroke:#5a5a5a,color:#ededed,stroke-width:1.5px
  classDef win fill:#0c0c0c,stroke:#bdf0a0,color:#bdf0a0,stroke-width:1.5px
  T("TARGET MOLECULE + HOST"):::mid
  subgraph EX["EXPLORE: retain alternative routes"]
    direction LR
    R1("natural"):::wide
    R2("engineered"):::wide
    R3("fed-substrate"):::wide
    R4("analog"):::wide
    R5("reverse-catabolism"):::wide
    R6("dark-step / de novo"):::wide
    R1 ~~~ R2 ~~~ R3 ~~~ R4 ~~~ R5 ~~~ R6
  end
  M("MINE + RESOLVE + STITCH"):::mid
  subgraph WIN["RETURN FOUR ROUTE VIEWS"]
    direction LR
    P1("minimal-gene"):::win
    P2("strongest-evidence"):::win
    P3("best host-fit"):::win
    P4("ambitious de novo"):::win
    P1 ~~~ P2 ~~~ P3 ~~~ P4
  end
  T --> EX --> M --> WIN
```

</details>

<details>
<summary>Evidence review diagram</summary>

```mermaid
%%{init:{'theme':'base','flowchart':{'htmlLabels':false,'padding':16,'subGraphTitleMargin':{'top':10,'bottom':18}},'themeVariables':{'fontFamily':'Menlo, Consolas, monospace','lineColor':'#7a7a7a','clusterBkg':'#0c0c0c','clusterBorder':'#3a3a3a','titleColor':'#dcdcdc'}}}%%
flowchart TD
  classDef rung fill:#0c0c0c,stroke:#5a5a5a,color:#ededed,stroke-width:1.5px
  classDef gate fill:#0c0c0c,stroke:#e0825c,color:#e0825c,stroke-width:1.5px
  classDef claim fill:#0c0c0c,stroke:#bdf0a0,color:#bdf0a0,stroke-width:1.5px
  L0("PLAN"):::rung
  L1("TOOLS READY"):::rung
  L2("INPUTS REAL"):::rung
  L3("EXECUTION HAPPENED"):::rung
  L4("EVIDENCE JOINED"):::rung
  L5("AUDITED, EVIDENCE-BACKED CLAIMS"):::claim
  G1{{"real execution proof"}}:::gate
  G2{{"joins to the target + controls pass"}}:::gate
  L0 --> L1 --> L2 --> G1 --> L3 --> G2 --> L4 --> L5
```

</details>

## Where it runs

Start on a laptop. Move only the lanes that need more compute, after an operator
approves the budget, data policy, and credentials outside this repository. The
campaign contract stays the same when the agent harness or compute provider
changes.

<details>
<summary>Agent and compute options</summary>

```mermaid
%%{init:{'theme':'base','flowchart':{'htmlLabels':false,'padding':16,'subGraphTitleMargin':{'top':10,'bottom':18}},'themeVariables':{'fontFamily':'Menlo, Consolas, monospace','lineColor':'#7a7a7a','clusterBkg':'#0c0c0c','clusterBorder':'#3a3a3a','titleColor':'#dcdcdc'}}}%%
flowchart LR
  classDef io fill:#0c0c0c,stroke:#5a5a5a,color:#ededed,stroke-width:1.5px
  classDef hub fill:#0c0c0c,stroke:#bdf0a0,color:#bdf0a0,stroke-width:1.5px
  subgraph H["ANY AGENT HARNESS"]
    direction TB
    H1("Claude Code"):::io
    H2("Codex"):::io
    H3("Symphony + Linear"):::io
    H4("your tracker"):::io
  end
  C(("ONE CAMPAIGN<br/>CONTRACT")):::hub
  subgraph P["COMPUTE YOU CHOOSE"]
    direction TB
    P1("laptop"):::io
    P2("RunPod"):::io
    P3("HPC / SSH"):::io
    P4("cloud / neocloud VM"):::io
    P5("AWS ElasticBLAST"):::io
  end
  H1 --> C
  H2 --> C
  H3 --> C
  H4 --> C
  C --> P1
  C --> P2
  C --> P3
  C --> P4
  C --> P5
```

</details>

## What stays in the checkout

The checkout contains the skill, prompts, schemas, validators, and compact
campaign summaries. Raw reads, database snapshots, model weights, full search
output, and exact external locations stay in ignored operator state. The
checkout keeps public accessions, placeholders, checksums, and reviewed summaries.

<details>
<summary>Repository data boundary</summary>

```mermaid
%%{init:{'theme':'base','flowchart':{'htmlLabels':false,'padding':16,'subGraphTitleMargin':{'top':10,'bottom':18}},'themeVariables':{'fontFamily':'Menlo, Consolas, monospace','lineColor':'#7a7a7a','clusterBkg':'#0c0c0c','clusterBorder':'#3a3a3a','titleColor':'#dcdcdc'}}}%%
flowchart LR
  classDef repo fill:#0c0c0c,stroke:#bdf0a0,color:#bdf0a0,stroke-width:1.5px
  classDef ext fill:#0c0c0c,stroke:#e0825c,color:#e0825c,stroke-width:1.5px
  subgraph IN["IN THE CHECKOUT · small · forkable · auditable"]
    direction TB
    R1("skill + prompts"):::repo
    R2("schemas + validators"):::repo
    R3("summaries · rankings"):::repo
    R4("public accessions + checksums"):::repo
  end
  subgraph OUT["OPERATOR-OWNED · heavy · stays put"]
    direction TB
    E1("raw reads / FASTA"):::ext
    E2("database snapshots · model weights"):::ext
    E3("full search outputs · provider workdirs"):::ext
  end
  R4 -. "placeholder + checksum" .-> OUT
```

</details>

```text
skills/bioprospector/   the skill: SKILL.md, CLIs, example campaigns, references
docs/                   user and agent documentation (start with QUICKSTART.md)
templates/              issue templates the agent draws from
demos/                  demo maps and sample outputs
schemas/                shared campaign + ledger contracts
src/                    installable bioprospector CLI
tests/                  validators and contract checks
```

## Talk to your agent

After you install the skill, give your agent a target, host, and compute boundary:

```text
Use the bioprospector skill in this checkout. Run doctor, keep everything local,
and start a campaign for <target molecule> in <host>. Explore the route space,
draft non-procedural construct-hypothesis lanes, and return a short review
package under .runtime/. Keep raw or private data, credentials, provider IDs,
and private paths outside the repository.
```

## Result boundaries

BioProspector returns plans, search contracts, rankings, and review packages.
Production, host performance, assay results, and deployment readiness require
separate execution records, controls, and expert review. See
[`NON_CLAIMS.md`](NON_CLAIMS.md) and
[`docs/no-false-success-gates.md`](docs/no-false-success-gates.md).

## Reference documentation

The [September 2026 tool review](docs/opportunity-radar.md) covers AI
annotation, evaluation, literature extraction, and provenance candidates, with
source dates and adoption limits.

Use [`docs/PUBLIC_LAUNCH_PAD.md`](docs/PUBLIC_LAUNCH_PAD.md) for the full
capability map, [`skills/bioprospector/SKILL.md`](../SKILL.md)
for the canonical agent instructions, and
[`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) for commands. The data boundary
is defined in
[`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md).

<details>
<summary><strong>Artifact contract</strong></summary>

A campaign uses versioned ledgers and review artifacts for routes, reaction
steps, candidates, evidence, controls, provider readiness, and claims. The
shared contract and full artifact list are in
[`docs/capability-map.md`](docs/capability-map.md) and
[`schemas/bioprospector-ledgers.json`](schemas/bioprospector-ledgers.json).

</details>
