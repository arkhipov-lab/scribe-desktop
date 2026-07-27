# Iteration: Reusable Layer

**Status:** commit-ready
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Separate reusable AI organization process from Scribe product and repository-specific context.

**Hypothesis:** If process, product, and repo context are split into `.ai/org/`, `.ai/product/`, and `.ai/repo/`, the AI development system becomes easier to port to another product without carrying Scribe-specific assumptions in every reusable rule.

**In scope:**
- Add `.ai/org/` for reusable roles, workflows, metrics, and schema targets.
- Add `.ai/product/` adapters for Scribe product invariants, roadmap, and scenarios.
- Add `.ai/repo/` adapters for Scribe stack, validation commands, and forbidden paths.
- Update workflow/skills docs so agents know which layer to read.
- Update process roadmap/planned work status for reusable process package.

**Out of scope:**
- Moving or deleting existing canonical Scribe docs.
- Full package extraction for use in another repository.
- Machine-readable schema implementation.
- Product-facing Scribe behavior changes.

**Human approval:**
- Source: explicit user request, "Реализуй Этап 5: Отделить Reusable Layer"
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Human / Codex | Approved scope in chat | done |
| Implementation prompt | Codex | Direct implementation from approved process scope | done |
| Implementation | Codex | `.ai/org`, `.ai/product`, `.ai/repo` layer split | done |
| Review | Codex independent review | loop 1 findings; loop 2 clean | done |
| Triage | review-triage | loop 2: review gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | passed 2026-07-27 by human Product Owner | done |
| Commit prep | commit-manager | commit prep ready; awaiting human approval | pending |
| Retrospective | iteration-retrospective | pending | pending |

## Implementation Summary

- Files changed:
  - `.ai/org/README.md`
  - `.ai/org/roles.md`
  - `.ai/org/workflows.md`
  - `.ai/org/metrics.md`
  - `.ai/org/schemas.md`
  - `.ai/product/invariants.md`
  - `.ai/product/roadmap.md`
  - `.ai/product/scenarios.md`
  - `.ai/repo/stack.md`
  - `.ai/repo/validation.md`
  - `.ai/repo/forbidden-paths.md`
  - `.ai/skills/README.md`
  - `.ai/skills/product-analyst.md`
  - `.ai/skills/roadmap-planner.md`
  - `.ai/skills/codex-review.md`
  - `.ai/skills/iteration-retrospective.md`
  - `.ai/skills/feature-manager.md`
  - `.ai/skills/commit-manager.md`
  - `.ai/skills/supervisor-qa.md`
  - `.ai/state/current-cycle.json`
  - `.ai/state/debt.md`
  - `AI_SYSTEM_ROADMAP.md`
  - `docs/iterations/2026-07-27-reusable-layer.md`
  - `docs/workflows/README.md`
- Behavior changed:
  - Added a reusable AI organization layer under `.ai/org/`.
  - Added Scribe product adapters under `.ai/product/`.
  - Added Scribe repository adapters under `.ai/repo/`.
  - Updated key skills and workflow index so agents know which layer to read for process, product, and repo context.
  - Marked the reusable package split as initially implemented and recorded full package extraction as future planned work.
- Assumptions:
  - Existing docs remain canonical; new `.ai/*` files are portability adapters and reusable process maps.
  - Moving canonical docs would create too much link churn for this iteration.
- Verification reported by implementer:
  - `scripts/ai-cycle-status.sh`
  - `git diff --check`

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `.ai/org/workflows.md:39` | Reusable org workflow hardcodes repo script paths (`scripts/ai-cycle-status.sh`, `scripts/ai-cycle-validate.sh`) instead of deferring to `.ai/repo/validation.md`. | fixed |
| R2 | Low | `.ai/skills/feature-manager.md:19-36` (also commit-manager, supervisor-qa) | Residual orchestration/gate skills omit portable-layer context pointers. Human note: key skills + README already satisfy scope intent; treat residual as Low polish. | fixed |
| R3 | Low | `AI_SYSTEM_ROADMAP.md:207-216` | P3 target still shows nested dirs while initial split uses flat adapter files; simplification not stated. | fixed |
| R4 | Low | `.ai/org/schemas.md:24-34` | Minimum current-cycle fields omit `gates.retrospective`. | fixed |

