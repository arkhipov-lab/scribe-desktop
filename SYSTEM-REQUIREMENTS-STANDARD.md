# Scribe — System Requirements (Standard)

Higher-quality build for more capable Macs.

## Install

- File: `Scribe-<version>.dmg` → app **Scribe**
- App size on disk: ~670 MB
- DMG size: ~286 MB

## Hardware & OS

| | Minimum | Recommended |
|---|---|---|
| CPU | Apple Silicon (M1 / M2 / M3 / M4), arm64 | **M2 Pro / M3 or newer** |
| Memory (RAM) | 16 GB | **16–32 GB** |
| macOS | 14 Sonoma or later | 14 Sonoma / 15 Sequoia |
| Free disk space | ~3 GB (app + models) | 5+ GB with headroom |

**Not supported:** Intel Mac, Windows, Linux.

## Models (downloaded on first use)

| Task | Model |
|---|---|
| Transcription | Whisper **medium** (`mlx-community/whisper-medium-mlx`) |
| Summary | Qwen2.5-**3B**-Instruct-4bit |

Models are stored in the Hugging Face cache (`~/.cache/huggingface`). Internet is required **only** for the first download of each model; after that everything works offline.

Peak RAM use is higher than Lite: the models are larger (the app unloads them between stages, but spare memory is still recommended).

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
