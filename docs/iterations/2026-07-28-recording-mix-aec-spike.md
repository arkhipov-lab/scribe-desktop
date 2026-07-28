# Iteration: Recording Mix AEC Spike (Phase 3 offline)

**Status:** shipped
**Date started:** 2026-07-28
**Date completed:** 2026-07-29
**Commit:** `102bac4`

## Approved Scope

**Goal:** Offline AEC(mic, reference=system) on fixtures; pick SpeexDSP vs WebRTC AEC3; prove bleed reduction without chewing user speech; note CPU — no product default.

**Hypothesis:** If AEC uses the digital system track as reference on Phase-1-aligned fixtures, speaker bleed on mic can be cancelled enough that matrix A sounds like one remote and C still keeps user speech — without runtime cost near Whisper.

**In scope:**
- Obtain/split dual-track fixtures (keep-raw / ffmpeg map); no sharing meeting audio
- Offline prototype tool/script (repo-local, not product default): AEC(mic, ref=system) → cleaned mic → optional compare mix
- Library spike: SpeexDSP and/or WebRTC AEC3 — pick one with reasons
- Stabilize delay assumption given Phase 1 sync
- Fixture matrix A–C (listen); optional short Whisper on A
- CPU wall time on a short/medium clip (arm64); paths/durations only in notes/logs
- Initiative update: Phase 3 in progress / spike notes; recommend integrate slice gates
- Light TESTING/DEVELOPMENT tip only if agents need how to run the spike

**Out of scope:**
- Shipping AEC as default Record path
- Phase 2 duck as product default
- Phase 4 mix polish / Phase 5 full scenario lock-in
- VPIO as primary Ideal bet
- Paid AEC SDKs; cloud audio APIs
- UX polish follow-ups; packaging/DMG unless a tiny local helper must link a lib
- Logging transcript or raw audio bodies
- Cloud sync, remote AI APIs, telemetry of meeting content, non-arm64 platforms

**Human approval:**
- Source: chat — Product Owner approved Phase 3, then roadmap-planner Option A (`recording-mix-aec-spike`)
- Date: 2026-07-28

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Product analysis | product-analyst | Recommend `recording-mix-aec-spike` over duck / UX / full integrate | done |
| Planning | roadmap-planner | Option A approved in chat | done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | chat prompt 2026-07-28 | done |
| Implementation pending | Cursor / implementation-agent | implement 2026-07-28 | done |
| Implementation summary received | feature-manager | this ledger § Implementation Summary | done |
| Review ready → Review | Codex | loop 1: 0 High, 1 Medium (R1), 2 Low (R2–R3) | done |
| Triage / auto-fix | review-triage | loop 1: auto-fix R1–R3; no human ask | done |
| Fix pass | implementation-agent | R1 undelayed mixes; R2 help/locals; R3 DEVELOPMENT typo — 2026-07-28 | done |
| Review ready → Review | Codex | loop 2: 0 High, 0 Medium, 0 Low new — R1–R3 verified fixed | done |
| Triage / auto-fix | review-triage | loop 2 clean; review gate clean → supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan + human **passed with follow-ups** 2026-07-29 (mic-only insight; Speex no-cancel) | done |
| Commit prep | commit-manager | commit `102bac4` created 2026-07-29 | done |
| Retrospective | iteration-retrospective | completed 2026-07-29; next planning → product-analyst (`recording-mix-dual-path`) | done |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Prompt recorded 2026-07-28 |
| Implementation pending | done | Implemented in same session |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `scripts/aec-spike.py` — offline SpeexDSP AEC via ctypes (Homebrew `libspeexdsp`); split dual-track m4a → mic/system 16 kHz mono; write `mic_aec`, `mix_plain`, `mix_aec`; `--ref-delay-ms` / `--filter-ms`; gated by `SCRIBE_AEC_SPIKE=1`
  - `DEVELOPMENT.md` — Record TCC tip + AEC spike how-to
  - `TESTING.md` § E — spike step 8
  - `docs/initiatives/recording-clean-mix.md` — Phase 3 in progress + SpeexDSP decision note
  - Cycle: this ledger + `.ai/state/current-cycle.json` + `.ai/state/review-findings.json`
- Behavior changed:
  - **No product Record path change** — spike tool only
