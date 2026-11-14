# Agent Installation

Link the BioProspector skill from a checkout you plan to keep. Run the
commands for your agent from the repository root.

## Codex

```bash
mkdir -p "$HOME/.codex/skills"
ln -s "$PWD/skills/bioprospector" "$HOME/.codex/skills/"
```

## Claude Code

```bash
mkdir -p "$HOME/.claude/skills"
ln -s "$PWD/skills/bioprospector" "$HOME/.claude/skills/"
```

If you already installed the skill, update its existing link to point to
this checkout.

## Other Agents

Point your agent to the [BioProspector skill](../../SKILL.md).
For Symphony workers, see the [coordination guide](symphony-linear-sidecar.md).

Ask your agent to use the `bioprospector` skill and run the local doctor.
Then give it a research question or use a prompt from the
[agent playbook](AGENT_PLAYBOOK.md).

## Install the CLI

With Python 3.11+, install the command from the checkout.

```bash
python3 -m pip install -e .
bioprospector --help
```

To use a wheel’s campaign commands, set `BIOPROSPECTOR_REPO_ROOT` to your
BioProspector checkout. See the [CLI reference](CLI_REFERENCE.md).
