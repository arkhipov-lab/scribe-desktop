# Scenario: Recording to transcript

## Goal

User records microphone + system audio, then transcribes the result locally.

## Preconditions

- Mic + Screen & System Audio permissions granted ([recording-permissions.md](./recording-permissions.md))
- App restarted after granting Screen Recording if needed
- `native/build/AudioRecorder` present (dev) or bundled helper (dist)
- ffmpeg available

## Flow

1. Click **Record**; speak and play system audio (call or local media).
2. Stop recording.
3. Confirm a finalized WAV is ready for transcription.
4. Click **Transcribe**; wait for transcript.

## Expected behavior

- Capture uses ScreenCaptureKit path; **no screen video is saved**.
- Temp WAV under `~/Library/Caches/Scribe/recordings/` during/after capture.
- Selecting/dropping/recording another file deletes the previous owned temp recording.
- Transcript produced on-device like file ingest.
- **Dual-path finalize:** no headphones (built-in speakers) → **mic-only** WAV; headphones / BT → **level-matched mic + system `amix`**; unknown route → mix (never mic-only). See [recording-clean-mix](../initiatives/recording-clean-mix.md) / `PP-2026-07-29-001`.

## Edge cases

- Permissions denied → clear error / guidance; no silent failure.
- Stop immediately → short/empty file handled without crash.
- Weak hardware → prefer Small / 1.5B for full-pipeline smoke.
- Speakers vs headphones → different bleed; do not assume mic-only is always enough (headphones need system audio).
- Bluetooth room speakers may still finalize as mix (possible double); USB/HDMI/AirPlay → unknown → mix.
- Output route is classified at **stop** (plug/unplug mid-call uses the end state).

## Related docs / tests

- [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md), [TESTING.md](../../TESTING.md) § E
- [ARCHITECTURE.md](../../ARCHITECTURE.md) recording layer
- [docs/initiatives/recording-clean-mix.md](../initiatives/recording-clean-mix.md)
