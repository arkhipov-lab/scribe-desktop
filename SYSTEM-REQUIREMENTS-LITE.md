# Low-memory Macs — model guidance

> **Note:** There is no separate Scribe Lite product anymore. One `Scribe-<version>.dmg` ships for everyone; pick **Small / 1.5B** under Processing options for the old Lite footprint.

## Install

- File: `Scribe-<version>.dmg` → app **Scribe**
- App size on disk: ~670 MB (models download separately)
- DMG size: ~286 MB

## Hardware & OS

| | Minimum | Comfortable for light models |
|---|---|---|
| CPU | Apple Silicon (M1 / M2 / M3 / M4), arm64 | M1 / M2 |
| Memory (RAM) | **8 GB** | 8–16 GB |
| macOS | 14 Sonoma or later | 14 Sonoma / 15 Sequoia |
| Free disk space | ~2 GB (app + smaller models) | 3+ GB with headroom |

**Not supported:** Intel Mac, Windows, Linux.

## Models (Small / 1.5B)

| Task | Model |
|---|---|
| Transcription | Whisper **small** |
| Summary | Qwen2.5-**1.5B**-Instruct-4bit |

On first launch, weaker Macs (M2 or older, or under ~12 GB RAM) get these defaults and **auto-summary off**. You can change them anytime in Processing options.

## macOS permissions

1. **Microphone**
2. **Screen & System Audio Recording**

Restart Scribe after granting Screen Recording.

## Network

- Not required after models are downloaded
- Recording and transcription do not use the cloud

For stronger defaults (medium / 3B), see [SYSTEM-REQUIREMENTS-STANDARD.md](SYSTEM-REQUIREMENTS-STANDARD.md).
