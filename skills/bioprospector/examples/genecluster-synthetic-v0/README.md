# Synthetic GeneCluster Atlas fixture

This fixture exercises the public GeneCluster Atlas contracts without real
organism data, private paths, raw sequences, or provider output.

It contract-checks:

- caller-level cluster summaries in `cluster_calls.tsv`
- cross-caller BGC consensus in `bgc_consensus.tsv`
- compact protein function votes in `protein_function_votes.tsv`
- function jury closeout in `protein_function_jury.tsv`

Claim ceiling: contract validation for caller summaries, BGC consensus,
function votes, and function jury rows on synthetic data. Biological
activity, physical clustering in a real organism, target-host production,
and wet-lab validation remain with the operator's evidence and
institutional review path.

Validate locally:

```bash
python3 skills/bioprospector/scripts/bioprospector_genecluster_atlas_contracts.py \
  --cluster-calls skills/bioprospector/examples/genecluster-synthetic-v0/cluster_calls.tsv \
  --bgc-consensus skills/bioprospector/examples/genecluster-synthetic-v0/bgc_consensus.tsv \
  --protein-function-votes skills/bioprospector/examples/genecluster-synthetic-v0/protein_function_votes.tsv \
  --protein-function-jury skills/bioprospector/examples/genecluster-synthetic-v0/protein_function_jury.tsv
```
