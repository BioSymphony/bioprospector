# Expected-output snapshots

These snapshots show representative BioProspector output formats without bundling
raw biological data, provider logs, private paths, or generated runtime folders.

They illustrate artifact structure for documentation review. To see a live
campaign's joined evidence, regenerate the full outputs locally:

```bash
make local-demo
```

Runtime outputs stay ignored under `.runtime/`; these snapshots are compact
public documentation artifacts.

Included snapshots:

- `campaign-plan.summary.json`: campaign graph summary.
- `genecluster-atlas-plan.summary.json`: metadata-only atlas plan summary.
- `pareto-frontier-ledger.sample.tsv`: route frontier sample rows.
- `workgraph-inventory.sample.md`: generated issue-lane inventory.
- `provider-readiness-tree.sample.md`: future RunPod, HPC, or cloud handoff format.
- `closeout-packet.sample.md`: promoted, parked, and killed candidate closeout format.
- `dossier-excerpt.md`: human-readable dossier excerpt.