- Library recommendation:
  - **Prefer SpeexDSP** for integrate (BSD-3, Homebrew, simple C API, ctypes spike, no new pip product dep)
  - WebRTC AEC3 only if Speex fails listening QA on real speakers-bleed fixtures
- Assumptions:
  - AudioRecorder dual-track layout: `0:a:0` system, `0:a:1` mic
  - Jul 27 dual m4a used for smoke (may not be strong speakers bleed); Supervisor QA should use a known speakers A fixture with keep-raw
  - Delay: try `--ref-delay-ms` if digital tracks are aligned but room delay remains
- Verification reported by implementer:
  - `SCRIBE_AEC_SPIKE=1 python3 scripts/aec-spike.py --input …/recording-20260727-120332.m4a` — pass (outputs written)
  - CPU: ~7.0 s audio → ~0.05 s wall after warmup (~150× realtime) on arm64; first run slower (~0.8 s)
  - RMS mic vs mic_aec barely changed on this fixture (listen QA required on true bleed capture)
  - `./scripts/ai-cycle-validate.sh` — pass
- Remaining work:
  - Codex review → triage → Supervisor QA listen A–C on speakers bleed fixture (+ optional Whisper)
  - After spike exit: plan `recording-mix-aec` integrate with fallback
- Documentation updates:
  - DEVELOPMENT, TESTING, initiative

## Spike results (paths only)

| Item | Result |
| --- | --- |
| Library | SpeexDSP (Homebrew) |
| Tool | `scripts/aec-spike.py` |
| Fixture used | `recording-20260727-120332.m4a` (dual-track) |
| CPU | ~150× realtime (warm) on ~7 s |
| Listening | Deferred to Supervisor QA on speakers bleed capture |

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `scripts/aec-spike.py:259-292` | When `--ref-delay-ms > 0`, delayed ref is written as `system_aligned` and used for both mixes — plain/AEC listen compares are skewed | fixed — delay only `aec_ref_pcm`; mixes use undelayed `mix_sys_pcm` |
| R2 | Low | `scripts/aec-spike.py:227-231` | `--ref-delay-ms` help says pad mic / trim ref; code pads ref; unused `delay_bytes` / `n` in `write_pcm16` | fixed — help text + unused locals removed |
| R3 | Low | `DEVELOPMENT.md:98` | Broken phrasing `and/\`native/build/AudioRecorder\`` | fixed — and/or native/build/AudioRecorder |

- Review loop number: 2
- Triage loop 1: auto-fix R1–R3 (Medium + first-loop cheap Lows); no human ask
- Fix pass 2026-07-28: R1–R3 applied; smoke `--ref-delay-ms 50` — `system_aligned` matches undelayed system prefix
- Triage loop 2: clean — no open High/Medium; Lows fixed; route supervisor-qa
- Next: `Use supervisor-qa.`

## Supervisor QA

### Plan (2026-07-28) — detailed PO checklist

**Slice under test:** `recording-mix-aec-spike` (offline tool only).  
**Not under test:** product Record mix already using AEC (later `recording-mix-aec`).

**What “pass” means for this slice**
- You can capture keep-raw dual-track audio on speakers, run `scripts/aec-spike.py`, and hear that Speex AEC **helps** remote bleed on fixture A without **destroying** your voice on fixture C.
- CPU cost of the spike looks cheap vs Whisper.
- Product Record still works as before (unchanged path).

**What you must NOT fail the slice for**
- Default Record still has double remote on speakers (expected — AEC not integrated yet).
- Bleed not 100% gone (Ideal is later).
- Headphones / UX polish follow-ups.

**Human result:** **Passed with follow-ups** (2026-07-29) — spike tool + CPU OK; Speex cancel **not** proven; PO product finding: **mic-only best for transcription**.

| Topic | Result |
| --- | --- |
| Keep-raw dual m4a A/B/C | Pass (`open --env SCRIBE_KEEP_RAW_RECORDING=1 ./dist/Scribe.app`) |
| Speex AEC(mic, ref=system) | **No help** — `mic` ≈ `mic_aec` ≈ `mic_aligned` on A/B/C; `mix_aec` ≈ `mix_plain` (double remains) |
| CPU | Pass (~144–164× realtime on ~26–32 s clips) |
| B user speech | Pass — not destroyed; system silent when remote silent |
| C overlap on mic | Pass for transcription ear-test — user audible ≈ remote on **mic**; mix still doubles and buries user |
| PO Ideal signal | **Mic track** (not amix, not Speex output) is currently best **on speakers**: one remote + balanced user; thinner lows acceptable for Whisper ≫ double in mix. **Headphones:** mic-only would lack remote (PO) — speakers-conditioned insight only |

