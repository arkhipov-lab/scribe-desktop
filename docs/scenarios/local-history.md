# Scenario: Local history

## Goal

User can browse, open, and delete on-disk sessions without any cloud sync.

## Preconditions

- At least one completed session (transcript, optionally summary)
- History sidebar available

## Flow

1. After transcription/summary, confirm a session appears in history.
2. Open a previous session; transcript/summary load into the UI.
3. Delete a session; confirm it disappears and files are gone under `history/sessions/`.

## Expected behavior

- Sessions under `~/Library/Application Support/Scribe/history/sessions/<id>/` with `meta.json`, `transcript.md`, `summary.md`, optional audio.
- Index drives the sidebar (`index.json`).
- Optional audio copy may be skipped for very large sources.
- All history remains local user data.
- User transcript edits persist into the session transcript file; reopening shows the edited plain text (summary unchanged until regenerate). See [editable-transcript.md](./editable-transcript.md).

## Edge cases

- Delete while viewing that session → UI clears or falls back safely.
- Corrupt/missing `meta.json` → skip or error without crashing the whole sidebar.

## Related docs / tests

- [LOCAL_DATA.md](../../LOCAL_DATA.md), [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md)
- Bridge: `list_sessions` / `open_session` / `delete_session`
