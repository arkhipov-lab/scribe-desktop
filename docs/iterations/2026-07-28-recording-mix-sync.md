# Iteration: Recording Mix Sync (Phase 0 + Phase 1)

**Status:** active
**Date started:** 2026-07-28
**Date completed:**
**Commit:**

## Approved Scope

**Goal:** On speakers, eliminate multi-second track skew between mic and system audio so mixed recordings no longer double/shift remote speech enough to break Whisper; keep headphones no worse; leave short acoustic bleed for later AEC.

**Hypothesis:** If mic and system share one coherent timeline (and early mic is not silently dropped), speaker-mode mixes stop destroying remote speech for Whisper, even before AEC removes short acoustic bleed.

**In scope:**
- Phase 0: keep/export pre-mix `.m4a` for failing/QA sessions (dev-friendly; no secrets in shared places); split tracks for inspection; record matrix A/B/C/D once and write notes (remote on both tracks? Δ range?) into this ledger and/or the initiative
- Phase 1 Swift: shared timeline — do not start writer only from first system sample while dropping earlier mic; align `startSession` / PTS; avoid silent drop-on-`!isReadyForMoreMediaData` without a strategy (queue and/or drop counts for diagnostics)
- Re-run QA matrix A–D after sync; optional short transcribe (E) if feasible
- Update initiative status when Phase 0/1 exit
- Light TESTING § E / scenario note only if behavior for agents/QA needs a durable tip (not full Phase 5 docs)

**Out of scope:**
- Phase 2 sidechain duck as product default (or any duck unless PO asks mid-slice)
- Phase 3 AEC (WebRTC/SpeexDSP/VPIO)
- Phase 4 mix polish / Phase 5 full docs lock-in
- Headphones-as-fix; paid AEC; cloud/audio APIs
- Frontend UX polish follow-ups; summary editing; Action items
- Dist packaging / notarization
- Logging transcript or raw meeting audio content
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — Product Owner approved product-analyst recommendation for `recording-mix-sync`, then roadmap-planner Option A
- Date: 2026-07-28

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend Phase 0+1 over UX polish / editable summary | done |
| Planning | roadmap-planner | Option A `recording-mix-sync` approved in chat | done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | chat prompt 2026-07-28 | done |
| Implementation pending | Cursor / implementation-agent | implement 2026-07-28 | done |
| Implementation summary received | feature-manager | this ledger § Implementation Summary | done |
| Review ready → Review | Codex | loop 1: 0 High, 2 Medium (R1–R2), 1 Low (R3) | done |
| Triage / auto-fix | review-triage | loop 1: auto-fix R1–R3; no human ask | done |
| Fix pass | implementation-agent | R1+R3 done; R2 waived to Supervisor QA (PO) | done |
| Review ready → Review | Codex | loop 2: 0 High, 0 Medium, 0 Low — R1–R3 verified fixed | done |
| Triage / auto-fix | review-triage | loop 2 clean; review gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated; human **passed with follow-ups** 2026-07-28 | done |
| Commit prep | commit-manager | prepared 2026-07-28; awaiting human approval | pending |
| Retrospective | iteration-retrospective | — | pending |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Prompt recorded 2026-07-28 |
| Implementation pending | done | Implemented in same session |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `native/AudioRecorder.swift` — shared writer queue; start session at `min(first system PTS, first mic PTS)` once both tracks have a first sample (or 400ms force timeout); queue pending samples instead of dropping early mic / not-ready; overflow + append-fail drop counts; `DIAG:` stderr metadata on session start and stop
  - `backend/recorder.py` — `SCRIBE_KEEP_RAW_RECORDING` keeps pre-mix `.m4a` after mix (path logged only)
  - `LOCAL_DATA.md` — document keep-raw env
  - `TESTING.md` § E — mix sync QA + split-track tip
  - `docs/initiatives/recording-clean-mix.md` — Phase 0/1 in progress
  - Cycle: this ledger + `.ai/state/current-cycle.json` + `.ai/state/review-findings.json`
- Behavior changed:
  - Mic buffers that arrive before the first system sample are retained and aligned to a common session start
  - Not-ready writer inputs queue up to a cap instead of silent drop; overflow counted
  - Optional keep of dual-track raw for Phase 0 diagnostics
- Assumptions:
  - Dual mic via ScreenCaptureKit remains macOS 15+; timeout covers single-track / late second track
  - Short acoustic double remote may remain (Phase 3 AEC) — success is no multi-second skew
  - Full matrix A–E is Supervisor QA (needs speakers + real remote audio)
- Verification reported by implementer:
  - Native `AudioRecorder` compile — pass (existing NSLock-in-async warning unchanged in character)
  - `python3 -m py_compile backend/recorder.py` — pass
  - `./scripts/ai-cycle-validate.sh` — pass
  - Interactive Record matrix A–D / speakers — deferred to Supervisor QA
- Remaining work:
  - Codex review → triage → human Supervisor QA (matrix A–D; optional E; note Δ / remaining double)
  - After QA: mark Phase 0/1 exit on initiative if matrix passes
- Documentation updates:
  - `TESTING.md`, `LOCAL_DATA.md`, initiative status

