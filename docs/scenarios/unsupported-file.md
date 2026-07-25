# Scenario: Unsupported file

## Goal

Unsupported media extensions fail clearly without crashing the app.

## Preconditions

- App running with bridge available
- A file with an unsupported extension (e.g. `.txt`, `.pdf`, `.flac` if not supported)

## Flow

1. Attempt to select or drop the unsupported file.
2. Observe error messaging and app state.

## Expected behavior

- Clear user-facing error (not a native crash, not a blank hang).
- Prior good session state is not silently corrupted in a surprising way (clearing vs keep — follow existing app behavior; must remain usable).
- Supported extensions list remains: `.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`.

## Edge cases

- Drop of mixed items → reject unsupported without accepting invalid paths.
- Path that exists but is unreadable → permission/IO error, not hang.

## Related docs / tests

- [TESTING.md](../../TESTING.md) § B, [AI_PIPELINE.md](../../AI_PIPELINE.md) ingest step