## Triage Decisions

- Human product note (2026-07-27): reusable layer + product/repo adapters are correct; canonical Scribe docs correctly left in place; skills/workflow README navigation and key skill layer awareness are good; validator/status pass; debt correctly records initial split done and full extraction planned. Main drawback: `.ai/org/workflows.md` still names repo command paths directly.
- Blocking findings (loop 1): R1 Medium — must AI-fix; then re-review.
- Low findings (loop 1): R2–R4 — cheap; include in the same AI fix prompt.
- Low findings accepted or deferred: none.
- Scope concerns: none. Diff stays inside approved reusable-layer process slice; no product Scribe behavior paths.
- Resolution (2026-07-27, loop 1): review gate dirty (`pending_re_review`); Cursor fix; then `Use codex-review.` (do not re-review before fix applied).
- Fix applied (2026-07-27): R1–R4 addressed — org workflows defer to repo validation adapter; feature-manager/commit-manager/supervisor-qa load portable layers; P3 status notes flat adapters; schemas include `gates.retrospective`.
- Resolution (2026-07-27, loop 2): re-review clean (no open High/Medium/Low); R1–R4 verified fixed; verification adequate for docs/process-only slice; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Reusable Layer

## Goal

Confirm that the AI development system now separates reusable process mechanics (`.ai/org/`) from Scribe product adapters (`.ai/product/`) and repository adapters (`.ai/repo/`), that agents are told which layer to read, and that this does not change Scribe’s on-device meeting product behavior or move/delete canonical Scribe docs.

## Environment

- No Scribe app launch required (docs/process-only slice).
- Inspect repository files and run the shell checks below.
- App log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Active ledger: `docs/iterations/2026-07-27-reusable-layer.md`
- Current cycle: `.ai/state/current-cycle.json`
- Org layer: `.ai/org/README.md`, `roles.md`, `workflows.md`, `metrics.md`, `schemas.md`
- Product adapters: `.ai/product/invariants.md`, `roadmap.md`, `scenarios.md`
- Repo adapters: `.ai/repo/stack.md`, `validation.md`, `forbidden-paths.md`
- Skills / workflows: `.ai/skills/README.md`, `docs/workflows/README.md`, plus layer pointers in feature-manager / commit-manager / supervisor-qa / key planning & review skills
- Process roadmap: `AI_SYSTEM_ROADMAP.md` (P3 Reusable Process Package)
- Debt register: `.ai/state/debt.md` (`P-2026-07-27-002` done; `P-2026-07-27-003` planned)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open active ledger Approved Scope | Goal is reusable layer split; moving canonical docs, full package extraction, schemas, and Scribe product behavior are out of scope. |
| 2 | Open Implementation Summary | Describes `.ai/org`, `.ai/product`, `.ai/repo`, skill/workflow navigation updates, and process-roadmap/debt status. |
| 3 | Confirm review/triage handoffs | R1–R4 fixed; loop 2 clean; no open High/Medium. |
| 4 | Open `.ai/org/README.md` (PO checklist, not code review) | States reusable process layer; points to roles/workflows/metrics/schemas; says avoid Scribe-specific details except via product/repo adapters. |
| 5 | Open `.ai/org/workflows.md` Gates section | Gate rules stay portable; cycle status/validator are described via `.ai/repo/validation.md`, not hardcoded `scripts/ai-cycle-*.sh` paths. |
| 6 | Open `.ai/product/invariants.md` and `.ai/repo/validation.md` | Product adapter points at canonical PRODUCT/ROADMAP/scenarios/privacy; repo adapter owns concrete validation commands. |
| 7 | Open `.ai/skills/README.md` and `docs/workflows/README.md` Portable layers | Both explain org vs product vs repo and when to use each. |
| 8 | Skim one orchestration skill (e.g. feature-manager) Automatic Context Loading | Includes `.ai/org/`, `.ai/product/`, `.ai/repo/` entries. |
| 9 | Open `AI_SYSTEM_ROADMAP.md` P3 + debt `P-2026-07-27-002` / `003` | Initial flat-adapter split noted; nested full extraction deferred; debt matches (002 done, 003 planned). |
| 10 | Run `bash scripts/ai-cycle-status.sh` | Shows this iteration in QA; validation passes. |
| 11 | Run `bash scripts/ai-cycle-validate.sh` | Passes for current QA-ready state. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Canonical docs preserved | Confirm PRODUCT.md / ROADMAP.md / docs/scenarios still exist at root; adapters link to them | No move/delete of canonical Scribe docs. |
| Org boundary honesty | Skim `.ai/org/workflows.md` for script path names | No direct `scripts/ai-cycle-status.sh` / `scripts/ai-cycle-validate.sh` in org workflows. |
| Flat vs nested honesty | Read P3 status line | States initial split uses flat adapter files; nested package layout deferred. |
| Schema minimum field | Open `.ai/org/schemas.md` Current-Cycle Minimum Fields | Includes `gates.retrospective`. |
| Product isolation | Compare changed paths to out-of-scope | No `frontend/` / `backend/` / native / packaging changes required for this slice. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| JSON validity | `jq empty .ai/state/current-cycle.json` | Exits 0. |
| Patch hygiene | `git diff --check` | Exits 0. |
| Scope hygiene | `git status --short --untracked-files=all` | Only process/docs/ledger/state / `.ai/*` adapter paths. |
| Gate honesty | Inspect current-cycle | Review/triage clean; `commit_allowed` still false; `supervisor_qa` not marked passed ahead of your decision. |
| Discoverability | Skim skills README + workflows README Portable layers | Org/product/repo layers are named and linked. |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI smoke.
- `(cd frontend && npm run build)`.
- Moving or deleting canonical Scribe docs.
- Full reusable package extraction for another repository.
- Machine-readable schema implementation beyond documenting targets.
- Approving or creating the git commit (later human checkpoint).

