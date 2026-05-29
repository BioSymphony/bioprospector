# Agent Install

BioProspector is a local agent skill. The install pattern is the same across
harnesses: symlink the `skills/bioprospector/` directory into the harness's
skills folder, then describe the campaign to your agent.

## Codex Skill

From the repository root:

```bash
mkdir -p "$HOME/.codex/skills"
ln -sfn "$PWD/skills/bioprospector" "$HOME/.codex/skills/bioprospector"
```

## Claude Code Skill

Claude Code reads skills from `~/.claude/skills/`. From the repository root:

```bash
mkdir -p "$HOME/.claude/skills"
ln -sfn "$PWD/skills/bioprospector" "$HOME/.claude/skills/bioprospector"
```

Claude Code discovers the skill by its `SKILL.md` frontmatter. Once linked,
ask Claude Code to use the `bioprospector` skill and it will follow the
campaign loop documented there.

## Symphony Workers

Symphony workers can use BioProspector by pointing the worker's repo root at
this checkout and referencing the skill in the worker's task brief. The
agent brief CLI produces a Symphony-compatible kickoff packet:

```bash
python3 skills/bioprospector/scripts/bioprospector_agent_brief.py \
  --campaign skills/bioprospector/examples/huperzine-frontier-public-v0/campaign-manifest.json \
  --out .runtime/symphony-brief/huperzine \
  --prefix HUPERZINE \
  --profile public-demo \
  --mode goal \
  --agent codex
```

The generated `agent-goal-prompt.txt`, `agent-brief.md`, `commands.sh`, and
`agent-brief.json` can be loaded into a Symphony task or piped into a
Linear-driven worker queue. The `--agent` flag accepts `codex`, `claude`,
or `goal` for different orchestrator conventions.

## Other Agents

Any agent that can read repository files works the same way. Point it at
the checkout, ask it to read `skills/bioprospector/SKILL.md`, `README.md`,
and the docs index, then have it write outputs under `.runtime/`. The
skill's CLIs run with stock Python 3.11+ and no third-party dependencies.

## Quick Sanity Check

After install, ask the agent to run the doctor and report what it sees:

```text
Use the bioprospector skill. Run the local doctor and the public audit,
then tell me which optional tools are available and which example campaigns
are ready to inspect.
```

The agent should call `python3 skills/bioprospector/scripts/bioprospector_doctor.py`
and `python3 scripts/public_audit.py .` and summarize the result.

Then ask the agent to use the `bioprospector` skill. The skill will direct the
agent to the route-expansion, enzyme-frontier, work-graph, provider-readiness,
dossier, example, and release-check scripts in this checkout.

## Copy One Prompt

```text
Use the bioprospector skill in this checkout. Turn <target molecule> in <host>
into a route atlas, enzyme frontier, candidate package, Pareto shortlist,
review dossier, and Linear-ready issue graph under .runtime/. Keep everything
local for now and do not write raw sequences, credentials, provider identifiers,
signed URLs, private paths, or large databases into the repo.
```

```text
Create a BioProspector campaign for <target molecule> in <host>. Start from
templates/target-contract.example.json, generate a scaffold under
.runtime/first-campaign/, run preflight and input audit, then tell me the route
families, likely dark steps, candidate-mining lanes, and smallest set of
operator decisions still needed before expansion.
```

More task prompts are in [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md).

## Repository Guidance

For agents that read repository instructions, include this short boundary in
the target repo's `AGENTS.md`:

```markdown
Use the BioProspector skill for bioprospecting, pathway planning, enzyme
candidate review, provider readiness, or claim-audited dossier work.

Do not store API keys, private sequences, raw reads, model weights, database
mirrors, provider pod IDs, signed URLs, or unpublished collaborator data in the
repo. Keep large and private artifacts outside git and reference them only by
safe pointers, checksums, or accession IDs.
```

## CLI Setup

The public package is source-checkout oriented so scripts, schemas, examples,
and agent skill files stay in one place.

```bash
python3 -m pip install -e .
bioprospector --help
```

If you invoke console scripts from outside the checkout, point them back to this
repo:

```bash
BIOPROSPECTOR_REPO_ROOT=/path/to/bioprospector \
  bioprospector doctor --json
```

An installed wheel without `BIOPROSPECTOR_REPO_ROOT` is intentionally limited:
version/help commands work, but script-backed commands fail closed rather than
guessing a checkout from the current directory.

## What Agents Should Do First

Agents should run local checks before generating provider plans:

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py
python3 scripts/public_audit.py .
```

For a campaign, run preflight and input audit before asking operator questions.
Ask only the smallest reversible set of questions needed for planning.

For ready-to-use prompts and closeout expectations, continue with
[`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md).
