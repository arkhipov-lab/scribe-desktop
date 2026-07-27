# Scenario: Summary generation

## Goal

After a transcript exists, user gets useful local meeting notes via mlx-lm.

## Preconditions

- Transcript present (from file or recording)
- Summary model available or downloadable
- Auto-summary on **or** user clicks Generate / Regenerate

## Flow

1. Complete transcription (or open a history session with transcript).
2. If auto-summary is on, wait for summary; else click Generate.
3. Review Summary pane (sections per preset).

## Expected behavior

- Short transcripts: single-pass summary.
- Long transcripts: map-reduce (chunk → summarize → merge) without uploading text.
- Status remains visible; ML memory released between stages as designed.
- Log must **not** contain summary body.
- Manual Generate / Regenerate always summarizes the **current** transcript text (including user edits). Editing the transcript does not auto-start summary; auto-summary still runs after a fresh Transcribe when enabled. See [editable-transcript.md](./editable-transcript.md).

## Edge cases

- Auto-summary off → transcription completes without starting summary; Generate still works.
- OOM-like failure on 8 GB → switch to 1.5B / shorter audio; clear error preferred over hang.
- Cancel mid-summary → [cancel-summary.md](./cancel-summary.md).
- After transcript edits, previous summary may be stale until the user regenerates.

## Related docs / tests

- [AI_PIPELINE.md](../../AI_PIPELINE.md), [TESTING.md](../../TESTING.md) § D
- [summary-controls.md](./summary-controls.md)
