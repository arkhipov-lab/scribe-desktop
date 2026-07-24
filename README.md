# Scribe

Personal macOS (Apple Silicon) desktop utility for fully local audio transcription and notes using MLX Whisper, a local summary model, React, and pywebview.

## Documentation

| Doc | Contents |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Entry point for AI coding agents |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Frontend → pywebview → Python → MLX / native flow |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Local setup, env vars, logs |
| [BUILDING.md](BUILDING.md) | Local `.app`, dist DMG, Lite/Standard profiles |
| [TESTING.md](TESTING.md) | Smoke checks and validation matrix |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution rules (including AI edits) |
| [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) | Local-only processing, permissions, logging |
| [ROADMAP.md](ROADMAP.md) | Planned work |
| [SYSTEM-REQUIREMENTS-STANDARD.md](SYSTEM-REQUIREMENTS-STANDARD.md) / [SYSTEM-REQUIREMENTS-LITE.md](SYSTEM-REQUIREMENTS-LITE.md) | Hardware profiles |

## Requirements

- macOS on Apple Silicon (M1/M2/M3/M4, arm64)
- Python 3.10+ (3.13 works)
- Node.js 20+ and npm
- ffmpeg via Homebrew (needed for local/dev builds; bundled into the dist app):

```bash
brew install ffmpeg
```

Expected ffmpeg path: `/opt/homebrew/bin/ffmpeg`

## Project layout

```text
frontend/             React + Vite + TypeScript UI
backend/              pywebview shell + mlx-whisper + summary
scripts/run-dev.sh    Development launcher
scripts/build.sh      Local .app (uses project .venv)
scripts/build-dist.sh Self-contained .app + DMG for sharing
requirements.txt      Python dependencies
```

## Development

```bash
chmod +x scripts/*.sh
./scripts/run-dev.sh
```

What it does:

1. Creates `.venv` if needed
2. Installs Python deps when missing/outdated
3. Installs frontend deps when missing
4. Starts Vite on `http://127.0.0.1:5173`
5. Opens the pywebview desktop window

Run against a production UI build instead of Vite:

```bash
USE_VITE_DEV=0 ./scripts/run-dev.sh
```

## Build

Local Finder `.app` (uses project `.venv`):

```bash
./scripts/build.sh
open "dist/Scribe.app"
```

Self-contained `.app` + versioned DMG for sharing (Lite or Standard):

```bash
./scripts/build-dist-standard.sh   # → dist/Scribe-<version>.dmg
./scripts/build-dist-lite.sh       # → dist/Scribe-Lite-<version>.dmg
```

Version comes from the repo-root `VERSION` file (auto-bumped on merge to `main` from conventional commits — see [CONTRIBUTING.md](CONTRIBUTING.md)). After that bump, local hooks build versioned DMGs and `.app` bundles into `dist/`.

Full packaging details, env knobs, runtime pruning, and Gatekeeper notes: **[BUILDING.md](BUILDING.md)**.

### Recording

The **Record** button captures **microphone + system audio** (via ScreenCaptureKit). No BlackHole required. Grant Microphone + Screen & System Audio Recording, then restart the app. Temp files live under `~/Library/Caches/Scribe/recordings/` and are deleted when you pick another file. See [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).

## Usage

1. Drop or select an audio/video file (`.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`) — or record
2. Choose language and summary options (preset, length, optional instructions)
3. Click **Transcribe**
4. Wait for local processing — first transcription downloads the Whisper model; first summary downloads the local LLM (each once, then cached)
5. Review **Transcript** and **Summary**, then Copy

Preferences (language, summary controls) are stored locally in `~/Library/Application Support/Scribe/settings.json`. All processing is local. No cloud upload.

## Models

Model IDs are **profile-driven**. Source of truth: [`backend/profile_config.py`](backend/profile_config.py) (`PROFILES`). Dist builds bake the chosen profile into `profile.json`; `transcriber.py` / `summarizer.py` read those values (they are not independent hard-coded defaults).

| Profile | Whisper | Summary |
| --- | --- | --- |
| **standard** (default) | `mlx-community/whisper-medium-mlx` | `mlx-community/Qwen2.5-3B-Instruct-4bit` |
| **lite** | `mlx-community/whisper-small-mlx` | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` |

Each model downloads once into the Hugging Face / MLX cache, then works offline. See [BUILDING.md](BUILDING.md) and the system-requirements docs for which profile to ship.

### Python dependencies

| File | Purpose |
| --- | --- |
| `requirements-runtime.txt` | What goes into the dist `.app` |
| `requirements.txt` | Local/dev default (`-r` runtime) |
| `requirements-dev.txt` | Runtime + PyInstaller extras |

The dist build drops unused `torch` (MLX path only) when smoke tests pass, and prunes caches/tests/packaging tools.

## Logs

```text
~/Library/Logs/Scribe/app.log
```

Transcript text is not logged.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| ffmpeg not found (local build) | `brew install ffmpeg` |
| Virtualenv missing when opening local .app | `./scripts/run-dev.sh` once, then `./scripts/build.sh` |
| Sharing with friends | Use `./scripts/build-dist.sh` (not `build.sh`) |
| Gatekeeper blocks unsigned app | Right-click → Open, or Privacy & Security → Open Anyway |
| First run is slow | Whisper + summary model downloads (multiple GB total), each once |
| Window does not open | Check the log file above |

## Architecture

```text
React + Vite UI
      ↓
pywebview JavaScript API
      ↓
Python (background thread)
      ↓
mlx-whisper + mlx-lm (Apple Silicon / MLX)
```

Details: [ARCHITECTURE.md](ARCHITECTURE.md).