## Pass criteria

- [x] `.ai/org/`, `.ai/product/`, and `.ai/repo/` exist and match the approved split intent.
- [x] Org workflows defer cycle commands to the repo validation adapter.
- [x] Skills/workflow docs tell agents which layer to read.
- [x] Review gate is clean (no open High/Medium; R1–R4 fixed).
- [x] `scripts/ai-cycle-validate.sh` / `scripts/ai-cycle-status.sh` pass on current state.
- [x] No Scribe product behavior changed by this iteration.
- [x] Canonical Scribe docs were not moved/deleted.
- [x] `git diff --check` passes.

## Fail criteria

- Org layer still hardcodes repo script paths for cycle status/validator.
- Layer split claims complete while product behavior or canonical docs were moved/changed.
- Review claimed clean while High/Medium remain open.
- Full package extraction or schema automation was silently treated as done without human approval.
- Forbidden paths required for the slice.

## Notes

- Accepted Lows: none (R2–R4 were fixed).
- Suggested order: ledger scope → org/product/repo skim → skills/workflows discoverability → P3/debt honesty → shell validators → path hygiene.
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
| `scripts/ai-cycle-validate.sh` | pass | Validate active state |
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
| Review loops | 2 | observed | Loop 1 fix + loop 2 clean re-review |
| High findings | 0 | observed | Loop 2 open count (loop 1 had R1 Medium, fixed) |
| Medium findings | 0 | observed | Loop 2 open count |
| Low findings | 0 | observed | Loop 2 open count (R2–R4 fixed) |
| Human decisions | 3 | observed | Implementation request + triage calibration note + QA pass |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | pending | observed | Iteration not complete (awaiting commit) |

## Retrospective

**What worked:** pending

**What caused rework:** pending

**Repeated failure patterns:** pending

**Process change recommended:** pending

**Next planning input:** pending
