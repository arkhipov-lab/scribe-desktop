# Scribe

> Turn meeting audio into a transcript and useful notes — on your Mac, without uploading anything.

---

# Vision

Most meeting tools push audio and text to the cloud. That is convenient for sync and collaboration, and expensive for privacy and trust.

Scribe is different.

It is a **personal, fully local** macOS (Apple Silicon) desktop app: pick or record audio, transcribe with MLX Whisper, then summarize with a local LLM. The user reviews and copies or exports what they need. Nothing leaves the machine for transcription or summary.

The product should feel like a sharp local utility — not a SaaS workspace, not a meeting bot, not a team platform.

---

# Core Goal

Reduce the workflow

> Meeting ended → useful notes I can act on

to as little manual work as possible: select/record → Transcribe → review transcript + summary → copy/export.

The user should spend time **reading and correcting** notes, not retyping what was said.

---

# Product Philosophy

**Privacy-first, local-first, user-owned.**

- Audio, transcripts, and summaries stay on-device.
- Files the user exports and history sessions are theirs.
- Network is expected only for one-time Hugging Face model download when a model is not cached.
- Logging never includes meeting content.

Scribe’s asset is **local meeting text the user controls** — not a synced workspace or a cloud AI subscription.

---

# Design Principles

## Local-only by default

Core processing (record mix, transcription, summary) runs on the local Mac. Do not add cloud transcription, remote summary APIs, accounts, or telemetry for meeting content.

## Slow ML stages must be visible and cancellable

Model load and long audio take time. Status must stay honest (`loading_model`, `transcribing`, summarizing phases). Cancel is cooperative and must return the UI to a sane idle state without corrupting an existing transcript when summary is cancelled.

## Defaults adapt to Apple Silicon hardware

First-launch defaults come from a local hardware probe: stronger Whisper/summary + auto-summary on capable Macs; lighter models and auto-summary off on weaker machines. Users can override under **Processing options**.

## User controls summary shape

Presets, summary length, summary language (independent of transcript language), and additional instructions shape notes. Model ids and token caps come from the backend catalog — not hard-coded in the UI.

## Export and history are local user-owned outputs

History lives under Application Support. Export writes `.md` / `.txt` the user chooses. No sync, no shared workspace.

## Logging must never contain meeting content

Logs may record paths, statuses, durations, model ids, and error types — never transcript or summary bodies. See [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).

---

# Primary User Flow

```
Open Scribe
      ↓
Drop / select media  —or—  Record (mic + system audio)
      ↓
Choose transcript language + summary language + Processing options (optional)
      ↓
Transcribe (MLX Whisper)
      ↓
Summary (MLX LM) when auto-summary is on, or Generate later
      ↓
Review Transcript + Summary → Copy / Export / History
```

---

# Capabilities (shipped direction)

| Area | Behavior |
| --- | --- |
| Ingest | File select/drop (`.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`) or Record |
| Transcription | Local mlx-whisper; transcript language picker; cancel |
| Summary | Local mlx-lm; presets, length, summary language, instructions; map-reduce for long text; cancel |
| Models | Whisper small/medium; Qwen2.5 1.5B/3B 4-bit; catalog in `backend/model_catalog.py` |
| History | On-disk sessions (meta, transcript, summary, optional audio) |
| Export / playback | Local notes export; in-app playback of selected/recorded audio |

Layer detail: [ARCHITECTURE.md](ARCHITECTURE.md). Pipeline detail: [AI_PIPELINE.md](AI_PIPELINE.md). Local paths: [LOCAL_DATA.md](LOCAL_DATA.md).

---

# Non-Goals

Scribe is **not** trying to:

- cloud-transcribe or cloud-summarize audio;
- offer accounts, team sync, or multi-device collaboration;
- join Zoom / Meet / Teams as a meeting bot;
- ship remote analytics or telemetry of meeting content;
- support Windows, Linux, or Intel Mac.

See also explicit non-goals in [ROADMAP.md](ROADMAP.md).

---

# Scenario Specifications

Vision describes *what* Scribe should achieve.

Concrete expected behavior lives in [docs/scenarios/](docs/scenarios/). Those scenarios guide implementation and manual QA.

---

# Related Documents

| Doc | Role |
| --- | --- |
| [LOCAL_DATA.md](LOCAL_DATA.md) | Settings, history, caches, logs, bridge state |
| [AI_PIPELINE.md](AI_PIPELINE.md) | End-to-end processing pipeline |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Frontend / backend / native layers |
| [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) | Privacy promise and logging rules |
| [DECISIONS.md](DECISIONS.md) | Why key choices were made |
| [ROADMAP.md](ROADMAP.md) | Planned work (hypothesis, not commitment) |
| [docs/MANIFEST.md](docs/MANIFEST.md) | Dual goals: product + AI development process |
