# Iteration: Summary Language Default And Processing Options Placement

**Status:** commit-ready
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Default summary language from the resolved UI/system locale; keep transcript language in the primary flow; move the summary-language override under Processing options.

**Hypothesis:** If summary language defaults from the user’s UI/system language and only power users override it under Processing options, most sessions need one fewer decision before useful notes.

**In scope:**
- Default `summary_language` from resolved UI locale (`en` / `ru` / `system`→navigator), mapped to Whisper language codes with fallback `en`
- Migration: preserve already-persisted `summary_language` on disk; change first-launch / missing-key seeding away from “copy transcript language” toward the UI/system default
- Move summary-language control from the primary flow into Processing options
- Keep transcript language control in the primary flow
- Persist override via the existing settings bridge
- Update `docs/scenarios/summary-controls.md` acceptance (Future → current), plus thin PRODUCT / LOCAL_DATA / TESTING / ROADMAP / locales as needed in the same pass
- On ship: mark `PP-2026-07-27-001` converted/closed in `.ai/state/product-followups.md`

**Out of scope:**
- `PP-2026-07-27-002` (auto-detect transcript language / remove transcript picker from primary flow)
- Editable results, partial copy, action-items view
- Advanced model knobs / markdown post-process checklist
- Process schemas (`P-2026-07-26-002`) / package extraction (`P-2026-07-27-003`)
- One-time remigration that rewrites existing persisted `summary_language` values
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — Product Owner approved roadmap Option A after product-analyst + roadmap-planner (default = resolved UI locale; preserve existing persisted `summary_language`)
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend PP-001 over editable results / P-002 / PP-002 | done |
| Planning | roadmap-planner | Option A approved in chat | done |
| Implementation prompt | feature-manager / cursor-implementation-prompt | chat prompt 2026-07-27 | done |
| Implementation | Cursor | chat implement 2026-07-27 | done |
| Review | Codex | loop 1: 0 High, 0 Medium, 1 Low (R1) | done |
| Triage | review-triage | Low-only; human AI-fix R1; gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human passed 2026-07-27 | done |
| Commit prep | commit-manager | commit prep 2026-07-27; await human approval | pending |
| Retrospective | iteration-retrospective | pending | pending |

## Implementation Summary

- Files changed:
  - `backend/settings.py` — missing `summary_language` no longer seeds from transcript language; first launch omits key on disk; `summary_language_persisted()`; merge only persists when key exists or patch sets it
  - `backend/app.py` — expose `summary_language_persisted` on state; prefs fallback uses `DEFAULT_LANGUAGE`
  - `frontend/src/App.tsx` — summary language moved into Processing options; boot seeds from UI locale when not persisted
  - `frontend/src/api.ts`, `vite-env.d.ts`, `locales/en.json`, `locales/ru.json`
  - `docs/scenarios/summary-controls.md`, `PRODUCT.md`, `LOCAL_DATA.md`, `TESTING.md`, `ROADMAP.md`, `AI_PIPELINE.md`
  - `.ai/state/current-cycle.json`, this ledger
- Behavior changed:
  - Primary flow shows transcript language only; summary language override is under Processing options
  - First launch / missing key: frontend seeds `summary_language` from resolved UI locale (`en`/`ru`/… → Whisper code, else `en`)
  - Existing on-disk `summary_language` preserved; UI locale changes after persist do not auto-rewrite
- Assumptions:
  - `summary_language_persisted` bridge flag is the signal for UI seed (no remigration of existing keys)
  - Interactive `./scripts/run-dev.sh` mixed-language smoke left for human Supervisor QA
  - PP-001 remains open in product-followups until ship
- Verification reported by implementer:
  - `(cd frontend && npm run build)` — pass
  - Settings migration smoke (missing≠transcript; first-launch omits key; patch persists; later merge keeps) — pass
  - `git diff --check` — pass
  - `scripts/ai-cycle-status.sh` / validate — pass after phase→review
  - Full interactive app smoke — not run (needs human QA)

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Low | `README.md:98` | Usage step still says choose transcript and summary language as primary-flow controls after summary language moved under Processing options. | fixed |

## Triage Decisions

