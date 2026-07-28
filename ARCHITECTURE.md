# Architecture

Scribe is a single-window macOS desktop app. The UI is a React SPA hosted inside **pywebview**; all transcription, summarization, and recording logic runs in a local Python process (MLX on Apple Silicon).

## High-level flow

```text
┌─────────────────────────────────────────────────────────────┐
│  React + Vite UI (frontend/)                                │
│  Polls window.pywebview.api → state (status, transcript…)   │
└─────────────────────────────┬───────────────────────────────┘
                              │ pywebview JS ↔ Python bridge
┌─────────────────────────────▼───────────────────────────────┐
│  backend/app.py  —  Api class + webview window              │
│  Background threads for transcription / summary             │
└───────┬─────────────────┬───────────────────┬───────────────┘
        │                 │                   │
        ▼                 ▼                   ▼
┌───────────────┐ ┌───────────────┐ ┌─────────────────────────┐
│ transcriber   │ │ summarizer    │ │ recorder                │
│ mlx-whisper   │ │ mlx-lm        │ │ CaptureRecorder         │
│ + ffmpeg      │ │ Qwen2.5 4bit  │ │ → native AudioRecorder  │
└───────────────┘ └───────────────┘ │ → ffmpeg mix → WAV      │
                                    └─────────────────────────┘
```

## Layers

### 1. Frontend (`frontend/`)

- **Role:** UX only — file drop/select, record controls, language, progress, plain-text editable transcript, Markdown summary display, partial copy (transcript / summary / action items), copy/export.
- **Bridge:** `frontend/src/api.ts` waits for `pywebviewready`, then calls methods typed in `vite-env.d.ts`.
- **No direct filesystem or ML access.** Paths and permissions are handled by Python / macOS.

### 2. Desktop shell (`backend/app.py`)

- Creates the pywebview window and exposes `Api` to JavaScript.
- Holds mutable app state (`status`, `transcript`, `summary`, timers, cancel events).
- Routes UI actions to recorder / transcriber / summarizer.
- Resolves UI URL: Vite dev URL (`--dev-url`) or packaged `frontend/dist/index.html`.
- Owns temporary recording cleanup when the user picks another file.

### 3. Transcription (`backend/transcriber.py`)

- Validates paths and extensions: `.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`.
- Locates **ffmpeg** (bundled app `bin/ffmpeg`, then `PATH`, then Homebrew).
- Runs **mlx-whisper** with the profile’s Whisper model.
- Emits status callbacks (`loading_model`, `transcribing`).
- Releases ML memory after transcription so summary can load.

### 4. Summary (`backend/summarizer.py`)

- Loads **mlx-lm** Instruct model from the active profile.
- Short transcripts: single prompt. Long transcripts: chunk → summarize → merge (map-reduce).
- Section headings localized for common languages.
- Cooperative cancel between stages only (not mid-token).

### 5. Recording (`backend/recorder.py` + `native/AudioRecorder.swift`)

- Python finds and launches the **AudioRecorder** Mach-O helper.
- Helper uses **ScreenCaptureKit** (+ AVFoundation) for microphone **and** system audio.
- Dual-track capture (system + mic) always. On stop, **dual-path finalize** (`backend/output_route.py` + `recorder.py`): **speakers / open air** → product WAV from **mic track only**; **headphones / Bluetooth private** → ffmpeg **`amix`** after mic level-match toward system; **unknown** route (USB/HDMI/AirPlay/etc.) → headphones-style mix so remote is not dropped. See closed initiative [docs/initiatives/recording-clean-mix.md](../docs/initiatives/recording-clean-mix.md).
- Finalized WAV under:

  ```text
  ~/Library/Caches/Scribe/recordings/
  ```

- Temp files are deleted when another file is selected/dropped/recorded.

### 6. Native launcher (`native/launcher.c`)

- Small Mach-O executable inside `.app/Contents/MacOS/Scribe`.
- Required so Finder double-click works; sets up environment and starts embedded or project Python running `backend/app.py`.

### 7. Models & hardware (`backend/model_catalog.py`, `hardware.py`)

One product build. Users pick Whisper (small/medium) and summary (1.5B/3B) under Processing options. First-launch defaults come from a local hardware probe (strong vs weak tier). Token budgets for summarization live next to the catalog entries.

App display name comes from `backend/profile_config.py` (`APP_NAME`). Dist builds bake `Resources/app.json` identity metadata.

### 8. Memory (`backend/memory.py`)

Between pipeline stages the app unloads the summary model (when applicable) and clears MLX Metal caches so 8 GB machines can survive Small / 1.5B runs.

## Packaging shapes

| Artifact | Python | ffmpeg | Models |
| --- | --- | --- | --- |
| Dev (`run-dev.sh`) | project `.venv` | Homebrew | HF cache on first use |
| Local `.app` (`build.sh`) | project `.venv` (machine-bound) | Homebrew / PATH | HF cache |
| Dist `.app` (`build-dist.sh`) | embedded relocatable CPython + `requirements-runtime.txt` | bundled into Resources | HF cache (still download once per machine) |

Fully frozen PyInstaller + MLX is brittle; dist prefers embedded interpreter + copied backend sources. See [BUILDING.md](BUILDING.md).

## Data & side effects

| Location | Contents |
| --- | --- |
| `~/Library/Logs/Scribe/app.log` | Status / errors (rotating); **not** transcript text |
| `~/Library/Caches/Scribe/recordings/` | Temporary WAVs |
| `~/.cache/huggingface/` (typical) | Downloaded MLX / Whisper weights |

## Trust boundaries

- UI is not a security boundary for secrets; treat the Python `Api` as the authority.
- Do not add network clients for audio/text processing.
- Model download is the only expected outbound ML traffic, and only on first cache miss.
