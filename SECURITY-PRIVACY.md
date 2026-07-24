# Security & privacy

Scribe is designed as a **personal, on-device** transcription and notes tool. This document describes what stays local, what permissions macOS grants, and what maintainers must not break.

## Privacy promise

| Data | Where it goes |
| --- | --- |
| Microphone / system audio | Processed on the local Mac only |
| Temporary recordings | `~/Library/Caches/Scribe/recordings/` then deleted when replaced |
| Transcripts & summaries | Held in app memory / UI; user may copy — **not uploaded** |
| Model weights | Downloaded once from Hugging Face (or compatible) into the local cache, then reused offline |
| Logs | `~/Library/Logs/Scribe/app.log` — statuses, paths, errors — **not transcript/summary text** |

There is **no** Scribe cloud backend for audio or text. Do not add one without an explicit product decision and a docs overhaul.

## Network

Expected network use:

1. **First-time model download** when a Whisper or summary model is not already cached.
2. **Build-time only** on developer machines (pip, npm, standalone Python tarball, wheels) — not required for end users after install, except (1).

Not expected:

- Uploading recordings, transcripts, or summaries
- Analytics / telemetry beacons
- Account login or license phone-home

After models are cached, transcription and summarization should work **offline**.

## macOS permissions

Recording uses the same permission family as screen capture because system audio is obtained via **ScreenCaptureKit**.

| Permission | Why |
| --- | --- |
| **Microphone** | Capture the user’s voice |
| **Screen & System Audio Recording** | Capture system audio from calls/apps; **video frames are not saved** |

Info.plist usage strings (dist builds) explain this in plain language (`NSMicrophoneUsageDescription`, `NSAudioCaptureUsageDescription`, `NSScreenCaptureDescription`).

After the user grants Screen Recording, they typically must **restart the app** before capture works. Document that in UX copy when you change onboarding.

File open/save uses standard macOS dialogs via pywebview; the app reads user-selected media paths for local processing.

## Local filesystem footprints

```text
~/Library/Logs/Scribe/app.log          # rotating application log
~/Library/Caches/Scribe/recordings/    # temporary WAVs from Record
~/.cache/huggingface/                  # typical model cache location (HF / MLX)
```

Temp recordings owned by the session are removed when the user selects, drops, or records another file. Do not leave orphaned sensitive audio in world-readable locations.

## Logging rules (maintainers)

**Allowed:** file paths, model ids, durations, status transitions, exception types/messages that do not include user speech text, ffmpeg exit codes, permission failures.

**Forbidden:**

- Full or partial transcript bodies
- Summary bodies
- Raw audio payloads
- Pasting meeting content into third-party issue trackers from automated tooling without user consent

If you need richer diagnostics, log hashes/lengths (`chars=%d`) — already used in places — not content.

## Threat model (lightweight)

Scribe is a **local utility**, not a hardened multi-user service.

| Concern | Mitigation / reality |
| --- | --- |
| Malicious HTML in UI | UI is first-party; still treat bridge as trusted code you control |
| Supply chain (pip/npm) | Pin thoughtfully in packaging; review dependency bumps |
| Unsigned dist builds | Ad-hoc codesign only today — Gatekeeper warnings expected until notarization |
| Other local users / malware | OS user isolation; anyone with local access can read the user’s files/logs |
| Prompt injection via transcript into the local LLM | Summarizer may follow malicious spoken/written instructions in the audio; treat summaries as untrusted text |

## Packaging & code signing

Current dist builds:

- Ad-hoc `codesign` and quarantine attribute clearing for smoother local open
- **Not** Developer ID + notarized

Until notarization lands (see [ROADMAP.md](ROADMAP.md)), instruct users to open via right-click → Open / Privacy & Security.

Never commit signing certificates, notary credentials, or API keys.

## Security review checklist for PRs

- [ ] No new network calls in the transcription/summary/record path
- [ ] No transcript/summary logging
- [ ] Temp audio still cleaned up on file replace
- [ ] Permission strings still accurate if capture behavior changes
- [ ] Profile / model changes do not accidentally phone home beyond HF download
- [ ] Native helper still does not write screen video to disk

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md) — data flow
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution rules
- [BUILDING.md](BUILDING.md) — what ships inside the `.app`