- Blocking findings (loop 1): none (0 High, 0 Medium).
- Low findings (loop 1): R1 — cheap README wording; recommend **one AI fix pass** (no full re-review required for Low-only polish).
- Low findings accepted or deferred: none (human requested AI fix, 2026-07-27).
- Scope concerns: none. Diff stays inside approved PP-001 / summary-language UX slice; no PP-002, editable results, or process leaps.
- Privacy / bridge: no content logging/upload; `vite-env.d.ts` includes `summary_language_persisted`; Api state exposes the flag.
- Docs: scenario + PRODUCT + TESTING + LOCAL_DATA + ROADMAP + AI_PIPELINE updated; residual Low is README usage step lag.
- Resolution (2026-07-27, loop 1): review gate not clean while R1 open; await human — request AI fix (recommended) or explicitly accept/defer R1 as debt.
- Fix applied (2026-07-27): R1 README usage step — transcript language primary; summary language under Processing options. No full re-review (Low-only polish).
- Resolution (2026-07-27): review gate clean; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Summary Language Default And Processing Options Placement

## Goal

Confirm that Scribe keeps **Transcript language** in the primary flow, puts **Summary language** under Processing options (with a sensible default from the UI/system language), that mixed-language notes still work, that existing saved summary-language preferences are not rewritten, and that meeting content still never appears in the log.

## Environment

- Start with `./scripts/run-dev.sh`
- Log path: `~/Library/Logs/Scribe/app.log` (privacy checks)
- Settings path (optional glance): `~/Library/Application Support/Scribe/settings.json` — preference codes only, no transcript/summary bodies
- No packaging / DMG build required for this slice

## Test data

- One short supported audio/video file (`.m4a` / `.mp3` / `.wav` / `.mp4` / `.mov`)
- Prefer languages you can judge by eye (e.g. transcript Russian, summary English — or the reverse)
- Note your sidebar UI language setting (Auto / EN / RU) — summary language should default from that resolved UI language when no saved summary language exists yet
- If models are not cached yet, first run may download once (local Hugging Face cache only)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Launch via `./scripts/run-dev.sh` | Window opens; no persistent “Desktop bridge is not available” |
| 2 | Look at the primary language row (beside Transcribe) | Only **Transcript language** is there — no summary-language control next to Transcribe |
| 3 | Open **Processing options** | **Summary language** control is present (with models, preset, length, instructions) |
| 4 | Confirm summary language vs UI language | On a fresh / unset preference, summary language matches the resolved UI locale intent (`en` / `ru`, else sensible English fallback). If you already had a saved summary language from before, that saved value is kept |
| 5 | Set transcript language ≠ summary language (summary language via Processing options) | Controls accept different values independently |
| 6 | Select or drop the short test file | File ready; prior result cleared if replacing |
| 7 | Click **Transcribe** | Status shows loading/transcribing; transcript follows transcript-language intent |
| 8 | Wait for summary (auto on) or **Generate / Regenerate** | Summary appears; notes follow the **summary** language intent |
| 9 | Quit app fully, relaunch `./scripts/run-dev.sh` | Transcript language and summary language preferences restored as you left them |
| 10 | Optional: open `settings.json` briefly | Preference codes / processing prefs only — no transcript or summary text |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Same languages | Set both to the same language; regenerate | Still works; no crash or forced “must differ” |
| Change summary language after transcript | Keep transcript; change summary language under Processing options; Regenerate | Existing transcript stays; new summary follows the new summary language |
| Change UI language after summary language is saved | Change sidebar UI language (EN ↔ RU); do not touch summary language | Summary language does **not** auto-rewrite just because UI language changed |
| Preserve existing preference | If you already had a saved summary language before this slice | It stays; app does not force it to match transcript language or silently remigrate |
| History open (if you have an older session) | Open a past session from the sidebar | Session loads; older sessions without a stored summary language fall back sensibly without crash |
| Cancel summary | Start summary, Cancel | Transcript remains intact; UI returns to a sane idle/ready summary state |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Bridge / shell | Confirm Transcribe + Processing options still work | No bridge error; app usable |
| Processing options | Tweak preset or length; regenerate | Still shapes summary as before |
| Log privacy | Skim `~/Library/Logs/Scribe/app.log` after the run | Paths/statuses/model ids OK; **no** transcript body, summary body, or additional-instructions body |
| File ingest | Select another supported file | Prior transcript/summary clear as usual |
| Local-only | No new account/cloud/summary-upload prompts | Processing stays on-device |
| README usage (optional glance) | Skim README Usage step 2 | Mentions transcript language primary; summary language under Processing options |

