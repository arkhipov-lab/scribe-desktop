# Initiative: Clean meeting mix (no double remote)

**Status:** active — Phase 3′ dual-path **QA passed** (`recording-mix-dual-path`, 2026-07-29); pending commit; Phase 3 AEC spike done; Phase 0+1 done
**Opened:** 2026-07-28  
**Owner roles:** product-analyst / roadmap-planner (slice scope) → feature-manager / implementer → human Supervisor QA  
**Related:** [recording-to-transcript](../scenarios/recording-to-transcript.md), `native/AudioRecorder.swift`, `backend/recorder.py`  
**Not:** general [ROADMAP.md](../../ROADMAP.md) polish; “just use headphones” as the only fix; paid AEC SDKs

---

## Problem

In-app Record captures **system audio** (ScreenCaptureKit) and **microphone**. Historically ffmpeg always `amix`ed both into one WAV (which doubles remote on speakers). Product finalize is now **dual-path** (mic-only vs leveled amix by output route) — see Phase 3′.

Observed:

- **User’s own voice is not duplicated** → mic path for near-end is fine.
- **Remote / system sound is duplicated** with a **variable** delay (short echo … multi-second lag) → the same program audio is present **digitally on the system track** and **acoustically on the mic** (speakers), and track timelines were often **misaligned** (Phase 1 reduced multi-second skew).

Code for the dual-track path has been effectively unchanged since early tags (`v1.1.0`+). “It used to be fine” is more likely **OS / usage / speakers vs headphones** than a Scribe regression between those versions. Dual mic via `captureMicrophone` is **macOS 15+** only.

Broken mix → Whisper hears doubled / shifted remote speech → **incomplete or corrupted transcripts**.

---

## Ideal (definition of done)

On **speakers** (worst case) and **headphones** (must not regress):

1. **P0 — Transcript integrity:** finalize audio must not double or time-shift remote speech enough to break Whisper. Transcript is complete and usable for the spoken meeting.
2. **P1 — Listening quality:** result is user-friendly — no obvious distortion, pumping, watery artifacts, or cut beginnings/ends of phrases. Overlapping speech remains audible for **both** sides when both are present in the chosen path.
3. **P2 — CPU:** processing must stay light on Apple Silicon (post-stop path). Prefer offline-on-stop. No paid/licensed AEC packages.

### Current Ideal direction (PO, 2026-07-29) — dual-path finalize

Evidence from offline AEC spike QA (`recording-mix-aec-spike`): on **speakers**, the **mic track alone** already has one remote + user at usable levels for Whisper; `amix(mic, system)` recreates the double. Speex `AEC(mic, ref=system)` did **not** cancel bleed. On **headphones**, mic-only would **miss** remote (no speaker bleed).

```text
headphones NOT connected (speakers / open air)
  → finalize WAV = mic only
     (remote arrives via acoustic bleed; no digital double)

headphones connected
  → finalize WAV = amix( level_match(mic), system )
     (remote from system; boost mic toward remote amplitude)
```

**Ship gate:** Supervisor QA matrix A–E (speakers + headphones) on `recording-mix-dual-path`. Detection: Core Audio default-output transport + data source (`backend/output_route.py`); unknown → mix.

### Deferred / backup Ideal paths

- **AEC then mix** (original Phase 3): Speex offline spike **failed** cancel; WebRTC AEC3 only if dual-path is rejected or needs a speakers fallback that keeps full-band system.
- **Sidechain duck (Phase 2):** still not product default.
- **Headphones-as-fix tip:** optional copy later; **not** the product fix (detection + dual-path is the fix).

Non-goals for this initiative:

- Telling users “just use headphones” as the only fix
- Cloud / third-party audio APIs
- Perfect studio mastering, diarization, or noise UX beyond what’s needed for (1)–(2)

---

## Constraints

| Constraint | Rule |
| --- | --- |
| Money | No paid SDKs / licensed AEC. Open-source (e.g. WebRTC AEC3, SpeexDSP) and Apple platform APIs OK if they fit the architecture. |
| Architecture | Scribe does **not** play meeting audio (Zoom/Meet does). Prefer **dual-path finalize** after 2026-07-29 QA. Apple **VoiceProcessingIO** alone remains a weak bet. AEC(mic, ref=system) is **backup**, not the primary Ideal bet after Speex spike. |
| Privacy | Never log transcript/summary or raw meeting audio content; paths/durations/metrics only. |
| Process | Each phase ships as a **bounded iteration** with human scope approval. Update this file’s status when a phase completes. |

