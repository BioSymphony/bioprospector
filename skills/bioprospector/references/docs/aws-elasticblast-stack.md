# AWS ElasticBLAST stack

Reviewed: 2026-08-30.

## Purpose

AWS ElasticBLAST is the BioProspector wide-search escalation lane for official
NCBI BLAST databases such as `nr`, `refseq_protein`, and `swissprot`.

RunPod is one supported optional execution pattern for controlled local
datasets, Swiss-Prot, UniRef, Pfam, DIAMOND, MMseqs2, HMMER, scoring, and
pathway stitching. Do not stage full `nr` on RunPod by default.

## Decision rule

Use RunPod first when the search can be answered by:

- Swiss-Prot or curated seed FASTAs
- UniRef50 or UniRef90
- selected NCBI Datasets proteomes
- Pfam or custom HMMs
- custom public/campaign-approved datasets

Use ElasticBLAST only when a wide/frontier step needs official NCBI BLAST
database coverage after cheaper lanes are insufficient.

## Database availability

ElasticBLAST supports NCBI cloud-hosted BLAST databases by database name, but
do not assume every NCBI Web BLAST database is available as an ElasticBLAST DB.
Treat ClusteredNR as a separate reviewed lane unless the operator confirms its
accepted database name against the current NCBI cloud listing.

## Readiness bundle

Generate a prep bundle from a campaign manifest:

```bash
python3 scripts/bioprospector_elasticblast_bundle.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json \
  --out .runtime/elasticblast-readiness/nootkatone-yeast-v0 \
  --bucket-uri s3://REPLACE_ME_OPERATOR_APPROVED_BUCKET/biosymphony-elasticblast \
  --database nr \
  --budget-usd 25
```

The bundle is written under `.runtime/`, which is git-ignored. It contains:

- `elasticblast-run-manifest.json`
- `elasticblast-search-plan.tsv`
- `elasticblast-run-ledger.tsv`
- `aws-safety-ledger.tsv`
- `configs/*.ini`
- `aws-setup-checklist.md`
- `cleanup-verification.md`
- `README.md`

The generator does not authenticate to AWS, create buckets, upload query files,
submit jobs, or download results.

## AWS setup boundary

Do not paste AWS access keys, secret keys, session tokens, root credentials, MFA
codes, or SSO verification codes into chat, Linear, repo files, or `.env` files.

For a first smoke test:

1. Sign into AWS Console with MFA.
2. Open AWS CloudShell in the selected region.
3. Run setup and smoke commands there.

For later runs, use an operator-managed profile or secret store:

```bash
aws configure sso --profile bioprospector
aws sso login --profile bioprospector
aws sts get-caller-identity --profile bioprospector
```

Codex may inspect non-secret command output and write local config templates,
but should not handle long-lived AWS secrets.

## Required safety controls

Before any `elastic-blast submit`:

- dedicated AWS sandbox account or reviewed project account
- an operator-approved budget; the generated example uses `$25`
- alerts at actual/forecasted thresholds
- Cost Anomaly Detection with a low threshold
- low EC2 vCPU quotas retained for smoke runs
- private S3 bucket with block-public-access and lifecycle cleanup
- ElasticBLAST janitor role or explicit cleanup procedure
- the current NCBI-supported version; the documentation reviewed on
  2026-08-30 specifies [`elastic-blast==1.5.0`](https://blast.ncbi.nlm.nih.gov/doc/elastic-blast/)
- one-node first run
- preemptible/spot enabled for scout runs
- public or separately approved query FASTA only

Budgets and anomaly alerts are delayed. They reduce risk but are not hard
real-time spending caps.

## Operator-owned live-run boundary

Generated configs are templates. A live ElasticBLAST run is an operator-owned
activity outside this public repo: activate the operator-managed environment,
submit only reviewed configs, monitor status, fetch only compact summaries, and
delete the job from the same secure shell after cleanup review.

After deletion, verify EC2, AWS Batch, and CloudFormation resources by tag and
region. Record cleanup status in `elasticblast-run-ledger.tsv`.

## Output contract

Raw ElasticBLAST outputs stay in S3 until parsed and reviewed. BioProspector
copies back only compact artifacts:

- candidate-funnel count updates
- candidate hit summaries
- rejected-candidate rows
- provenance records with config, database, region, and an opaque result pointer
- final shortlist rows
- cleanup status and aggregate budget status

Do not copy full BLAST result archives or uploaded query FASTAs into this repo.

## Bounded campaign role

For a bounded campaign, use ElasticBLAST only for unresolved wide-search steps:

1. RunPod Swiss-Prot/Pfam/UniRef lanes first.
2. Compress candidate families.
3. Escalate only unresolved wide/frontier steps to ElasticBLAST.
4. Cap each step at one node and a small result limit until the cleanup loop is
   proven.
5. Red-team claims before using NCBI-wide results in route stitching.
