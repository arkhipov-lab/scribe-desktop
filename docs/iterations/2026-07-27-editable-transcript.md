# Iteration: Editable Raw Transcript

**Status:** shipped
**Date started:** 2026-07-27
**Date completed:** 2026-07-27
**Commit:** `ca1098b1ff8766646fac0fe584668eaa0ab221a1`

## Approved Scope

**Goal:** Let the user edit the transcript as plain text (not Markdown), keep edits as left until Transcribe overwrites them, keep summary Markdown display-only, and have manual Generate/Regenerate summarize the **current** transcript text (fully replacing the summary). Keep first-run auto-summary after Transcribe when the auto-summary checkbox is on.

**Hypothesis:** If users can correct Whisper output as plain text in-app and regenerate notes from that text on demand, they spend less time outside Scribe fixing notes — without turning the app into a Markdown document editor.

**In scope:**
- Transcript pane: plain-text display and edit (no Markdown rendering/processing for transcript)
- Persist edits as the user left them (in-session Api state; local history when a session exists; copy/export use current text)
- **Transcribe** again fully overwrites the transcript (edits discarded), consistent with clear-on-retranscribe; summary cleared/replaced per existing pipeline start rules
- Summary pane: unchanged Markdown rendering; **not** editable this slice
- After a fresh Transcribe: if **auto-summary** is enabled, generate the first summary automatically from the new Whisper transcript (existing behavior retained)
- After the user edits the transcript: do **not** auto-start summary; manual **Generate / Regenerate** uses the current transcript string and fully overwrites the summary
- Bridge/API + `vite-env.d.ts` so backend state, history, export, and summary see the edited transcript
- New/updated scenario(s) plus PRODUCT / TESTING / README / ROADMAP / pipeline surfaces updated in one pass
- No transcript/summary bodies in logs

**Out of scope:**
- Editable summary / Markdown WYSIWYG / raw-MD dual-pane editor
- Changing how summary Markdown is rendered
- Auto-regenerate summary on every transcript keystroke/blur/edit
- `PP-2026-07-27-002` (language auto-detect)
- Partial copy actions, action-items view, markdown post-process checklist
- Diarization, timestamps/SRT/VTT, PDF export, Advanced model knobs
- Process work (P-004 handoff skill, P-007 automation, schemas, package extraction)
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — Product Owner approved roadmap Option A after product-analyst + roadmap-planner; addendum: transcript-only raw text; Transcribe/Regenerate overwrite rules; first auto-summary still automatic when checkbox set; manual summary only for further transcript edits
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend editable results; PO narrowed to transcript-only raw text | done |
| Planning | roadmap-planner | Option A approved in chat (with auto-summary clarification) | done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | chat prompt 2026-07-27 | done |
| Implementation pending | Cursor | chat implement 2026-07-27 | done |
| Implementation summary received | feature-manager records Cursor summary | this ledger § Implementation Summary | done |
| Review ready → Review | Codex | loop 1: 1 High (R1), 1 Medium (R2), 2 Low (R3–R4) | done |
| Triage / auto-fix | review-triage | loop 1: auto-fix R1/R2/R4; PO Decision B on R3; fixes applied 2026-07-27 | done |
| Review ready → Review | Codex | loop 2: 0 High, 0 Medium, 0 Low — R1–R4 verified fixed | done |
| Triage / auto-fix | review-triage | loop 2 clean; review gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human passed 2026-07-27 | done |
| Commit prep | commit-manager | commit `ca1098b` created 2026-07-27 | done |
| Retrospective | iteration-retrospective | completed 2026-07-27; next planning → product-analyst (PP-003 vs PP-002 vs P-004) | done |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Prompt in chat 2026-07-27 |
| Implementation pending | done | Cursor implement 2026-07-27 |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `backend/history.py` — `update_session_transcript` (writes transcript without clearing summary)
  - `backend/app.py` — `Api.update_transcript` (state + history; reject while transcribing/recording; log chars/session only)
  - `frontend/src/vite-env.d.ts` — `update_transcript` on bridge
  - `frontend/src/App.tsx` — plain-text transcript editor; dirty/poll protection; debounce persist; flush before summary/export; regenerate hint; clear on Transcribe/open/new
  - `frontend/src/styles.css` — `.transcript-editor` / hint styles
  - `frontend/src/locales/en.json`, `ru.json` — `result.transcriptEditedHint`
  - Docs: `docs/scenarios/editable-transcript.md` + README index; `summary-generation.md`, `export-notes.md`, `local-history.md`; `PRODUCT.md`, `ROADMAP.md`, `TESTING.md`, `README.md`, `LOCAL_DATA.md`, `AI_PIPELINE.md`, `AGENTS.md`
  - Cycle: this ledger + `.ai/state/current-cycle.json`
