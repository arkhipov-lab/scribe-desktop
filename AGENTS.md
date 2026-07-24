# AGENTS.md

Guidance for AI coding agents working on **Scribe** — a personal, fully local macOS (Apple Silicon) desktop app for audio transcription and meeting notes.

Read this file first. Then open the linked docs for depth.

| Doc | When to read |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understanding frontend / backend / native boundaries |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Local run, env vars, logs |
| [BUILDING.md](BUILDING.md) | `.app` / DMG packaging |
| [TESTING.md](TESTING.md) | How to validate changes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Change style, what not to commit |
| [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) | Local-only processing, permissions, logging rules |
| [ROADMAP.md](ROADMAP.md) | Planned work (do not implement unless asked) |
| [README.md](README.md) | User-facing overview |
| [SYSTEM-REQUIREMENTS-STANDARD.md](SYSTEM-REQUIREMENTS-STANDARD.md) / [SYSTEM-REQUIREMENTS-LITE.md](SYSTEM-REQUIREMENTS-LITE.md) | Hardware profiles |

---

## What this project is

- **Product name:** Scribe
- **Platform:** macOS **arm64 only** (Apple Silicon). Not Windows, Linux, or Intel Mac.
- **Stack:** React + Vite UI → pywebview JS bridge → Python backend → MLX Whisper + MLX LM, plus a Swift `AudioRecorder` helper (ScreenCaptureKit).
- **Promise:** audio and text stay on-device. No cloud transcription/summary upload.

---

## Quick start (agents)

```bash
chmod +x scripts/*.sh
./scripts/run-dev.sh
```

Typical verification after code changes:

```bash
# Frontend typecheck + production UI build
(cd frontend && npm run build)

# Optional: run against built UI instead of Vite
USE_VITE_DEV=0 ./scripts/run-dev.sh
```

Do **not** run a full `./scripts/build-dist.sh` unless the task is packaging-related — it is slow and downloads/caches a standalone Python runtime.

---

## Repository map

```text
frontend/                 React + Vite + TypeScript UI
  src/App.tsx             Main UI
  src/api.ts              pywebview API client
  src/vite-env.d.ts       Shared TS types for the bridge

backend/                  Python desktop shell + ML pipeline
  app.py                  pywebview window + Api class (JS bridge)
  transcriber.py          mlx-whisper transcription
  summarizer.py           mlx-lm summary (map-reduce for long text)
  recorder.py             AudioRecorder subprocess + ffmpeg mix
  profile_config.py       model token presets (catalog source)
  model_catalog.py        runtime Whisper / summary choices
  hardware.py             local Mac probe for recommended defaults
  memory.py               unload models / clear MLX cache between stages
  logger.py               rotating file log (no transcript body)
  languages.py            Whisper language list

native/
  AudioRecorder.swift     mic + system audio capture
  launcher.c              Mach-O stub for .app launch
  build/                  compiled helpers (gitignored)

scripts/
  run-dev.sh              primary local launcher
  build.sh                local .app (uses project .venv)
  build-dist.sh           self-contained .app + versioned DMG
  build-dist-{lite,standard}.sh
  bump-version.sh         conventional-commit semver bump
  read-version.sh         print VERSION
  release-build-local.sh  standard+lite .app/DMG after release bump
  install-git-hooks.sh    core.hooksPath → .githooks
  bundle-ffmpeg.sh / prune-runtime.sh / …

VERSION                   semver source of truth (baked into .app / DMG name)
.githooks/                post-merge: bump on main, then local dist builds
.github/workflows/        optional remote bump + GitHub Release publish

requirements-runtime.txt  deps embedded in dist .app
requirements.txt          local/dev (-r runtime)
requirements-dev.txt      runtime + PyInstaller extras

dist/                     build output — do not commit
.cache/                   dist runtime cache — do not commit
```

---

## Do not touch (unless explicitly asked)

- `dist/`, `.cache/`, `frontend/dist/`, `.venv/`, `node_modules/`
- Bundled/built artifacts (`native/build/`, generated `assets/AppIcon.icns` unless icon work is requested)
- Adding cloud upload, remote telemetry, or third-party AI APIs for transcription/summary
- Broad refactors unrelated to the task
- Committing secrets, recordings, or model weight caches

---

## Change style

1. **Match existing patterns** in nearby files (imports, naming, error shape returned to the UI).
2. **Keep the local-only contract.** Network may be used only for one-time Hugging Face model download.
3. **Never log transcript or summary text.** Log paths, statuses, durations, and error types only. See [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).
4. **Respect profiles.** Model IDs and app naming come from `backend/profile_config.py` / baked `profile.json`, not hard-coded strings in the UI.
5. **Apple Silicon only.** Reject or gate work that assumes x86_64 or non-macOS.
6. **Prefer small, focused diffs.** No drive-by cleanup or unsolicited markdown unless docs were requested.
7. **Frontend ↔ backend contract:** update `frontend/src/vite-env.d.ts` when adding/changing `Api` methods in `backend/app.py`.

---

## API surface (bridge)

The React UI talks only through `window.pywebview.api` (`Api` in `backend/app.py`). Important methods:

| Method | Role |
| --- | --- |
| `get_state` / polling | Current status, transcript, summary, errors |
| `select_file` / `set_file_path` | Choose or drop media |
| `start_recording` / `stop_recording` | Mic + system audio |
| `start_transcription` / `cancel_transcription` | Whisper pipeline |
| `start_summary` / `cancel_summary` | Local LLM notes |
| `get_summary_presets` / `get_whisper_models` / `get_summary_models` / `get_settings` / `update_settings` | Processing options + local prefs |
| `check_ffmpeg` / `get_app_info` / `get_languages` | Capability / metadata |

Heavy work runs on **background threads**; the UI polls state. Do not block the pywebview main thread with long ML calls.

---

## Validation checklist (minimum)

After meaningful changes, use [TESTING.md](TESTING.md). At least:

1. App launches via `./scripts/run-dev.sh`
2. File select or drop still works for a supported extension
3. If you touched recording: start/stop recording and confirm a WAV appears under `~/Library/Caches/Scribe/recordings/`
4. If you touched ML: a short file still transcribes and summarizes
5. Logs at `~/Library/Logs/Scribe/app.log` show no transcript body
6. `(cd frontend && npm run build)` passes after UI/TS changes

---

## Environment reminders

| Variable | Meaning |
| --- | --- |
| `USE_VITE_DEV=1` (default) | Dev UI from Vite `http://127.0.0.1:5173` |
| `USE_VITE_DEV=0` | Build frontend, load `frontend/dist` |
| `PYTHON_BIN` | Python used to create `.venv` (default `python3`) |
| `SCRIBE_PROFILE` | ignored (legacy) |
| `SCRIBE_ROOT` | Resources root inside packaged `.app` |
| `PROFILE` / `MAKE_DMG` / `FORCE_RUNTIME` | Dist build knobs — see [BUILDING.md](BUILDING.md) |

---

## When stuck

1. Read `~/Library/Logs/Scribe/app.log`
2. Confirm `uname -m` is `arm64` and Homebrew ffmpeg exists for local/dev (`/opt/homebrew/bin/ffmpeg`)
3. Confirm `native/build/AudioRecorder` exists after `run-dev.sh`
4. Prefer fixing the smallest failing layer (UI bridge → Python Api → transcriber/recorder → native binary)