Follow-ups: `PP-2026-07-29-001` (dual-path: speakers mic-only / headphones mic+system+level), `PP-2026-07-29-002` (Speex inadequate → WebRTC only if still AEC+mix). Updates `PP-004` / `PP-005` / `PP-006` context.

**What failed vs what we fixed into memory**
- **Failed (spike hypothesis):** prove Speex removes bleed so cleaned-mic+system mix beats plain mix.
- **Succeeded / fixed as product learning:** on speakers, raw **mic** already carries usable non-doubled meeting audio for P0 transcription; product amix is what recreates the double. Next Ideal planning must weigh **mic-only finalize** vs continued AEC+mix.

---

#### Part 0 — One-time setup (~5 min)

| Step | What you do | Success looks like |
| --- | --- | --- |
| 0.1 | In Terminal: `brew install speexdsp` | Install finishes without error |
| 0.2 | From repo root: `SCRIBE_KEEP_RAW_RECORDING=1 ./scripts/build.sh` | Builds `dist/Scribe.app` |
| 0.3 | `open dist/Scribe.app` | App opens |
| 0.4 | System Settings → Privacy: Mic + Screen & System Audio granted to **Scribe** (the dist app), then quit/reopen if you just granted Screen Recording | Record can start without permission errors |

Why dist app: TCC for Record often fails if you only unlocked `/Applications/Scribe.app` but run from Terminal/Cursor.

---

#### Part 1 — Capture three fixtures (speakers ON)

Use **laptop/external speakers**, not headphones. Open a call or play remote speech so system audio is real.

After each recording: **Stop**, then in Finder go to  
`~/Library/Caches/Scribe/recordings/`  
You need the **dual-track `.m4a`** kept because of `SCRIBE_KEEP_RAW_RECORDING=1` (name like `recording-YYYYMMDD-HHMMSS.m4a`).  
Do **not** only use the final mixed WAV for the spike — the spike needs both tracks inside the m4a.

| Fixture | How to speak | Length | Write down the .m4a filename |
| --- | --- | --- | --- |
| **A** | Remote talks; you stay silent | 20–40 s | |
| **B** | You talk; remote silent | 15–30 s | |
| **C** | Both talk / interrupt each other | 20–40 s | |

**Sanity before spike:** open the product WAV from the same session in QuickTime — you should still hear the familiar “double remote” on speakers for A (Phase 1 leftover). That is the bleed we want AEC to fight on the **mic** track.

---

#### Part 2 — Run the spike on fixture A

In Terminal, from the **repo root** (replace the path with your real A file):

```bash
mkdir -p /tmp/scribe-aec-spike-A
SCRIBE_AEC_SPIKE=1 python3 scripts/aec-spike.py \
  --input "$HOME/Library/Caches/Scribe/recordings/recording-….m4a" \
  --outdir /tmp/scribe-aec-spike-A
```

| Step | What you do | Success looks like |
| --- | --- | --- |
| 2.1 | Command finishes | No crash; prints `aec_wall_s=…` and `realtime_factor=…x` |
| 2.2 | Open folder `/tmp/scribe-aec-spike-A` | Files: `mic.wav`, `system.wav`, `mic_aec.wav`, `mix_plain.wav`, `mix_aec.wav` (and aligned copies) |
| 2.3 | Write the CPU line here | `aec_wall_s=____` `realtime_factor=____` |

**Listen order for A (important):**

1. Play **`mic.wav`** — this is “what the mic heard,” including remote from speakers (bleed). You should hear remote clearly on mic alone if bleed is real.
2. Play **`mic_aec.wav`** — same mic after AEC. Ask: is remote quieter / almost gone?
3. Play **`mix_plain.wav`** — old-style mix (mic + system). Often doubles remote.
4. Play **`mix_aec.wav`** — cleaned mic + system. Ask: closer to **one** remote?

| Question (A) | Your answer (fill in) |
| --- | --- |
| Is bleed audible on `mic.wav`? | yes / no / weak |
| Is `mic_aec` clearly better than `mic` for remote bleed? | yes / no / slightly |
| Is `mix_aec` better than `mix_plain`? | yes / no / slightly |
| Any “watery” / robotic artifacts that make A unusable? | yes / no |
| Verdict for A | help / no help / worse |

