# Iteration: Pipeline Operator UX And Auto-Fix Policy

**Status:** retrospective
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** `d339880aaacf680bfc484d9390ea4c8a4a9678a4`

## Approved Scope

**Goal:** Reduce Product Owner / human operator involvement in the engineering loop by making the post-approval pipeline more deterministic: feature-manager as sole entrypoint, clear implementation handoff states, auto-fix policy for review loops, and PO-readable product-analyst output.

**Hypothesis:** If routine engineering coordination (entrypoint ambiguity, premature review handoffs, asking humans about auto-fixable findings) is removed from PO-facing workflows, the system can run a more autonomous engineering loop after scope approval while preserving human authority over product decisions, QA, and commits.

**In scope:**
- Clarify post-approval entrypoint: always `Use feature-manager.`; cursor-implementation-prompt is internal/specialized
- Explicit implementation phase: prompt prepared → pending → summary received → review ready
- Auto-fix policy for High/Medium and cheap first-loop Lows; second+ loop Low auto-fix or policy debt
- Product wishes remain in product-followups, not debt
- product-analyst output: Recommendation → Short Candidate Comparison → Evidence Appendix
- Ledger / org convention updates for handoff and auto-fix recording
- New iteration ledger + current-cycle state for this slice

**Out of scope:**
- Automating Cursor execution
- Real CLI orchestrator / PO console / onboarding modes
- Full JSON schemas for all role outputs
- CI integration
- Scribe product behavior changes
- Removing specialized skills
- Auto-committing without human approval
- Weakening PO authority or accepting unresolved High/Medium as debt

**Human approval:**
- Source: chat — Product Owner provided approved task / implementation prompt for process slice
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | human-approved task scope | this ledger + task text | done |
| Implementation prompt prepared | Cursor (task paste) | terminal task / this iteration | done |
| Implementation pending | Cursor | implementing | done |
| Implementation summary received | Cursor | this section | done |
| Review ready → Review | Codex | loop 1: 0H/3M/1L; loop 2 re-review: 0H/0M/0L (R1–R4 verified) | done |
| Triage / auto-fix | review-triage | loop 1 auto-fix R1–R4; loop 2 clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human **passed with follow-ups** 2026-07-27 (P-004–P-009) | done |
| Commit prep | commit-manager | commit `d339880` created 2026-07-27 | done |
| Retrospective | iteration-retrospective | pending — `Use iteration-retrospective.` | pending |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Task provided as bounded implementation prompt |
| Implementation pending | done | Cursor implemented docs/skills/state |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/cursor-implementation-prompt.md`
  - `.ai/skills/review-triage.md`
  - `.ai/skills/product-analyst.md`
  - `.ai/skills/README.md`
  - `.ai/skills/roadmap-planner.md`
  - `.ai/skills/codex-review.md`
  - `docs/workflows/feature-development-pipeline.md`
  - `docs/workflows/iteration-ledger.md`
  - `docs/workflows/README.md`
  - `docs/workflows/ai-product-development-cycle.md`
  - `.ai/org/workflows.md`
  - `.ai/org/roles.md`
  - `.ai/org/schemas.md`
  - `.ai/state/debt.md`
  - `.ai/state/current-cycle.json`
  - `docs/iterations/2026-07-27-pipeline-operator-ux.md`
  - `SUPERVISOR.md`
  - `AGENTS.md`
- Behavior changed (AI Native SDLC):
  - Post-approval next step is always feature-manager
  - Implementation pending/summary states required before review
  - Review-triage auto-fixes High/Medium and cheap first-loop Lows without asking the human every time
  - Second+ loop Lows may auto-fix or be recorded as Low debt without human ask when not product-facing
  - product-analyst leads with Recommendation, then short comparison, then Evidence Appendix
- Assumptions:
  - No automatic Cursor execution in this slice
  - Validator phase set names already cover `implementation-prompt` / `implementing` / `review`
  - SUPERVISOR.md included because it had the ambiguous PO-facing “or” next-step wording
- Verification reported by implementer:
  - `scripts/ai-cycle-status.sh`
  - `scripts/ai-cycle-validate.sh`
  - `git diff --check`
  - Manual `rg` checks for ambiguous next-step and auto-fix policy wording
- Remaining work:
  - Independent review (`Use codex-review.`)
  - Triage / QA / commit / retrospective
- Documentation updates:
  - Process docs and skills as listed; no Scribe product docs

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `.ai/skills/commit-manager.md:41`, `:105`, `:190` | Commit-manager still requires human-explicit Low acceptance and blocks “silent” Low accept — contradicts auto-fix / second-loop policy defer. | fixed |
| R2 | Medium | `SUPERVISOR.md:163` | PO triage table still says Low → request AI fix or explicitly accept/defer, pulling humans into routine Lows. | fixed |
| R3 | Low | `.ai/skills/supervisor-qa.md:48` | Precondition “explicitly accepted” ignores policy-deferred Lows. | fixed |
| R4 | Medium | `.ai/skills/review-triage.md` (+ feature-manager / pipeline / org mirrors) | Auto-defer of “minor/style-only” Lows needs hard rule: product-facing Low must never be silently deferred (PO clarification 2026-07-27). | fixed |

## Triage Decisions

### Loop 1
- Blocking findings: R1, R2, R4 (Medium) — AI-fixed in auto-fix pass
- Auto-fix pass generated: yes — R1–R4
- Auto-fix applied: yes (2026-07-27 Cursor)
- Low findings auto-fixed: R3
- Low findings accepted or deferred: none
- Human involvement required: yes (policy delineation only)
- Human involvement reason: Product Owner clarified that product-facing Lows cannot be silently deferred under auto-debt policy; R1–R3 themselves did not require human ask

### Loop 2 (re-review triage)
- Review outcome: 0 High, 0 Medium, 0 Low
- Blocking findings: none
- Auto-fix pass generated: no (clean)
- Auto-fix applied: n/a
- Low findings auto-fixed: none new
- Low findings accepted or deferred: none
- Human involvement required: no
- Human involvement reason: n/a
- Scope concerns: none — process docs/skills only; R1–R4 verified fixed; no Scribe product behavior
- Product wishes routed to follow-ups: none
- Review gate: **clean**
- Next: `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

