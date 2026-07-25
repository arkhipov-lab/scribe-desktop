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
| Implementation summary + approved slice | What shipped |
| Latest review + accepted Lows | Watch-outs only |

Do **not** read source files to invent behavior. Derive cases from docs, slice, and summary.

When docs conflict on expected behavior, stop and ask the human.

---

## Preconditions

- Implementation summary exists
- Review gate clean (no unresolved High/Medium)
- Lows fixed or explicitly accepted
- Approved slice exists

If gate not clean, stop and route to review-triage / codex-review.

---

## Responsibilities

- Infer user-facing goal and affected flows (file/record/transcribe/summary/history/export/permissions as relevant)
- Happy path + edge cases + regression checks in product language
- Pass / fail criteria
- Out of scope (do not fail the iteration for postponed work)
- Environment: prefer `./scripts/run-dev.sh` (and note Vite vs `USE_VITE_DEV=0` if relevant)

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
```

---

## Human Checkpoints

Skill ends after generating the plan. Human executes QA, reports pass/fail, or **explicitly skips** (must be recorded by commit-manager).

On failure → bounded fix prompt → review loop. Do not invoke commit-manager until pass or explicit skip.

---

## Workflow position

```
codex-review → review-triage → supervisor-qa → manual QA → commit-manager
```
