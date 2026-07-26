# Iteration: Retrospective Metrics

**Status:** shipped
**Date started:** 2026-07-27
**Date completed:** 2026-07-27
**Commit:** `0f73cc394824e04a04a2e0c64a2330ea34a7e081`

## Approved Scope

**Goal:** Add retrospective and metrics support to the AI development system.

**Hypothesis:** If each iteration ends with a structured retrospective and honest metrics, future planning can use evidence about rework, repeated failures, and human routine effort instead of reconstructing lessons from chat.

**In scope:**
- Add `.ai/skills/iteration-retrospective.md`.
- Add a metrics table contract with observed vs estimated source separation.
- Add repeated failure analysis to retrospective output.
- Update ledger/workflow/skills so retrospective is part of the cycle.
- Update validator only where needed for retrospective phase support.

**Out of scope:**
- Automated metrics collection.
- Full machine-readable metrics schema.
- Process auditor or product analyst roles.
- Product-facing Scribe behavior changes.
- CI integration.

**Human approval:**
- Source: explicit user request, "Реализуй Этап 3: Добавить Retrospective + Metrics"
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Human / Codex | Approved scope in chat | done |
| Implementation prompt | Codex | Direct implementation from approved process scope | done |
| Implementation | Codex | Retrospective skill, metrics docs, workflow updates | done |
| Review | Codex independent review | loop 1: 3 Medium + 1 Low | done |
| Triage | review-triage | loop 1: route to AI fix (R1–R4) | done |
| Fix | Cursor | R1–R4 applied 2026-07-27 | done |
| Review | Codex re-review | loop 2: 0 High/Medium, 2 Low | done |
| Triage | review-triage | loop 2: human requested AI fix for R5–R6 | done |
| Fix | Cursor | R5–R6 Low polish 2026-07-27 | done |
| Supervisor QA | supervisor-qa | plan generated 2026-07-27; human passed 2026-07-27 | done |
| Commit prep | commit-manager | commit `0f73cc3` created 2026-07-27 | done |
| Retrospective | iteration-retrospective | completed 2026-07-27; next planning → P-002 schemas | done |

## Implementation Summary

