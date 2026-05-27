## Summary

Describe the public-safe change and the user workflow it improves.

## Safety Boundary

- [ ] No credentials, tokens, signed URLs, private paths, provider IDs, or account IDs.
- [ ] No raw/private biological data, raw reads, full FASTA/GFF files, database mirrors, model weights, or unpublished sequences.
- [ ] Claim language stays bounded; no biological validation, production, or assay success is implied without joined evidence.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_doctor.py --include-runtime
make release-check
```
