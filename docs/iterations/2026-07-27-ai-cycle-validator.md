# Iteration: AI Cycle Validator

**Status:** commit-ready
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Add lightweight AI cycle validator scripts for the durable process state.

**Hypothesis:** If agents can run a simple validator before phase transitions and commit prep, the workflow will catch stale state, broken gate order, unresolved findings, missing ledgers, and forbidden paths earlier.

**In scope:**
- Add `scripts/ai-cycle-status.sh`.
- Add `scripts/ai-cycle-validate.sh`.
- Validate `.ai/state/current-cycle.json`.
- Validate that the active ledger file exists.
- Validate gate order: `commit_allowed=true` requires clean review/triage and QA passed or skipped.
- Validate that shipped iterations record a commit hash.
- Check unresolved High/Medium findings in the active ledger.
- Check forbidden paths in staged or working-tree changes.
- Add short documentation for when to run the validator.
- Update only workflow/skills locations that actually use the validator.

**Out of scope:**
- Full JSON schemas for every role output.
- Replacing human approval gates.
- Product-facing Scribe behavior changes.
- CI integration.

**Human approval:**
- Source: explicit user request, "Реализуй Этап 2: Добавить Validator"
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Human / Codex | Approved scope in chat | done |
| Implementation prompt | Codex | Direct implementation from approved process scope | done |
| Implementation | Codex | Validator scripts and process docs | done |
| Review | Codex independent review | loop 1: 1 Medium + 2 Low | done |
| Triage | review-triage | blocking R1 → AI fix; R2–R3 included (cheap) | done |
| Fix | Cursor | R1–R3 fixed in validator + debt register | done |
| Re-review | Codex independent review | loop 2 clean (no open findings); R1–R3 verified fixed | done |
| Triage | review-triage | review gate clean; route to supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated 2026-07-27; human passed 2026-07-27 | done |
| Commit prep | commit-manager | pending human commit approval | pending |

## Implementation Summary

- Files changed:
  - `scripts/ai-cycle-status.sh`
  - `scripts/ai-cycle-validate.sh`
  - `.ai/state/current-cycle.json`
  - `docs/iterations/2026-07-27-ai-cycle-validator.md`
  - `docs/workflows/README.md`
  - `docs/workflows/feature-development-pipeline.md`
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/supervisor-qa.md`
  - `.ai/skills/commit-manager.md`
  - `.ai/state/debt.md`
- Behavior changed:
  - Agents can inspect active cycle state with `scripts/ai-cycle-status.sh`.
  - Agents can validate JSON state, ledger existence, phase gates, commit prerequisites, shipped commit hash, unresolved High/Medium findings, and forbidden paths with `scripts/ai-cycle-validate.sh`.
  - Unresolved-findings matching treats `fixed`/`resolved`/`closed`/`clean` as prefixes so annotated statuses like `fixed (verified on re-review)` count as resolved, and reads status from the last table column so finding text may contain `|`.
  - `commit_allowed=true` success path prints an explicit OK line.
  - Workflow docs and the skills that actually use validation now name when to run it.
- Assumptions:
  - The validator stays lightweight and shell-based.
  - `jq` is available for JSON state checks.
- Verification reported by implementer:
  - `scripts/ai-cycle-status.sh`
  - `scripts/ai-cycle-validate.sh`
  - `git diff --check`
  - Regression: prior ledger `fixed (...)` statuses no longer false-fail
  - Spot-check: synthetic Medium `open` still fails

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `scripts/ai-cycle-validate.sh:208-209` | Unresolved-findings matcher required exact fixed/resolved/closed/clean, so established statuses like `fixed (verified on re-review)` false-failed; also broke when finding text contained `|`. | fixed |
| R2 | Low | `.ai/state/debt.md:27` | Planned item `P-2026-07-26-001` (Cycle validator) still `planned` while this iteration implements it. | fixed |
| R3 | Low | `scripts/ai-cycle-validate.sh:81-100` | When `commit_allowed=true` and prerequisites pass, no `OK` line is printed. | fixed |

## Triage Decisions

- Blocking findings (loop 1): R1 Medium — fixed; verified on re-review.
- Low findings fixed (loop 1): R2, R3 — fixed; verified on re-review.
- Low findings accepted or deferred: none.
- Scope concerns: none. Diff stays inside approved process-validator slice; no product/CI/schema expansion.
- Resolution (2026-07-27, loop 1): review gate dirty (`pending_re_review`); routed to Cursor fix, then re-review.
- Fix applied (2026-07-27): R1 prefix match for resolved statuses + status from last table column; R2 `P-2026-07-26-001` → `in_progress`; R3 OK line on `commit_allowed` success.
- Resolution (2026-07-27, loop 2): re-review clean (no open High/Medium/Low); verification adequate for docs/process-only slice; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27

# Supervisor QA — AI Cycle Validator

## Goal

Confirm that agents can inspect and validate durable AI cycle state with lightweight scripts, without replacing human approval gates or changing Scribe’s on-device meeting behavior.

## Environment

- No Scribe app launch is required (docs/process-only slice).
- Inspect repository files and run the shell checks below.
- Optional privacy note: app log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-27-ai-cycle-validator.md`
- Current cycle: `.ai/state/current-cycle.json`
- Debt / planned work: `.ai/state/debt.md`
- Scripts: `scripts/ai-cycle-status.sh`, `scripts/ai-cycle-validate.sh`
- Workflows: `docs/workflows/README.md`, `docs/workflows/feature-development-pipeline.md`
- Skills: `.ai/skills/feature-manager.md`, `.ai/skills/supervisor-qa.md`, `.ai/skills/commit-manager.md`

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open `docs/workflows/README.md` Cycle validator section | Names both scripts and when to run status vs validate. |
| 2 | Open `docs/workflows/feature-development-pipeline.md` Mandatory State Updates | Requires status on resume and validate before QA/commit prep. |
| 3 | Open feature-manager / supervisor-qa / commit-manager skills | Each skill that uses the validator names when/how to run it; human gates remain. |
| 4 | Open `.ai/state/current-cycle.json` | Points at this ledger; `review_gate` and `triage_status` are `clean`; `commit_allowed` is `false`; `supervisor_qa` is still pending. |
| 5 | Open `.ai/state/debt.md` | `P-2026-07-26-001` Cycle validator is `in_progress` (not still `planned`). |
| 6 | Run `bash scripts/ai-cycle-status.sh` | Prints iteration/phase/gates, then validation passes. |
| 7 | Run `bash scripts/ai-cycle-validate.sh` | Passes for current clean QA-ready state. |
| 8 | Skim active ledger Review Findings | R1–R3 are `fixed`; no open High/Medium. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Annotated fixed statuses | Mentally check R1 fix / ledger note | Statuses like `fixed (verified on re-review)` count as resolved (prefix match). |
| Finding text with `\|` | Mentally check R1 fix | Status still read from last table column. |
| Commit gate closed | Inspect `commit_allowed` | Remains `false` until you pass/skip QA and later approve commit. |
| Human gates preserved | Inspect commit-manager / supervisor-qa | Validator does not replace human QA or commit approval. |
| Product isolation | Compare approved out-of-scope + changed paths | No Scribe record/transcribe/summary/history/export behavior change required. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| JSON validity | `jq empty .ai/state/current-cycle.json` | Exits 0. |
| Patch hygiene | `git diff --check` | Exits 0. |
| Validator on current state | `bash scripts/ai-cycle-validate.sh` | Exits 0; reports clean review/triage for `phase=QA`. |
| Scope hygiene | `git status --short --untracked-files=all` | Only process/docs/state/script paths; no `frontend/`, `backend/`, `dist/`, or generated artifacts required for the slice. |
| Gate order honesty | Inspect current-cycle | Review/triage clean before QA execution; `supervisor_qa` not marked done ahead of your decision. |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Full structured schemas, CI integration, or new AI roles.
- Approving or creating the git commit (later human checkpoint).
- Marking `P-2026-07-26-001` done (that belongs at ship/commit).

