# Structured State And Schema Targets

Current machine-readable state:

```text
.ai/state/current-cycle.json
.ai/state/review-findings.json
.ai/org/schemas/current-cycle.schema.json
.ai/org/schemas/review-findings.schema.json
```

Current human-readable state:

```text
docs/iterations/YYYY-MM-DD-<slug>.md
.ai/state/debt.md
.ai/state/product-followups.md
```

## Current-Cycle Schema

`scripts/ai-cycle-validate.sh` validates `.ai/state/current-cycle.json` against
[`.ai/org/schemas/current-cycle.schema.json`](./schemas/current-cycle.schema.json)
using a stdlib Python subset checker (`scripts/ai-cycle-schema-check.py`). No
external JSON Schema package is required.

Required top-level fields:

- `schema_version`
- `iteration` (`id`, `name`, `ledger_path`, `status`, `date_started`, `date_completed`)
- `approved_scope` (`source`, `date`, `goal`, `in_scope`, `out_of_scope`)
- `phase`
- `gates` (`scope_approved`, `implementation_finished`, `review_gate`, `triage_status`, `supervisor_qa`, `retrospective`, `commit_allowed`, `committed`)
- `artifacts` (registers, latest role artifacts, `commit`, `previous_iteration`, `latest_implementation_prompt`, `latest_implementation_summary`)
- `metrics` (`review_loops`, `human_decisions`, finding counts, `qa_outcome`, `outcome`)
- `last_updated`
- `handoff` (`next_role`, `reason`, `required_inputs`, `blocked_by`, `latest_artifacts`)

Use `null` where evidence is not available yet (especially pending review metrics and unset artifact pointers). Do not invent fake zeroes — except finding counts once `.ai/state/review-findings.json` exists for the iteration: then `metrics.*_findings` must equal the structured counts (including `0`).

## Review Findings Schema

`scripts/ai-cycle-validate.sh` also validates `.ai/state/review-findings.json` against
[`.ai/org/schemas/review-findings.schema.json`](./schemas/review-findings.schema.json).

Required top-level fields:

- `schema_version`
- `iteration_id` (must match `current-cycle.iteration.id`)
- `findings` (array)
- `last_updated`

Each finding requires:

- `id` (stable inside the iteration, e.g. `R1`)
- `review_loop` (integer ≥ 1)
- `severity` (`High` | `Medium` | `Low`)
- `status` (`open` | `fixed` | `accepted_debt` | `deferred` | `not_reproducible`)
- `summary` (non-empty)
- `location` (string path/line, or `null` only for process-level / repo-wide findings)
- `owner` (next role / owner)
- `resolution` (string or `null`)
- `debt_id` (required when `status=accepted_debt`; must exist in `.ai/state/debt.md`)
- `product_followup_id` (only for product-facing wishes routed to `.ai/state/product-followups.md`; never with review debt)

Validator rules beyond schema shape:

- `metrics.high_findings` / `medium_findings` / `low_findings` must equal structured counts.
- High/Medium findings must be `fixed` or `not_reproducible` (commit blocked otherwise).
- `accepted_debt` must reference an existing debt id.
- Product wishes must not be accepted as technical review debt.
- Markdown ledger High/Medium checks remain as a compatibility layer during the transition.

Markdown ledgers stay the human-readable record. Structured findings are the auditable/countable source for metrics and gates.

## Structured Handoff

`current-cycle.handoff` is the structured source for **who acts next**.

- Every phase transition must update `handoff` (not only `phase` / `gates`).
- Terminal states (`shipped`, `cancelled`, `rejected`) use `next_role=none`.
- Human checkpoints use `next_role=human-product-owner` and name the decision in `blocked_by` or `reason`.
- Feature-manager remains the normal orchestrator after scope approval.
- `cursor-implementation-prompt` stays internal/specialized — not a Product Owner-facing next role.

Allowed `next_role` values: `product-analyst`, `roadmap-planner`, `feature-manager`, `implementation-agent`, `codex-review`, `review-triage`, `supervisor-qa`, `commit-manager`, `iteration-retrospective`, `human-product-owner`, `none`.

## Phases

Allowed `phase` / `iteration.status` values:

`planned`, `implementation-prompt`, `implementing`, `review`, `fixing`, `QA`, `commit-ready`, `retrospective`, `shipped`, `cancelled`, `rejected`.

Prefer `implementation-prompt` / `implementing` while the summary is still pending; move to `review` only after the implementation summary is recorded in `artifacts.latest_implementation_summary` and the ledger.

## Future Schema Targets

Add stricter schemas only when a validator or automation consumer needs them:

- roadmap recommendation;
- product analysis;
- implementation summary;
- triage decisions;
- QA outcome;
- commit preparation;
- retrospective;
- metrics;
- product follow-up rows.
