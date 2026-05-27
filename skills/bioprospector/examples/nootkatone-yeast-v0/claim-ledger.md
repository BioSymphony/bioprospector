# Claim Ledger

## Claim Levels

- `hypothesis`: plausible route or candidate needing evidence.
- `domain_supported`: supported by domain or motif only.
- `ortholog_supported`: supported by homology to characterized enzymes.
- `evidence_supported`: supported by multiple reproducible evidence lanes.
- `characterized_elsewhere`: activity characterized outside the target host.
- `validated_elsewhere`: route or enzyme validated outside this campaign.
- `validated_in_target`: direct evidence in the target host for this campaign context.
- `rejected`: reviewed and rejected.

## Current Claims

| Claim ID | Claim | Level | Evidence | Caveat |
| --- | --- | --- | --- | --- |
| C001 | Nootkatone planning should be split into valencene formation, valencene oxidation, dehydrogenase support, CPR pairing, and host-fit review. | evidence_supported | route-ledger and reaction-step seed rows | No candidate has been scored by a live search yet. |
| C002 | P450 specificity and expression are likely dominant bottlenecks for nootkatone route design in yeast. | hypothesis | literature-seeded route risk | Requires evidence review and host-fit scoring. |
| C003 | Fed valencene bioconversion is the clearest validation handoff route family. | hypothesis | route-ledger seed row | Does not prove de novo production or product recovery. |
| C004 | AWS ElasticBLAST is an escalation lane for NCBI-wide search, not the default search lane. | evidence_supported | aws-safety-ledger and elasticblast-search-plan | RunPod Swiss-Prot/UniRef/Pfam lanes should run first when sufficient. |
| C005 | RunPod manual Pod is one reviewed optional heavy-search provider pattern, while local, cloud, neocloud, HPC, and managed workflows remain compatible through the same artifact contracts. | evidence_supported | compute-provider-ledger and workflow-framework-ledger | Provider choice cannot bypass no-false-success gates or target-evidence joins. |
| C006 | Long runs need stage progress and provider launch preflight before execution claims. | evidence_supported | stage-contract-ledger, stage-progress-ledger, provider-launch-preflight-ledger | Provider desired status, pod billing, or image name is not proof that work ran. |

## Boundary Note

This scaffold is public demo material only. It does not claim that nootkatone,
valencene, nootkatol, or any related product is produced in `Saccharomyces
cerevisiae` by this campaign. Candidate rows are seed review records until
public accessions, search provenance, host-fit review, route-stitching review,
and red-team checks are complete.
