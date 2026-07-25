# Scenario: Offline after cache

## Goal

After models are cached, transcription and summarization work without network.

## Preconditions

- Whisper (and summary, if testing summary) already downloaded for the selected catalog entries
- Network disabled or unreachable (e.g. airplane mode / unplug)

## Flow

1. Confirm Processing options point at already-cached models.
2. Select a short local file (or use a ready recording).
3. Transcribe; generate summary if in scope.
4. Confirm success without requiring network.

## Expected behavior

- Full local pipeline succeeds for cached models.
- No attempt to upload audio or text.
- If user selects an **uncached** model while offline → clear failure to download/load, not a hang claiming success.

## Edge cases

- Partial cache corruption → error suggesting re-download when online.
- History open / export / playback should still work offline.

## Related docs / tests

- [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md), [AI_PIPELINE.md](../../AI_PIPELINE.md) invariants
- [first-run-model-download.md](./first-run-model-download.md)
