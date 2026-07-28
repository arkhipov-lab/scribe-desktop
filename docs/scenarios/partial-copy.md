# Scenario: Partial copy

## Goal

User copies transcript, full summary, or the Action items section to the clipboard without relying only on the active results tab or a full export file.

## Preconditions

- Transcript and/or summary present in the current session (from transcription, summary, or an opened history session)

## Flow

1. Open the results panel after transcription (and summary if available).
2. Click the **Copy** control to open the copy menu.
3. Choose **Copy transcript**, **Copy summary**, or **Copy action items**.
4. Paste elsewhere and confirm the clipboard matches the chosen content.

## Expected behavior

- **Copy transcript** copies the current plain-text transcript (including in-app edits).
- **Copy summary** copies the full Markdown summary text.
- **Copy action items** copies only the Action items section body when that section exists and is non-empty (localized headings such as “Action items” / “Задачи” / … are recognized).
- Menu items for missing content are disabled (or Action items shows unavailable feedback when the section is absent/empty).
- Copy works regardless of which results tab (Transcript / Summary) is active.
- Logs never contain transcript or summary bodies.

## Edge cases

- Transcript only (no summary) → Copy transcript enabled; Copy summary and Copy action items disabled.
- Summary without an Action items heading → Copy action items disabled.
- Empty Action items body (e.g. placeholder “None”) → Copy action items disabled.
- Open a history session → copy uses that session’s transcript/summary.
- Clipboard permission fallback still copies when the primary clipboard API fails (existing pattern).

## Related docs / tests

- [export-notes.md](./export-notes.md), [editable-transcript.md](./editable-transcript.md), [summary-generation.md](./summary-generation.md)
- [TESTING.md](../../TESTING.md) § C / § D / export
- Frontend: results Copy menu; `extractActionItems` helper
