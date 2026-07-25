# AI Pipeline

How Scribe turns selected or recorded audio into a transcript and meeting notes — fully on-device.

> Authoritative layer boundaries: [ARCHITECTURE.md](ARCHITECTURE.md). Privacy and network rules: [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).

---

## Pipeline Overview

```
File select / drop  —or—  Record (mic + system audio)
        │
        ▼
┌───────────────────┐
│ 1. Path / ext     │  ← validate media; clear prior results as designed
│    validation     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 2. ffmpeg         │  ← locate; convert / mix as needed → processable audio
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 3. Whisper model  │  ← id from settings + backend/model_catalog.py
│    selection      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 4. MLX Whisper    │  ← status callbacks; cooperative cancel
│    transcription  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 5. Release ML     │  ← unload / clear MLX cache between stages
│    memory         │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 6. Summary opts   │  ← preset, language, length, additional instructions
└────────┬──────────┘
         │ auto-summary on  —or—  user Generate
         ▼
┌───────────────────┐
│ 7a. Short text    │  ← single-pass mlx-lm summary
│ 7b. Long text     │  ← chunk → map → reduce (map-reduce)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 8. Local outputs  │  ← UI state, history session, export, playback
└───────────────────┘
```

Heavy work runs on **background threads**. The React UI polls `get_state` — it must not block the pywebview main thread with ML.

---

## Step Details

### 1. Ingest — file or recording

**File:** `select_file` / `set_file_path` (native drop). Extensions: `.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`. Unsupported paths fail clearly (see [docs/scenarios/unsupported-file.md](docs/scenarios/unsupported-file.md)).

**Record:** `start_recording` / `stop_recording` → Swift `AudioRecorder` (ScreenCaptureKit + mic) → ffmpeg mix → WAV under `~/Library/Caches/Scribe/recordings/`. Temp recordings owned by the app are cleaned up when the user picks another file.

### 2. ffmpeg

Locate bundled `bin/ffmpeg` (dist), then `PATH`, then Homebrew (`/opt/homebrew/bin/ffmpeg` for local/dev). Used for format conversion and recording mix/normalize. Missing ffmpeg must surface a clear user-facing error in local/dev.

### 3. Whisper model selection

Runtime choices and HF ids live in `backend/model_catalog.py`. First-launch defaults come from `backend/hardware.py`. The UI lists options from the bridge (`get_whisper_models`) — it does **not** hard-code model ids or token caps.

### 4. MLX Whisper transcription

`backend/transcriber.py` runs mlx-whisper. Status callbacks (e.g. `loading_model`, `transcribing`) update shared state. Cancel is cooperative (`cancel_transcription`).

### 5. ML memory release

After transcription (and between stages as designed), `backend/memory.py` unloads models / clears MLX Metal caches so smaller Macs can load the summary model.

### 6. Summary controls

Preset, length, additional instructions, auto-summary, and summary model come from settings + catalog (`get_summary_presets`, `get_summary_models`, `get_settings` / `update_settings`). Additional-instructions body must not be logged.

### 7. Summary generation

`backend/summarizer.py` + mlx-lm:

| Transcript size | Strategy |
| --- | --- |
| Short | Single prompt |
| Long | Chunk → summarize chunks → merge (map-reduce) |

Section headings are localized for common languages. Cancel is cooperative between stages (not mid-token). See [docs/scenarios/summary-generation.md](docs/scenarios/summary-generation.md).

### 8. Local outputs

- **App state** via `get_state` (transcript, summary, status, errors).
- **History** under Application Support (`meta.json`, `transcript.md`, `summary.md`, optional audio) — [LOCAL_DATA.md](LOCAL_DATA.md).
- **Export** (`export_notes`), **playback** (`get_playback_src`), **save audio copy** as user actions.

---

## Invariants

| Invariant | Rule |
| --- | --- |
| No content upload | Audio, transcript, and summary are never uploaded for processing |
| Network | Hugging Face (or compatible) model download on cache miss is the only expected runtime ML network use |
| Catalog ownership | Frontend does not hard-code Whisper/summary HF ids or token caps |
| Logging | Transcript and summary **bodies** are never logged — [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) |
| Threading | Long ML / IO work runs on background threads; UI polls state |
| Cancellation | Cooperative; leave UI in a recoverable idle/ready state |
| Bridge contract | `Api` methods in `backend/app.py` stay in sync with `frontend/src/vite-env.d.ts` |
| Platform | macOS Apple Silicon (arm64) only |

---

## Status and cancellation

| Concern | Behavior |
| --- | --- |
| Progress | Status strings / phases visible in UI; elapsed timing where applicable |
| Cancel transcription | Stops cooperative work; no corrupt half-state presented as success |
| Cancel summary | Must not wipe an existing good transcript |
| First model use | Download may take minutes; status should show loading — [docs/scenarios/first-run-model-download.md](docs/scenarios/first-run-model-download.md) |

---

## Related Documents

- [PRODUCT.md](PRODUCT.md) — product goals and non-goals
- [ARCHITECTURE.md](ARCHITECTURE.md) — where each step lives in code
- [LOCAL_DATA.md](LOCAL_DATA.md) — settings, history, caches
- [DECISIONS.md](DECISIONS.md) — why MLX, map-reduce, Swift recorder, etc.
- [TESTING.md](TESTING.md) — smoke checks for pipeline changes
- [docs/scenarios/](docs/scenarios/) — concrete flows and edge cases