## Out of scope

- Auto-detect transcript language / remove transcript picker (`PP-2026-07-27-002`)
- In-app editing of transcript/summary before export
- Partial copy / action-items view
- Advanced model knobs / markdown post-process checklist
- Process schemas / package extraction
- One-time remigration that rewrites everyone’s existing summary language to UI locale
- Failing the iteration because summary quality is imperfect for a rare language pair (judge language *intent*, not literary perfection)
- Approving or creating the git commit (later)
- Closing `PP-001` in the follow-ups register (that happens on ship / commit)

## Pass criteria

- [ ] Primary flow shows transcript language only (no summary-language control beside Transcribe)
- [ ] Summary language is available under Processing options
- [ ] Mixed transcript vs summary language run produces notes in the summary-language intent
- [ ] Language preferences survive quit + relaunch
- [ ] Changing summary language does not wipe an existing transcript
- [ ] Changing UI language after summary language is saved does not auto-rewrite summary language
- [ ] Log does not contain transcript/summary/additional-instructions bodies
- [ ] No cloud upload / account flow introduced
- [ ] Review gate remains clean (R1 already fixed)

## Fail criteria

- Summary language still forced into the primary flow beside Transcribe
- Summary ignores summary language when it differs from transcript language
- Preferences lost after relaunch
- Changing summary language clears the transcript
- Existing saved summary language is silently rewritten without user action (except true first-launch / missing-key seed)
- Transcript/summary text appears in the app log
- Crash or persistent bridge failure on the happy path

## Notes

- Accepted Lows: none (R1 was fixed).
- Suggested order: launch → primary flow layout → Processing options summary language → mixed-language transcribe/summary → UI-locale non-rewrite check → relaunch prefs → log privacy skim → optional history open.
- This is product QA of the language UX placement + defaulting, not engineering code review.
- You decide pass / fail / explicit skip. **Pass with follow-ups** is allowed — new wishes go to `.ai/state/product-followups.md`, not debt.
- Do not fail QA because `PP-002` is still open.
- After pass or skip, use `Use commit-manager.`

## State updates (plan generated)

- Ledger: Supervisor QA plan recorded; outcome **passed** 2026-07-27
- Current cycle: `supervisor_qa=passed`; `commit_allowed=true`; route to commit-manager
- Product follow-ups: none new from this QA (`PP-001` still open until ship; `PP-002` remains open)

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: Human Product Owner passed product QA. No new product follow-ups from this check.

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `(cd frontend && npm run build)` | pass | tsc + vite |
| Settings migration smoke | pass | missing≠transcript; first-launch omit; persist on patch |
| `./scripts/run-dev.sh` | pass | human supervisor QA |
| Log privacy | pass | human supervisor QA |

## Debt

Accepted or deferred review/QA/process debt only. Product wishes go under Product Follow-ups / Wishes and in `.ai/state/product-followups.md`.

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |

## Product Follow-ups / Wishes

Local capture for this iteration. Curated source of truth: `.ai/state/product-followups.md`.

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |
| `PP-2026-07-27-001` | Summary language default + Processing options placement | Planning → ship | Converted/closed in product-followups.md on commit prep |
| `PP-2026-07-27-002` | Auto-detect transcript language / fewer primary-flow selectors | Planning | Remains open / deferred (out of scope) |

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | in progress | estimated | `date_started` 2026-07-27; not completed |
| Agent turns | pending | estimated | |
| Approx token use | unavailable | estimated | No token meter in this session |
| Review loops | 1 | observed | Loop 1: 0 High/Medium, 1 Low |
| High findings | 0 | observed | Review findings table |
| Medium findings | 0 | observed | Review findings table |
| Low findings | 1 | observed | R1 README; fixed before QA |
| Human decisions | 4 | observed | Feed analyst→planner; approve Option A; AI-fix R1; QA pass |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | commit-ready | observed | QA passed; awaiting commit |

## Retrospective

**What worked:**

**What caused rework:**

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |

**Process change recommended:**

**Next planning input:**
