# Structured State And Schema Targets

Current machine-readable state:

```text
.ai/state/current-cycle.json
```

Current human-readable state:

```text
docs/iterations/YYYY-MM-DD-<slug>.md
.ai/state/debt.md
.ai/state/product-followups.md
```

## Current-Cycle Minimum Fields

- `schema_version`
- `iteration.id`
- `iteration.name`
- `iteration.ledger_path`
- `iteration.status`
- `phase`
- `gates.scope_approved`
- `gates.implementation_finished`
- `gates.review_gate`
- `gates.triage_status`
- `gates.supervisor_qa`
- `gates.retrospective`
- `gates.commit_allowed`
- `artifacts.debt_register`
- `artifacts.product_followups_register` (register file is required; JSON key may be omitted and defaults to `.ai/state/product-followups.md`)
- `artifacts.commit`
- `metrics.review_loops`
- `metrics.human_decisions`
- `last_updated`

## Optional Current-Cycle Artifacts (recommended)

Record when useful; not all required for validator pass:

- `artifacts.latest_implementation_prompt` — handoff prepared
- `artifacts.latest_implementation_summary` — summary received / review ready
- `artifacts.latest_review` / `artifacts.latest_triage`
- `artifacts.latest_auto_fix` — auto-fix pass generated/applied notes
- `artifacts.human_involvement_reason` — why human was asked mid-loop (if any)
- `artifacts.previous_iteration`

Phases already used by the validator include `planned`, `implementation-prompt`, `implementing`, `review`, `fixing`, `QA`, `commit-ready`, `retrospective`, `shipped`, `cancelled`. Prefer `implementation-prompt` / `implementing` while the summary is still pending; move to `review` only after the implementation summary is recorded.

## Future Schema Targets

Add stricter schemas only when a validator or automation consumer needs them:

- roadmap recommendation;
- product analysis;
- implementation summary;
- review findings;
- triage decisions;
- QA outcome;
- commit preparation;
- retrospective;
- metrics;
- product follow-up rows.
