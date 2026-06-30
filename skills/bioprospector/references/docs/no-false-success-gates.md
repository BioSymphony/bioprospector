# No-False-Success Gates

BioProspector must not treat a planned command, runner flag, mock summary, or
reference database hit as campaign success.

## Gates

1. Input audit before questions
   - Read the manifest, target contract, and ledgers first.
   - Ask the operator only for explicit `missing_operator_items`.

2. Operator intake before dispatch
   - Ask zero questions when the audit and operator request are sufficient.
   - If questions are needed, ask at most three grouped prompts.
   - Record skipped or assumed answers in `operator-intake-ledger.tsv`.
   - Treat `skip and go` as planning permission only, not execution or claim-closeout approval.

3. Maturity ladder
   - `L0`: plan exists
   - `L1`: tools ready
   - `L2`: inputs/materialized
   - `L3`: execution performed
   - `L4`: evidence joined
   - `L5`: claim-audited dossier

4. Artifact proof, not flag proof
   - Runner flags are intent only.
   - `L3` requires an execution artifact with `dry_run=false`, `mock_tools=false`, and `status=materialized`.
   - Tool proof rows are useful, but mock or dry-run proof cannot satisfy `L3` and cannot replace execution artifacts.

5. Stage and provider proof
   - Long runs require stage contracts, progress events, done markers, timeouts, and resume paths.
   - Provider desired state, pod billing, or job submission is not progress proof.
   - Blocking provider-launch-preflight rows must pass before live execution.
   - Silent fallback closes as degraded/partial, not success.

6. Target evidence join
   - Candidates must join to step, organism/sample, and target dataset evidence before target claims.
   - Public/reference hits remain reference context until joined target evidence exists.

7. Decoy and negative controls
   - Wide/frontier search lanes need passed blocking controls before candidate promotion.
   - Failed controls force downgrade or rerun through a separate execution issue.

8. Final contract self-check
   - Closeout joins inputs, execution artifacts, tool proof, target evidence, controls, package indexes, maturity, rankings, and claims.
   - Provider-side sequence packages need materialized pointers, checksums, cluster membership, graph joins, and no pending evidence-event joins before L5.
   - The self-check returns blockers instead of creating new evidence.

## Commands

```bash
python3 scripts/bioprospector_input_audit.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json

python3 scripts/bioprospector_contract_self_check.py \
  --campaign examples/nootkatone-yeast-v0/campaign-manifest.json
```

For live closeout:

```bash
python3 scripts/bioprospector_contract_self_check.py \
  --campaign path/to/live/campaign-manifest.json \
  --require-real-execution \
  --require-target-evidence \
  --require-decoy-controls \
  --require-maturity L5
```

The nootkatone public demo is intentionally planning-only. It should pass the
planning self-check and fail live closeout requirements until real execution,
target evidence, controls, and claim audit artifacts exist.
