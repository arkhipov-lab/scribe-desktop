# Scenario: Cancel transcription

## Goal

User can cancel an in-progress transcription and return to a sane idle/ready state.

## Preconditions

- Supported file selected
- Transcription started (preferably during model load or long audio)

## Flow

1. Click **Transcribe**.
2. While status shows loading/transcribing, click **Cancel**.
3. Observe UI and subsequent actions (re-transcribe still possible).

## Expected behavior

- Cancel is cooperative; UI does not claim a successful full transcript.
- App returns to a recoverable idle/ready state without crash.
- Log shows cancel/status metadata only — no partial transcript body.

## Edge cases

- Cancel just as transcription completes → last status must not leave contradictory UI.
- Cancel then immediately Transcribe again → second run works.

## Related docs / tests

- [AI_PIPELINE.md](../../AI_PIPELINE.md) invariants, [TESTING.md](../../TESTING.md) § C
