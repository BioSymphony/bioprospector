# AWS ElasticBLAST Readiness Prep

## Goal

Prepare a review-only AWS ElasticBLAST escalation bundle for NCBI-wide BLAST
when local or RunPod-local lanes are insufficient.

## Required Artifacts

- ignored `.runtime/elasticblast-readiness/...` bundle
- `elasticblast-search-plan.tsv`
- `elasticblast-run-ledger.tsv`
- `aws-safety-ledger.tsv`
- `provider-launch-preflight-ledger.tsv`

## Acceptance Criteria

- Search plan records database, program, query pointers, node count, budget, preemptible policy, cleanup, and approval status.
- AWS budget, quota, S3, janitor/cleanup, query-data approval, and data policy remain blockers until explicitly reviewed.
- Generated configs do not create buckets, upload queries, submit jobs, or handle AWS credentials.
- ElasticBLAST output is reference/search evidence only until joined to target evidence, controls, execution artifacts, and claim audit.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
python3 skills/bioprospector/scripts/bioprospector_contract_self_check.py --campaign path/to/campaign-manifest.json --require-decoy-controls
```
