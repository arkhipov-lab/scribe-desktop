# Iteration: Recording Mix Dual Path (Phase 3′)

**Status:** shipped
**Date started:** 2026-07-29
**Date completed:** 2026-07-29
**Commit:** `c13dd58bb1a26a457471d0b57714ab1e2d0f4c97`

## Approved Scope

**Goal:** On Record stop, finalize WAV by audio route: no headphones → **mic-only**; headphones → **amix(level_match(mic), system)** so speakers lose digital+acoustic double while headphones keep remote + audible user — without AEC.

**Hypothesis:** If finalize follows dual-path with a conservative unknown-route fallback that never drops remote, matrix A–C on speakers and D on headphones pass for Whisper without Speex/WebRTC.

**In scope:**
- macOS headphone / private-output detection (jack, BT/AirPods, USB-C as feasible); document edge cases
- Finalize path change (primarily `backend/recorder.py`; native helper only if required for reliable route detect)
- No headphones → product WAV from **mic track only** (still capture dual-track; don’t amix for product file)
- Headphones → `amix` after mic amplitude level-match toward system/remote
- Unknown route fallback that **does not drop remote** (prefer headphones-style mix); never delete the only audio copy
- Keep dual-track capture; optional keep-raw unchanged
- Docs: initiative Phase 3′ in progress/done notes; scenario/TESTING/ARCHITECTURE as needed when behavior ships
- Supervisor QA matrix A–E (speakers + headphones) + light CPU note

**Out of scope:**
- AEC / Speex / WebRTC as product default
- Phase 2 sidechain duck
- UX polish follow-ups `PP-001`–`003`
- “Just use headphones” tip as the product fix
- Packaging/DMG unless a tiny native helper must ship for detection
- Logging transcript or raw audio bodies
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — product-analyst dual-path recommendation approved; roadmap-planner **Option A** (`recording-mix-dual-path`) approved
- Date: 2026-07-29

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend `recording-mix-dual-path` (Phase 3′) | done |
| Planning | roadmap-planner | Option A approved in chat | done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | chat prompt 2026-07-29 | done |
| Implementation | Cursor / implementation-agent | dual-path finalize | done |
| Review | Codex | loop 1: 0H/1M/2L | done |
| Triage / auto-fix | review-triage | loop 1 fix_applied R1–R3 | done |
| Fix pass | implementation-agent | R1–R3 | done |
| Re-review | Codex | loop 2: 0 new; R1–R3 verified | done |
| Triage | review-triage | loop 2 clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan + human **passed with follow-ups** 2026-07-29 | done |
| Commit prep | commit-manager | commit `c13dd58` created 2026-07-29 | done |
| Retrospective | iteration-retrospective | completed 2026-07-29; next planning → product-analyst | done |

## Commit preparation

**Commit created:** `c13dd58bb1a26a457471d0b57714ab1e2d0f4c97`

```
feat(recording): dual-path finalize by speakers vs headphones
```

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Prompt recorded 2026-07-29 |
| Implementation pending | done | |
| Implementation summary received | done | 2026-07-29 |

## Implementation Summary

- Files changed:
  - `backend/output_route.py` — **new**; Core Audio ctypes probe of default output transport + data source; classes `speakers` / `headphones` / `unknown` with `finalize_mode`
  - `backend/recorder.py` — dual-path `_mix_to_wav`: speakers → extract mic (`0:a:1`); headphones/unknown → volumedetect level-match mic toward system then `amix`; salvage fallbacks never delete only copy; log route_class/mode/transport/data_source/reason + gain dB only; level-match window capped to first **30s**
  - Docs: `docs/initiatives/recording-clean-mix.md`, `docs/scenarios/recording-to-transcript.md`, `TESTING.md` § E, `ARCHITECTURE.md`, `LOCAL_DATA.md`
  - Cycle: this ledger + `.ai/state/current-cycle.json`
- Behavior changed:
  - Built-in speakers (`bltn` + `ispk`) → product WAV = **mic-only**
  - Built-in headphones jack (`hdpn`) or Bluetooth/BLE → **level-match amix(mic, system)**
  - USB / HDMI / DP / AirPlay / aggregate / virtual / probe failure → **unknown → mix** (do not mic-only)
  - Dual-track capture unchanged; keep-raw unchanged; no AEC; no frontend/Api change
- Assumptions:
  - AudioRecorder stream order remains `0:a:0` system, `0:a:1` mic
  - Route sampled at **stop/finalize** (not continuously during record)
  - Device display name unavailable via simple ctypes on this Mac — USB left ambiguous→mix
  - Level-match clamp −12…+24 dB from mean_volume delta (first 30s window)
- Verification reported by implementer:
  - `python3 -m py_compile backend/recorder.py backend/output_route.py` — pass
  - Offline finalize on keep-raw `recording-20260728-232804.m4a`: route `speakers`/`mic_only`; product size matches mic extract; level-match reported ~+10.4 dB — pass
  - `./scripts/ai-cycle-validate.sh` — pass
  - Interactive Record matrix A–E (speakers + headphones + log privacy) — deferred to Supervisor QA
