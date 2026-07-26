# Iteration: AI Memory Foundation

**Status:** commit-ready
**Date started:** 2026-07-26
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Make durable AI development memory mandatory for future iterations.

**Hypothesis:** If every iteration has an explicit ledger, current-cycle state, and debt register, future AI roles can continue work without reconstructing process history from chat.

**In scope:**
- Create `docs/iterations/`.
- Add a ledger entry for this process iteration.
- Create `.ai/state/current-cycle.json`.
- Create `.ai/state/debt.md`.
- Update workflow docs and skills so agents read and update iteration memory.

**Out of scope:**
- Automated cycle validation scripts.
- Machine-readable schemas beyond the initial current-cycle state file.
- New retrospective, process-auditor, or product-analyst roles.
- Product-facing Scribe behavior changes.

**Human approval:**
- Source: explicit user request, "Сделай это"
- Date: 2026-07-26

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Human / Codex | Approved scope in chat | done |
| Implementation prompt | Codex | Direct implementation from approved process scope | done |
| Implementation | Codex | Process docs and state files | done |
| Review | Codex independent review | re-review loop 3 clean (no open findings) | done |
| Triage | review-triage | clean gate; route to supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated 2026-07-27; human passed 2026-07-27 | done |
| Commit prep | commit-manager | prepared 2026-07-27; awaiting explicit human commit approval | done |
| Retrospective | iteration-retrospective | pending role not yet implemented | pending |

## Implementation Summary