---

## Success / QA matrix (target)

| # | Setup | Expect |
| --- | --- | --- |
| A | Speakers; remote talks; user silent | One clean remote; no delayed second copy |
| B | Speakers; user talks; remote silent | One clean user; normal level |
| C | Speakers; overlap / interruptions | Both audible; no dropped “important” tails; no multi-second echo |
| D | Headphones (regression) | Remote present (via system); user audible; no new double; mic not buried |
| E | Transcribe A–C (and D if changed) | Transcript complete; no doubled garbled remote |

CPU smoke: stop→finalize on a ~30–60 min recording should not feel like a second “ML job”; note wall time in the iteration ledger (no meeting audio in logs).

---

## Phased plan

Work **in order** for Phases 0–1 (done). After 2026-07-29, **prefer Phase 3′ dual-path** over shipping Speex/WebRTC AEC as default. Re-run the QA matrix after each phase.

### Phase 0 — Diagnostics (baseline)

**Status:** done — notes in ledger `2026-07-28-recording-mix-sync` (QA 2026-07-28): speakers still have remote on mic (bleed); Δ consistent / length-independent; transcript OK

---

### Phase 1 — Track sync (Swift)

**Status:** done — QA 2026-07-28: remaining double is fixed-delay (not growing with duration); Whisper usable; acoustic bleed remains

---

### Phase 2 — Sidechain duck (ffmpeg) — experiment only

**Status:** deferred as product default; optional only if PO asks; **superseded in priority by dual-path**

---

### Phase 3 — AEC with system track as reference (spike / backup)

**Goal (original):** Remove speaker bleed from mic using digital system as reference; then mix cleaned mic + system.

**Spike result (2026-07-29):** offline SpeexDSP (`scripts/aec-spike.py`) — tool/CPU OK (~150× RT); **no audible cancel** on correct `AEC(mic, ref=system)` (`mic≈mic_aec`; `mix_aec≈mix_plain`). Library choice for AEC+mix: **do not** prefer Speex; WebRTC AEC3 only if Ideal returns to AEC+mix.

**Status:** spike **done** (pass w/ follow-ups). **Integrate Speex as product default: no.** Keep tool for experiments. AEC integrate slice **deprioritized** vs Phase 3′.

---

### Phase 3′ — Dual-path finalize (current Ideal path)

**Goal:** Ship PO dual-path so speakers avoid digital+acoustic double without requiring AEC; headphones keep system remote + leveled mic.

**Work:**

1. Detect headphones / private output vs speakers (macOS Core Audio / route — spike reliability; BT AirPods, USB-C, jack, HDMI-TV edge cases).
2. On stop/finalize:
   - **No headphones →** write product WAV from **mic track only** (still capture dual-track raw if useful for QA; don’t amix for product file).
   - **Headphones →** `amix` after **level-matching mic toward system** (amplitude toward remote; avoid burying user — see `PP-006` / `PP-007`).
3. Fallback if detection unknown: prefer path that **does not drop remote** (document explicitly in slice — likely headphones-style mix or prompt); never delete the only audio copy.
4. Matrix A–E + CPU; update scenario/TESTING when behavior ships.

**Cures:** Speakers double from amix; headphones missing-remote if mic-only were universal.  
**Tradeoffs:** Detection errors; mic-only on speakers has thinner remote band (PO: OK for Whisper).  
**Breaks risk:** False “no headphones” → mic-only with no bleed → lost remote; false “headphones” on speakers → double returns. Mitigate with detection spike + conservative fallback.  
**CPU:** Very low (route check + optional level match + amix).  
**Exit:** Matrix A–E pass; detection notes in ledger.

**Status:** **QA passed** — slice `recording-mix-dual-path` (2026-07-29); close Ideal / PP-001 on commit. Follow-up: `PP-2026-07-29-001`.

---

### Phase 4 — Mix polish

**Goal:** P1 listening quality without harming P0 (especially headphones mic level — `PP-007`; overlap — `PP-006`).

