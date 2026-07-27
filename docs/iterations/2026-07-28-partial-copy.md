# Iteration: Partial Copy Actions

**Status:** shipped
**Date started:** 2026-07-28
**Date completed:** 2026-07-28
**Commit:** `80f07e70884db02069a37501a9a90cbdfab3c799`

## Approved Scope

**Goal:** Add explicit Copy transcript, Copy summary, and Copy action items actions so users can put the right content on the clipboard without depending only on the active results tab or a full export.

**Hypothesis:** If users can copy transcript, summary, or action items in one click without switching tabs or exporting a file, the review → reuse loop gets shorter for the most common post-meeting actions.

**In scope:**
- Explicit copy actions for transcript, full summary, and Action items section when present
- Parse Action items from summary markdown using known localized / English section headings; empty or missing section → clear disabled or short feedback (not a crash)
- i18n labels / tooltips; brief “Copied” feedback (reuse existing pattern)
- Prefer frontend clipboard from existing transcript/summary state (no new backend Api unless a real gap appears)
- Scenario `docs/scenarios/partial-copy.md` + TESTING / scenarios index updates
- Light product-doc touch (PRODUCT / README / ROADMAP capability wording) in one pass
- No transcript/summary bodies in logs

**Out of scope:**
- Editable summary (PP-003)
- Dedicated Action items task-list view
- Export format changes
- Timestamps / `.srt` / `.vtt`, diarization
- Language auto-detect (PP-002)
- Process work (P-004, schemas, package extraction)
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — Product Owner approved product-analyst partial-copy recommendation, then roadmap-planner Option A (transcript / summary / action items)
- Date: 2026-07-28

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend partial copy over PP-003 / P-004 / PP-002 | done |
| Planning | roadmap-planner | Option A approved in chat | done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | chat prompt 2026-07-28 | done |
| Implementation pending | Cursor / implementation-agent | implement 2026-07-28 | done |
| Implementation summary received | feature-manager records summary | this ledger § Implementation Summary | done |
| Review ready → Review | Codex | loop 1: 0 High, 1 Medium (R1), 2 Low (R2–R3) | done |
| Triage / auto-fix | review-triage | loop 1: auto-fix R1–R3; route to implementation-agent | done |
| Fix pass | implementation-agent | R1–R3 fixed 2026-07-28 | done |
| Review ready → Review | Codex | loop 2: 0 High, 0 Medium, 0 Low — R1–R3 verified fixed | done |
| Triage / auto-fix | review-triage | loop 2 clean; review gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human **passed** 2026-07-28 | done |
| Commit prep | commit-manager | commit `80f07e7` created 2026-07-28 | done |
| Retrospective | iteration-retrospective | completed 2026-07-28; next planning → product-analyst | done |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Prompt recorded 2026-07-28 |
| Implementation pending | done | Implemented in same session |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `frontend/src/actionItems.ts` — extract Action items section from summary markdown (localized headings + empty/placeholder handling)
  - `frontend/src/App.tsx` — Copy menu with transcript / summary / action items; clipboard helper + outside-click / Escape close
  - `frontend/src/styles.css` — `.copy-menu` / `.copy-menu-list` / `.copy-menu-option`
  - `frontend/src/locales/en.json`, `ru.json` — copy menu strings
  - Docs: `docs/scenarios/partial-copy.md` + README index; `PRODUCT.md`, `README.md`, `ROADMAP.md`, `TESTING.md`, `ARCHITECTURE.md`
  - Cycle: this ledger + `.ai/state/current-cycle.json` + `.ai/state/review-findings.json`
- Behavior changed:
  - Results toolbar Copy opens a menu: Copy transcript, Copy summary, Copy action items
  - Actions work independent of active tab; unavailable targets are disabled
  - Action items parsed from `##` headings matching known localized Action items titles; empty/placeholder bodies disabled
- Assumptions:
  - Frontend-only clipboard is enough (no new Api)
  - Action items headings mirror `backend/summarizer.py` meeting_notes localization + English “Action items”
  - Heading-less summaries do **not** count as action items (R1 fix)
