# Scribe Lite — System Requirements

Lighter build for Macs with less memory (including M1 / 8 GB). Same UI and workflows as Standard, smaller models.

## Install

- File: `Scribe-Lite.dmg` → app **Scribe Lite**
- App size on disk: ~670 MB (same runtime; models differ and download separately)
- DMG size: ~286 MB

## Hardware & OS

| | Minimum | Recommended |
|---|---|---|
| CPU | Apple Silicon (M1 / M2 / M3 / M4), arm64 | **M1 or newer** |
| Memory (RAM) | **8 GB** | 8–16 GB |
| macOS | 14 Sonoma or later | 14 Sonoma / 15 Sequoia |
| Free disk space | ~2 GB (app + models) | 3+ GB with headroom |

**Not supported:** Intel Mac, Windows, Linux.

## Models (downloaded on first use)

| Task | Model |
|---|---|
| Transcription | Whisper **small** (`mlx-community/whisper-small-mlx`) |
| Summary | Qwen2.5-**1.5B**-Instruct-4bit |

Models are stored in the Hugging Face cache (`~/.cache/huggingface`). Internet is required **only** for the first download of each model; after that everything works offline.

Transcript and summary quality is lower than Standard, but peak RAM use is much lower. Memory is released between transcription and summary.

## macOS permissions

To record a call on the same computer:

1. **Microphone**
2. **Screen & System Audio Recording** (system audio from Meet / Zoom / Teams, etc.)

Restart Scribe Lite after granting Screen Recording.

## Network

- Not required after models are downloaded
- Recording and transcription do not use the cloud — everything runs locally

## Who this build is for

- Macs with **8 GB** RAM (often base M1 / M2)
- Stable runs without heavy swapping or freezes
- Fine on stronger machines too if you prefer speed/lightness over max quality

If you have **16 GB+** and want better quality, use [Scribe (Standard)](SYSTEM-REQUIREMENTS-STANDARD.md).
