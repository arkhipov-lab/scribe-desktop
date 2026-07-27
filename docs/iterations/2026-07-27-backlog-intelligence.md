# Iteration: Backlog Intelligence

**Status:** commit-ready
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Add backlog intelligence through a `product-analyst` role.

**Hypothesis:** If next-work recommendations connect ROADMAP, scenarios, debt, recent metrics, and retrospectives, the AI development system can recommend what to do next based on evidence rather than roadmap order alone.

**In scope:**
- Add `.ai/skills/product-analyst.md`.
- Connect ROADMAP + scenarios + debt + recent metrics in the skill contract.
- Recommend next work by product value, process/risk evidence, effort, risk, and enablement.
- Update workflow/skills so product analysis feeds roadmap planning.
- Update process roadmap status for product analytics.

**Out of scope:**
- Automated backlog scoring.
- Full machine-readable backlog schema.
- Process auditor role.
- Product-facing Scribe behavior changes.
- Editing product roadmap priorities without human approval.

**Human approval:**
- Source: explicit user request, "Реализуй Этап 4: Добавить Backlog Intelligence"
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Human / Codex | Approved scope in chat | done |
| Implementation prompt | Codex | Direct implementation from approved process scope | done |
| Implementation | Codex | Product analyst skill and workflow updates | done |
| Review | Codex independent review | loop 1 findings R1–R5 | done |
| Triage | review-triage | loop 1: fix required; AI fix prompt | done |
| Fix | Cursor | R1–R5 applied | done |
| Re-review | Codex independent review | loop 2 clean (0 High/Medium/Low) | done |
| Triage | review-triage | loop 2: review gate clean; route to supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated 2026-07-27; human passed 2026-07-27 | done |
| Commit prep | commit-manager | commit-ready 2026-07-27; awaiting human approval | pending |
| Retrospective | iteration-retrospective | pending | pending |

## Implementation Summary

- Files changed:
  - `.ai/skills/product-analyst.md`
  - `.ai/skills/README.md`
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/roadmap-planner.md`
  - `.ai/state/current-cycle.json`
  - `.ai/state/debt.md`
  - `AI_SYSTEM_ROADMAP.md`
  - `docs/iterations/2026-07-27-backlog-intelligence.md`
  - `docs/workflows/README.md`
  - `docs/workflows/feature-development-pipeline.md`
  - `docs/workflows/ai-product-development-cycle.md`
- Behavior changed:
  - Added `Use product-analyst.` as the backlog intelligence role.
  - Product analysis now connects ROADMAP, scenarios, debt, recent metrics, and retrospective evidence.
  - Roadmap planning now consumes product-analyst output when available.
  - Workflow docs place product analysis before roadmap planning.
  - Process roadmap and planned work register mark the product analyst role as initially implemented.
- Assumptions:
  - Product analyst supports, but does not replace, roadmap-planner or human Product Owner decisions.
  - Recommendations remain markdown-first until structured schemas are justified.
- Verification reported by implementer:
  - `scripts/ai-cycle-status.sh`
  - `git diff --check`

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `docs/workflows/feature-development-pipeline.md:81-87` | Workflow diagram places human review/approval before `product-analyst`, inverting step detail and intended handoff. | fixed |
| R2 | Medium | `.ai/skills/feature-manager.md:45` | Preconditions still say “run roadmap-planner first” while responsibilities require product-analyst first when choosing next work. Human confirmed must fix before close. | fixed |
| R3 | Low | `docs/workflows/feature-development-pipeline.md:57`; Related Files ~241 | Assistant Manager still only requires `roadmap-planner`; Related Files omits `product-analyst.md`. | fixed |
| R4 | Low | `.ai/skills/roadmap-planner.md:209-211` | Integration string omits product-analyst. | fixed |
| R5 | Low | `.ai/skills/feature-manager.md:107-108`; `:170-174` | Output Contract lists Planning before Product analysis; Cycle overview still starts at roadmap-planner. | fixed |

## Triage Decisions

- Human product note (2026-07-27): product-analyst role framing, non-responsibilities, context loading, and output contract are correct; role supports PO and does not own decisions. `ai-cycle-validate.sh` passes. Two inconsistencies must be fixed before close: feature-manager precondition (R2) and inverted pipeline diagram (R1).
- Blocking findings (loop 1): R1–R2 Medium — must AI-fix; then re-review.
- Low findings (loop 1): R3–R5 — cheap; include in the same AI fix prompt.
- Low findings accepted or deferred: none.
- Scope concerns: none. Diff stays inside approved backlog-intelligence process slice; no product Scribe paths.
- Resolution (2026-07-27, loop 1): review gate dirty (`pending_re_review`); Cursor fix; re-review.
- Fix applied (2026-07-27): R1–R5 addressed in workflow diagram, feature-manager preconditions/overview/output order, pipeline Manager duty + Related Files, and roadmap-planner Integration.
- Resolution (2026-07-27, loop 2): re-review clean (no open High/Medium/Low); R1–R5 verified fixed; verification adequate for docs/process-only slice; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Backlog Intelligence

## Goal

Confirm that the AI development system now has a `product-analyst` backlog-intelligence step: it compares ROADMAP, scenarios, debt, metrics, and retrospectives, recommends next work, and feeds roadmap planning — without taking Product Owner decision power or changing Scribe’s on-device meeting behavior.

## Environment

- No Scribe app launch required (docs/process-only slice).
- Inspect repository files and run the shell checks below.
- App log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-27-backlog-intelligence.md`
- Current cycle: `.ai/state/current-cycle.json`
- Skill: `.ai/skills/product-analyst.md`
- Workflows: `docs/workflows/feature-development-pipeline.md`, `docs/workflows/ai-product-development-cycle.md`, `docs/workflows/README.md`
- Related skills: `.ai/skills/roadmap-planner.md`, `.ai/skills/feature-manager.md`, `.ai/skills/README.md`
- Process roadmap: `AI_SYSTEM_ROADMAP.md` (P2 Product Analytics)
- Debt register: `.ai/state/debt.md` (planned item `P-2026-07-27-001` marked done)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open active ledger Approved Scope | Goal is backlog intelligence via `product-analyst`; Scribe product changes and automated scoring/schemas are out of scope. |
| 2 | Open Implementation Summary | Describes new skill, evidence sources, roadmap-planner consumption, workflow wiring, and process-roadmap status update. |
| 3 | Confirm review/triage handoffs | R1–R5 fixed; loop 2 clean; no open High/Medium. |
| 4 | Open `.ai/skills/product-analyst.md` (as Product Owner checklist, not code review) | Invocation `Use product-analyst.`; supports PO; does not approve scope / implement / review / commit; context includes PRODUCT, ROADMAP, scenarios, debt, ledgers/metrics; output has candidate comparison + “what roadmap alone would suggest.” |
| 5 | Open pipeline Workflow Steps diagram | Order is `product-analyst → human reviews analysis → roadmap-planner → human approves scope → feature pipeline`. |
| 6 | Open feature-manager Preconditions / Cycle overview | New cycle starts with product-analyst (when choosing next work), then roadmap-planner; overview matches. |
| 7 | Open roadmap-planner Integration / responsibilities | Consumes product-analyst output when available; still produces a bounded slice for human approval. |
| 8 | Run `bash scripts/ai-cycle-status.sh` | Shows this iteration in QA; validation passes. |
| 9 | Run `bash scripts/ai-cycle-validate.sh` | Passes for current QA-ready state. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Role does not own product direction | Skim product-analyst Purpose / Non-responsibilities / Human Checkpoints | Explicitly supports PO; does not approve scope or edit ROADMAP silently. |
| Roadmap alone vs evidence | Skim product-analyst output contract | Includes “What roadmap alone would suggest” and evidence that would change the recommendation. |
| Optional vs required analysis | Skim feature-manager / Manager duty | product-analyst runs when choosing next work from roadmap/debt/metrics; roadmap-planner still required and can proceed with a minimum evidence check if analysis is absent. |
| Process roadmap honesty | Open `AI_SYSTEM_ROADMAP.md` P2 + debt `P-2026-07-27-001` | Initial skill marked added/done; schemas deferred to future need. |
| Product isolation | Compare changed paths to out-of-scope | No `frontend/` / `backend/` / native / packaging changes required for this slice. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| JSON validity | `jq empty .ai/state/current-cycle.json` | Exits 0. |
| Patch hygiene | `git diff --check` | Exits 0. |
| Scope hygiene | `git status --short --untracked-files=all` | Only process skills/docs/ledger/state paths. |
| Gate honesty | Inspect current-cycle | Review/triage clean; `commit_allowed` still false; `supervisor_qa` not marked passed ahead of your decision. |
| Discoverability | Skim `.ai/skills/README.md` and workflows README | `Use product-analyst.` appears before `Use roadmap-planner.` |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Automated backlog scoring or machine-readable backlog schemas.
- Process auditor role.
- Editing product ROADMAP priorities.
- Approving or creating the git commit (later human checkpoint).
- Actually running a full product-analyst recommendation for the next product slice (optional later; not required to pass this iteration).