**If A barely changes:** retry with delay (room lag), same input, new outdir:

```bash
SCRIBE_AEC_SPIKE=1 python3 scripts/aec-spike.py \
  --input "$HOME/Library/Caches/Scribe/recordings/recording-….m4a" \
  --outdir /tmp/scribe-aec-spike-A-delay80 \
  --ref-delay-ms 80
```

Try 40, then 80, then 120 if needed. Note which (if any) helped.  
If **none** help but the tool runs: that is still a valid spike result → follow-up “try WebRTC AEC3”, not necessarily FAIL (tool + Speex choice still documented).

---

#### Part 3 — Fixture B (your voice only)

Same spike command with B’s m4a → `/tmp/scribe-aec-spike-B`.

| Question (B) | Your answer |
| --- | --- |
| Does `mic_aec` still sound like you (not hollow / chopped)? | yes / no |
| Verdict for B | OK / distorted |

---

#### Part 4 — Fixture C (overlap) — critical

Same with C → `/tmp/scribe-aec-spike-C`.

| Question (C) | Your answer |
| --- | --- |
| When you and remote overlap, is **your** voice still audible on `mic_aec` / `mix_aec`? | yes / muffled / gone |
| Would a transcript still catch your interruptions? (ear judgment OK) | yes / doubtful / no |
| Verdict for C | OK / damaged |

**Fail this slice** if C is ruined **and** A barely improved.  
**Pass with follow-ups** if A helps but C is “OK but fragile” — note it for integrate.

---

#### Part 5 — Small safety / regression (quick)

| Step | What you do | Pass if |
| --- | --- | --- |
| 5.1 | Run spike **without** `SCRIBE_AEC_SPIKE=1` | Script refuses and exits |
| 5.2 | In Scribe: Record → Stop **without** caring about spike | Product WAV still plays |
| 5.3 | Optional: Transcribe the **product** WAV from A (~short) | Transcript still usable (Phase 1 bar) |
| 5.4 | Optional: open `~/Library/Logs/Scribe/app.log` | Paths/status only — no pasted meeting text/audio |

---

#### Part 6 — How to score the iteration

| Outcome | When to choose |
| --- | --- |
| **pass** | Spike runs; A clearly helped (at delay 0 or after delay probe); C not destroyed; CPU looks cheap; Record still works |
| **pass with follow-ups** | Tool OK, but Speex weak → need WebRTC; or C marginal; or delay must be tuned — list follow-ups in chat |
| **fail** | Spike broken on valid dual m4a; **or** C destroyed while A not helped; **or** product Record broken |

Do **not** paste meeting audio into chat. Reply with filled answers for Parts 2–5 and one of: pass / pass with follow-ups / fail.

---

#### Out of scope (reminder)

AEC inside Record, ducking, mix polish, headphones-as-fix, perfect Ideal silence, committing fixtures.

## Verification

- [x] Spike script runs
- [x] SpeexDSP link via Homebrew
- [x] ai-cycle-validate
- [x] Listen A–C on speakers bleed fixture (Supervisor QA)
- [ ] Optional Whisper on A
- [x] CPU note confirmed (~150× realtime)

## Debt / Follow-ups

- Drives: `PP-2026-07-28-004`, `PP-2026-07-28-005`
- Related: `PP-006`, `PP-007`
- New from this QA: `PP-2026-07-29-001` (dual-path Ideal: speakers mic-only / headphones mix+level), `PP-2026-07-29-002` (Speex no-cancel)
- Next product slice (not this commit): `recording-mix-dual-path` per initiative Phase 3′

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Review loops | 2 | observed | ledger / current-cycle |
| Human decisions | 5 | observed | Phase 3; Option A; QA pass w/ follow-ups; dual-path Ideal; commit |
| High / Medium / Low findings | 0 / 1 / 2 (all fixed) | observed | review-findings.json |
| QA outcome | passed (with follow-ups) | observed | ledger |
| Outcome | shipped | observed | commit `102bac4` + this retrospective |

## Retrospective

# Iteration Retrospective — Recording Mix AEC Spike (Phase 3 offline)

## Outcome

