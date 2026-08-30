# First Campaign

This path creates a compact campaign scaffold for a new target molecule and
host. Use it when you want the agent to build the first route, enzyme,
evidence, and review lanes before deciding whether any deeper search is worth
running.

## 1. Start from the target contract

Copy the example contract to ignored runtime space and edit the planning fields.

```bash
mkdir -p .runtime/first-campaign
cp templates/target-contract.example.json .runtime/first-campaign/target-contract.json
```

Keep the contract compact and useful:

- target molecule name
- host or host family
- campaign goal
- optimization goals
- hard boundaries such as `planning_only` and `no_private_sequences`
- likely route families or seed reactions, if known
- review priorities such as host fit, evidence strength, source context, or
  diversity

Do not add private sequence data, unpublished constructs, collaborator notes,
credentials, provider IDs, or raw database paths.

## 2. Generate the scaffold

```bash
python3 skills/bioprospector/scripts/bioprospector_new_campaign.py \
  --target-contract .runtime/first-campaign/target-contract.json \
  --out .runtime/first-campaign/campaign \
  --campaign-id first-target-campaign-v0
```

The scaffold creates a manifest, required ledgers, a claim ledger, provenance,
and a self-learning row. It gives the agent a durable shape for route expansion,
candidate mining, dark-step review, and later dossier export.

## 3. Validate Before Expanding

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py \
  --campaign .runtime/first-campaign/campaign/campaign-manifest.json \
  --repo-root . \
  --scan-local-artifacts

python3 skills/bioprospector/scripts/bioprospector_input_audit.py \
  --campaign .runtime/first-campaign/campaign/campaign-manifest.json
```

Fix missing headers, invalid enum values, or unsafe local artifacts before
asking an agent to expand the campaign.

## 4. Expand Locally

Generate issue drafts and graph outputs under ignored runtime space:

```bash
python3 skills/bioprospector/scripts/bioprospector_issue_dry_run.py \
  --campaign .runtime/first-campaign/campaign/campaign-manifest.json \
  --prefix FIRST \
  --out .runtime/first-campaign/issues

python3 skills/bioprospector/scripts/bioprospector_campaign_graph.py \
  --campaign .runtime/first-campaign/campaign/campaign-manifest.json \
  --out .runtime/first-campaign/campaign-plan.json
```

Use the issue drafts as local review surfaces or paste them into your own work
tracker after checking repository and claim boundaries.

## 5. Promote Only Compact Summaries

Keep generated runtime artifacts ignored unless you intentionally promote a
small, reviewed summary into `docs/`, `demos/`, or `skills/bioprospector/examples/`.

Before promoting anything:

```bash
python3 scripts/public_audit.py .runtime/first-campaign
python3 scripts/check_docs_links.py .
```