- Files changed:
  - `.ai/skills/iteration-retrospective.md`
  - `.ai/skills/README.md`
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/commit-manager.md`
  - `.ai/state/current-cycle.json`
  - `.ai/state/debt.md`
  - `docs/iterations/2026-07-27-retrospective-metrics.md`
  - `docs/workflows/README.md`
  - `docs/workflows/feature-development-pipeline.md`
  - `docs/workflows/ai-product-development-cycle.md`
  - `docs/workflows/iteration-ledger.md`
  - `scripts/ai-cycle-validate.sh`
  - `AI_SYSTEM_ROADMAP.md`
- Behavior changed:
  - Added `Use iteration-retrospective.` as a formal AI process skill.
  - Retrospectives include metrics with `Value`, `Source type`, and `Evidence`, plus repeated-failure analysis.
  - Post-commit flow: commit-manager sets `phase=retrospective` + `committed=true` + commit hash; retrospective then sets `phase=shipped` / `status=shipped`.
  - Validator: `phase=retrospective` requires clean review/triage, completed QA, `committed=true`, and commit hash; `committed=true` alone does not force shipped; shipped markers still must agree.
  - Ledger status vocabulary includes `retrospective`.
- Assumptions:
  - Metrics remain ledger-first and human-readable.
  - Token use and human effort are estimated unless directly available.
- Verification reported by implementer:
  - `bash -n scripts/ai-cycle-validate.sh`
  - `git diff --check`
  - Synthetic retrospective/shipped validator cases (see Verification)
  - Active-cycle `scripts/ai-cycle-validate.sh` after marking R1–R4 fixed

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `.ai/skills/commit-manager.md:91`; `scripts/ai-cycle-validate.sh:155-214` | Post-commit handoff marks `shipped` then routes to retrospective, but `committed=true` forces `phase=shipped`, so `phase=retrospective` cannot validate after a real commit. | fixed |
| R2 | Medium | `docs/workflows/iteration-ledger.md:82`; `scripts/ai-cycle-validate.sh:155` | Validator accepts `phase=retrospective`, but ledger status vocabulary omits `retrospective`. | fixed |
| R3 | Medium | `docs/iterations/2026-07-27-retrospective-metrics.md:69-72`; `scripts/ai-cycle-validate.sh:155-168` | New retrospective validator path was not synthetically verified. | fixed |
| R4 | Low | `.ai/skills/iteration-retrospective.md:35-41` | Skill preconditions allow nearly-complete / QA-pending without requiring commit, conflicting with post-commit pipeline placement. | fixed |
| R5 | Low | `.ai/skills/feature-manager.md:172` | Cycle overview still ends `commit-manager → summary → next`, omitting `iteration-retrospective`. | fixed |
| R6 | Low | `.ai/skills/iteration-retrospective.md:5` | Purpose still says “completed or nearly completed” while preconditions require commit or cancelled/rejected. | fixed |

## Triage Decisions

- Blocking findings (loop 1): R1–R3 Medium — fixed; verified on re-review.
- Low findings (loop 1): R4 — fixed; verified on re-review.
- Blocking findings (loop 2): none — re-review clean on High/Medium.
- Low findings (loop 2): R5, R6 — human requested AI fix (2026-07-27); fixed; no full re-review for Low-only polish.
- Low findings accepted or deferred: none.
- Scope concerns: none. Diff stays inside approved retrospective + metrics process slice.
- Resolution (2026-07-27, loop 1): review gate dirty; Cursor fix; re-review.
- Fix applied (2026-07-27): R1–R4 addressed.
- Resolution (2026-07-27, loop 2): High/Medium clean; human chose AI fix for R5–R6; review gate clean; route to `Use supervisor-qa.`
## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Retrospective Metrics

## Goal

Confirm that the AI development cycle now has a durable retrospective + metrics step after commit (skill, ledger contract, workflow wiring, and validator support for `phase=retrospective`) — without changing Scribe product behavior.

## Environment

- No Scribe app launch required (docs/process-only slice).
- Inspect repository state and run the shell checks below.
- App log path is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-27-retrospective-metrics.md`
- Current cycle: `.ai/state/current-cycle.json`
- Skill: `.ai/skills/iteration-retrospective.md`
- Script: `scripts/ai-cycle-validate.sh`
- Debt register: `.ai/state/debt.md` (planned item P-2026-07-26-003 marked done)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open active ledger Approved Scope | Goal is retrospective + metrics for the AI process; product Scribe changes are out of scope. |
| 2 | Open Implementation Summary | Describes skill, metrics Value/Source type/Evidence, repeated-failure analysis, post-commit `phase=retrospective` then shipped. |
| 3 | Confirm review/triage handoffs | R1–R6 fixed; no open High/Medium; Lows resolved. |
| 4 | Open `.ai/skills/iteration-retrospective.md` (as Product Owner checklist, not code review) | Invocation `Use iteration-retrospective.`; metrics + repeated-failure output; post-commit / cancelled-or-rejected preconditions. |
| 5 | Run `bash scripts/ai-cycle-status.sh` | Shows this iteration in QA; validation passes. |
| 6 | Run `bash scripts/ai-cycle-validate.sh` | Passes for current QA-ready state. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Post-commit retrospective | Mentally confirm / optionally synthetic: `phase=retrospective`, `status=retrospective`, `committed=true`, valid commit hash, clean review/QA | Validator **passes**. |
| Retrospective without commit | Synthetic: `phase=retrospective` with `committed=false` | Validator **fails**. |
| Commit during QA | Synthetic: `committed=true` while `phase=QA` | Validator **fails**. |
| Shipped still consistent | Synthetic: `phase=shipped`, `status=shipped`, `committed=true`, valid hash | Validator **passes**. |
| Product isolation | Compare changed paths to out-of-scope | No `frontend/` / `backend/` / native / packaging changes required. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| JSON validity | `jq empty .ai/state/current-cycle.json` | Exits 0. |
| Patch hygiene | `git diff --check` | Exits 0. |
| Scope hygiene | `git status --short --untracked-files=all` | Only process skills/docs/validator/ledger/state paths. |
| Gate honesty | Inspect current-cycle | Review/triage clean; `commit_allowed` still false; QA not marked passed ahead of your decision. |
| Workflow discoverability | Skim skills README / pipeline skill table | `Use iteration-retrospective.` appears after commit. |

## Out of scope

- Running `./scripts/run-dev.sh` or Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Automated metrics collection, machine-readable schemas, CI.
- Actually running a full retrospective on a prior shipped iteration (later checkpoint after this commit).
- Approving/creating the git commit (later checkpoint).

