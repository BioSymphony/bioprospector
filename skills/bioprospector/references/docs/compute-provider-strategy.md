# Compute Provider Strategy

BioProspector is a control plane. Provider choice must not change the scientific
contract, claim language, or closeout gates.

For the user-facing local-to-cloud progression, see
[`WORKFLOWS.md`](WORKFLOWS.md#5-cloud-readiness).

## Reviewed Provider Patterns

RunPod manual Pods are the documented optional v0 pattern for controlled heavy
search lanes:

- manual Pod plus reviewable scripts
- persistent network volume mounted at `/workspace`
- workdir under `/workspace/bioprospector/runs/<campaign_id>`
- provider launch preflight before paid compute
- image pull and private registry auth verified before launch
- tool/image smoke before database staging
- compact summaries copied back to the repo
- no full `nr` mirror by default

AWS ElasticBLAST is a reviewed escalation lane for official NCBI BLAST
database scale. RunPod remains the primary lane for candidate compression,
scoring, route stitching, and provenance assembly.

Neocloud, cloud VM, SSH/HPC, local-full, and managed workflow providers can be
approved for a specific compatible role only after they prove the same storage,
progress, artifact, cost, secrets, and self-check contracts. Approval means
accepted for that role, not exempt from gates.

Candidate-intelligence execution, such as signal/transmembrane/PTM prediction or
public UniProt/PubMed mutant extraction, is a compatible provider role. It can
run on neocloud or similar providers when the job is explicit, scoped to public
or approved AA-sequence pointers, and preflight proves tool availability, public
API access, egress policy, workdir, stage contract, and compact ledger egress.

## Compatible Provider Classes

Use `compute-provider-ledger.tsv` to declare provider choices:

- `local_lite`: preflight, issue generation, mock/path checks
- `local_full`: user-owned local hardware with external data paths
- `runpod_manual_pod`: reviewed heavy-search path
- `runpod_ssh_pod`: future RunPod path if SSH runner is approved
- `ssh_hpc`: institutional cluster or rented machine over SSH
- `cloud_vm`: generic AWS/GCP/Azure VM path
- `neocloud_vm`: GPU/CPU neocloud VM path
- `managed_workflow`: future managed workflow backend
- `elasticblast_cloud`: official NCBI BLAST database escalation

Provider-specific adapters are allowed only if they preserve the same ledgers:

- input audit
- run maturity
- execution artifacts
- target evidence
- decoy controls
- claim audit
- final contract self-check

At least one active RunPod row must set `blessed_path=true` with
`role=blessed_default`; those are internal ledger vocabulary values for the
reviewed example path, not a requirement that public users buy or use RunPod.
Non-default rows may also set `blessed_path=true` only for a bounded role:

- `elasticblast_cloud` with `role=wide_blast_escalation` or `role=blessed_escalation`
- `neocloud_vm`, `cloud_vm`, `ssh_hpc`, `local_full`, or `managed_workflow` with
  `role=blessed_compatible` or `role=blessed_escalation`

Other non-RunPod rows remain compatible options, fallback options, or future
paths until explicitly promoted.

## Workflow Frameworks

Use `workflow-framework-ledger.tsv` to declare runner frameworks:

- shell scripts for readiness and smoke checks
- Python CLIs for validators and ledger joins
- Nextflow or Snakemake for resumable live campaigns
- CWL/WDL or managed workflows only after wrappers emit the same ledgers

Framework choice is an implementation detail. It cannot weaken claim gates.
At least one active framework row must support `runpod_*` or `all_providers` so
the reviewed path is always represented in the runner contract.

## Success Path

1. Local lite: preflight, input audit, issue generation, planning self-check.
2. Provider readiness: tool/image/path smoke, no database staging.
3. Provider launch preflight: image pull, registry auth, volume, payload, branch/snapshot, secrets, and stage contract gates pass.
4. Small provider run: one lane, small curated resource, stage progress, and execution artifact row.
5. Evidence join: target-evidence and decoy-control ledgers updated.
6. Strict self-check: require real execution, target evidence, controls, and L5.
7. Only then widen searches, add agents, or escalate to ElasticBLAST.

## Stop Conditions

Stop before execution if:

- provider credentials would enter repo, Linear, or chat
- heavy data would be copied into the repo
- public API access, predictor tools, or provider egress needed for an on-demand candidate-intelligence run are unverified
- the provider cannot preserve an external workdir or volume
- the runner cannot emit execution-artifact rows
- the run cannot emit stage-progress rows with heartbeat, done marker, and resume path
- the workflow cannot distinguish mock/dry-run from real execution
- provider desired state is being treated as proof of container/workflow progress
- a fallback would be silent instead of partial/degraded
- reference hits would be presented as target organism/sample evidence

## No Download Preference

Default to no downloads during runs. The acceptable order is:

1. use prebuilt tool image
2. use provider volume/cache already staged
3. stage small curated resources through a reviewed issue
4. use a reviewed compatible neocloud/HPC/cloud provider when it preserves the same contracts
5. use ElasticBLAST for official NCBI-wide BLAST

Do not install tools live, mirror full `nr`, or copy raw search outputs back to
the repo during normal BioProspector campaigns.
