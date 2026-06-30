# Workflow Framework Compatibility

## Goal

Define how shell scripts, Python CLIs, Nextflow, Snakemake, CWL, WDL, or managed workflows satisfy the same BioProspector output contract.

## Required Artifacts

- `workflow-framework-ledger.tsv`
- provenance and resume requirements
- execution-artifact output requirements

## Acceptance Criteria

- Framework choice does not change campaign semantics.
- Live runners emit execution artifacts with explicit `dry_run` and `mock_tools` values.
- Resumable frameworks are preferred for real campaigns; shell/Python remains acceptable for readiness and smoke checks.

## Validation

```bash
python3 skills/bioprospector/scripts/bioprospector_preflight.py --campaign path/to/campaign-manifest.json
```
