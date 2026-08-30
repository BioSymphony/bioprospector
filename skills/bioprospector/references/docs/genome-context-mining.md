# Genome context and BGC mining

Genome-context lanes handle anchor-neighborhood searches, co-localized genes,
and cryptic biosynthetic gene cluster evidence. They are planning lanes until an
operator approves external data access and compute.

## Use Cases

- Search around known pathway anchor genes.
- Find co-localized P450s, oxidoreductases, transporters, UGTs, or tailoring enzymes.
- Compare candidate neighborhoods against known BGCs.
- Triage novelty and gene-cluster family support.

## Tool Families

- antiSMASH and plantiSMASH for BGC detection.
- cblaster for clustered homolog searches.
- GECCO and DeepBGC for scalable BGC prediction.
- BiG-SCAPE, BiG-SLiCE, and MIBiG for cluster-family and known-product comparison.

## Output Boundary

Raw genome FASTA, GFF, GenBank, antiSMASH archives, and BGC databases stay
outside this repo. BioProspector stores only:

- `genome-mining-plan.tsv`
- `genome-hit-ledger.tsv`
- public accession IDs, opaque external pointers managed outside this
  repository, coordinates, checksums, and compact claim summaries

Neighborhood support is evidence, not functional validation.
