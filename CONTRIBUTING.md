# Contributing

Thanks for helping with Scribe. This document covers contribution norms for humans and AI assistants. Agents should also read [AGENTS.md](AGENTS.md).

## Product constraints (non-negotiable)

1. **Apple Silicon only** — do not add Intel / Windows / Linux support unless that is an explicit project goal change.
2. **Fully local processing** — no cloud upload of audio, transcripts, or summaries. Do not add remote AI APIs for core features.
3. **Privacy-aware logging** — never write transcript or summary text to logs, crash reports, or analytics.
4. **macOS permissions honesty** — recording uses microphone + system audio (ScreenCaptureKit). Do not claim “screen video is saved” in user-facing copy; video is not persisted.

## Before you start

- Prefer a focused change that solves one problem.
- Skim [ARCHITECTURE.md](ARCHITECTURE.md) so edits land in the right layer.
- For packaging work, read [BUILDING.md](BUILDING.md).
- Validate with [TESTING.md](TESTING.md).

## What not to commit

Never add these to git (already gitignored in most cases):

| Path / pattern | Why |
| --- | --- |
| `dist/` | Built apps and DMGs |
| `.cache/` | Embedded Python / wheel caches |
| `.venv/`, `node_modules/`, `frontend/dist/` | Local installs / builds |
| `native/build/` | Compiled helpers |
| `assets/AppIcon.iconset/` | Icon intermediates |
| `*.log`, recordings, HF model caches | User/runtime data |
| `.env`, credentials, signing identities | Secrets |

Do **not** regenerate or commit bundled dist artifacts unless the maintainer explicitly asks.

## Code guidelines

### General

- Match existing style in the file you edit.
- Keep diffs small; avoid unrelated refactors and drive-by formatting.
- Do not add unsolicited markdown docs; update existing docs when behavior changes.
- Prefer clear user-facing errors (`TranscribeError`, `SummaryError`, `RecorderError`) over stack traces in the UI.

### Backend (Python)

- Public JS bridge methods live on `Api` in `backend/app.py` and must remain callable from the WebView.
- Long ML / IO work stays on background threads; update shared state under the existing lock.
- Model IDs and app naming come from `profile_config` / `profile.json`, not scattered literals.
- After transcription, rely on `release_ml_memory` so summary can load on smaller Macs.
- Log metadata only: paths, model ids, durations, status, exception types.

### Frontend (React / TypeScript)

- Keep `frontend/src/vite-env.d.ts` in sync with Python `Api` methods.
- UI should tolerate slow first-run model downloads and cancelled jobs.
- Do not assume browser `File.path` outside the desktop WebView.

### Native

- `AudioRecorder.swift` is the system-audio path — change carefully and retest permissions + restart behavior.
- Keep `MACOSX_DEPLOYMENT_TARGET` / arm64 assumptions aligned with packaging scripts.

## AI-assisted edits (extra rules)

| Do | Don’t |
| --- | --- |
| Follow [AGENTS.md](AGENTS.md) first | Invent cloud sync / accounts / telemetry |
| Update docs when packaging or privacy behavior changes | Commit `dist/` “to make the PR easier to try” |
| Run frontend build + relevant smoke checks | Log full transcript “for debugging” |
| Ask before notarization, signing, or license changes | Broaden scope into ROADMAP items unprompted |

## Pull requests

When PRs are used:

1. Describe *why* the change exists.
2. Note which smoke checks from [TESTING.md](TESTING.md) you ran.
3. Call out profile impact (`standard` / `lite`) and any first-run download implications.
4. Link related ROADMAP items only if intentionally advancing them.

## Commit messages

Prefer short, imperative summaries focused on intent, e.g. “Fix temp recording cleanup after drop” rather than “Update recorder.py”.

Do not create commits unless the maintainer asks you to.
