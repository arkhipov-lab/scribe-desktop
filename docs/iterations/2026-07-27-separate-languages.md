# Iteration: Separate Transcript vs Summary Language

**Status:** QA
**Date started:** 2026-07-27
**Date completed:** pending
**Commit:** pending

## Approved Scope

**Goal:** Let the user set Whisper transcript language and summary output language independently, with local persistence.

**Hypothesis:** If transcript and summary languages are independent, bilingual users can keep accurate Whisper language while getting notes in their preferred language without retyping.

**In scope:**
- Add a distinct summary-language preference (e.g. `summary_language`) alongside existing Whisper `language`
- Sensible migration: existing single `language` seeds both until the user changes them
- UI: two clear controls (transcript language vs summary language)
- Bridge/`Api` + `vite-env.d.ts` + settings load/save/normalize
- Summarizer uses summary language for prompts/section headings; Whisper keeps transcript language
- History metadata honesty for both languages where already recorded
- Update `docs/scenarios/summary-controls.md` and thin docs touch-ups (`LOCAL_DATA`, `AI_PIPELINE` / README as needed)

**Out of scope:**
- In-app editing of transcript/summary
- Partial copy / action-items view
- Advanced model knobs / markdown post-process checklist
- Diarization, timestamps, packaging, notarization
- Process work (`P-002`, `P-003`)
- Changing the Whisper language list catalog itself beyond reuse
- Cloud sync / remote AI APIs / telemetry of meeting content

**Human approval:**
- Source: chat — Product Owner approved roadmap Option A after product-analyst + roadmap-planner
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend separate languages over edit-in-app / P-002 / P-003 | done |
| Planning | roadmap-planner | Option A approved in chat | done |
| Implementation prompt | feature-manager / cursor-implementation-prompt | Prompt in chat (2026-07-27) | done |
| Implementation | Cursor | Separate language prefs + UI + history + docs | done |
| Review | Codex | loop 1: 0 High, 0 Medium, 2 Low | done |
| Triage | review-triage | Low-only; human AI-fix R1–R2; gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human passed 2026-07-27 (follow-ups captured, not in this slice) | done |
| Commit prep | commit-manager | preparation ready; await human commit approval | pending |
| Retrospective | iteration-retrospective | pending | pending |

## Implementation Summary

- Files changed:
  - `backend/settings.py` — `summary_language` default, normalize/migration, persist
  - `backend/app.py` — state/prefs, summary worker uses `summary_language`, history open/used fields
  - `backend/history.py` — store/clear `summary_language` on summary update / retranscribe
  - `frontend/src/vite-env.d.ts`, `api.ts`, `App.tsx`, `LanguageSelect.tsx`, `styles.css`
  - `frontend/src/locales/en.json`, `ru.json`
  - `docs/scenarios/summary-controls.md`, `LOCAL_DATA.md`, `AI_PIPELINE.md`, `README.md`, `TESTING.md`
  - `.ai/state/current-cycle.json`, `docs/iterations/2026-07-27-separate-languages.md`
- Behavior changed:
  - Transcript (Whisper) language and summary language are independent controls.
  - Older settings without `summary_language` seed it from `language`.
  - Summarizer prompts use `summary_language`; Whisper keeps `language`.
  - History meta records `summary_language` when a summary is saved; older sessions fall back to `language`.
- Assumptions:
  - Same Whisper language list is reused for summary language (no separate catalog).
  - Session title generation still uses transcript language.
  - Manual `./scripts/run-dev.sh` mixed-language ML smoke left for human QA (build + settings unit smoke done by implementer).