- Verification reported by implementer:
  - `(cd frontend && npm run build)` — pass
  - `./scripts/ai-cycle-validate.sh` — pass
  - `./scripts/run-dev.sh` interactive copy smoke — not run in this pass (manual QA)
- Remaining work:
  - Independent review → triage → supervisor QA → commit
- Documentation updates:
  - Scenario + PRODUCT/README/ROADMAP/TESTING/ARCHITECTURE as above

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `frontend/src/actionItems.ts:61-69` | Heading-less summary fallback treats entire body as action items, violating scenario | fixed |
| R2 | Low | `TESTING.md:48` | Partial-copy smoke only under § C; missing § D summary coverage | fixed |
| R3 | Low | `docs/iterations/2026-07-28-partial-copy.md:79` | Interactive run-dev copy smoke not executed by implementer | fixed |

## Triage Decisions

- Review loop number: 2 (re-review clean after loop 1 fix pass)
- Blocking findings: none open (R1 Medium fixed)
- Auto-fix pass generated: loop 1 yes (R1–R3); loop 2 none needed
- Auto-fix applied: loop 1 yes — 2026-07-28
- Low findings auto-fixed: R2, R3 (loop 1)
- Low findings accepted or deferred (with/without human; reason): none
- Human involvement required: no
- Human involvement reason (if any): n/a
- Scope concerns: none
- Product wishes routed to follow-ups (not debt): none
- Loop 2: re-review verified R1–R3 fixed; 0 new findings; review gate clean → supervisor-qa

## Supervisor QA

**Plan:** generated 2026-07-28 in chat (Supervisor QA — Partial Copy Actions). Human executes product QA.

**Outcome:** passed

**Human decision:**
- Date: 2026-07-28
- Notes: Human Product Owner passed product QA (“All passed”). No new product follow-ups reported.

## State updates

- Ledger: Supervisor QA **passed** 2026-07-28; no new follow-ups
- Current cycle: moved to `commit-ready` after pass
- Product follow-ups (if any): none

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `(cd frontend && npm run build)` | pass | after R1 fix |
| `extractActionItems` edge cases (tsx) | pass | with section / placeholder / no heading / ru |
| `./scripts/run-dev.sh` interactive copy menu | pass | human Supervisor QA 2026-07-28 |
| `scripts/ai-cycle-validate.sh` | pass | review gate clean |

## Commit Preparation

**Prepared:** 2026-07-28
**Commit:** `80f07e70884db02069a37501a9a90cbdfab3c799` created 2026-07-28 after explicit human approval.

Suggested message:

```
feat(ui): add partial copy for transcript, summary, and action items

Let users copy the right notes piece from the results toolbar without
switching tabs or exporting a file.
```

### Changed files (summary)

| File | Purpose |
| --- | --- |
| `frontend/src/actionItems.ts` | Extract Action items section from summary markdown |
| `frontend/src/App.tsx` | Copy menu (transcript / summary / action items) |
| `frontend/src/styles.css` | Copy menu styles |
| `frontend/src/locales/en.json`, `ru.json` | Copy menu i18n |
| `docs/scenarios/partial-copy.md` | Scenario |
| `docs/scenarios/README.md` | Index |
| `PRODUCT.md`, `README.md`, `ROADMAP.md`, `TESTING.md`, `ARCHITECTURE.md` | Capability / smoke docs |
| `docs/iterations/2026-07-28-partial-copy.md` | Iteration ledger |
| `.ai/state/current-cycle.json` | Cycle state |
| `.ai/state/review-findings.json` | Structured findings |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |

## Product Follow-ups / Wishes

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |

## Metrics

| Metric | Value | Source |
| --- | --- | --- |
| Elapsed time | ~same evening session (planning → ship) | estimated |
| Agent turns | ~14 user skill/step turns | estimated |
| Approx token use | not measured | estimated |
| Review loops | 2 | observed |
| High findings | 0 | observed (structured) |
| Medium findings | 1 | observed (structured R1; fixed) |
| Low findings | 2 | observed (structured R2–R3; fixed) |
| Human decisions | 4 (partial-copy direction; Option A; QA pass; commit) | observed |
| QA outcome | passed | observed |
| Outcome | shipped | observed |

