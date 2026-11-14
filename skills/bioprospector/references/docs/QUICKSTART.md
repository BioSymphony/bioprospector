# Quickstart

Try the bundled examples or [install the agent skill](AGENT_INSTALL.md)
to start with your own research question.

## Run the Local Demo

From the skill directory, use Python 3.11+ to check the checkout and validate
the starter manifest.

```bash
python3 scripts/bioprospector_doctor.py
python3 scripts/bioprospector_preflight.py \
  --campaign examples/vanillin-yeast-v0/campaign-manifest.json
```

From the full source checkout, run `make first-look` to generate the demo
and open the report path it prints.

## Continue With a Campaign

Use the [first campaign guide](FIRST_CAMPAIGN.md) to create and validate a
manifest. See the [agent playbook](AGENT_PLAYBOOK.md) for task prompts or the
[workflow guide](WORKFLOWS.md) for tracker and compute handoffs.