## Pass criteria

- [x] product-analyst exists and is framed as recommendation/support for the Product Owner.
- [x] Workflow/skills place analysis before roadmap planning without removing human approval.
- [x] Review gate is clean (no open High/Medium; R1–R5 fixed).
- [x] `scripts/ai-cycle-validate.sh` / `scripts/ai-cycle-status.sh` pass on current state.
- [x] No Scribe product behavior changed by this iteration.
- [x] `git diff --check` passes.

## Fail criteria

- product-analyst can approve scope, write implementation prompts, or silently edit ROADMAP/PRODUCT.
- Pipeline still runs human approval before product-analyst, or omits the role after claiming it was added.
- Review claimed clean while High/Medium remain open.
- Product-facing Scribe behavior changed.
- Forbidden paths required for the slice.

## Notes

- Accepted Lows: none (R3–R5 were fixed).
- Suggested order: ledger scope → skill checklist → pipeline diagram → shell validators → path hygiene.
- This is product review of the AI-organization increment, not engineering code review.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: pass

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `scripts/ai-cycle-status.sh` | pass | Includes validator run |
| `scripts/ai-cycle-validate.sh` | pass | After R1–R5 marked fixed |
| `git diff --check` | pass | Patch hygiene |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| None | n/a | No accepted/deferred review, QA, or process-failure debt recorded for this iteration | n/a |

## Metrics

Separate observed facts from estimates.

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | pending | observed | Ledger timestamps pending completion |
| Agent turns | pending | observed | Conversation turns pending completion |
| Approx token use | pending | estimated | Estimate unavailable during implementation |
| Review loops | 2 | observed | Loop 1 Mediums+Lows → fix; loop 2 clean re-review |
| High findings | 0 | observed | Review findings table |
| Medium findings | 2 fixed (0 open) | observed | R1–R2 fixed and verified |
| Low findings | 3 fixed (0 open) | observed | R3–R5 fixed and verified |
| Human decisions | 3 | observed | Scope approval; triage must-fix note; QA pass |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | pending | observed | Iteration not complete |

## Retrospective

**What worked:** pending

**What caused rework:** pending

**Repeated failure patterns:** pending

**Process change recommended:** pending

**Next planning input:** pending