## Pass criteria

- [x] Retrospective + metrics process behavior matches approved goal.
- [x] Review gate is clean (no open High/Medium; Lows fixed).
- [x] `scripts/ai-cycle-validate.sh` / `scripts/ai-cycle-status.sh` pass on current state.
- [x] Human gates (QA decision, later commit) are not replaced by the script.
- [x] No Scribe product behavior changed by this iteration.
- [x] `git diff --check` passes.

## Fail criteria

- Post-commit retrospective path still conflicts with shipped/committed validation.
- Review claimed clean while High/Medium remain open.
- Product-facing Scribe behavior changed.
- Forbidden paths required for the slice.

## Notes

- Suggested order: ledger/scope skim → skill invocation skim → status/validate → optional synthetic edge checks → scope hygiene.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: pass

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `bash -n scripts/ai-cycle-validate.sh` | pass | Shell syntax |
| `git diff --check` | pass | Patch hygiene |
| Synthetic: retrospective happy (committed + clean gates) | pass | |
| Synthetic: retrospective dirty review | pass | fails as required |
| Synthetic: retrospective not committed | pass | fails as required |
| Synthetic: committed=true during phase=QA | pass | fails as required |
| Synthetic: consistent shipped | pass | |
| Synthetic: status=shipped + phase=retrospective | pass | fails as required |
| Synthetic: half-shipped phase only | pass | fails as required |
| Active `scripts/ai-cycle-validate.sh` | pass | After R1–R4 marked fixed |
| Low polish R5–R6 | pass | `git diff --check` + active validate |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| None | n/a | No accepted/deferred review, QA, or process-failure debt recorded for this iteration | n/a |

## Metrics

Separate observed facts from estimates.

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | same calendar day (2026-07-27) | estimated | `date_started` = `date_completed`; wall-clock span not instrumented |
| Agent turns | ~20 across implement/review/QA/commit | estimated | Skill invocations in this chat cycle; exact turn counter unavailable |
| Approx token use | unavailable | estimated | No token meter in this session |
| Review loops | 2 | observed | Ledger handoffs: loop 1 Mediums → fix → loop 2 Lows |
| High findings | 0 | observed | Review findings table |
| Medium findings | 3 | observed | R1–R3 in loop 1; all fixed before ship |
| Low findings | 3 | observed | R4–R6; all fixed before ship |
| Human decisions | 4 | observed | Scope approval; AI-fix R5–R6; QA pass; commit approval |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | shipped | observed | Commit `0f73cc3` + retrospective complete |

## Retrospective

**What worked:**
- Bounded process slice stayed out of Scribe product paths.
- Review caught the post-commit `shipped` vs `retrospective` gate conflict before ship.
- Synthetic validator cases (after R3) made the chosen phase model enforceable.
- Human Low decision was cheap and cleared the gate without another full review loop.

**What caused rework:**
- First implementation wired retrospective after commit but still jumped to `shipped` and left `committed=true` as a shipped marker, conflicting with the prior shipped-consistency rules.
- Ledger/status vocabulary and overview diagrams lagged the new phase (R2, R5, R6).
- New validator path shipped without synthetic checks until review (R3).

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| New phase/gate disagrees with existing shipped/commit consistency | This iteration R1; earlier `2026-07-26-ai-memory-foundation` illegal QA-before-review-clean state; `2026-07-27-validator-shipped-consistency` existed because markers drifted | yes | gate: when adding a phase, update consistency checks + skill handoffs in the same slice |
| New validator behavior under-verified until review | This iteration R3; `2026-07-27-ai-cycle-validator` needed synthetic matcher cases after loop 1 | yes | test: implementer verification must include synthetic pass/fail cases for new validate branches |
| Skill/overview copy drifts from pipeline steps | This iteration R5–R6 (Low); not clearly repeated earlier | unknown | none for now (fixed); revisit only if it recurs |

**Process change recommended:**
1. Treat “new cycle phase” as a checklist item: update `commit-manager` / pipeline / ledger vocab / `check_*` consistency together, and record synthetic validate cases in Verification before review.
2. No second process change recommended this iteration.

**Next planning input:**
Planned process work `P-2026-07-26-002` (structured role output schemas) is the next natural AI-system slice; otherwise return to product ROADMAP if the Product Owner wants Scribe-facing work next.
