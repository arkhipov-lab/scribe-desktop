# Scenario: Export notes

## Goal

User exports transcript and/or summary to a local `.md` or `.txt` file they choose.

## Preconditions

- Transcript and/or summary present in the current session

## Flow

1. Trigger export (export notes action).
2. Choose destination via macOS save dialog.
3. Open the file in another app; confirm expected content.

## Expected behavior

- Export writes only to the user-selected path — no upload.
- Content matches what the user sees (within format differences), including an edited plain-text transcript.
- Does not require network.

## Edge cases

- Export with transcript only / summary only → sensible file, not empty crash.
- Cancel save dialog → no file written; app continues.

## Related docs / tests

- [PRODUCT.md](../../PRODUCT.md), [LOCAL_DATA.md](../../LOCAL_DATA.md)
- Api: `export_notes`
