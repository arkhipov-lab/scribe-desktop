# Development

Local development for Scribe on **macOS Apple Silicon (arm64)**.

## Prerequisites

| Requirement | Notes |
| --- | --- |
| macOS on Apple Silicon | `uname -m` must be `arm64` |
| Python 3.10+ | 3.13 works; used for `.venv` |
| Node.js 20+ and npm | Frontend toolchain |
| Homebrew ffmpeg | Local/dev (dist bundles its own) |
| Xcode CLT / Swift | Compiles `native/AudioRecorder.swift` |

```bash
brew install ffmpeg
# Expected path: /opt/homebrew/bin/ffmpeg
```

Optional reading: [SYSTEM-REQUIREMENTS-STANDARD.md](SYSTEM-REQUIREMENTS-STANDARD.md), [SYSTEM-REQUIREMENTS-LITE.md](SYSTEM-REQUIREMENTS-LITE.md).

## First-time setup

```bash
chmod +x scripts/*.sh
./scripts/run-dev.sh
```

`run-dev.sh` will:

1. Refuse non-arm64 hosts
2. Create `.venv` if missing
3. `pip install -r requirements.txt` when deps are missing/outdated
4. `npm install` in `frontend/` when needed
5. Compile `native/build/AudioRecorder` if missing or stale
6. Start Vite on `http://127.0.0.1:5173`
7. Launch `backend/app.py --dev-url …` (pywebview window)

## Day-to-day commands

| Goal | Command |
| --- | --- |
| Default dev (Vite HMR + desktop window) | `./scripts/run-dev.sh` |
| Production UI build inside the window | `USE_VITE_DEV=0 ./scripts/run-dev.sh` |
| Frontend typecheck + Vite build only | `(cd frontend && npm run build)` |
| Local Finder-friendly `.app` (uses `.venv`) | `./scripts/build.sh` — see [BUILDING.md](BUILDING.md) |

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `USE_VITE_DEV` | `1` | `1` = Vite URL; `0` = build + load `frontend/dist` |
| `DEV_URL` | `http://127.0.0.1:5173` | UI URL when Vite mode is on |
| `PYTHON_BIN` | `python3` | Interpreter used to create `.venv` |
| `SCRIBE_PROFILE` | unset → `standard` | Force `standard` or `lite` model set in dev |
| `SCRIBE_ROOT` | unset | Set inside packaged apps to Resources root |
| `MACOSX_DEPLOYMENT_TARGET` | `14.0` | Native compile target (Sonoma+) |
| `PATH` | — | Dev script prepends `/opt/homebrew/bin` for ffmpeg |

Legacy alias: `LOCAL_TRANSCRIBER_ROOT` is still accepted where `SCRIBE_ROOT` is read.

### Switching profiles in development

```bash
SCRIBE_PROFILE=lite ./scripts/run-dev.sh
# or write profile.json at repo root / backend/ (see profile_config.py)
```

Lite uses smaller Whisper + summary models and tighter token limits — useful when testing memory behavior on 8 GB machines.

## Where to look when something breaks

### Application log

```text
~/Library/Logs/Scribe/app.log
```

Rotating file (≈2 MB × 3 backups) plus console while running under the terminal. Transcript/summary **bodies are not logged** — only paths, statuses, durations, and exceptions.

### Temporary recordings

```text
~/Library/Caches/Scribe/recordings/
```

### Common failures

| Symptom | Likely cause |
| --- | --- |
| Script exits on arch check | Not arm64 / Rosetta-only shell |
| `ffmpeg not found` | Install Homebrew ffmpeg; ensure PATH |
| Window never opens | Check log; pywebview / display issues |
| Recording permission errors | Grant Mic + Screen & System Audio; **restart app** |
| First transcription very slow | Model download into Hugging Face cache |
| `Desktop bridge is not available` | UI loaded outside pywebview, or API not ready yet |
| Stale AudioRecorder | Delete `native/build/AudioRecorder` and re-run `run-dev.sh` |

## Working on the frontend alone

You can run Vite without the desktop shell for layout work:

```bash
cd frontend && npm run dev -- --host 127.0.0.1 --port 5173
```

Bridge calls will fail in a normal browser — use the full `run-dev.sh` path to exercise `pywebview.api`.

## Working on the backend alone

```bash
source .venv/bin/activate
cd backend
# With a pre-built UI:
python app.py
# Or point at Vite:
python app.py --dev-url http://127.0.0.1:5173
```

Ensure ffmpeg and `native/build/AudioRecorder` exist if you test recording.

## Dependencies

| File | Use |
| --- | --- |
| `requirements-runtime.txt` | What ships inside the dist `.app` (`mlx-whisper`, `mlx-lm`, `pywebview`) |
| `requirements.txt` | Local/dev default (`-r` runtime) |
| `requirements-dev.txt` | Runtime + PyInstaller (experimental local freeze) |

Python packages land in `.venv/`. Frontend packages in `frontend/node_modules/`. Both are gitignored.

## Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — system boundaries
- [TESTING.md](TESTING.md) — smoke checks
- [AGENTS.md](AGENTS.md) — agent-oriented entry point
