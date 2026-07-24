# Scribe — System Requirements

Single app for Apple Silicon. Whisper and summary model sizes are chosen in-app (**Processing options**) with hardware-based defaults.

## Install

- File: `Scribe-<version>.dmg` → app **Scribe**
- App size on disk: ~670 MB (models download separately)
- DMG size: ~286 MB

## Hardware & OS

| | Minimum | Recommended for Medium / 3B |
|---|---|---|
| CPU | Apple Silicon (M1 / M2 / M3 / M4), arm64 | **M3 or newer** (or M-series with **16 GB+**) |
| Memory (RAM) | **8 GB** (use Small / 1.5B) | **16–32 GB** |
| macOS | 14 Sonoma or later | 14 Sonoma / 15 Sequoia |
| Free disk space | ~2–3 GB (app + lighter models) | 5+ GB with headroom |

**Not supported:** Intel Mac, Windows, Linux.

## Models

| Role | Options | Strong default | Weak default |
|---|---|---|---|
| Transcription | Whisper small / medium | medium | small |
| Summary | Qwen2.5 1.5B / 3B (4-bit) | 3B | 1.5B |

- **Strong** (M3+ with enough RAM): Medium + 3B, auto-summary on  
- **Weak** (M2 or older, or under ~12 GB RAM): Small + 1.5B, auto-summary off  

Change anytime under Processing options. Models live in the Hugging Face cache (`~/.cache/huggingface`). Internet is required **only** for the first download of each selected model.

Peak RAM depends on the selected pair — the app unloads models between stages, but spare memory still helps for Medium / 3B.

## macOS permissions

To record a call on the same computer:

1. **Microphone**
2. **Screen & System Audio Recording** (system audio from Meet / Zoom / Teams, etc.)

Restart Scribe after granting Screen Recording.

## Network

- Not required after models are downloaded
- Recording and transcription do not use the cloud — everything runs locally
