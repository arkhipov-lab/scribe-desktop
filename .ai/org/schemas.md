# Structured State And Schema Targets

Current machine-readable state:

```text
.ai/state/current-cycle.json
```

Current human-readable state:

```text
docs/iterations/YYYY-MM-DD-<slug>.md
.ai/state/debt.md
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
- `artifacts.commit`
- `metrics.review_loops`
- `metrics.human_decisions`
- `last_updated`

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
- metrics.

