# BioSymphony BioProspector

![BioProspector biosynthetic-pathway planning banner](docs/assets/bioprospector-banner-woodblock-2to1.jpg)

**A portable agent skill for turning a target molecule and host into route
options, enzyme and gene search plans, and evidence-bounded review packages.**

BioProspector gives research agents a shared campaign contract for
biosynthetic-pathway planning and evidence review. Provide a target molecule,
host, constraints, and compute boundary. The skill organizes route exploration,
candidate mining, dark-step resolution, and route review into compact ledgers
and reviewable handoffs.

Start locally. When a lane needs more compute, the same contract can prepare
operator-reviewed work for RunPod, HPC, a cloud VM, or AWS ElasticBLAST. It
works with Claude Code, Codex, Symphony with Linear, and tracker-neutral queues.

The repository includes planning examples for **vanillin**, **nootkatone**, and
**Huperzine A**, each designed to be adapted to another target.

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

A campaign gives an agent concrete work products:

- **A broader route space:** compare natural, engineered, fed-substrate,
  analog, reverse-catabolism, dark-step, and de novo route families early.
- **Explicit unknowns:** turn missing chemistry, unknown genes, and hidden
  multi-gene steps into testable hypotheses with counterevidence.
- **Traceable candidates:** shortlist genes for each reaction, preserve source
  pointers, summarize domains, and record rejected candidates.
- **Four route views:** return minimal-gene, strongest-evidence,
  best-host-fit, and ambitious options with their trade-offs.
- **Clear evidence boundaries:** keep plans, execution records, search results,
  controls, and claims separate so reviewers can see what remains unproven.

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

The public examples are planning fixtures. They do not show that a search ran
or that a route, host, construct, or assay was validated.

## Where it runs

Start on a laptop. Move only the lanes that need more compute, after an operator
approves the budget, data policy, and credentials outside this repository. The
campaign contract stays the same when the agent harness or compute provider
changes.

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

## What stays in the checkout

The checkout contains the skill, prompts, schemas, validators, and compact
campaign summaries. Raw reads, database snapshots, model weights, full search
output, and exact external locations stay in ignored operator state. The
checkout keeps public accessions, placeholders, checksums, and reviewed summaries.

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

```text
skills/bioprospector/   the skill: SKILL.md, CLIs, example campaigns, references
docs/                   user and agent documentation (start with QUICKSTART.md)
templates/              issue templates the agent draws from
demos/                  demo maps and sample outputs
schemas/                shared campaign + ledger contracts
src/                    installable bioprospector CLI
tests/                  validators and contract checks
```

## Verify the checkout

To verify the checkout and generate the local demo:

```bash
python3 scripts/bioprospector_doctor.py --include-runtime
make local-demo
```

The demo builds Huperzine A planning artifacts: route options, candidate
pointers, a ranked route set, a metadata-only gene-cluster plan, and a compact
review package. Every claim remains labeled by its evidence level.

New here? Start with [`docs/QUICKSTART.md`](docs/QUICKSTART.md) and [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md). To run a campaign for your own molecule, see [`docs/FIRST_CAMPAIGN.md`](docs/FIRST_CAMPAIGN.md). Copy-paste agent prompts live in [`docs/AGENT_PLAYBOOK.md`](docs/AGENT_PLAYBOOK.md).

## Talk to your agent

Once the skill is installed, give the agent a target, host, and boundary:

```text
Use the bioprospector skill in this checkout. Run doctor, keep everything local,
and start a campaign for <target molecule> in <host>. Explore the route space,
draft non-procedural construct-hypothesis lanes, and return a short review
package under .runtime/. Keep raw or private data, credentials, provider IDs,
and private paths outside the repository.
```

```text
Use BioProspector to resolve the dark steps in the Huperzine A example: turn the
unknown chemistry into single-gene and multi-gene hypotheses with counterevidence,
then identify the lowest-cost non-procedural evidence check that would distinguish them.
```

## Result boundaries

BioProspector returns plans, search contracts, rankings, and review packages.
Production, host performance, assay results, and deployment readiness require
separate execution records, controls, and expert review. See
[`NON_CLAIMS.md`](NON_CLAIMS.md) and
[`docs/no-false-success-gates.md`](docs/no-false-success-gates.md).

## Reference documentation

Use [`docs/PUBLIC_LAUNCH_PAD.md`](docs/PUBLIC_LAUNCH_PAD.md) for the full
capability map, [`skills/bioprospector/SKILL.md`](../SKILL.md) for the canonical
agent instructions, and [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) for
commands. The data boundary is defined in
[`docs/PRIVACY_SECURITY_MODEL.md`](docs/PRIVACY_SECURITY_MODEL.md).

<details>
<summary><strong>Artifact contract</strong></summary>

A campaign uses versioned ledgers and review artifacts for routes, reaction
steps, candidates, evidence, controls, provider readiness, and claims. The
shared contract and full artifact list are in
[`docs/capability-map.md`](docs/capability-map.md) and
[`schemas/bioprospector-ledgers.json`](schemas/bioprospector-ledgers.json).

</details>