## Pass criteria

- [x] Validator scripts exist and are executable / runnable via `bash`.
- [x] Workflow docs explain when to run status vs validate.
- [x] Skills that use the validator name it at the right handoffs.
- [x] Human approval gates are not replaced by the scripts.
- [x] `current-cycle.json` is valid and gate order is honest.
- [x] `P-2026-07-26-001` is `in_progress`.
- [x] `scripts/ai-cycle-validate.sh` and `scripts/ai-cycle-status.sh` pass.
- [x] `git diff --check` passes.
- [x] No open High/Medium findings in the active ledger.
- [x] No Scribe product behavior changed by this iteration.

## Fail criteria

- Validator replaces or skips human QA/commit approval.
- Review/triage claimed clean while High/Medium findings remain open.
- `commit_allowed=true` while review/QA prerequisites are unmet.
- Planned validator work still shows `planned` with no active iteration.
- Any product-facing Scribe behavior is changed by this iteration.
- Forbidden paths (`dist/`, `.venv/`, etc.) are part of the required slice.

## Notes

- Watch-outs from loop 1 (all fixed): findings-status exact match, planned-work status, missing commit-allowed OK line.
- Suggested order: steps 1–5 (docs/state) → 6–7 (scripts) → regression shell checks → scope hygiene.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`

## State updates

- Ledger: human Product Owner reported **pass** on 2026-07-27; pass criteria marked complete.
- Current cycle: `supervisor_qa` = `passed`; move to `commit-ready`; `commit_allowed` remains gated until commit-manager + explicit commit approval.

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: pass

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `scripts/ai-cycle-validate.sh` | pass | Validate active state after R1–R3 fix |
| `scripts/ai-cycle-status.sh` | pass | Print status and run validator |
| `git diff --check` | pass | Patch hygiene |
| Findings-parser regression (`fixed (...)`) | pass | Temp state pointing at prior ledger with annotated fixed statuses |
| Synthetic Medium `open` still fails | pass | Temp ledger with open Medium row |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| None | n/a | No accepted/deferred review, QA, or process-failure debt recorded for this iteration | n/a |

## Metrics

Separate observed facts from estimates.

| Metric | Value | Source |
| --- | --- | --- |
| Elapsed time | pending | observed |
| Agent turns | pending | observed |
| Approx token use | pending | estimated |
| Review loops | 2 | observed |
| High findings | 0 | observed |
| Medium findings | 0 open (1 fixed in loop 1: R1) | observed |
| Low findings | 0 open (2 fixed in loop 1: R2–R3) | observed |
| Human decisions | 2 | observed |

## Retrospective

**What worked:** pending

**What caused rework:** pending

**Repeated failure patterns:** pending

**Process change recommended:** pending

**Next planning input:** pending
