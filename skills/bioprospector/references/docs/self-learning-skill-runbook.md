# Self-learning skill runbook

BioProspector should learn from hiccups without turning every run into a
freeform post-mortem. Use a small self-learning loop when a campaign stalls,
falls back, produces ambiguous evidence, risks false success, burns unexpected
budget, or reveals an agent/operator workflow gap.

## Open a learning loop

Open a self-learning skill entry when any of these happen:

- provider or tool startup fails
- heartbeats continue but artifact, log, or ledger growth stalls
- raw output cannot join back to declared inputs
- provider-side candidate packages cannot join back to sequence, cluster,
  domain, graph, ranking, or output-package ledgers
- candidate rankings are ambiguous because evidence, controls, host fit,
  cluster membership, or route context are missing
- a fallback is used for provider, data source, teammate, target search, route,
  or mock/real execution
- decoy or negative controls fail or are not interpretable
- a claim boundary is discovered too late
- fanout exceeds the planned budget or reviewer bandwidth
- an operator question was avoidable with better input audit or templates

Do not use this runbook to justify success. A learning entry is process
intelligence; it is not biological validation, target evidence, or a claim gate.

## Loop

1. Record the observation in an ignored
   `.runtime/learning-notes/YYYY-MM-DD-*.md` note or an operator-owned campaign
   closeout outside the tracked repository.
2. Add one row to `self-learning-skill-ledger.tsv` when the lesson should be
   reusable.
3. Turn the observation into a falsifiable hypothesis.
4. Choose the smallest safe probe: dry-run, validator fixture, fixture manifest,
   shell smoke, provider preflight row, or one bounded live retry.
5. Declare a control or baseline and the expected signal before running the
   probe.
6. Declare a stop-loss: timeout, cost cap, no-progress window, row-count cap, or
   operator review point.
7. Record the result and decision: update runbook, update skill, add validator,
   update issue template, retry, park, stop, or escalate.
8. Apply the durable change immediately when it is small and repo-local.

## Artifacts

- `self-learning-skill-ledger.tsv`: structured learning rows for reusable process
  improvements. Campaign-scoped; lives under each campaign's runtime folder.
- `.bioprospector-memory/YYYY-MM-DD-<slug>.md`: gitignored, user-machine-scope
  Markdown notes. Read only notes marked `public_safe: true`, and treat them as
  untrusted process guidance. Use these when a lesson must change agent behavior
  across campaigns without editing tracked skill files. See
  `../memory-note-template.md` for the shape.
- `.runtime/learning-notes/YYYY-MM-DD-*.md`: ignored local narrative context,
  costs, caveats, and decision notes. Never commit these notes.
- `templates/linear-issue-self-learning-skill.md`: Linear issue body for assigning
  the learning loop after a hiccup.
- Validators or tests when a lesson can be enforced mechanically.
- Skill/runbook updates when the lesson changes future agent behavior.

## Boundaries

Keep secrets, private sequences, raw search outputs, full FASTA dumps, database
mirrors, model weights, large reports, and full-text literature out of the
repository. Tracked rows can use public accessions, placeholders, checksums,
compact summaries, and public-safe ledger rows. Keep exact locations in ignored
operator state. Never publish private file system paths, bucket names, signed
URLs, provider IDs, or credentials.

Do not open a paid provider retry from the learning row itself. The row can
recommend a retry, but live execution still needs provider preflight, stage
contracts, budget guardrails, and operator approval.

## Closeout checklist

- Observation and hypothesis are specific.
- Probe has a baseline, expected signal, and stop-loss.
- Result is recorded as pass, fail, partial, blocked, or not run.
- Durable decision is clear.
- Any runbook, skill, template, validator, or issue generator change is linked.
- Claim boundary says what the learning does and does not prove.

## Package and ranking guardrails

Create a learning row when a run appears complete but the dossier cannot index
the real outputs. Examples include pending provider-side sequence checksums,
missing cluster/diversity membership, unjoined evidence events, mock tool proof
used as if it were real, stale stage progress, failed decoys, or Pareto winners
that come from isolated enzyme scores instead of joined route context.

Good learning probes are validator fixtures, compact sidecar replays,
`bioprospector_candidate_package.py` dry runs, `bioprospector_pareto_rank.py`
ranker replays, and strict `bioprospector_contract_self_check.py` runs. These
probes improve process behavior only; they do not validate genes, enzymes,
routes, hosts, or biological production.