- Files changed:
  - `docs/iterations/README.md`
  - `docs/iterations/2026-07-26-ai-memory-foundation.md`
  - `docs/workflows/iteration-ledger.md`
  - `docs/workflows/README.md`
  - `docs/workflows/ai-product-development-cycle.md`
  - `docs/workflows/feature-development-pipeline.md`
  - `docs/MANIFEST.md`
  - `.ai/state/current-cycle.json`
  - `.ai/state/debt.md`
  - `.ai/skills/README.md`
  - `.ai/skills/codex-review.md`
  - `.ai/skills/commit-manager.md`
  - `.ai/skills/cursor-implementation-prompt.md`
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/review-triage.md`
  - `.ai/skills/roadmap-planner.md`
  - `.ai/skills/supervisor-qa.md`
  - `AGENTS.md`
  - `AI_CONVENTION.md`
  - `AI_SYSTEM_ROADMAP.md`
- Behavior changed:
  - AI process iterations now have mandatory durable memory artifacts.
  - Skills are expected to read and update current-cycle, ledger, and debt state.
- Assumptions:
  - Markdown remains the primary durable human-readable record.
  - `current-cycle.json` is intentionally small until validator scripts exist.
- Verification reported by implementer:
  - Documentation/state consistency review.

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `.ai/state/debt.md` | Debt register mixed planned process work with accepted/deferred review debt, conflicting with the no-open-Medium review gate. | fixed (verified on re-review) |
| R2 | Medium | `docs/workflows/feature-development-pipeline.md`; `.ai/skills/feature-manager.md` | State was described as winning over chat too broadly, weakening explicit human Product Owner authority. | fixed (verified on re-review) |
| R3 | Medium | `.ai/skills/codex-review.md` | Independent reviewer was instructed to mutate ledger/current-cycle state after review, changing the reviewed diff and weakening role separation. | fixed (verified on re-review) |
| R4 | Medium | `.ai/state/current-cycle.json`; active ledger handoffs/status | Durable memory encoded illegal gate order: `phase`/`supervisor_qa` advanced to QA while `review_gate` was still `pending_re_review`. | fixed (triage durable-memory correction 2026-07-27) |
| R5 | Low | active ledger Implementation Summary | Files-changed list omitted several modified/untracked process paths. | fixed (triage ledger update 2026-07-27) |

## Triage Decisions

- Blocking findings (loop 1): R1–R3 Medium — fixed earlier; verified on re-review.
- Blocking findings (loop 2): R4 Medium — illegal QA-before-review-clean state in durable memory. Fixed during triage by resetting phase/gates and Supervisor QA handoff; no separate product-code change required.
- Blocking findings (loop 3): none — re-review clean.
- Low findings fixed: R5 — expanded Implementation Summary file list to match working tree.
- Low findings accepted or deferred: none.
- Scope concerns: none. `AI_CONVENTION.md` / `AI_SYSTEM_ROADMAP.md` document process convention/roadmap without implementing out-of-scope roles or validators.
- Resolution (2026-07-27): review gate clean; verification adequate for docs/process-only slice; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (regenerated after clean review gate)

# Supervisor QA — AI Memory Foundation

## Goal

Confirm that this process iteration makes durable AI development memory mandatory for future work, without changing Scribe’s on-device meeting behavior, weakening human Product Owner authority, or treating planned future process work as commit-blocking review debt.

## Environment

- No Scribe app launch is required (docs/process-only slice).
- Inspect repository files and run the two shell checks below.
- Optional privacy note: app log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-26-ai-memory-foundation.md`
- Current cycle: `.ai/state/current-cycle.json`
- Debt / planned work: `.ai/state/debt.md`
- Iteration index: `docs/iterations/README.md`
- Workflows: `docs/workflows/` (especially `feature-development-pipeline.md`, `iteration-ledger.md`)
- Skills: `.ai/skills/` (especially `feature-manager.md`, `codex-review.md`, `supervisor-qa.md`, `commit-manager.md`)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open `docs/iterations/README.md` | Explains that every approved iteration gets a durable ledger under `docs/iterations/`. |
| 2 | Open the active ledger | Records approved scope, handoffs, implementation summary, review/triage, this QA plan, verification, debt/planned work, metrics, and next planning input. |
| 3 | Open `.ai/state/current-cycle.json` | Points at this ledger; `review_gate` is `clean`; `commit_allowed` is `false` until you pass/skip QA and approve commit. |
| 4 | Open `.ai/state/debt.md` | Open Debt is empty/separate from Planned Process Work; planned validator/schema/retrospective items have priority, not review severity. |
| 5 | Open `docs/workflows/feature-development-pipeline.md` | Mandatory state updates exist; newer explicit human instruction overrides stale state and must be written back to ledger/current-cycle. |
| 6 | Open `.ai/skills/feature-manager.md` | Requires reading/updating ledger, current-cycle, and debt; same human-authority rule. |
| 7 | Open `.ai/skills/codex-review.md` | Review proposes state updates only; does not edit ledger/current-cycle/debt during review. |
| 8 | Open `.ai/skills/supervisor-qa.md` and `.ai/skills/commit-manager.md` | QA and commit prep require durable state updates and human checkpoints. |
| 9 | Skim `AGENTS.md` / `docs/MANIFEST.md` links to `AI_CONVENTION.md` and `AI_SYSTEM_ROADMAP.md` | Process convention and roadmap are discoverable; they do not claim new roles or validators already shipped. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Stale state vs new human instruction | Compare pipeline + feature-manager wording | Explicit human instruction wins; must be recorded back into state. |
| Planned work vs review debt | Inspect `.ai/state/debt.md` | Validator / schemas / retrospective sit under Planned Process Work, not Open Debt. |
| Reviewer role separation | Inspect `codex-review` skill | No instruction to mutate working-tree state files after review. |
| Gate order honesty | Inspect current-cycle + ledger handoffs | Review is clean before QA execution; Supervisor QA is not marked done ahead of a dirty review gate. |
| Commit still gated | Inspect `commit_allowed` | Remains `false` until you report QA pass/skip and later approve commit. |
| Product isolation | Compare approved out-of-scope + changed paths | No Scribe record/transcribe/summary/history/export behavior change required to pass this iteration. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Human authority | Search repo docs/skills for `state wins` | No old “state wins over chat” wording remains. |
| Reviewer mutation | Search `codex-review` for instructions to edit state after review | Only “propose updates” / “do not edit” language remains. |
| JSON validity | Run `jq empty .ai/state/current-cycle.json` | Command exits 0. |
| Patch hygiene | Run `git diff --check` | Command exits 0. |
| Scope hygiene | Run `git status --short --untracked-files=all` | Only process/docs/state paths; no `frontend/`, `backend/`, `dist/`, or generated artifacts required for the slice. |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Implementing cycle validators, full schemas, or new AI roles.
- Approving or creating the git commit (that is a later human checkpoint).

