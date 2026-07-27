# Iteration: Partial Copy Actions

**Status:** commit-ready
**Date started:** 2026-07-28
**Date completed:** pending
**Commit:** pending

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
| Commit prep | commit-manager | prep recorded 2026-07-28; awaiting human commit approval | done |
| Retrospective | iteration-retrospective | — | pending |

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
**Commit:** pending — awaiting explicit human approval

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
| Elapsed time | pending | |
| Agent turns | pending | |
| Approx token use | pending | |
| Review loops | 2 | observed |
| High findings | 0 | observed (structured) |
| Medium findings | 1 | observed (structured R1; fixed) |
| Low findings | 2 | observed (structured R2–R3; fixed) |
| Human decisions | 3 (analyst + Option A + QA pass; +1 pending commit approval) | observed |
| QA outcome | passed | observed |
| Outcome | pending | |

## Retrospective

pending

## Notes

- Previous iteration: `2026-07-28-review-findings-reconciliation` (shipped).
- Deferred this cycle: PP-002, PP-003, P-004, Action items view.
