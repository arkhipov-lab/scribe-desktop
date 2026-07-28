# Initiative: Clean meeting mix (no double remote)

**Status:** **closed** — Ideal P0 met via dual-path finalize (`c13dd58`, 2026-07-29)  
**Opened:** 2026-07-28  
**Closed:** 2026-07-29  
**Owner roles:** product-analyst / roadmap-planner (slice scope) → feature-manager / implementer → human Supervisor QA  
**Related:** [recording-to-transcript](../scenarios/recording-to-transcript.md), `backend/output_route.py`, `backend/recorder.py`, `native/AudioRecorder.swift`  
**Not:** general [ROADMAP.md](../../ROADMAP.md) polish; “just use headphones” as the only fix; paid AEC SDKs

---

## Exit summary

| Item | Result |
| --- | --- |
| **P0 transcript integrity** | **Met** — speakers mic-only avoids digital+acoustic double; headphones keep remote via leveled amix. QA 4 modes pass (speakers; BT; aux; mid-record speakers→BT). |
| **P1 listening polish** | **Out of initiative** — optional later wishes (`PP-2026-07-28-006`, UI I/O `PP-2026-07-29-003` / headset mic `PP-2026-07-29-004`). Not required to close. |
| **P2 CPU** | **Met** — route check + capped 30s level-match; no paid AEC. |
| **AEC path** | Spike done; Speex not product default (`PP-2026-07-29-002`). Integrate only if PO reopens. |

**Shipped slices:** `recording-mix-sync` → `recording-mix-aec-spike` → `recording-mix-dual-path`.

---

## Problem (historical)

In-app Record captures **system audio** (ScreenCaptureKit) and **microphone**. Historically ffmpeg always `amix`ed both into one WAV (which doubles remote on speakers).

Observed:

- **User’s own voice is not duplicated** → mic path for near-end is fine.
- **Remote / system sound is duplicated** with a **variable** delay → program audio on the **system track** and **acoustically on the mic** (speakers), plus former track **misalignment** (Phase 1 fixed multi-second skew).

Broken mix → Whisper hears doubled / shifted remote → **incomplete or corrupted transcripts**.

---

## Ideal (definition of done) — achieved path

On **speakers** and **headphones**:

1. **P0 — Transcript integrity:** finalize must not double/time-shift remote enough to break Whisper.  
2. **P1 — Listening quality:** user-friendly (optional polish after close).  
3. **P2 — CPU:** light post-stop path; no paid AEC.

### Shipped Ideal — dual-path finalize

```text
headphones NOT connected (speakers / open air)
  → finalize WAV = mic only
     (remote via acoustic bleed; no digital double)

headphones connected
  → finalize WAV = amix( level_match(mic), system )
     (remote from system; mic amplitude toward remote)

unknown route (USB/HDMI/AirPlay/…)
  → headphones-style mix (never drop remote)
```

Detection: Core Audio default-output transport + data source (`backend/output_route.py`).

### Deferred / backup (not required to keep initiative open)

- **AEC then mix:** Speex spike failed cancel; WebRTC AEC3 only if PO reopens (`PP-2026-07-29-002`).
- **Sidechain duck (Phase 2):** not product default.
- **Mix polish / UI device display:** product follow-ups, not this campaign.

Non-goals (unchanged): headphones tip as only fix; cloud audio APIs; studio mastering / diarization.

---

## Constraints

| Constraint | Rule |
| --- | --- |
| Money | No paid SDKs / licensed AEC. |
| Architecture | Dual-path finalize is the shipped Ideal. AEC(mic, ref=system) remains backup only. |
| Privacy | Never log transcript/summary or raw meeting audio content. |
| Process | Phases shipped as bounded iterations with human approval. |

---

## Success / QA matrix — final

| # | Setup | Result (2026-07-29) |
| --- | --- | --- |
| A–C | Speakers modes | **Pass** (mic-only path) |
| D | Headphones BT + aux | **Pass** (level-match amix) |
| E | Transcribe / usable | **Pass** as exercised |
| Extra | Speakers → mid-record BT headphones | **Pass** (route at stop) |

---

## Phased plan (final statuses)

### Phase 0 — Diagnostics — **done**
Ledger `2026-07-28-recording-mix-sync`.

### Phase 1 — Track sync (Swift) — **done**
QA 2026-07-28: multi-second skew fixed; bleed remained until Phase 3′.

### Phase 2 — Sidechain duck — **deferred** (not needed for close)

### Phase 3 — AEC spike — **done** (Speex not for default)

### Phase 3′ — Dual-path finalize — **done**
Shipped `c13dd58` (`recording-mix-dual-path`).

### Phase 4 — Mix polish — **cancelled for this initiative**
Optional later via product follow-ups if PO prioritizes P1 listening.

### Phase 5 — Docs & scenario lock-in — **done**
Scenario / TESTING § E / ARCHITECTURE / LOCAL_DATA updated with dual-path; Ideal PPs closed.

---

## Priority rules (retained for agents)

1. P0 transcript > P1 listening.  
2. Safe finalize fallback over deleting the only WAV.  
3. Prefer post-stop processing.  
4. Headphones tip is not Ideal exit.  
5. Prefer dual-path over AEC unless PO reopens AEC+mix.

---

## Suggested iteration slicing (archive)

| Slice | Gate | Outcome |
| --- | --- | --- |
| `recording-mix-sync` | No multi-second double | **shipped** |
| `recording-mix-aec-spike` | Speex listen + CPU | **shipped**; Speex not default |
| `recording-mix-dual-path` | Matrix A–E | **shipped** `c13dd58` |
| `recording-mix-aec` | Only if PO reopens | not planned |
| `recording-mix-polish` | Listening polish | **not in this initiative** — use follow-ups |

---

## Current decision log

| Date | Decision |
| --- | --- |
| 2026-07-28 | Root cause: system-on-both-tracks + timeline skew; own voice not doubled. |
| 2026-07-28 | Ideal = clean dual source; no paid AEC; no headphones-as-fix. |
| 2026-07-28 | Path: diagnostics → sync → (duck optional) → AEC spike → polish. |
| 2026-07-28 | Phase 3 offline Speex spike; Phase 2 duck not default. |
| 2026-07-29 | Speex cancel not proven. Ideal → **dual-path**. |
| 2026-07-29 | Option A `recording-mix-dual-path` approved and **shipped** (`c13dd58`). |
| 2026-07-29 | **Initiative closed** — P0 Ideal met. Phase 4 polish cancelled here; leftover wishes stay in product-followups (`PP-2026-07-29-003`/`004`, optional `PP-006`). |

---

## Pointers elsewhere

- Closed Ideal rows: `PP-2026-07-28-004`, `PP-2026-07-29-001`, `PP-2026-07-28-005`, `PP-2026-07-28-007` in [product-followups.md](../../.ai/state/product-followups.md)
- Speex note (open): `PP-2026-07-29-002`
- Post-close UX: `PP-2026-07-29-003`, `PP-2026-07-29-004`
- ROADMAP: Clean meeting mix marked done
- Per-slice history: [docs/iterations/](../iterations/)