- **Status:** shipped
- **Commit:** `102bac4811169ce41f4c98e29267ab2155df8693` (`102bac4`)
- **QA:** passed (with follow-ups)

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | ~same calendar day evening → next midnight (2026-07-28 → 07-29) | estimated | chat + commit timestamp |
| Agent turns | ~20 skill/step turns | estimated | implement → review → triage → fix → re-review → triage → QA plan → keep-raw/TCC → listen → Ideal docs → commit → retrospective |
| Approx token use | not measured | estimated | no tooling report |
| Review loops | 2 | observed | ledger / current-cycle |
| High findings | 0 | observed | review-findings.json |
| Medium findings | 1 | observed | review-findings.json (R1 fixed) |
| Low findings | 2 | observed | review-findings.json (R2–R3 fixed) |
| Human decisions | 5 | observed | Phase 3; Option A; QA verdict; dual-path Ideal; commit |
| QA outcome | passed (with follow-ups) | observed | ledger |
| Outcome | shipped | observed | commit `102bac4` + this retrospective |

## Rework Analysis

- **What caused rework:** Review loop 1 Medium R1 (`--ref-delay-ms` contaminated mix compares) + Lows (help text, DEVELOPMENT typo). QA friction: first spike attempt used product `.wav` (one stream) instead of keep-raw dual `.m4a`; direct `Contents/MacOS/Scribe` broke TCC Settings; needed `open --env SCRIBE_KEEP_RAW_RECORDING=1`.
- **What avoided rework:** Scope kept AEC out of product Record; auto-fix R1–R3 without ask; pass-with-follow-ups when Speex failed Ideal hypothesis but tool/CPU succeeded; PO dual-path Ideal captured in initiative + PP-* instead of forcing Speex integrate.
- **Human routine effort:** High for audio listen matrix A/B/C + permissions/keep-raw unblock; routine for commit approval. More product judgment than CSS slices (Ideal reframe).

## Repeated Failure Analysis

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| Dev Record TCC / wrong launch identity | Contents/MacOS binary → Settings won’t open; fixed via `open --env` on `.app` | yes (echoes sync-slice TCC lesson) | docs already updated; keep `open --env` in DEVELOPMENT/TESTING |
| QA plan assumed wrong input artifact | PO passed `.wav` to `--input`; dual `.m4a` required | new / likely for keep-raw tools | supervisor-qa: first step = “green light” file type + stream count before listen |
| Phase/Ideal wording vs spike library proof | Speex no-cancel ≠ slice fail; Ideal moved to dual-path | related to sync-slice Phase vs Ideal | supervisor-qa: separate “tool/CPU exit” vs “library proves Ideal” rows |
| Auto-fix Medium/Low without ask | R1–R3 | yes (desired) | none |

## Process Recommendations

1. For offline tooling QA that needs keep-raw dual-track: Supervisor QA plans must start with a **file gate** (`.m4a` + ≥2 audio streams) and the **working keep-raw launch** (`open --env SCRIBE_KEEP_RAW_RECORDING=1 ./dist/Scribe.app`) — not `Contents/MacOS/*` and not product `.wav`.
2. For library spikes: label QA criteria as **spike exit** (tool runs, CPU, no product regression) vs **Ideal proof** (library achieves product outcome) so a negative library result can still be pass-with-follow-ups without PO confusion.

## Debt / Planned Work Updates

- **Debt register:** no new Open Debt
- **Planned process work:** unchanged (recommendations above are operational; already partially in DEVELOPMENT/TESTING)
- **Product follow-ups captured:** yes — `PP-2026-07-29-001` (dual-path Ideal), `PP-2026-07-29-002` (Speex no-cancel); `PP-004`…`007` updated toward dual-path

## Next Planning Input

Use `product-analyst` (then `roadmap-planner`). **Primary:** `recording-mix-dual-path` (Phase 3′ — no headphones → mic-only; headphones → mic+system with mic level match; detection + fallbacks). **Deprioritize:** Speex/AEC integrate unless PO reopens backup Ideal. Secondary: UX `PP-001`…`003`.

## State Updates

- Ledger: retrospective completed; status shipped; metrics finalized
- Current cycle: `phase=shipped`, `retrospective=done`, `handoff.next_role=none`, commit hash retained
- Structured review-findings.json: metrics aligned (0/1/2 all fixed)
- Debt register: unchanged