- Verification reported by implementer:
  - `(cd frontend && npm run build)` — pass
  - `PYTHONPATH=backend` settings migration assert (`ru`→`ru` seed; `ru`+`en` independent) — pass
  - `git diff --check` / `scripts/ai-cycle-status.sh` — pass
  - Full interactive mixed-language transcription/summary — not run (needs app + models)

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Low | `TESTING.md:29` | § A still says “Language dropdown populates” after two language controls shipped; §§ C/D updated but bridge smoke line was not. | fixed |
| R2 | Low | `PRODUCT.md:79` (also `:60`, `:95`) | Primary flow / capabilities still describe a single “language” control; README/scenario/pipeline updated, PRODUCT was not. | fixed |

## Triage Decisions

- Blocking findings (loop 1): none (0 High, 0 Medium).
- Low findings (loop 1): R1–R2 — both cheap thin doc edits; recommend one AI fix pass (no full re-review required for Low-only polish).
- Low findings accepted or deferred: none (human requested AI fix both, 2026-07-27).
- Scope concerns: none. Diff stays inside approved separate-languages product slice; no process/P-002/P-003 or unrelated ROADMAP leaps.
- Privacy / bridge: no content logging/upload; `vite-env.d.ts` includes `summary_language` / `used_summary_language`; Api prefs/update_settings allowlist updated.
- Docs: scenario + LOCAL_DATA + AI_PIPELINE + README + TESTING C/D updated; PRODUCT + TESTING § A residual Lows only.
- Resolution (2026-07-27, loop 1): review gate not clean while R1–R2 open; await human — request AI fix (recommended) or explicitly accept/defer each Low as debt.
- Fix applied (2026-07-27): R1 TESTING § A both language controls; R2 PRODUCT summary-shape / primary flow / capabilities wording. No full re-review (Low-only polish).
- Resolution (2026-07-27): review gate clean; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Separate Transcript vs Summary Language

## Goal

Confirm that Scribe lets you set **Transcript language** and **Summary language** independently, that Whisper and notes respect those choices, that both preferences survive relaunch, and that meeting content still never appears in the log.

## Environment

- Start with `./scripts/run-dev.sh`
- Log path: `~/Library/Logs/Scribe/app.log` (privacy checks)
- Settings path (optional glance): `~/Library/Application Support/Scribe/settings.json` — preference codes only, no transcript/summary bodies
- No packaging / DMG build required for this slice

## Test data

- One short supported audio/video file (`.m4a` / `.mp3` / `.wav` / `.mp4` / `.mov`)
- Prefer languages you can judge by eye (e.g. transcript Russian, summary English — or the reverse)
- If models are not cached yet, first run may download once (local Hugging Face cache only)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Launch via `./scripts/run-dev.sh` | Window opens; no persistent “Desktop bridge is not available” |
| 2 | Look at language controls | Two clear controls: **Transcript language** and **Summary language**; both populate with searchable language lists |
| 3 | Set transcript language ≠ summary language | Controls accept different values independently |
| 4 | Select or drop the short test file | File ready; prior result cleared if replacing |
| 5 | Click **Transcribe** | Status shows loading/transcribing; transcript appears in the chosen transcript language intent |
| 6 | Wait for summary (auto on) or **Generate / Regenerate** | Summary appears; notes follow the **summary** language intent (not forced to transcript language) |
| 7 | Quit app fully, relaunch `./scripts/run-dev.sh` | Both language preferences restored as you left them |
| 8 | Optional: open `settings.json` briefly | Contains language codes / processing prefs only — no transcript or summary text |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Same languages | Set both controls to the same language; regenerate | Still works; no crash or forced “must differ” |
| Change summary language after transcript | Keep transcript; change summary language; Regenerate | Existing transcript stays; new summary follows the new summary language |
| Change transcript language only | Change transcript language without re-transcribing | Does not require rewriting an already-finished transcript in this slice; next Transcribe uses the new transcript language |
| History open (if you have an older session) | Open a past session from the sidebar | Session loads; if it has no separate summary language stored, UI falls back sensibly (transcript language) without crash |
| Cancel summary | Start summary, Cancel | Transcript remains intact; UI returns to a sane idle/ready summary state |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Bridge / shell | Confirm both language controls + Transcribe still work | No bridge error; app usable |
| Processing options | Open Processing options; tweak preset or length; regenerate | Still shapes summary as before |
| Log privacy | Skim `~/Library/Logs/Scribe/app.log` after the run | Paths/statuses/model ids OK; **no** transcript body, summary body, or additional-instructions body |
| File ingest | Select another supported file | Prior transcript/summary clear as usual |
| Local-only | No new account/cloud/summary-upload prompts | Processing stays on-device |

