# Scribe — System Requirements

Single app build for Apple Silicon. Model size is chosen in-app (Processing options) with hardware-based defaults.

## Install

- File: `Scribe-<version>.dmg` → app **Scribe**
- App size on disk: ~670 MB
- DMG size: ~286 MB

## Hardware & OS

| | Minimum | Recommended for medium / 3B |
|---|---|---|
| CPU | Apple Silicon (M1 / M2 / M3 / M4), arm64 | **M3 or newer** (or M-series with **16 GB+**) |
| Memory (RAM) | 8 GB (use Small / 1.5B) | **16–32 GB** |
| macOS | 14 Sonoma or later | 14 Sonoma / 15 Sequoia |
| Free disk space | ~3 GB (app + models) | 5+ GB with headroom |

**Not supported:** Intel Mac, Windows, Linux.

## Models

| Role | Options | Strong default | Weak default |
|---|---|---|---|
| Transcription | Whisper small / medium | medium | small |
| Summary | Qwen2.5 1.5B / 3B (4-bit) | 3B | 1.5B |

Strong defaults (plus auto-summary on) apply on M3+ with enough RAM. Weaker Macs get Small / 1.5B and auto-summary off. See also [SYSTEM-REQUIREMENTS-LITE.md](SYSTEM-REQUIREMENTS-LITE.md).

Models are stored in the Hugging Face cache (`~/.cache/huggingface`). Internet is required **only** for the first download of each selected model.

Peak RAM use depends on the selected models — the app unloads them between stages, but spare memory is still recommended for medium / 3B.

## macOS permissions

To record a call on the same computer:

1. **Microphone**
2. **Screen & System Audio Recording** (system audio from Meet / Zoom / Teams, etc.)

Restart Scribe after granting Screen Recording.

## Network

- Not required after models are downloaded
- Recording and transcription do not use the cloud — everything runs locally

## Who this build is for

- Macs with **16 GB+** RAM
- Best transcript and summary quality
- Typical case: M3 / M4 with 16–24 GB

If the Mac has **8 GB** RAM (often M1), prefer [Scribe Lite](SYSTEM-REQUIREMENTS-LITE.md).
