# Iteration: Product Follow-Ups And Wishes Register

**Status:** shipped
**Date started:** 2026-07-27
**Date completed:** 2026-07-27
**Commit:** `b48047d7ceb228a95756463e634fa9dba3c34608`

## Approved Scope

**Goal:** Add a durable, non-blocking register for Product Owner follow-ups, QA wishes, and future product ideas so they are not mixed with review debt or lost in chat.

**Hypothesis:** If product wishes live in a dedicated register wired into QA, triage, product analysis, roadmap planning, and retrospectives, agents will capture them without failing iterations or treating them as debt.

**In scope:**
- Create `.ai/state/product-followups.md` as the global curated register
- Define what belongs / does not belong there
- Move `PP-2026-07-27-001` and `PP-2026-07-27-002` out of `.ai/state/debt.md` into the new register
- Narrow `debt.md` to accepted/deferred debt and planned process work
- Update iteration ledger template with a Product Follow-ups / Wishes section
- Update supervisor-qa, review-triage, product-analyst, roadmap-planner, and iteration-retrospective skills
- Lightweight validator existence check for the follow-ups register
- Update `.ai/product/roadmap.md` and related adapters so follow-ups are planning evidence
- Update active cycle state and this ledger

**Out of scope:**
- Implementing any captured follow-up (PP-001 / PP-002 stay open)
- Automated scoring / prioritization of wishes
- Full machine-readable backlog schema
- Moving planned process work out of `debt.md`
- Product-facing Scribe behavior changes
- CI integration
- New Product Owner console / onboarding flows

**Human approval:**
- Source: chat — Product Owner approved analysis/plan for process slice
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | Cursor (analysis) + human approval | Approved scope in chat | done |
| Implementation | Cursor | Product follow-ups register + skill/docs wiring | done |
| Review | Codex | loop 1: 0 High, 0 Medium, 5 Low | done |
| Triage | review-triage | Low-only; human AI-fix R1–R5; gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human passed 2026-07-27 | done |
| Commit prep | commit-manager | commit `b48047d` created 2026-07-27 | done |
| Retrospective | iteration-retrospective | completed 2026-07-27; next planning → product-analyst (PP-001 vs editable results vs P-002) | done |

## Implementation Summary

- Files changed:
  - `.ai/state/product-followups.md` (created; PP-001/PP-002)
  - `.ai/state/debt.md` (removed Planned Product Work; narrowed intro)
  - `.ai/state/current-cycle.json`
  - `docs/iterations/2026-07-27-product-followups-register.md`
  - `docs/iterations/2026-07-27-separate-languages.md` (path migration notes)
  - `docs/workflows/iteration-ledger.md` (+ Product Follow-ups section)
  - `docs/workflows/README.md`, `feature-development-pipeline.md`, `ai-product-development-cycle.md`
  - `docs/iterations/README.md`
  - `.ai/skills/supervisor-qa.md`, `review-triage.md`, `product-analyst.md`, `roadmap-planner.md`, `iteration-retrospective.md`, `feature-manager.md`, `README.md`
  - `.ai/product/roadmap.md`, `.ai/org/schemas.md`, `.ai/org/workflows.md`
  - `ROADMAP.md`, `docs/scenarios/summary-controls.md`, `AI_SYSTEM_ROADMAP.md`
  - `scripts/ai-cycle-validate.sh` (register existence check)
- Behavior changed:
  - Product wishes live in `.ai/state/product-followups.md`, not `debt.md`
  - Supervisor QA may **pass with follow-ups captured** without failing the iteration
  - Triage does not treat wishes as review debt
  - Product analyst reads follow-ups as first-class planning evidence
  - Roadmap planner may convert a follow-up to a bounded slice only after PO approval
  - Retrospective records whether follow-ups were captured
  - Validator requires debt + product-followups registers to exist
- Assumptions:
  - Planned process work stays in `debt.md` this slice
  - ROADMAP language UX checkboxes remain with pointer to the register
