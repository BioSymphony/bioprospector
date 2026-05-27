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
| C001 | Huperzine A is a useful public BioProspector stress case because the scaffold must preserve unresolved chemistry, source-context ambiguity, and claim ceilings. | evidence_supported | target contract, unknown-step ledger, pathway-inference ledger | This is a claim about demo design, not biology. |
| C002 | The public scaffold should not claim a complete huperzine A pathway. | evidence_supported | route-stitching scorecard and red-team route | No live search, assay, or target evidence has run. |
| C003 | Endophyte comparator evidence must stay separate from lycophyte or target-organism evidence. | hypothesis | organism-sample and target-dataset ledgers | Comparator evidence can inform search planning, not close route claims. |
| C004 | Candidate-family rows for CAO/DAO, PKS-III, 2OGD/CYP/dehydrogenase, and unknown tailoring modules are prioritization hypotheses. | hypothesis | enzyme draft board and family sweep rows | Domain or family membership is not activity validation. |
| C005 | RunPod and ElasticBLAST entries are readiness contracts only. | evidence_supported | provider, stage, and execution-artifact ledgers | They do not prove provider execution or search output. |

## Boundary Note

This scaffold is public demo material only. It does not claim that huperzine A,
precursors, intermediates, or any pathway product is produced in any host.
Candidate rows are seed review records until public accessions, source context,
target evidence, decoy controls, route stitching, and red-team checks are
complete.
