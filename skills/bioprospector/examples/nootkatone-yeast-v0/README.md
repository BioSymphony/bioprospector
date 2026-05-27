# Nootkatone Yeast Frontier Demo

This compact public demo exercises wide/frontier search planning, candidate
compression, target-evidence and decoy-control gates, provider readiness
contracts, Pareto ranking, and dossier export.

Claim ceiling: ranked planning candidates and evidence gaps. The demo runs
entirely on tracked manifests. Job submission, database downloads, raw
sequence storage, candidate activity, and nootkatone production claims
remain with the operator's live closeout path and institutional review.

Validate locally:

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py \
  --campaign skills/bioprospector/examples/nootkatone-yeast-v0/campaign-manifest.json
```
