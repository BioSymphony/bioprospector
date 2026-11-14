# Agent Playbook

Use the [tool guide](tool-stack.md) to choose tools and the
[integration guide](TOOL_INTEGRATIONS.md) to map results into ledgers.

## Investigate a Research Question

```text
Use BioProspector to answer <question> with <inputs>. Choose tools from its
catalog and check their inputs and access. Define a comparison and controls
if needed, then run the calls. Use each result to select the next call.
Report what you found, source IDs, and any conflicting or missing evidence.
```

## Start a Campaign

```text
Set up a BioProspector campaign for <research question> using my target
contract. Validate the manifest and audit its inputs. Write a short review
with the questions that need a decision.
```

See the [first campaign guide](FIRST_CAMPAIGN.md) for the target contract
and example commands.

## Choose a Follow-Up

```text
Read the existing candidate records. Identify the uncertainty that most
affects the comparison and choose a tool that can address it. Check its
inputs and explain how the result affects your ranking.
```

## Coordinate Review

Use the [workflow guide](WORKFLOWS.md) for campaign handoffs and the
[Symphony and Linear guide](symphony-linear-sidecar.md) for tracker setup.
Ask the agent to report output files, evidence supporting each conclusion,
and unresolved questions.
