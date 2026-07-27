# Scenario: Editable transcript

## Goal

User corrects the Whisper transcript as plain text in-app; edits persist as left until Transcribe overwrites them; summary stays Markdown and read-only; regenerating summary uses the current transcript text.

## Preconditions

- A transcript exists (from file/recording transcription or an opened history session)
- Optional: a summary already exists

## Flow

1. Open the **Transcript** tab after transcription (or open a history session).
2. Confirm the transcript is plain text (not Markdown-rendered) and editable.
3. Edit the transcript; wait briefly or switch tabs — edits remain.
4. Copy / Export — content matches the edited transcript.
5. If a summary already exists, regenerate via **Generate / Regenerate** — notes reflect the edited transcript and replace the previous summary.
6. Click **Transcribe** again on the same (or new) audio — transcript is fully replaced; prior edits are discarded; summary is cleared/replaced per the normal pipeline. If auto-summary is on, the first summary after this Transcribe runs automatically.

## Expected behavior

- Transcript is plain text only (no Markdown processing for display or edit).
- Summary remains Markdown display-only (not editable in this scenario).
- Edits update Api state and, when a history session exists, the on-disk transcript file; summary is **not** cleared merely because the user edited the transcript.
- Editing the transcript does **not** auto-start summary.
- Auto-summary after a **fresh Transcribe** still runs when the auto-summary setting is on.
- Manual Generate/Regenerate always uses the **current** transcript string and fully overwrites the summary.
- Logs never contain transcript or summary bodies.

## Edge cases

- Edit while transcription/recording is running → editor disabled / updates rejected.
- Emptying the transcript then Generate → clear error (no transcript to summarize).
- Open another history session → loads that session’s transcript; local dirty edits from the previous session are discarded.
- Cancel summary after regenerate → existing transcript (including edits) remains intact.
- Editing during an in-flight summary is allowed; the regenerate hint stays if the transcript no longer matches what summarization started from.

## Related docs / tests

- [summary-generation.md](./summary-generation.md), [export-notes.md](./export-notes.md), [local-history.md](./local-history.md)
- [TESTING.md](../../TESTING.md) § C / § D / history / export
- Api: `update_transcript`, `start_summary`, `start_transcription`