- Verification reported by implementer:
  - `scripts/ai-cycle-status.sh` — pass
  - `scripts/ai-cycle-validate.sh` — pass
  - `git diff --check` — pass
  - Manual: PP-001/PP-002 in product-followups.md; absent from debt.md

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Low | `.ai/org/schemas.md:33` | `product_followups_register` described as optional while validator/workflows require the register file. | fixed |
| R2 | Low | `.ai/skills/commit-manager.md:26` | Commit-manager still only loads debt.md; no check that QA wishes were written to product-followups. | fixed |
| R3 | Low | `.ai/skills/roadmap-planner.md:161` | Output still says “Product debt from deferral” after follow-ups/debt split. | fixed |
| R4 | Low | `docs/iterations/README.md:11` | Ledger contents list omits product follow-ups (file pointer on line 13 already updated). | fixed |
| R5 | Low | `docs/workflows/feature-development-pipeline.md:126-127` | Debt bullet ends with `.` before sibling follow-ups bullet. | fixed |

## Triage Decisions

- Blocking findings (loop 1): none (0 High, 0 Medium).
- Low findings (loop 1): R1–R5 — all cheap wording/consumer polish in docs/skills; recommend **one AI fix pass** (no full re-review required for Low-only polish).
- Low findings accepted or deferred: none (human requested AI fix all, 2026-07-27).
- Scope concerns: none. Diff is process/docs/skills/validator only; no Scribe product behavior; PP-001/PP-002 remain open wishes, not implemented.
- Privacy / bridge: N/A (no product code).
- Docs: register + skills + ledger template + adapters wired; residual Lows are incomplete-consumer wording.
- Resolution (2026-07-27, loop 1): review gate not clean while R1–R5 open; await human — request AI fix (recommended) or explicitly accept/defer each Low as debt.
- Fix applied (2026-07-27): R1 schemas required-file wording; R2 commit-manager follow-ups check; R3 roadmap-planner deferral label; R4 iterations README contents list; R5 pipeline list punctuation. No full re-review (Low-only polish).
- Resolution (2026-07-27): review gate clean; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Product Follow-Ups And Wishes Register

## Goal

Confirm that Product Owner / QA product wishes now have a durable home separate from review debt, that PP-001 / PP-002 are discoverable there, that agents are instructed to capture wishes without failing an iteration, and that Scribe’s on-device meeting product was not changed by this process slice.

## Environment

- No Scribe app launch is required (docs/process-only slice).
- Inspect repository files and run the shell checks below.
- App log path `~/Library/Logs/Scribe/app.log` is irrelevant for this slice.

## Test data