- Remaining work:
  - Human Supervisor QA (matrix A–E)
- Documentation updates:
  - Listed above; initiative Phase 3′ = implemented pending QA

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `backend/recorder.py` `_volumedetect_mean_db` | Full-file dual `volumedetect` + amix on sync `stop_recording` can stall long headphone finalizes; no 30–60 min CPU note | fixed (verified on re-review) — first 30s `-t` window |
| R2 | Low | `LOCAL_DATA.md` | Still describes Record as always ffmpeg mix; dual-path not mentioned | fixed (verified on re-review) |
| R3 | Low | `TESTING.md` § E (+ scenario) | Detection edges under-documented | fixed (verified on re-review) |

## Triage Decisions

- Review loop **1:** auto-fix R1–R3 (Medium + cheap Lows).
- Review loop **2:** 0 new findings; R1–R3 verified → **clean**. No human ask. Route Supervisor QA.
- Scope: matches dual-path slice; no creep.

## Supervisor QA

### Plan (2026-07-29)

**Goal to confirm (Phase 3′ exit):** On **speakers**, Stop yields a **mic-only** product file so remote is not digitally+acoustically doubled; on **headphones**, remote stays present via system + leveled mic; unknown routes never drop remote. Whisper on A–C (and D if changed) remains usable.

**How to run:** `./scripts/run-dev.sh`  
Prefer a local `./scripts/build.sh` + `open dist/Scribe.app` if Record TCC is flaky under Terminal.  
Optional keep-raw: `open --env SCRIBE_KEEP_RAW_RECORDING=1 ./dist/Scribe.app`  
Logs: `~/Library/Logs/Scribe/app.log`

| # | What to do | Pass if (Phase 3′ exit) |
| --- | --- | --- |
| 1 | **Speakers** (no headphones): Record, remote talks, you silent (A) | Log `route_class=speakers` `mode=mic_only`. Listen: **one** remote (no digital second copy). Thin remote band OK. |
| 2 | Speakers: you talk, remote silent (B) | One clean user voice; normal level |
| 3 | Speakers: overlap / interruptions (C) | Both audible enough for Whisper; no multi-second digital double |
| 4 | **Headphones** or BT earbuds (D) | Log `route_class=headphones` (or BT) `mode=level_match_amix`. Remote present; user audible (not buried); no new double of remote |
| 5 | Optional short **Transcribe** on A–C (and D if you changed path) (E) | Transcript complete; not garbled doubled remote |
| 6 | After stop: WAV under `~/Library/Caches/Scribe/recordings/` | File present and playable |
| 7 | Check `app.log` for finalize lines | `route_class` / `mode` / `transport` / `window_s` / gain — **no** transcript or audio bodies |
| 8 | Light CPU note | Stop on a few-minute clip does not feel like a second ML job (30s detect window already shipped) |

**Edges (do not fail Ideal for these; note if seen):** Bluetooth *room* speakers may still mix (possible double); USB/HDMI/AirPlay → mix; route decided at **stop** (plug/unplug mid-call uses end state).

**Out of scope for this QA (do not fail):** AEC/Speex/WebRTC; Phase 2 duck; UX `PP-001`–`003`; perfect full-band remote on mic-only; packaging/DMG.

**Watch-outs:** Re-check `PP-006` (overlap) / `PP-007` (headphones mic level) as notes only — do not block Phase 3′ if P0 transcript is OK.

**Report back:** pass / pass with follow-ups / fail. Fill results table below.

### Human result

**Passed with follow-ups** (2026-07-29).

**QA unblock (2026-07-29):** `dist/Scribe.app` failed to open after build (`kLSNoExecutableErr` / instant quit) because new `backend/output_route.py` was not copied into the `.app`. Fixed in `scripts/build.sh` + `scripts/build-dist.sh`; rebuild completed — app launches again.

| # | Result | Notes |
| --- | --- | --- |
| 1 Speakers + mic | Pass | |
| 2 BT headphones + mic | Pass | |
| 3 Aux headphones + mic | Pass | |
| 4 Speakers → mid-record switch to BT headphones | Pass | Finalize uses route at stop (expected) |
| 5–8 Transcribe / WAV / log / CPU | Pass (as exercised) | |

**Product follow-ups captured:** `PP-2026-07-29-003` (show input/output devices in UI), `PP-2026-07-29-004` (headset-mic vs default input clarification). Related Ideal items `PP-004` / `PP-001` / `PP-005` / `PP-007` noted ready to close on ship.

**PO question (answered in chat):** headset-with-mic does **not** auto-switch Scribe input unless macOS sets that mic as the **default input**; Record uses `AVCaptureDevice.default(for: .audio)`.

## Verification

- [x] Dual-path finalize on speakers (mic-only) — offline smoke
- [x] Dual-path finalize on headphones (mix + level) — Supervisor QA (BT + aux)
- [x] Unknown-route fallback does not drop remote — code path (conservative classify)
- [x] Matrix A–E — Supervisor QA (4 modes passed)
- [x] ai-cycle-validate
- [x] No transcript/audio body in logs — metadata only (QA confirm in app.log)
- [x] **CPU (R1):** level-match first **30s** only; ~29s fixture level-match+amix ≈ **0.18s**; mic-only ≈ **0.06s**

