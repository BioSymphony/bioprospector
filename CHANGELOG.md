# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-26

Initial public release. Agentic harness for discovering biosynthetic pathways
to target molecules: enzyme mining, pathway stitching, host-fit review,
construct hypotheses, and compute-portable work graphs.

### Added

- Agent skill packaging under `skills/bioprospector/SKILL.md` and install
  pointers for Claude Code, Codex, and Symphony workers
  (`docs/AGENT_INSTALL.md`).
- Local-memory pattern under `.bioprospector-memory/` (gitignored): the
  agent reads durable Markdown notes at the start of every campaign and
  writes new ones when it hits and overcomes a non-obvious issue, so the
  user's local checkout compounds across campaigns without anything going
  upstream. Five-section shape template under
  `skills/bioprospector/references/memory-note-template.md`.
- Campaign control plane: scaffold, preflight, input audit, issue dry-run,
  agent brief, handoff, status, stage contract, self-learning,
  retrospective.
- Evidence ingest for BLAST6, DIAMOND, MMseqs (12-column TSV), HMMER
  `--domtblout`, and domain summary tables. Raw sequence inputs are
  rejected at the boundary.
- GeneCluster Atlas planner, normalizers, and contract validator for
  cluster calls, BGC consensus, function votes, and function jury rows.
- Candidate package, campaign graph compile, Pareto rank, dossier export.
- Review-only provider readiness bundles for RunPod and AWS ElasticBLAST.
  Bundles produce launch packets for operator review; they do not create
  pods, submit jobs, or touch AWS.
- Release gates: `bioprospector_doctor.py`, `public_audit.py`,
  `check_docs_links.py`, `check_docs_index.py`,
  `check_release_metadata.py`. CI matrix covers Python 3.10 through 3.13.
- Synthetic samples under `demos/sample-inputs/` (BLAST6, DIAMOND, MMseqs,
  HMMER) and `skills/bioprospector/examples/genecluster-synthetic-v0/`
  (cluster calls, BGC consensus, function votes, function jury).
- Public demos: nootkatone frontier and huperzine dark-step walkthroughs
  with compact expected outputs under `demos/expected-outputs/`.
- Ledger schema `schemas/bioprospector-ledgers.json` (version 1.2.0)
  covering 73 ledger headers, 7 required and 69 optional ledger keys.
- Linear-style issue templates under `templates/` covering active-site
  audit, assay handoff, BGC context, candidate intelligence, candidate
  package, chemoenzymatic fallback, compound-source priors, compute
  provider, contract self-check, dark-step resolver, decoy control,
  ElasticBLAST prep, enzyme family sweep, evidence lane, genome mining,
  host comparison, input audit, ledger schema, literature ledger, and
  metabolic model lanes.
- README Why This Is Powerful section surfacing the L0-L5 maturity ladder,
  the multi-winner Pareto frontier (minimal-gene, highest-evidence,
  clearest validation handoff, best host-fit, ambitious de novo,
  diversity-library), and the self-learning loop.
- README diagrams: public/private boundary, ledger-labeled core workflow,
  and multi-harness portability bowtie.
- Campaign-shaped When To Reach For This chooser in `docs/USE_CASES.md`
  leading the existing workflow and operational recipes.
- Runnable tool-use round-trip walkthrough in the README so the
  evidence-ingest path can be exercised on the synthetic BLAST6, DIAMOND,
  MMseqs, and HMMER samples without a real search.
- Freshness nudges: SKILL.md claim policy now requires tool versions, build
  dates, database snapshot dates, and parameters in
  `evidence_event_ledger.tsv` so claims are version-anchored; the literature
  ledger template asks the agent to include preprint scans (biorxiv,
  chemrxiv, field-specific servers) for fast-moving biosynthesis targets and
  record the preprint server, deposit date, and version.

[0.1.0]: https://github.com/BioSymphony/biosymphony-bioprospector/releases/tag/v0.1.0