- Follow-ups register: `.ai/state/product-followups.md`
- Debt register: `.ai/state/debt.md`
- Current cycle: `.ai/state/current-cycle.json`
- Active ledger: `docs/iterations/2026-07-27-product-followups-register.md`
- Ledger template: `docs/workflows/iteration-ledger.md`
- Skills: `.ai/skills/supervisor-qa.md`, `review-triage.md`, `product-analyst.md`, `roadmap-planner.md`, `iteration-retrospective.md`, `commit-manager.md`
- Adapters: `.ai/product/roadmap.md`, `.ai/org/workflows.md`, `.ai/org/schemas.md`
- Pointers: `ROADMAP.md` (Language UX follow-ups), `docs/scenarios/summary-controls.md` Future note
- Scripts: `scripts/ai-cycle-status.sh`, `scripts/ai-cycle-validate.sh`

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open `.ai/state/product-followups.md` | Exists; explains belongs / does-not-belong; says wishes are not review debt and do not block commit |
| 2 | Skim Open Follow-Ups table | `PP-2026-07-27-001` and `PP-2026-07-27-002` are present with status `open` |
| 3 | Open `.ai/state/debt.md` | No Planned Product Work section; no `PP-2026-07-27-001` / `002` rows; intro points wishes to product-followups.md |
| 4 | Open `docs/workflows/iteration-ledger.md` Required Template | Has a **Product Follow-ups / Wishes** section separate from **Debt** |
| 5 | Open supervisor-qa skill | Allows **pass with follow-ups captured**; writes wishes to product-followups, not debt |
| 6 | Open review-triage skill | Says wishes are not review debt / not filed in debt.md |
| 7 | Open product-analyst + roadmap-planner skills | Follow-ups are planning evidence; converting to a slice needs Product Owner approval |
| 8 | Open iteration-retrospective + commit-manager skills | Retrospective checks capture; commit-manager verifies wishes landed in follow-ups when noted |
| 9 | Open ROADMAP Language UX follow-ups + scenario Future note | Point at `.ai/state/product-followups.md` (not debt.md) |
| 10 | Run `bash scripts/ai-cycle-status.sh` then `bash scripts/ai-cycle-validate.sh` | Both pass; validator reports product-followups register exists |
| 11 | Skim active ledger Review Findings | R1–R5 are `fixed`; no open High/Medium |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Wishes vs debt boundary | Compare product-followups “does not belong” vs debt.md intro | Review findings, engineering debt, and planned process work stay in debt; wishes stay in follow-ups |
| Pass without implementing PP-001/002 | Re-read approved out-of-scope | Leaving PP-001/002 open is correct; do **not** fail QA for unimplemented wishes |
| Planned process work still in debt | Skim debt.md Planned Process Work | `P-2026-07-26-002`, `P-2026-07-27-003`, etc. still live there (intentionally not moved this slice) |
| Commit gate honesty | Inspect current-cycle gates | `commit_allowed` is still `false` until you pass/skip QA and later approve commit |
| Product isolation | Compare out-of-scope + `git status` | No requirement to change Scribe record/transcribe/summary/history UX for this slice |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| JSON validity | `jq empty .ai/state/current-cycle.json` | Exits 0 |
| Patch hygiene | `git diff --check` | Exits 0 |
| Validator | `bash scripts/ai-cycle-validate.sh` | Exits 0; debt + product-followups existence OK; clean review/triage |
| Scope hygiene | `git status --short --untracked-files=all` | Process/docs/state/script paths; no required `frontend/` or `backend/` product changes |
| Gate order | Inspect current-cycle | Review/triage `clean`; `supervisor_qa` not marked done ahead of your decision |

## Out of scope

- Running `./scripts/run-dev.sh` or any Scribe UI / ML smoke
- `(cd frontend && npm run build)`
- Implementing PP-001 / PP-002 (or any other product wish)
- Automated scoring / backlog schema / CI
- Moving planned process work out of `debt.md`
- Approving or creating the git commit (later)

## Pass criteria

- [x] `.ai/state/product-followups.md` exists and holds PP-001 / PP-002 as open
- [x] `.ai/state/debt.md` no longer lists those wishes as Planned Product Work
- [x] Iteration ledger template has a Product Follow-ups / Wishes section
- [x] Supervisor QA skill allows pass with follow-ups captured (not fail)
- [x] Triage / analyst / planner / retrospective / commit-manager reference the register correctly
- [x] ROADMAP + scenario Future note point at the follow-ups register
- [x] `scripts/ai-cycle-status.sh` and `scripts/ai-cycle-validate.sh` pass
- [x] `git diff --check` passes
- [x] No open High/Medium in the active ledger
- [x] No Scribe product behavior change required by this iteration

## Fail criteria

- PP-001 / PP-002 missing from product-followups or still presented as debt in debt.md
- Wishes treated as blocking review debt or as a reason to fail QA
- Validator does not require / find the follow-ups register
- Skills still tell agents to park QA wishes only in debt.md
- Slice quietly changed Scribe transcription/summary UX
- Open High/Medium findings remain

## Notes