## Pass criteria

- [x] Iteration memory primitives exist and are discoverable (`docs/iterations/`, `current-cycle.json`, `debt.md`).
- [x] Workflow docs require reading/updating durable memory.
- [x] Skills require durable memory at the right handoffs.
- [x] Human authority wording is correct.
- [x] Debt and planned process work are not conflated.
- [x] `codex-review` does not mutate state files.
- [x] Gate order is honest (no QA-done-while-review-dirty).
- [x] `current-cycle.json` is valid JSON.
- [x] `git diff --check` passes.
- [x] No Scribe product behavior changed by this iteration.

## Fail criteria

- A High/Medium review issue is accepted as ordinary Open Debt before commit.
- State is described as overriding newer explicit human instructions.
- `codex-review` is told to edit ledger/current-cycle/debt during review.
- Planned process work appears as commit-blocking review debt.
- Durable state claims QA complete while review is still dirty.
- Any product-facing Scribe behavior is changed by this iteration.

## Notes

- No accepted Low debt on this iteration (R5 was fixed).
- Watch-outs from review history (all fixed): debt taxonomy, human authority wording, reviewer non-mutation, premature QA state advancement.
- Planned process work (not blockers): cycle validator, structured schemas, retrospective role.
- Suggested order: steps 1–4 (artifacts) → 5–8 (contracts) → regression shell checks → scope hygiene.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`

## State updates

- Ledger: human Product Owner reported **pass** on 2026-07-27; pass criteria marked complete.
- Current cycle: `supervisor_qa` = `passed`; `commit_allowed` remains false until commit-manager + explicit commit approval.

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: pass

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| Documentation/state consistency review | pass | Performed during implementation |
| Review-finding fix consistency | pass | `debt.md`, current-cycle state, active ledger, and affected skills/workflow docs updated |
| `(cd frontend && npm run build)` | skipped | Docs/process-only change |
| `./scripts/run-dev.sh` | skipped | Docs/process-only change |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| None | n/a | No accepted/deferred review, QA, or process-failure debt recorded for this iteration | n/a |

## Planned Process Work

| Item | Type | Why planned | Start condition |
| --- | --- | --- | --- |
| Cycle validator | process_roadmap | This iteration only makes memory mandatory; enforcement belongs to the next stage | Start of enforceable gates work |
| Structured schemas | process_roadmap | Deferred until there is a concrete validator/consumer | First validator/schema consumer is introduced |
| Retrospective role | process_roadmap | Durable memory should exist before retrospectives compare iteration evidence | After at least one complete ledger-backed iteration |

## Metrics

Separate observed facts from estimates.

| Metric | Value | Source |
| --- | --- | --- |
| Elapsed time | pending | observed |
| Agent turns | pending | observed |
| Approx token use | pending | estimated |
| Review loops | 3 | observed |
| High findings | 0 (open) | observed |
| Medium findings | 0 open (3 in loop 1; 1 in loop 2; all fixed) | observed |
| Low findings | 0 open (1 in loop 2; fixed) | observed |
| Human decisions | 2 | observed |

## Retrospective

**What worked:** The process gap was already clearly identified in `AI_CONVENTION.md`, `AI_SYSTEM_ROADMAP.md`, and `docs/workflows/iteration-ledger.md`.

**What caused rework:** Loop 1 process-contract wording (debt taxonomy, human authority, reviewer mutation). Loop 2 premature QA advancement in durable state before review was clean.

**Repeated failure patterns:** pending

**Process change recommended:** Make the next stage a lightweight cycle validator after this memory foundation is reviewed.

**Next planning input:** Prefer enforceable gates and validator scripts before adding more AI roles.
