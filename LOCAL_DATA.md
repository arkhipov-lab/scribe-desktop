# Local Data

How Scribe stores and exposes data on the local Mac.

> There is **no** SQL database or server-side schema. Prefer this document over inventing a relational “data model.” Layer ownership: [ARCHITECTURE.md](ARCHITECTURE.md). Privacy rules: [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).

---

## Overview

```text
Runtime app state  ←→  pywebview Api.get_state (in-memory)
Settings           →   ~/Library/Application Support/Scribe/settings.json
History            →   ~/Library/Application Support/Scribe/history/
Temp recordings    →   ~/Library/Caches/Scribe/recordings/
Logs               →   ~/Library/Logs/Scribe/app.log
Model weights      →   Hugging Face / MLX cache (typically ~/.cache/huggingface/)
```

---

## App state (`get_state`)

Mutable session state lives in the Python `Api` (`backend/app.py`): status, transcript, summary, timers, cancel events, selected path, errors, etc.

| Rule | Detail |
| --- | --- |
| Authority | Python owns filesystem and ML; UI only calls the bridge |
| Shape | Response shapes must match `frontend/src/vite-env.d.ts` |
| Polling | UI polls; do not push long ML work onto the WebView main thread |
| Content | Transcript/summary text may sit in memory for the UI — never written to the app log |

---

## Settings

**Path:** `~/Library/Application Support/Scribe/settings.json`

Stores preferences only, for example:

- transcript `language` and `summary_language` / processing options
- Whisper and summary model choices
- summary preset, length, additional instructions
- auto-summary on/off
- UI prefs such as sidebar open

**Must not contain** transcripts or summaries.

On first launch (no settings file), `backend/hardware.py` picks strong vs weak defaults. See [SYSTEM-REQUIREMENTS.md](SYSTEM-REQUIREMENTS.md) and [docs/scenarios/weak-hardware-defaults.md](docs/scenarios/weak-hardware-defaults.md).

---

## History

**Root:** `~/Library/Application Support/Scribe/history/`

| Path | Role |
| --- | --- |
| `history/index.json` | Light sidebar index |
| `history/sessions/<id>/` | One session folder |
| `…/meta.json` | Metadata (title, dates, languages, flags such as has_summary) |
| `…/transcript.md` | Transcript text |
| `…/summary.md` | Summary text (when present) |
| `…/audio.*` | Optional copied audio (skipped if source is very large) |

History is **local user data** — on-device only, no sync. Deleting a session removes that session’s files. Logs must still omit transcript/summary bodies even when history exists.

Bridge: `list_sessions`, `open_session`, `delete_session`. See [docs/scenarios/local-history.md](docs/scenarios/local-history.md).

---

## Temporary recordings

**Path:** `~/Library/Caches/Scribe/recordings/`

WAVs produced by Record (Swift helper + ffmpeg mix). Owned temp files are **deleted** when the user selects, drops, or records another file. Do not leave orphaned sensitive audio in world-readable locations.

---

## Logs

**Path:** `~/Library/Logs/Scribe/app.log`

Rotating application log (see `backend/logger.py`).

| Allowed | Forbidden |
| --- | --- |
| Paths, model ids, durations, status transitions | Transcript bodies |
| Exception types / safe messages | Summary bodies |
| ffmpeg exit codes, permission failures | Raw audio payloads; additional-instructions content |

Prefer lengths/hashes (`chars=%d`) when debugging size — never content. [docs/scenarios/privacy-logging.md](docs/scenarios/privacy-logging.md).

---

## Model cache

Downloaded Whisper / summary weights live in the local Hugging Face / MLX cache (typically `~/.cache/huggingface/`). First use of each selected model may download once; afterward transcription and summary should work offline ([docs/scenarios/offline-after-cache.md](docs/scenarios/offline-after-cache.md)).

Model ids and token caps are defined in `backend/model_catalog.py`, not in the React UI.

---

## Bridge contract

| Concern | Rule |
| --- | --- |
| Types | Keep `frontend/src/vite-env.d.ts` aligned with `Api` in `backend/app.py` |
| Errors | Prefer clear user-facing error shapes over raw stack traces in the UI |
| Export / playback | User-triggered; writes or serves local bytes only |

---

## Related Documents

- [PRODUCT.md](PRODUCT.md) — what user-owned data is for
- [AI_PIPELINE.md](AI_PIPELINE.md) — how state and files are produced
- [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) — authoritative privacy/logging rules
- [DECISIONS.md](DECISIONS.md) — why history is filesystem-based
- [TESTING.md](TESTING.md) — smoke checks involving settings/history/logs