## Phase 0 diagnostics notes

| Setup | Remote on both tracks? | Approx Δ | Notes |
| --- | --- | --- | --- |
| A Speakers; remote only | Yes (bleed/double) | Fixed / length-independent; noticeable | Quiet MacBook: “something in background”; loud: clear duplicate (not just echo). **Transcript not hurt.** 10s and ~4min same character |
| B Speakers; user only | N/A | — | Passed (as before) |
| C Speakers; overlap | Same double as A | Fixed | User voice hard to hear under remote |
| D Headphones | No double | — | Mic quiet vs system in mix |

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `native/AudioRecorder.swift:184-217` | Stop flush is single-pass; remaining pending can be discarded without retry/count | fixed — drainPendingAtStop retry + drops_at_stop |
| R2 | Medium | ledger verification | No Record→Stop→WAV smoke; compile-only | fixed — PO: smoke waived to Supervisor QA |
| R3 | Low | `LOCAL_DATA.md:81` | Keep-raw should warn about accumulation / unset env | fixed |

- Review loop number: 2 (re-review after R1–R3 fixes; R2 smoke→QA)
- Triage loop 1: auto-fix R1–R3
- Triage loop 2: clean — no open High/Medium; Lows fixed; route supervisor-qa
- Fix pass 2026-07-28: R1 drain retry; R3 LOCAL_DATA warning; R2 compile OK, CLI capture declined TCC — **PO later waived implementer smoke to Supervisor QA** (2026-07-28)

## Supervisor QA

### Plan (2026-07-28)

**Goal to confirm:** On speakers, remote speech is not doubled with a multi-second delay in the mixed recording; headphones are no worse; short room-like echo is OK (AEC is later).

**How to run:** `./scripts/run-dev.sh` (optional: `SCRIBE_KEEP_RAW_RECORDING=1 ./scripts/run-dev.sh` for track split).

| # | What to do | Pass if |
| --- | --- | --- |
| 1 | Record on **speakers**, remote talks, you silent (A) | One clean remote; no multi-second second copy |
| 2 | Speakers, you talk, remote silent (B) | One clean user voice; normal level |
| 3 | Speakers, overlap / interruptions (C) | Both audible; no multi-second echo; no dropped important tails |
| 4 | **Headphones** regression (D) | No worse than before; no new artifacts |
| 5 | Optional: short Transcribe on A–C (E) | Transcript complete; not garbled doubled remote |
| 6 | Confirm WAV under `~/Library/Caches/Scribe/recordings/` after stop | File present and usable |
| 7 | Optional keep-raw: split tracks with `ffprobe` / `ffmpeg -map 0:a:0` and `0:a:1`; note Δ | Notes filled in ledger Phase 0 table |
| 8 | Check `~/Library/Logs/Scribe/app.log` | Paths/DIAG/counts only — no meeting audio body |

**Out of scope for this QA (do not fail):** AEC, ducking, headphones-as-fix, UX polish follow-ups, perfect silence of short acoustic bleed.

**Watch-outs:** R2 was waived here on purpose — this matrix **is** the Record smoke. Short acoustic double may remain.

**Report back:** pass / fail (and any product follow-ups). Fill Phase 0 table if you ran keep-raw splits.

**Human result (2026-07-28):** **Passed with follow-ups** for Phase 1 scope (agent + PO evidence).

| # | Result | Notes |
| --- | --- | --- |
| 1 | Pass for Phase 1 / P0 | Double remains; Δ consistent (not duration-dependent); transcript OK. Ideal “one clean remote” still open → AEC |
| 2 | Pass | Unchanged vs before |
| 3 | Follow-up | Same double; user voice buried on overlap → PP-006 |
| 4 | Pass (+ note) | No double; mic quiet vs system → PP-007 |
| 5 | Pass | Transcript usable on A |
| 6–8 | Skipped | — |

Follow-ups: `PP-2026-07-28-005` (fixed-delay double / AEC), `PP-006` (overlap audibility), `PP-007` (headphones mic level). `PP-004` remains open for Ideal.

## Verification

- [x] AudioRecorder compiles
- [x] recorder.py compiles
- [x] ai-cycle-validate
- [x] Interactive matrix A–D (Supervisor QA) — Phase 1 verdict pass w/ follow-ups
- [x] Optional transcribe E — pass on A
- [ ] keep-raw / log privacy checks — skipped by QA

## Debt / Follow-ups

- Source follow-up: `PP-2026-07-28-004` (Ideal; next Phase 3 AEC)
- New from this QA: `PP-2026-07-28-005`, `PP-2026-07-28-006`, `PP-2026-07-28-007`
- Deferred this cycle: Phase 2–5 implementation; UX `PP-001`–`003`; `PP-2026-07-27-002` / `003`; Action items; process `P-004`

## Metrics

| Metric | Value |
| --- | --- |
| Review loops | 2 |
| Human decisions | 4 (analyst + planner + R2→QA + QA verdict) |
| High / Medium / Low findings | 0 / 2 / 1 (all fixed) |
| QA outcome | passed (with follow-ups) |
| Outcome | |

## Retrospective

_Pending._