## Out of scope

- In-app editing of transcript/summary before export
- Partial copy / action-items view
- Advanced model knobs / markdown post-process checklist
- Diarization, timestamps, packaging, notarization
- Process work (schemas, reusable package extraction)
- Failing the iteration because summary quality is imperfect for a rare language pair (judge language *intent*, not literary perfection)
- Approving or creating the git commit (later)

## Pass criteria

- [ ] Two independent language controls are visible and usable
- [ ] Mixed transcript vs summary language run produces notes in the summary-language intent
- [ ] Both language preferences survive quit + relaunch
- [ ] Changing summary language does not wipe an existing transcript
- [ ] Log does not contain transcript/summary/additional-instructions bodies
- [ ] No cloud upload / account flow introduced
- [ ] Review gate remains clean (R1–R2 already fixed)

## Fail criteria

- Only one language control, or changing one always forces the other
- Summary ignores summary language when it differs from transcript language
- Preferences lost after relaunch
- Changing summary language clears the transcript
- Transcript/summary text appears in the app log
- Crash or persistent bridge failure on the happy path

## Notes

- Accepted Lows: none (R1–R2 were fixed).
- Suggested order: launch → both controls → mixed-language transcribe/summary → relaunch prefs → log privacy skim → optional history open.
- This is product QA of the bilingual language split, not engineering code review.
- You decide pass / fail / explicit skip. After pass or skip, use `Use commit-manager.`

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: Passed with product suggestions explicitly deferred out of this iteration. Capture (not implement now): (1) default summary language = system language; hide summary-language select in primary flow / expose under Processing options; (2) longer-term remove language selectors from direct flow; auto-detect transcript language from audio. Recorded as `PP-2026-07-27-001` / `002` in `.ai/state/debt.md` + ROADMAP language UX follow-ups + scenario Future note.

## State updates (plan generated)

- Ledger: Supervisor QA plan recorded; outcome **passed** 2026-07-27
- Current cycle: `supervisor_qa=passed`; `commit_allowed=true`; route to commit-manager
- Debt register: planned product work `PP-2026-07-27-001`, `PP-2026-07-27-002` added

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `(cd frontend && npm run build)` | pass | tsc + vite |
| Settings migration smoke | pass | missing `summary_language` seeds from `language` |
| `./scripts/run-dev.sh` mixed-language | pass | human supervisor QA |
| Log privacy (no transcript/summary body) | pass | human supervisor QA |

## Debt

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| `PP-2026-07-27-001` Summary language default + Processing options placement | product_followup | QA suggestion; feasible now; out of this iteration by PO | Next product planning after this ships |
| `PP-2026-07-27-002` Auto-detect transcript language / fewer primary-flow selectors | product_followup | QA longer-term desire; needs investigation | After PP-001 or when PO prioritizes |

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | pending | | |
| Agent turns | pending | | |
| Approx token use | pending | | |
| Review loops | 1 | observed | loop 1 review complete |
| High findings | 0 | observed | review loop 1 |
| Medium findings | 0 | observed | review loop 1 |
| Low findings | 2 | observed | R1–R2 fixed |
| Human decisions | 5 | observed | + AI-fix R1–R2; QA pass with deferred follow-ups |
| QA outcome | passed | observed | human 2026-07-27 |
| Outcome | QA passed → commit-ready | observed | await commit-manager |

## Retrospective

**What worked:**

**What caused rework:**

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |

**Process change recommended:**

**Next planning input:**
