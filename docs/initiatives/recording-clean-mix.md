# Initiative: Clean meeting mix (no double remote)

**Status:** active — next work = Phase 0 diagnostics + Phase 1 sync  
**Opened:** 2026-07-28  
**Owner roles:** product-analyst / roadmap-planner (slice scope) → feature-manager / implementer → human Supervisor QA  
**Related:** [recording-to-transcript](../scenarios/recording-to-transcript.md), `native/AudioRecorder.swift`, `backend/recorder.py`  
**Not:** general [ROADMAP.md](../../ROADMAP.md) polish; headphones-as-product-fix; paid AEC SDKs

---

## Problem

In-app Record captures **system audio** (ScreenCaptureKit) and **microphone**, then ffmpeg `amix`es both tracks into one WAV.

Observed:

- **User’s own voice is not duplicated** → mic path for near-end is fine.
- **Remote / system sound is duplicated** with a **variable** delay (short echo … multi-second lag) → the same program audio is present **digitally on the system track** and **acoustically on the mic** (speakers), and track timelines are often **misaligned**.

Code for the dual-track path has been effectively unchanged since early tags (`v1.1.0`+). “It used to be fine” is more likely **OS / usage / speakers vs headphones** than a Scribe regression between those versions. Dual mic via `captureMicrophone` is **macOS 15+** only.

Broken mix → Whisper hears doubled / shifted remote speech → **incomplete or corrupted transcripts**.

---

## Ideal (definition of done)

On **speakers** (worst case) and headphones (regression):

1. **P0 — Transcript integrity:** mixed audio must not double or time-shift remote speech enough to break Whisper. Transcript is complete and usable for the spoken meeting.
2. **P1 — Listening quality:** mix is user-friendly — no obvious distortion, pumping, watery artifacts, or cut beginnings/ends of phrases. Overlapping speech (interruptions that continue) remains audible for **both** sides.
3. **P2 — CPU:** processing must stay light on Apple Silicon (post-stop mix path and any realtime path). Prefer offline-on-stop over heavy realtime. No paid/licensed AEC packages.

Non-goals for this initiative:

- Telling users “just use headphones” as the fix
- Cloud / third-party audio APIs
- Perfect studio mastering, diarization, or noise UX beyond what’s needed for (1)–(2)

---

## Constraints

| Constraint | Rule |
| --- | --- |
| Money | No paid SDKs / licensed AEC. Open-source (e.g. WebRTC AEC3, SpeexDSP) and Apple platform APIs OK if they fit the architecture. |
| Architecture | Scribe does **not** play meeting audio (Zoom/Meet does). Apple **VoiceProcessingIO** alone is a weak bet: it expects the app to render far-end. Prefer **AEC(mic, reference = system track)**. |
| Privacy | Never log transcript/summary or raw meeting audio content; paths/durations/metrics only. |
| Process | Each phase ships as a **bounded iteration** with human scope approval. Update this file’s status when a phase completes. |

---

## Success / QA matrix (target)

| # | Setup | Expect |
| --- | --- | --- |
| A | Speakers; remote talks; user silent | One clean remote; no delayed second copy |
| B | Speakers; user talks; remote silent | One clean user; normal level |
| C | Speakers; overlap / interruptions | Both audible; no dropped “important” tails; no multi-second echo |
| D | Headphones (regression) | No worse than today; no new artifacts |
| E | Transcribe A–C | Transcript complete; no doubled garbled remote |

CPU smoke: stop→mix on a ~30–60 min recording should not feel like a second “ML job”; note wall time in the iteration ledger (no meeting audio in logs).

---

## Phased plan

Work **in order**. Do not skip Phase 1. Do not promote Phase 2 to product default if Ideal is still the goal. Re-run the QA matrix after each phase.

### Phase 0 — Diagnostics (baseline)

**Goal:** Prove content vs timeline on real captures.

**Work:**

- Keep / export pre-mix `.m4a` for failing sessions (dev-friendly; don’t leave secrets in shared places).
- Split tracks: `ffprobe` + `ffmpeg -map 0:a:0` / `0:a:1`.
- Record A/B/C/D once; note Δ between tracks and whether remote appears on mic.

**Cures:** Confusion about root cause.  
**Tradeoffs:** Manual time.  
**Breaks:** Nothing in product.  
**Exit:** Written notes in this file or the first iteration ledger: “remote on both tracks?”, “Δ range?”.

**Status:** pending

---

### Phase 1 — Track sync (Swift)

**Goal:** One shared timeline for mic + system; stop multi-second desync.

**Work (intent):**

- Do not start the writer session only from the first **system** sample while **dropping** earlier mic buffers.
- Align `startSession` / PTS policy so both inputs share a coherent clock.
- Avoid silent drop-on-`!isReadyForMoreMediaData` without a strategy (queue, or count drops for diagnostics).

**Cures:** Variable multi-second lag between identical remote content on the two tracks.  
**Tradeoffs:** Alone, **does not** remove acoustic double remote (short room echo may remain).  
**Breaks risk:** Low–medium if PTS handling is wrong (start gaps, rejected samples). Mitigate with A/D matrix + keep raw `.m4a` for compare.  
**Exit:** On speakers, any remaining double is **short** (room-like), not seconds. Transcript no longer destroyed by huge delay.  
**CPU:** Negligible.

