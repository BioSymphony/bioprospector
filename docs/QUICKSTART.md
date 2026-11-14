# Quickstart

Try the bundled examples or [install the agent skill](AGENT_INSTALL.md)
to start with your own research question.

## Run the Local Demo

From the repository root, use Python 3.11+, Git, and Make.

```bash
make first-look
```

Open the review report at `.runtime/local-demo/huperzine/dossier.md`. The
demo also writes a campaign graph, candidate summaries, route rankings, and
synthetic GeneCluster records under `.runtime/local-demo/`.

## Import a Synthetic Search Result

To try the importer on its own, use the bundled DIAMOND-format table.

```bash
PYTHONPATH=src python3 -m biosymphony_bioprospector.cli evidence-ingest \
  --hits demos/sample-inputs/example.diamond.tsv \
  --format diamond --step-id S002 \
  --out .runtime/example-diamond
```

Open `.runtime/example-diamond/evidence-event-ledger.tsv` to see how the
importer records each hit. The other tables index candidates and record
filtering counts.

## Continue With a Campaign

Use the [first campaign guide](FIRST_CAMPAIGN.md) to create and validate a
manifest. See the [agent playbook](AGENT_PLAYBOOK.md) for task prompts or the
[workflow guide](WORKFLOWS.md) for tracker and compute handoffs.
