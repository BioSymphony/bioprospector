# CLI Reference

All commands are local control-plane helpers. They do not launch RunPod,
submit ElasticBLAST, seed Linear, download databases, or write raw/private
biological data into the repo, tracker, chat, or publishable artifacts. Future
operator-approved execution should keep raw/heavy outputs in user-approved
external locations and return compact ledgers, pointers, hashes, summaries, and
dossiers.

The package is a checkout-oriented launcher: scripts, schemas, examples, and
agent skill files stay in the repository. Install editable, or run with
`PYTHONPATH=src` from the repo root:

```bash
PYTHONPATH=src python3 -m biosymphony_bioprospector.cli --help
PYTHONPATH=src python3 -m biosymphony_bioprospector.cli commands --json
```

For safety, packaged entry points execute scripts only from the editable
checkout that owns the CLI, or from an explicit `BIOPROSPECTOR_REPO_ROOT`. They
do not discover and run repo-shaped code from the caller working directory.
An installed wheel without `BIOPROSPECTOR_REPO_ROOT` can print version/help, but
script-backed commands fail closed instead of guessing a checkout.

## Health and release

| Command | Purpose |
| --- | --- |
| `bioprospector doctor --include-runtime` | Check schema, examples, optional tools, public audit, and forbidden tracked paths. |
| `bioprospector workspace-status` | Summarize git state, runtime sidecar counts, key files, and suggested commands. Paths, names, branches, and commit identifiers are hidden by default. |
| `bioprospector commands --json` | Print a machine-readable command index for wrappers, docs, and agents. |
| `bioprospector quickstart` | Print the local-only first-run path. |
| `bioprospector --version` | Print the package version without checkout discovery. |
| `python3 scripts/public_audit.py .` | Scan the public tree for secrets, private paths, raw artifacts, and forbidden tracked output. |
| `python3 scripts/check_docs_links.py .` | Check local Markdown links without network access. |

## Campaign Control Plane

| Command | Purpose |
| --- | --- |
| `bioprospector new-campaign` | Create a compact campaign scaffold from a target contract. |
| `bioprospector preflight` | Validate manifest fields, ledger keys, headers, enums, joins, and local artifact policy. |
| `bioprospector input-audit` | Summarize declared inputs before asking operator questions. |
| `bioprospector campaign-status` | Summarize route counts, search widths, gates, maturity, and next commands. |
| `bioprospector agent-brief` | Build a Codex/Claude/goal-ready kickoff brief over campaign status, graph, and safety boundaries. |
| `bioprospector campaign-handoff` | Build a review-only handoff packet with status, graph, commands, and safety notes. |
| `bioprospector issue-dry-run` | Generate public-safe Linear-style issue bodies without seeding Linear. |
| `bioprospector contract-self-check` | Join inputs, artifacts, target evidence, controls, maturity, and claims before closeout. |
| `bioprospector stage-contract` | Validate stage contracts, progress rows, stale heartbeats, and strict live closeout gates. |
| `bioprospector self-learning` | Append a reusable process-learning row after a hiccup. |

## Evidence and dossier

| Command | Purpose |
| --- | --- |
| `bioprospector evidence-ingest` | Convert compact BLAST6/DIAMOND/MMseqs/HMMER/domain tables into evidence ledgers. |
| `bioprospector campaign-graph` | Compile a machine-readable campaign DAG. |
| `bioprospector candidate-package` | Build candidate sequence-pointer, diversity, graph, ranking, and package ledgers. |
| `bioprospector pareto-rank` | Produce candidate rankings and route-level Pareto views. |
| `bioprospector retrospective` | Scan local after-run folders into a redacted retrospective ledger. |
| `bioprospector dossier-export` | Export a compact claim-bounded Markdown dossier. |

## GeneCluster Atlas

| Command | Purpose |
| --- | --- |
| `bioprospector genecluster-atlas-plan` | Build metadata-only source, route, and Atlas contract ledgers. |
| `bioprospector genecluster-atlas-normalizers` | Normalize compact summary/fixture tables into Atlas contract artifacts. |
| `bioprospector genecluster-atlas-contracts` | Validate cluster calls, BGC consensus, function votes, function jury rows, and handoff manifests. |

## Provider Readiness

| Command | Purpose |
| --- | --- |
| `bioprospector runpod-bundle` | Write review-only RunPod readiness files; does not create pods. |
| `bioprospector elasticblast-bundle` | Write review-only AWS ElasticBLAST config; does not touch AWS. |
| `bioprospector elasticblast-probe` | Read-only local/AWS readiness probe; does not submit jobs. |
| `bioprospector public-demo-smoke --skip-provider-bundles` | Generate issue drafts and dossier sidecars without provider readiness bundles. |

Use `--help` on individual commands for arguments.