- Behavior changed:
  - Transcript is plain-text editable (no MarkdownBody); summary stays Markdown read-only
  - Edits persist to Api + history session transcript; summary not cleared on edit
  - Auto-summary after Transcribe unchanged; edits do not auto-start summary
  - Manual Generate/Regenerate flushes edits then summarizes current transcript (overwrites summary)
  - Transcribe clears/overwrites transcript (and summary per existing pipeline)
- Assumptions:
  - History filename `transcript.md` kept; content treated as plain text
  - Light “regenerate” hint when summary may be stale after edits
  - Full interactive `./scripts/run-dev.sh` ML smoke left for human Supervisor QA
- Verification reported by implementer:
  - `(cd frontend && npm run build)` — pass
  - `git diff --check` — pass
  - `.venv` import smoke for `update_session_transcript` / method presence — pass
  - `scripts/ai-cycle-status.sh` — pass (before phase→review)
  - Interactive app / history reopen / log privacy — not run (needs human QA)
- Remaining work:
  - Codex review → triage → Supervisor QA
- Documentation updates:
  - Listed above; product-surface checklist includes README Usage

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | High | `frontend/src/App.tsx:544-575` (`flushTranscript` / `clearTranscriptDraft` / `onTranscribe`) | In-flight `flushTranscript` is not invalidated when Transcribe/open/new clears the draft; a late successful `update_transcript` can overwrite the new Whisper transcript in state/history. | fixed |
| R2 | Medium | `frontend/src/App.tsx:557-565` | On `update_transcript` `ok: false`, flush still clears dirty and applies `merged.transcript \|\| text`. | fixed |
| R3 | Low | `frontend/src/App.tsx:465-469`, `452-456` | Transcript stays editable during summary; `summaryStale` cleared on any summary `completed`, even if user edited mid-summary. | fixed — PO chose Option B |
| R4 | Low | `ARCHITECTURE.md:31` | Frontend role still says transcript/summary “display” only after editable transcript shipped. | fixed |

## Triage Decisions

- Review loop number: 2 (re-review after R1–R4 fixes)
- Blocking findings: none (0 High, 0 Medium open)
- Auto-fix pass generated: n/a for loop 2 (clean)
- Auto-fix applied: loop 1 applied 2026-07-27 — R1–R4
- Low findings auto-fixed: R4 (loop 1); none open in loop 2
- Low findings accepted or deferred: none
- Human involvement required: no (for this clean loop-2 triage); prior R3 Decision B already recorded
- Human involvement reason: n/a this step
- Scope concerns: none
- Product wishes routed to follow-ups (not debt): none new
- Resolution (2026-07-27, loop 2): review gate clean; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-27 (see below)

# Supervisor QA — Editable Raw Transcript

## Goal

Confirm that Scribe lets you edit the transcript as plain text (not Markdown), keeps those edits until you Transcribe again, leaves the summary as Markdown-only (not editable), still auto-summarizes after Transcribe when auto-summary is on, and only updates notes from edits when you manually Generate/Regenerate.

## Environment

- Start with `./scripts/run-dev.sh`
- Log path for privacy skim: `~/Library/Logs/Scribe/app.log`

## Test data

