# Scenario: First-run model download

## Goal

First use of a Whisper or summary model downloads once into the local cache with visible progress/status, then becomes reusable.

## Preconditions

- Selected model not yet in Hugging Face / MLX cache (or cache cleared for test)
- Network available for download
- User starts Transcribe and/or Summary

## Flow

1. Pick a model under Processing options (or use first-launch default).
2. Start transcription (and summary if auto-summary on).
3. Wait through download + load; observe status.
4. Complete a short run; optionally quit and repeat offline ([offline-after-cache.md](./offline-after-cache.md)).

## Expected behavior

- Download is the expected network use — no audio/transcript upload.
- Status shows loading; UI remains responsive enough to cancel if offered.
- Weights land in local cache (typically `~/.cache/huggingface/`).
- Subsequent runs of the same model skip re-download.

## Edge cases

- Network drop mid-download → recoverable error; retry later.
- Disk full → clear failure.
- Switching to another catalog model → separate first download for that id.

## Related docs / tests

- [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) Network, [SYSTEM-REQUIREMENTS.md](../../SYSTEM-REQUIREMENTS.md)
- [TESTING.md](../../TESTING.md) § C–D, dist first-run notes
