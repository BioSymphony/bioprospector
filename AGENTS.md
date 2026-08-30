# BioSymphony BioProspector agent guide

Guide for agents and operators working in this repo.

## Mission

Equip long-running planning agents to run real bioprospecting and
pathway-stitching campaigns. The same campaign contract drives Symphony with
Linear, Claude Code workers with Linear, Codex with any tracker, or another
multi-agent harness the operator already uses, and it scales across local
compute, RunPod, HPC, cloud VMs, neocloud, managed workflows, and AWS
ElasticBLAST.

The repo ships:

- the canonical BioProspector skill
- compact public examples for vanillin, nootkatone, Huperzine A, and a
  synthetic GeneCluster fixture
- route, reaction-step, candidate, evidence, control, and claim ledgers
- RunPod and AWS ElasticBLAST readiness generators that produce launch
  packets for operator review
- metadata-only GeneCluster atlas source, route, and contract planning, plus
  summary normalization and contract validation
- local checkout doctor for schema, examples, optional tool visibility,
  audit status, and forbidden tracked paths
- Linear and Symphony issue templates and sidecar workflow drafts
- validator and public-release audit checks

## Public safety rules

Do not add:

- API keys, provider credentials, signed URLs, SSH keys, or registry auth
- private workstation paths or non-public local history
- pod IDs, network volume IDs, account IDs, or private project identifiers
- private Linear issue text, internal run logs, cost records, or raw pod output
- unpublished biological data, private sequences, raw reads, database mirrors, model weights, or restricted datasets
- wet-lab protocols, construct automation, or claims of biological validation

Use synthetic or explicitly public examples only. Keep public examples compact
and label dry-run or mock artifacts clearly.

## Required checks

Run before committing public-release changes:

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime
make release-check
```

That gate compiles the scripts, runs unit tests, validates the public example
campaigns, runs planning self-checks, generates local-only demo sidecars, and
scans both the tree and `.runtime` output for public-release blockers.

Before each public release, also read [`docs/PUBLIC_SWITCH_CHECKLIST.md`](docs/PUBLIC_SWITCH_CHECKLIST.md)
and confirm no `.runtime`, `logs`, raw biological artifacts, private paths, or
provider identifiers are tracked.

## Skill loop

Use [`skills/bioprospector/SKILL.md`](skills/bioprospector/SKILL.md). Summary:
target contract -> input audit -> minimal operator intake -> route universe ->
reaction steps -> candidate mining lanes -> target evidence and controls ->
route stitching -> claim audit -> review-package ledgers.

## Claim boundaries

Treat outputs as design intelligence and prioritization, not biological
validation. Do not claim production, validation in a host, route completion, or
assay success without direct evidence joined through the declared ledgers.
