# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Require Python 3.11+. `check_release_metadata.py` uses `tomllib`, which is in
  the standard library only on Python 3.11 and newer.
- Test Python 3.11 through 3.14 in CI. Pin `actions/checkout` 7.0.1 and
  `actions/setup-python` 7.0.0 to reviewed immutable revisions.
- Refresh the external-tool index with MMseqs2, DIAMOND,
  nf-core/proteinfamilies, runpodctl, cblaster, BiG-SLiCE, and Folddisco
  information reviewed on August 30, 2026. The BiG-SLiCE entry records its
  August 2025 release date. Tool pages distinguish discovery from compatibility.
- Rewrite the README and supporting prose for a clearer reader path, explicit
  planning-fixture boundaries, and compact public-artifact guidance.
- Add durable design principles, a public roadmap, and a release checklist.
- Require process notes to declare `public_safe: true` before agents read them.

### Fixed

- CI installs the package and dev extras before `make release-check`, so the
  release gate runs. Previously the workflow had no install step and stopped on
  a missing `pytest`.
- Public audits reject common credential and private-key filenames as well as
  generic user-home paths without embedding local identities in the source.
- Workspace and retrospective summaries hide local history, exact run paths,
  identifiers, cost records, and timing records by default.

## [0.1.0] - 2026-05-26

Initial public release. Planning toolkit for biosynthetic-pathway campaigns,
enzyme-mining plans, pathway stitching, host-fit review, and portable work graphs.

### Added

- Agent skill packaging under `skills/bioprospector/SKILL.md` and install
  pointers for Claude Code, Codex, and Symphony workers
  (`docs/AGENT_INSTALL.md`).
- Local process-note pattern under `.bioprospector-memory/` (gitignored), with
  a template that prohibits secrets, private paths, campaign-specific data, raw
  sequences, provider identifiers, and signed URLs.
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
  `check_release_metadata.py`. CI matrix covers Python 3.11 through 3.13.
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
- README sections for the L0-L5 maturity ladder and route rankings
  (minimal-gene, highest-evidence,
  clearest validation handoff, best host-fit, ambitious de novo,
  diversity-library), and the self-learning loop.
- README diagrams for the public-data boundary, ledger-labeled workflow,
  agent harnesses, and compute providers.
- Campaign use-case chooser in `docs/USE_CASES.md`
  leading the existing workflow and operational recipes.
- Runnable tool-use round-trip walkthrough in the README so the
  evidence-ingest path can be exercised on the synthetic BLAST6, DIAMOND,
  MMseqs, and HMMER samples without a real search.
- Provenance requirements: SKILL.md claim policy requires tool versions, build
  dates, database snapshot dates, and parameters in
  `evidence_event_ledger.tsv` so claims are version-anchored; the literature
  ledger template asks the agent to include preprint scans (biorxiv,
  chemrxiv, field-specific servers) for fast-moving biosynthesis targets and
  record the preprint server, deposit date, and version.

[0.1.0]: https://github.com/BioSymphony/bioprospector/releases/tag/v0.1.0