## Retrospective

# Iteration Retrospective — Partial Copy Actions

## Outcome

- **Status:** shipped
- **Commit:** `80f07e70884db02069a37501a9a90cbdfab3c799` (hash record `9f3d953`)
- **QA:** passed

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | ~same evening session | estimated | dates 2026-07-28; commits `80f07e7` / `9f3d953` |
| Agent turns | ~14 user skill/step turns | estimated | analyst → planner → implement → review → triage → fix → re-review → triage → QA → commit → retrospective |
| Approx token use | not measured | estimated | no tooling report |
| Review loops | 2 | observed | ledger / current-cycle |
| High findings | 0 | observed | review-findings.json |
| Medium findings | 1 | observed | review-findings.json (R1 fixed) |
| Low findings | 2 | observed | review-findings.json (R2–R3 fixed) |
| Human decisions | 4 | observed | partial-copy direction; Option A; QA pass; commit |
| QA outcome | passed | observed | ledger |
| Outcome | shipped | observed | commit + this retrospective |

## Rework Analysis

- **What caused rework:** Loop 1 Medium R1 — implementer added a heading-less “whole summary as action items” fallback that contradicted the new scenario edge case (no Action items heading → disabled). Cheap Lows: TESTING only under § C (R2); interactive run-dev smoke deferred (R3).
- **What avoided rework:** Auto-fix of R1–R3 without human interrupts; frontend-only scope (no bridge/Api); re-review clean; product-analyst → roadmap Option A kept scope small; tsx edge-case check for extractActionItems after R1.
- **Human routine effort:** Authority checkpoints only (direction, Option A, QA, commit). Zero review-loop involvement.

## Repeated Failure Analysis

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| Asking human about routine Lows | R2/R3 auto-fixed; no ask | no (improved) | none; keep auto-fix |
| Helpful fallback contradicts scenario written in same slice | R1 heading-less body → action items vs scenario “no heading → disabled” | new (parser/fallback class) | skill/prompt: when adding extract/parse helpers with fallbacks, check scenario edge cases in the same implement pass |
| Product-surface TESTING incomplete across sections | R2 § C only; prior cycles had README/ARCHITECTURE lag | yes (surface checklist theme) | docs: when UX spans multiple TESTING sections, update all relevant sections in one pass |
| Interactive smoke deferred to supervisor QA | R3 this slice; acceptable with alternate verification | unknown (situational) | none as gate; prefer cheap automated/tsx checks when GUI smoke is impractical |

## Process Recommendations

1. For parser/extract helpers: do not ship “convenience” fallbacks that the accompanying scenario explicitly disables — verify edge-case rows before review.
2. When a UX change spans ingest + summary smoke, update TESTING § C and § D (and related) in the same implement pass — same class of lag as prior product-surface checklist gaps.

## Debt / Planned Work Updates

- **Debt register:** no new Open Debt
- **Planned process work:** unchanged (P-004 still planned; P-002 schemas remain demand-driven)
- **Product follow-ups captured:** no — QA added none; PP-002 / PP-003 remain open from prior cycles

## Next Planning Input

Use `product-analyst` (then roadmap-planner). Compare: `PP-2026-07-27-003` (editable summary without Markdown document editor — needs design), parked `PP-2026-07-27-002` (language auto-detect), Action items *view* (ROADMAP P2), and process `P-2026-07-27-004` (implementation-runner). Prefer product if a bounded non-MD summary-edit approach is clear; otherwise a small process handoff slice or pause for PP-003 design validation.

## State Updates

- Ledger: retrospective completed; status shipped; metrics finalized
- Current cycle: `phase=shipped`, `retrospective=done`, `handoff.next_role=none`, commit hash retained
- Structured review-findings.json: metrics aligned (0/1/2); R1–R3 fixed
- Debt register: unchanged

## Notes

- Previous iteration: `2026-07-28-review-findings-reconciliation` (shipped).
- Deferred this cycle: PP-002, PP-003, P-004, Action items view.