**Outcome:** passed (with process follow-ups captured)

**Human decision:**
- Date: 2026-07-27
- Notes: All pass criteria satisfied. Process follow-ups recorded as Planned Process Work P-2026-07-27-004…009 in `.ai/state/debt.md` (not product wishes). QA item “harden auto-fix product-facing boundaries” already satisfied this iteration by R4 — no duplicate open item.
# Supervisor QA — Pipeline Operator UX And Auto-Fix Policy

## Goal

Confirm that after you approve a bounded slice, the AI development loop is clearer and less chatty: one normal next step (`Use feature-manager.`), review does not start before implementation is done, routine review findings are auto-fixed without asking you every time, product-facing Lows are never silently deferred, product analysis leads with a recommendation, and Scribe’s on-device meeting product was not changed.

## Environment

- No Scribe app launch is required (docs/process-only slice).
- Inspect repository docs/skills/state and run the shell checks below.
- App log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-27-pipeline-operator-ux.md`
- Current cycle: `.ai/state/current-cycle.json`
- Skills: `.ai/skills/feature-manager.md`, `.ai/skills/cursor-implementation-prompt.md`, `.ai/skills/review-triage.md`, `.ai/skills/product-analyst.md`, `.ai/skills/commit-manager.md`, `.ai/skills/README.md`
- Operator guide: `SUPERVISOR.md`
- Workflows: `docs/workflows/feature-development-pipeline.md`, `docs/workflows/iteration-ledger.md`, `docs/workflows/README.md`
- Debt / follow-ups: `.ai/state/debt.md`, `.ai/state/product-followups.md`

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open `SUPERVISOR.md` § after scope approval / Useful Prompts | Normal next step is `Use feature-manager.` — not a choice vs `cursor-implementation-prompt`. |
| 2 | Open `.ai/skills/cursor-implementation-prompt.md` Purpose | Described as internal/specialized handoff; feature-manager is the normal PO entrypoint. |
| 3 | Open `.ai/skills/feature-manager.md` implementation phase model | Sequence is: scope approved → prompt prepared → pending → summary received → review ready → codex-review. |
| 4 | Open `.ai/skills/review-triage.md` auto-fix policy | High/Medium auto-fix; cheap first-loop Lows auto-fix; product-facing Lows ask human and **must never be silently deferred**. |
| 5 | Open `SUPERVISOR.md` triage table | Cheap Lows → AI; product-facing / UX tradeoff → your judgment; never silently deferred. |
| 6 | Open `.ai/skills/product-analyst.md` Output Contract | Order is Recommendation → Short Candidate Comparison → Evidence Appendix. |
| 7 | Open `.ai/skills/commit-manager.md` Low preconditions / human checkpoints | Lows fixed or policy-deferred; human checkpoint only for product-facing Lows — not every Low. |
| 8 | Open active ledger Review Findings | R1–R4 are `fixed`; loop 2 re-review was clean. |
| 9 | Run `bash scripts/ai-cycle-status.sh` | Shows this iteration; phase QA; review/triage clean; supervisor QA pending. |
| 10 | Run `bash scripts/ai-cycle-validate.sh` | Passes. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Product ambiguity labeled “style-only” | Read review-triage hard rule | When in doubt whether a Low is product-facing, do not silent-defer — ask you. |
| Second+ loop minor non-product Low | Read review-triage / feature-manager | May auto-fix once more or record Low debt with reason; does not block QA. |
| Product wish vs debt | Open `product-followups.md` vs `debt.md` | Wishes stay in follow-ups; not mixed into review debt. Open PP-002 remains a wish, not debt. |
| Commit still human | Inspect commit-manager + current-cycle | `commit_allowed` is false; no auto-commit; you still approve commits. |
| Implementation before review | Inspect pipeline + feature-manager | Review must not start while implementation is still pending / no summary. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Scope hygiene | `git status --short --untracked-files=all` | Process/docs/skills/state (+ this ledger); no required `frontend/` / `backend/` product changes. |
| Patch hygiene | `git diff --check` | Exits 0. |
| Validator | `bash scripts/ai-cycle-validate.sh` | Exits 0; clean review/triage for `phase=QA`. |
| Human authority | Skim SUPERVISOR + feature-manager checkpoints | You still own scope, product-facing tradeoffs, QA pass/fail/skip, and commits. |
| Scribe product | Compare approved out-of-scope | No record/transcribe/summary/history/export behavior change in this slice. |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Automating Cursor execution, CLI orchestrator, PO console.
- Creating the git commit (later human checkpoint).
- Implementing PP-002 or other product follow-ups.

## Pass criteria

- [x] After scope approval, normal docs/skills point to `Use feature-manager.` (not an alternative with cursor-implementation-prompt).
- [x] Implementation pending/summary states are explicit before review.
- [x] Auto-fix policy is clear for High/Medium and cheap Lows.
- [x] Product-facing Lows cannot be silently deferred (hard rule visible to operators).
- [x] product-analyst leads with Recommendation before evidence.
- [x] Commit-manager / SUPERVISOR no longer pull you into every routine Low.
- [x] `scripts/ai-cycle-status.sh` and `scripts/ai-cycle-validate.sh` pass.
- [x] `git diff --check` passes.
- [x] No open High/Medium in the active ledger.
- [x] No Scribe product behavior changed by this iteration.

## Fail criteria

- Docs still present feature-manager and cursor-implementation-prompt as equal PO next steps.
- Review can start without an implementation summary.
- Routine High/Medium / cheap Lows still require your approval every time.
- Product-facing Lows can be silently deferred as debt.
- product-analyst still buries the recommendation under process evidence.
- Commit can proceed without your explicit approval.
- Scribe product behavior was changed unexpectedly.

## Notes

- Loop 1 findings R1–R4 were auto-fixed; mid-loop human involvement was the product-facing no-silent-defer clarification.
- Open product wish PP-002 remains in follow-ups; not failed for it.
- **Pass with follow-ups (2026-07-27):** process items captured as Planned Process Work P-004–P-009 (not product wishes). QA “harden auto-fix boundaries” already done this slice via R4.
- Next: `Use commit-manager.`

## State updates

- Ledger: Supervisor QA **passed with follow-ups** 2026-07-27; P-004–P-009 recorded
- Current cycle: `supervisor_qa=passed`; `commit_allowed=true`; route to commit-manager
- Product follow-ups: no new product wishes; process follow-ups in `debt.md` Planned Process Work

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `scripts/ai-cycle-status.sh` | pass | phase=review, implementation finished |
| `scripts/ai-cycle-validate.sh` | pass | |
| `git diff --check` | pass | |
| Manual rg ambiguous next-step | pass | No PO-facing “feature-manager or cursor-implementation-prompt” alternatives; historical ledgers only |
| Manual rg auto-fix policy | pass | Documented in review-triage, feature-manager, pipeline |
| `(cd frontend && npm run build)` | skipped | no frontend changes |
| `./scripts/run-dev.sh` | skipped | no product behavior changes |

## Debt

Accepted or deferred review debt: none this iteration.

Planned process work from Supervisor QA (see `.ai/state/debt.md`):

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| P-2026-07-27-004 | process_roadmap | Implementation-runner / handoff skill — out of scope this slice | After this ships |
| P-2026-07-27-005 | process_validation | Confirm product-analyst recommendation-first on next real cycle | Next planning cycle |
| P-2026-07-27-006 | process_metrics | Measure human review-fix involvement drop in next retrospective | Next retrospective after this |
| P-2026-07-27-007 | process_roadmap | Automate implement→review→triage loop — later autonomy | After P-004 + stable auto-fix evidence |
| P-2026-07-27-008 | process_ux | Hide cursor-implementation-prompt in future PO console | When PO console/UI starts |
| P-2026-07-27-009 | process_roadmap | Validator implementation-phase consistency checks | After P-004 or next validator hardening |

## Product Follow-ups / Wishes

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |
| — | (none new) | Supervisor QA | Process follow-ups went to Planned Process Work P-004–P-009, not this register. PP-002 unchanged. |

## Metrics

| Metric | Value | Source |
| --- | --- | --- |
| Review loops | 2 | observed |
| High findings | 0 | observed |
| Medium findings | 3 | observed (R1, R2, R4; all fixed) |
| Low findings | 1 | observed (R3; fixed) |
| Human decisions | 4 | observed (scope + auto-defer delineation + QA pass + commit approval) |
| QA outcome | passed | observed (with process follow-ups P-004–P-009) |
| Outcome | committed; retrospective pending | observed |

## Retrospective

Pending after ship.
