# Scenario: File transcription

## Goal

User selects or drops a supported media file and gets a local transcript.

## Preconditions

- App running via `./scripts/run-dev.sh` (or packaged app)
- ffmpeg available (Homebrew for local/dev; bundled in dist)
- Supported file: `.m4a`, `.mp3`, `.wav`, `.mp4`, or `.mov`
- Language chosen (or default)

## Flow

1. Select file via dialog **or** drop onto the window.
2. Confirm the UI shows the file is ready (no bridge error).
3. Click **Transcribe**.
4. Wait for status (`loading_model` / `transcribing` as applicable).
5. Read transcript in the UI.

## Expected behavior

- Supported extensions are accepted; processing stays on-device.
- Transcript appears in app state / UI.
- Log at `~/Library/Logs/Scribe/app.log` has path/status metadata, **not** transcript body.
- Choosing a new file clears prior transcript/summary as designed.

## Edge cases

- Very short / silent audio → empty or minimal transcript without crash.
- First use of Whisper model → download wait ([first-run-model-download.md](./first-run-model-download.md)).
- Missing ffmpeg (local) → clear error, not hang.

## Related docs / tests

- [AI_PIPELINE.md](../../AI_PIPELINE.md), [TESTING.md](../../TESTING.md) § B–C
- [unsupported-file.md](./unsupported-file.md), [cancel-transcription.md](./cancel-transcription.md)