**Status:** pending — **next implementation slice after Phase 0 notes (or combined 0+1)**

---

### Phase 2 — Sidechain duck (ffmpeg) — experiment only

**Goal:** Measure a cheap content band-aid after sync.

**Work:** Before `amix`, duck mic when system energy is high (`sidechaincompress` or equivalent).

**Cures:** Much of remote bleed when tracks are aligned and speech rarely overlaps.  
**Tradeoffs:** Pumping; **overlapping speech** may attenuate the user; quiet remote may not duck.  
**Breaks risk:** High for P1 Ideal (interruptions).  
**Product rule:** **Not** the default path to Ideal. Optional A/B only; ship only if PO explicitly accepts “good enough” and Ideal is deferred.  
**CPU:** Very low (ffmpeg filters on stop).

**Status:** deferred as product default; optional spike after Phase 1

---

### Phase 3 — AEC with system track as reference (Ideal path)

**Goal:** Remove speaker bleed from mic using digital system audio as reference; then mix cleaned mic + system.

```text
system ──► reference ──┐
mic ───────────────────┴─► AEC ──► cleaned mic ──┐
system (program) ───────────────────────────────┴─► amix → WAV
```

**Work:**

1. Offline prototype on saved `mic.wav` + `sys.wav` (WebRTC AEC3 or SpeexDSP — pick one after spike).
2. Stabilize delay assumption **after** Phase 1 sync.
3. Integrate into stop/finalize path (native helper or local library; bundleable in dist; no network).
4. Keep a safe fallback: if AEC fails, behave like Phase 1 mix (never delete the only copy of audio).

**Cures:** Double remote on speakers while keeping user + remote for transcription and listening.  
**Tradeoffs:** Integration/tuning time; must validate overlap (C).  
**Breaks risk:** Bad delay → watery mic or chewed user speech; running AEC on the wrong signal → damaged remote. Mitigate with offline fixtures + matrix + fallback.  
**VPIO:** Optional micro-spike only; do not bet Ideal on it without evidence it cancels **other apps’** playback.  
**CPU:** Prefer **on stop** over realtime; target modest arm64 cost (document measured time). Reject approaches that rival Whisper runtime for a 1-hour meeting.

**Status:** pending (blocked on Phase 1 exit)

---

### Phase 4 — Mix polish

**Goal:** P1 listening quality without harming P0.

**Work (only after Phase 3 passes A–E):** light level match between cleaned mic and system; avoid aggressive gates/EQ.

**Cures:** Uneven loudness, harshness.  
**Tradeoffs / breaks:** Over-gating cuts phrase onsets; over-normalization pumps.  
**CPU:** Low.

**Status:** pending

---

### Phase 5 — Docs & scenario lock-in

**Goal:** Make the Ideal behavior durable for agents and QA.

**Work:** Update [recording-to-transcript](../scenarios/recording-to-transcript.md), [TESTING.md](../../TESTING.md) § recording, [ARCHITECTURE.md](../../ARCHITECTURE.md) / [DECISIONS.md](../../DECISIONS.md) if the mix pipeline changes; close related product follow-up.

**Status:** pending

---

## Priority rules (when tradeoffs appear)

1. **Never** ship a change that improves “sounds nicer in quiet remote-only” but **drops or muffles** overlapping user speech enough to lose transcript content (P0 > P1).
2. Prefer **fallback to synced plain mix** over a failing AEC that corrupts the only WAV.
3. Prefer **post-stop** processing over realtime CPU load unless realtime is proven cheap and necessary.
4. Headphones tip may appear as optional help copy later; it is **not** a phase exit criterion.

---

## Suggested iteration slicing

| Slice | Scope | Gate |
| --- | --- | --- |
| `recording-mix-sync` | Phase 0 notes + Phase 1 Swift sync (+ keep/split raw for QA) | Matrix A–D: no multi-second double |
| `recording-mix-aec-spike` | Phase 3 offline prototype only (no product default) | A–C on fixtures; CPU note |
| `recording-mix-aec` | Phase 3 integrated + fallback | Full matrix A–E + CPU |
| `recording-mix-polish` | Phase 4 + Phase 5 docs | Listening + scenario |

Phase 2 duck spike only if PO asks for a temporary mitigation before AEC.

---

## Current decision log

| Date | Decision |
| --- | --- |
| 2026-07-28 | Root cause framed as system-on-both-tracks + timeline skew; own voice not doubled. |
| 2026-07-28 | Ideal = clean dual source for transcript + listening; no paid AEC; no headphones-as-fix. |
| 2026-07-28 | Ordered path: diagnostics → sync → (duck optional) → reference AEC → polish. VPIO not primary. |
| 2026-07-28 | P0 transcript integrity over P1 beauty; light CPU; preserve overlaps. |

---

## Pointers elsewhere

- Discoverability wish: `PP-2026-07-28-004` in [`.ai/state/product-followups.md`](../../.ai/state/product-followups.md)
- One-line ROADMAP pointer under **Audio & transcription quality**
- Per-slice history: [docs/iterations/](../iterations/)