- Accepted Lows: none (R1–R5 were fixed).
- Suggested order: open follow-ups + debt → ledger template → key skills → ROADMAP/scenario pointers → run status/validate → skim review table → confirm no product code in scope.
- This is **process QA** of the AI development memory model, not engineering code review and not Scribe product QA.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`
- New process wishes you notice during this QA may be captured as follow-ups without failing the iteration (**pass with follow-ups**).

## State updates (plan generated)

- Ledger: Supervisor QA plan recorded; outcome **passed** 2026-07-27
- Current cycle: `supervisor_qa=passed`; `commit_allowed=true`; route to commit-manager
- Product follow-ups: none new from this QA (PP-001/PP-002 already in register; no new wishes)

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: Human Product Owner passed process QA. No new product follow-ups from this check.

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `scripts/ai-cycle-status.sh` | pass | phase=review after implement |
| `scripts/ai-cycle-validate.sh` | pass | debt + product-followups existence OK |
| `git diff --check` | pass | |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |

## Product Follow-ups / Wishes

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |
| `PP-2026-07-27-001` | Summary language default + Processing options placement | Migration | Moved from debt.md into product-followups.md (source: separate-languages QA) |
| `PP-2026-07-27-002` | Auto-detect transcript language / fewer primary-flow selectors | Migration | Moved from debt.md into product-followups.md (source: separate-languages QA) |

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | same calendar day (2026-07-27) | estimated | `date_started` = `date_completed`; wall-clock span not instrumented |
| Agent turns | ~10 across plan/implement/review/triage/fix/QA/commit/retrospective | estimated | Skill invocations in this chat cycle; exact turn counter unavailable |
| Approx token use | unavailable | estimated | No token meter in this session |
| Review loops | 1 | observed | Loop 1: 0 High/Medium, 5 Low; Low-only AI fix; no full re-review |
| High findings | 0 | observed | Review findings table |
| Medium findings | 0 | observed | Review findings table |
| Low findings | 5 | observed | R1–R5; fixed before QA |
| Human decisions | 4 | observed | Approve process slice; AI-fix Lows; QA pass; commit |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | shipped | observed | Commit `b48047d` + retrospective complete |

## Retrospective

**What worked:**
- Clear process slice: split wishes from debt without touching Scribe product behavior.
- PP-001/PP-002 migrated into a durable register before the next product-analyst cycle could re-blur them with debt.
- Engineering review stayed clean of High/Medium (1 loop); Low-only polish avoided a wasteful full re-review.
- Scope discipline held: follow-ups remained open wishes; not implemented mid-slice.
- Process QA was cheap and appropriate (docs/scripts only; no app launch).

**What caused rework:**
- First implement pass updated the named skills and adapters but left residual consumer/wording gaps (schemas “optional” wording, commit-manager context, roadmap-planner “product debt” label, iterations README contents list, pipeline punctuation) — R1–R5 Lows.
- No Medium/High engineering rework; residual was incomplete-consumer lag on a new durable state artifact.

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| New durable process artifact incomplete across all consumers on first pass | This iteration R1–R5 (schemas/commit-manager/planner label/README/pipeline); prior reusable-layer + backlog-intelligence skill/index lag; separate-languages product-surface lag | yes | docs/skill: when adding `.ai/state/*` or process memory, same implement pass must update ledger template + validator + every skill that reads/writes durable memory (including commit-manager) + org/product adapters + indexes |
| Premature re-review before Low fix | Not observed (Low-only, no re-review) | no (held) | none; keep Low-only path without mandatory re-review |
| Process Mediums on first review | 0 Medium this slice | no (improved for this slice) | none formal |

**Process change recommended:**
1. Keep applying the existing “update all consumers in one pass” checklist when adding durable state: include **commit-manager** and schema/validator contract wording explicitly — this slice’s Lows show those were easy to miss when the slice prompt named only a subset of skills.
2. No second process change recommended. Do not invent scoring/backlog schema until a real consumer needs it (`P-2026-07-26-002` remains planned).

**Next planning input:**
Use `product-analyst` (then roadmap-planner) to choose among: `PP-2026-07-27-001` (summary language default + Processing options placement — high UX value, already captured); P2 editable results; planned process `P-2026-07-26-002` (schemas); leave `PP-2026-07-27-002` and `P-2026-07-27-003` parked until evidence/priority is clearer.