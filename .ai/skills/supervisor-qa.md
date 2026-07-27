# Supervisor QA

## Purpose

Generate a complete **manual QA plan** for the current iteration — written for the human Product Owner, not for developers. Validates observable Scribe behavior **without reading code**.

Does not inspect source, duplicate code review, generate Cursor prompts, prepare commits, or invent features outside the approved slice.

---

## Invocation

```
Use supervisor-qa.
```

---

## Automatic Context Loading

| Source | Purpose |
|--------|---------|
| [PRODUCT.md](../../PRODUCT.md) | UX expectations / non-goals |
| [ROADMAP.md](../../ROADMAP.md) | Slice context |
| [docs/scenarios/](../../docs/scenarios/) | Expected flows |
| [TESTING.md](../../TESTING.md) | Smoke vocabulary |
| [README.md](../../README.md) / [DEVELOPMENT.md](../../DEVELOPMENT.md) | How to run the app |
| [`.ai/org/`](../org/) | Reusable process roles, gates, and metrics for process iterations |
| [`.ai/product/`](../product/) | Product invariants and scenario adapters |
| [`.ai/repo/`](../repo/) | Repo validation commands for QA checks |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration and gate state |
| [`.ai/state/debt.md`](../state/debt.md) | Accepted/deferred debt to mention as watch-outs |
| [`.ai/state/product-followups.md`](../state/product-followups.md) | Open product wishes (do not fail QA for these) |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Approved scope, review/triage status, accepted Lows |
| Implementation summary + approved slice | What shipped |
| Latest review + accepted Lows | Watch-outs only |

Do **not** read source files to invent behavior. Derive cases from docs, slice, and summary.

When docs conflict on expected behavior, stop and ask the human.

---

## Preconditions

- Implementation summary exists
- Review gate clean (no unresolved High/Medium)
- Lows fixed or accepted/deferred under review-triage auto-fix policy (reasons recorded in ledger/debt); product-facing Lows must not have been silently deferred
- Approved slice exists
- Active ledger and current-cycle state exist
- `scripts/ai-cycle-validate.sh` passes for the current state

If gate not clean, stop and route to review-triage / codex-review.

---

## Responsibilities

- Infer user-facing goal and affected flows (file/record/transcribe/summary/history/export/permissions as relevant)
- Happy path + edge cases + regression checks in product language
- Pass / fail criteria
- Out of scope (do not fail the iteration for postponed work)
- Environment: prefer `./scripts/run-dev.sh` (and note Vite vs `USE_VITE_DEV=0` if relevant)
- Record the generated plan in the active ledger and update current-cycle state to `QA`
- After human QA: allow **pass with follow-ups captured** — record PO/QA product wishes in `.ai/state/product-followups.md` and the ledger Product Follow-ups section; do **not** file them as debt and do **not** fail the iteration for unimplemented wishes

---

## Non-responsibilities

- Does not decide pass/fail — human does
- Does not commit or expand scope

---

## Output Contract

```markdown
# Supervisor QA — <iteration name>

## Goal

<product language>

## Environment

- Start with `./scripts/run-dev.sh` (or packaged app if this slice is packaging)
- Note log path: `~/Library/Logs/Scribe/app.log` when privacy checks matter

## Test data

<short audio/video file, permissions state, settings reset, etc.>

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | ... | ... |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|

## Out of scope

- ...

## Pass criteria

- [ ] ...

## Fail criteria

- ...

## Notes

Accepted Lows, assumptions, suggested order (e.g. permissions before record).
Product wishes heard during QA (if any) — capture after pass; do not treat as fail criteria.

## State updates

- Ledger:
- Current cycle:
- Product follow-ups (if any):
```

---

## Human Checkpoints

Skill ends after generating the plan and recording that the plan was generated. Human executes QA, reports pass/fail, or **explicitly skips** (must be recorded in the active ledger, `.ai/state/current-cycle.json`, and by commit-manager).

A **pass with follow-ups** is a valid pass: write wishes to `.ai/state/product-followups.md` (and the ledger follow-ups section), keep commit gate open, and do not expand the current slice unless the Product Owner explicitly re-scopes.

On failure → bounded fix prompt → review loop. Do not invoke commit-manager until pass or explicit skip.

---

## Workflow position

```
codex-review → review-triage → supervisor-qa → manual QA → commit-manager
```