- A short local audio/video file (already-cached Whisper/summary models preferred)
- Auto-summary **on** for the first pass; optionally repeat with auto-summary **off**
- An existing history session if available (or create one during the happy path)

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Launch app; select/drop a short file; Transcribe with auto-summary on | Transcript appears as editable plain text (not Markdown rendering). First summary appears automatically. Summary pane still looks like formatted notes (Markdown). |
| 2 | Edit the transcript; wait a few seconds; switch tabs | Edits remain as you left them. A regenerate hint may appear if a summary already exists. Summary does **not** restart by itself. |
| 3 | Copy (transcript tab) and/or Export notes | Copied/exported text includes your edited transcript. |
| 4 | Regenerate summary | New summary replaces the old one and reflects the edited transcript. Hint clears if notes now match. |
| 5 | Transcribe again on the same file | Transcript is fully replaced (edits gone). Summary cleared/replaced per normal pipeline; with auto-summary on, first summary runs again automatically. |
| 6 | Open the session from History (after an edit + save/persist) | Edited transcript loads; summary unchanged until you regenerate. |
| 7 | Skim `~/Library/Logs/Scribe/app.log` | Paths/status/lengths OK; **no** transcript or summary body. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Auto-summary off | Transcribe with auto-summary off | No automatic summary; Generate still works from current transcript. |
| Edit during summary (Decision B) | Start regenerate; edit transcript while summary is running | Editing still allowed; after summary finishes, regenerate hint stays if text no longer matches what summarization started from. |
| Empty transcript then Generate | Clear transcript text; Generate | Clear error / no crash; no nonsense summary. |
| New Transcript / other session | Switch session or start New Transcript after dirty edits | Prior in-progress edits discarded; loaded/new state is coherent. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Summary Markdown | View Summary tab | Still Markdown-rendered; not an editor. |
| Summary language / Processing options | Open Processing options | Summary language still under Processing options; transcript language in primary flow. |
| Cancel summary | Cancel mid-summary after regenerate | Transcript (including edits) remains intact. |
| Privacy | Log skim after the flows above | No meeting content in the log. |

## Out of scope

- Editable summary / Markdown document editor (`PP-2026-07-27-003`)
- Language auto-detect (`PP-2026-07-27-002`)
- Partial copy actions, diarization, timestamps/SRT, PDF
- Process automation work

## Pass criteria

- [ ] Transcript is plain-text editable; summary is Markdown display-only
- [ ] Edits persist until Transcribe overwrites them; history reopen shows edited transcript
- [ ] Auto-summary still runs after Transcribe when enabled
- [ ] Edits do not auto-start summary; manual Generate/Regenerate uses current transcript and replaces summary
- [ ] Copy/export reflect edited transcript
- [ ] Log has no transcript/summary bodies
- [ ] No crash or stuck bridge on the happy path

## Fail criteria

- Transcript still Markdown-only / not editable, or summary unexpectedly editable
- Edits lost without Transcribe, or Transcribe fails to overwrite edits
- Auto-summary broken when checkbox on, or summary auto-starts on every edit
- Regenerate ignores edited transcript
- History does not keep edited transcript
- Transcript/summary text appears in the app log

## Notes

- Engineering review is clean (loop 2); this is product QA of observable behavior.
- Do not fail QA because `PP-002` / `PP-003` are still open.
- **Pass with follow-ups** is allowed — new wishes go to `.ai/state/product-followups.md`, not debt.
- After pass or explicit skip, use `Use commit-manager.`

## State updates (plan generated)

- Ledger: Supervisor QA plan recorded; outcome pending human decision
- Current cycle: `phase=QA`; `supervisor_qa` awaiting human; `commit_allowed=false` until pass/skip
- Product follow-ups: none new until QA reports them

**Outcome:** passed

**Human decision:**
- Date: 2026-07-27
- Notes: Human Product Owner passed product QA (“all passed”). No new product follow-ups reported.

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `(cd frontend && npm run build)` | pass | implementer + fix pass + commit-prep |
| `./scripts/run-dev.sh` | pass | human Supervisor QA |
| History reopen after edit | pass | human Supervisor QA |
| Log privacy | pass | human Supervisor QA |

## Debt

Accepted or deferred review/QA/process debt only. Product wishes go under Product Follow-ups / Wishes and in `.ai/state/product-followups.md`.

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |

## Product Follow-ups / Wishes

Local capture for this iteration. Curated source of truth: `.ai/state/product-followups.md`.

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |
| `PP-2026-07-27-003` | Editable summary later without a full Markdown document editor | Planning | Deferred; summary stays Markdown display-only |
| `PP-2026-07-27-002` | Auto-detect transcript language / fewer primary selectors | Planning | Remains open / parked |

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | same calendar day (2026-07-27) | estimated | Planning through commit same evening; wall-clock span not instrumented |
| Agent turns | ~16 across analysis/plan/implement/review/triage/fix/re-review/triage/QA/commit/retrospective | estimated | Skill invocations in this chat cycle; exact turn counter unavailable |
| Approx token use | unavailable | estimated | No token meter in this session |
| Review loops | 2 | observed | Loop 1 findings + auto-fix; loop 2 re-review clean |
| High findings | 1 | observed | R1; fixed before QA |
| Medium findings | 1 | observed | R2; fixed before QA |
| Low findings | 2 | observed | R3–R4; fixed before QA |
| Human decisions | 5 | observed | Option A approval; auto-summary clarification; R3 Decision B; QA pass; commit |
| QA outcome | passed | observed | Supervisor QA human decision 2026-07-27 |
| Outcome | shipped | observed | Commit `ca1098b` (+ hash record `9b5b22b`) + retrospective complete |