**Work:** After Phase 3′ (or AEC if revived): refine level match; avoid aggressive gates/EQ.

**Status:** pending (partially overlaps headphones branch of 3′)

---

### Phase 5 — Docs & scenario lock-in

**Goal:** Make Ideal behavior durable for agents and QA.

**Work:** Update [recording-to-transcript](../scenarios/recording-to-transcript.md), [TESTING.md](../../TESTING.md) § recording, [ARCHITECTURE.md](../../ARCHITECTURE.md) / [DECISIONS.md](../../DECISIONS.md) when finalize path ships; close `PP-2026-07-28-004` when Ideal exit met.

**Status:** **partial** — scenario / TESTING § E / ARCHITECTURE updated with dual-path; close when QA passes and Ideal exit met (`PP-004` / `PP-001`)

---

## Priority rules (when tradeoffs appear)

1. **Never** ship a change that improves “sounds nicer in quiet remote-only” but **drops or muffles** overlapping user speech enough to lose transcript content (P0 > P1).
2. Prefer a **safe finalize fallback** over a path that can delete or corrupt the only WAV.
3. Prefer **post-stop** processing over realtime CPU load unless realtime is proven cheap and necessary.
4. **Do not** treat “tell user to wear headphones” as Ideal exit; headphone **detection** for dual-path is in-scope engineering.
5. Prefer **dual-path (3′)** over AEC integrate unless PO reopens AEC+mix after WebRTC evidence.

---

## Suggested iteration slicing

| Slice | Scope | Gate |
| --- | --- | --- |
| `recording-mix-sync` | Phase 0 notes + Phase 1 Swift sync (+ keep/split raw for QA) | Matrix A–D: no multi-second double — **shipped** |
| `recording-mix-aec-spike` | Phase 3 offline Speex prototype only | A–C listen + CPU — **QA pass w/ follow-ups**; Speex not for default |
| `recording-mix-dual-path` | Phase 3′ detection + mic-only / headphones mix+level | Full matrix A–E + detection edge notes |
| `recording-mix-aec` | Phase 3 AEC integrate (backup Ideal only) | Only if PO rejects dual-path or needs AEC fallback |
| `recording-mix-polish` | Phase 4 + Phase 5 docs | Listening + scenario |

Phase 2 duck spike only if PO asks.

---

## Current decision log

| Date | Decision |
| --- | --- |
| 2026-07-28 | Root cause framed as system-on-both-tracks + timeline skew; own voice not doubled. |
| 2026-07-28 | Ideal = clean dual source for transcript + listening; no paid AEC; no headphones-as-fix. |
| 2026-07-28 | Ordered path: diagnostics → sync → (duck optional) → reference AEC → polish. VPIO not primary. |
| 2026-07-28 | Phase 3 starts with offline AEC spike (`recording-mix-aec-spike`); integrate is a later slice. Phase 2 duck still not product default. |
| 2026-07-28 | Spike tool: `scripts/aec-spike.py` + Homebrew SpeexDSP (ctypes). CPU ~150× realtime (arm64). |
| 2026-07-29 | Speex cancel **not** proven on speakers fixtures. **Ideal direction changed:** dual-path finalize — no headphones → **mic-only**; headphones → **mic+system with mic level matched to remote**. AEC integrate deprioritized (`PP-2026-07-29-001`, `002`). Next slice: `recording-mix-dual-path`. |
| 2026-07-29 | PO approved product-analyst + roadmap **Option A** — start iteration `recording-mix-dual-path` (Phase 3′). |
| 2026-07-29 | Dual-path **QA passed** (speakers; BT headphones; aux headphones; mid-record speakers→BT). Follow-ups: UI show I/O devices (`PP-2026-07-29-003`); headset-mic default question (`PP-2026-07-29-004`). |

---

## Pointers elsewhere

- Umbrella bug: `PP-2026-07-28-004` in [`.ai/state/product-followups.md`](../../.ai/state/product-followups.md)
- Dual-path Ideal: `PP-2026-07-29-001`; Speex result: `PP-2026-07-29-002`
- Speakers bleed after sync: `PP-2026-07-28-005`; overlap level: `PP-006`; headphones mic quiet: `PP-007`
- One-line ROADMAP pointer under **Audio & transcription quality**
- Per-slice history: [docs/iterations/](../iterations/)