## Debt / Follow-ups

- Close on ship: `PP-2026-07-28-004`, `PP-2026-07-29-001`, `PP-2026-07-28-005`, `PP-2026-07-28-007` (as noted)
- New from QA: `PP-2026-07-29-003` (UI I/O devices), `PP-2026-07-29-004` (headset mic / default input)
- Deferred: `PP-2026-07-29-002` (AEC), UX `PP-001`–`003` (control-height)

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Review loops | 2 | observed | review-findings / ledger |
| Human decisions | 4 | observed | analyst; Option A; QA pass w/ follow-ups; commit |
| High / Medium / Low findings | 0 / 1 / 2 (all fixed) | observed | review-findings.json |
| QA outcome | passed_with_followups | observed | ledger |
| Outcome | shipped | observed | commit `c13dd58` + this retrospective |

## Retrospective

# Iteration Retrospective — Recording Mix Dual Path (Phase 3′)

## Outcome

- **Status:** shipped
- **Commit:** `c13dd58bb1a26a457471d0b57714ab1e2d0f4c97` (process note `bb383ac`)
- **QA:** passed with follow-ups

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | ~same calendar day (~00:35–01:11 after prior ship; dual-path slice same night) | estimated | commit timestamps + ledger date |
| Agent turns | ~14 skill/step turns | estimated | implement → review → triage → fix → re-review → QA → build unblock → QA result → commit → retrospective |
| Approx token use | not measured | estimated | no tooling report |
| Review loops | 2 | observed | ledger / current-cycle |
| High findings | 0 | observed | review-findings.json |
| Medium findings | 1 | observed | R1 (volumedetect CPU) fixed |
| Low findings | 2 | observed | R2, R3 fixed |
| Human decisions | 4 | observed | analyst; Option A; QA; commit |
| QA outcome | passed_with_followups | observed | ledger |
| Outcome | shipped | observed | `c13dd58` |

## Rework Analysis

- **What caused rework:** Review loop 1 Medium R1 (full-file volumedetect on Stop) + two doc Lows. Mid-QA: new `output_route.py` missing from `build.sh` / `build-dist.sh` explicit copy lists → `.app` would not stay open (`ModuleNotFoundError` / `kLSNoExecutableErr`).
- **What avoided rework:** Clear Ideal from Speex-fail QA; conservative unknown→mix; auto-fix without asking on R1–R3; pass-with-follow-ups for UI I/O wishes; mid-record speakers→BT confirmed route-at-stop behavior.
- **Human routine effort:** Authority checkpoints + real Record matrix (4 modes) + build unblock. Similar to prior recording slices (TCC / local `.app` preferred).

## Repeated Failure Analysis

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| Explicit packaging file lists omit new modules | QA blocker this cycle | yes (first hard hit; same class as “forgot to wire X into dist”) | planned process work `P-2026-07-29-001`; checklist in implementation prompt |
| Long sync Stop work on bridge thread | R1 Medium volumedetect | related to prior “don’t block bridge” | cap analysis (done); note full amix still O(duration) |
| Auto-fix High/Medium without asking | R1–R3 | yes (desired) | none; keep policy |
| Pass-with-follow-ups for Ideal remainder | PP-003/004 new; Ideal PPs closed | yes (desired) | none |

## Process Recommendations

1. When adding a new `backend/*.py` imported by the app, **always** update `scripts/build.sh` and `scripts/build-dist.sh` (or replace explicit `cp` lists with a safe copy-all). Tracked as `P-2026-07-29-001`.
2. No second process change recommended this cycle.

## Debt / Planned Work Updates

- **Debt register:** no new Open Debt
- **Planned process work:** added `P-2026-07-29-001` (backend module packaging checklist)
- **Product follow-ups captured:** yes — closed `PP-004`/`001`/`005`/`007`; open `PP-2026-07-29-003`, `PP-2026-07-29-004`; kept `PP-006` (low), `PP-002` (AEC), UX `PP-001`–`003` (control-height)

## Next Planning Input

Use `product-analyst` (then roadmap-planner). Primary candidates: **show audio I/O in UI** (`PP-2026-07-29-003` + headset-mic `PP-004`); UX polish `PP-2026-07-28-001`–`003`; editable summary `PP-2026-07-27-003`. Do **not** reopen Speex AEC unless Ideal regresses. Initiative Phase 4 mix polish only if PO still hears quality gaps after dual-path.

## State Updates

- Ledger: retrospective completed; status shipped; metrics finalized
- Current cycle: `phase=shipped`, `retrospective=done`, `handoff.next_role=none`, commit hash retained
- Structured review-findings.json: metrics aligned (0/1/2 all fixed)
- Debt register: `P-2026-07-29-001` planned
- Product follow-ups: Ideal items closed; UI I/O open