## Retrospective

**What worked:**
- Full product loop held: product-analyst → roadmap-planner → feature-manager → implement → review → triage → fix → re-review → QA → commit → retrospective.
- PO narrowed scope early (transcript-only, no Markdown editor, auto-summary clarification) — avoided a large edit-surface detour.
- Auto-fix policy held: R1 High / R2 Medium / R4 cheap Low fixed without asking whether to fix; only product-facing R3 asked the PO (Decision B).
- Loop 2 re-review clean (0/0/0); no endless Low polish.
- Product follow-ups stayed out of debt: PP-003 captured at planning; PP-002 remained parked; QA added no new wishes.
- P-005 already validated earlier this planning cycle (recommendation-first analyst); this product ship provides P-006 measurement evidence.

**What caused rework:**
- First implement pass missed an in-flight debounced persist race (R1 High): late `update_transcript` could overwrite a fresh Whisper result — classic editable-state + async flush hazard.
- Failed flush still cleared dirty (R2 Medium) — incomplete error path on the new persist helper.
- ARCHITECTURE.md frontend role lagged (R4 Low) despite other product surfaces updating — checklist still incomplete for architecture layer wording.
- R3 was not implementer error: genuine product/UX tradeoff correctly escalated.

**Human routine effort:**
- Decisions stayed authority checkpoints: scope (with addendum), product-facing Low (R3), QA, commit — not “should we fix this High/Medium/doc Low?”
- **P-006 measurement (vs pre-auto-fix slices):** Prior product/process slices often asked the human to approve AI-fix of routine Lows (`summary-language-ux`, `product-followups-register`). This cycle auto-fixed R1/R2/R4 and only interrupted for product-facing R3 — confirms the policy intent on a real product iteration after the operator-UX baseline.

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| User-facing / architecture docs incomplete on first pass | R4 ARCHITECTURE.md; prior README Usage miss (`summary-language-ux`); earlier PRODUCT/TESTING lag | yes | docs: extend product-surface checklist to include **ARCHITECTURE.md** layer blurbs when capabilities/UX change |
| Debounced bridge write vs pipeline overwrite race | R1 High this iteration | new (first editable-state slice) | skill/prompt: when implementing editable local state + poll/bridge persist, require in-flight invalidate + server-side generation/epoch guard in the same pass |
| Asking human about routine Lows | Not observed (R4 auto-fixed; R1/R2 auto-fixed) | no (improved) | none; keep auto-fix; P-006 marked done |
| Product-facing Low silent-defer risk | R3 asked PO (Decision B) | no (policy held) | keep hard rule |

**Process change recommended:**
1. Extend the “update all product surfaces in one pass” checklist to explicitly include **ARCHITECTURE.md** (frontend/backend role lines) when user-visible capabilities change — same class of lag as README Usage previously.
2. Add a short **editable-state / debounced persist** checklist item to feature-manager / cursor-implementation prompts (invalidate in-flight writes; epoch or equivalent server guard; failed persist must not clear dirty) when the slice touches local draft + bridge sync. Mark **P-006 done** with this iteration’s measurement (no new ceremony beyond that).

**Next planning input:**
Use `product-analyst` (then roadmap-planner). Compare: `PP-2026-07-27-003` (editable summary without Markdown document editor — needs design approach), parked `PP-2026-07-27-002` (language auto-detect), and process `P-2026-07-27-004` / `P-009` (implementation-runner / validator). Prefer product if a bounded non-Markdown summary-edit approach is clear; otherwise a small process handoff slice or pause for PP-003 design validation.

## State updates (retrospective)

- Ledger: retrospective complete; metrics finalized; status shipped
- Current cycle: `phase=shipped`, `retrospective=done`, commit hash retained
- Debt register: P-006 → done (measurement recorded)
- Product follow-ups: PP-002 / PP-003 remain open; no new wishes from QA
