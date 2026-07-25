# Scenario: Privacy logging

## Goal

Application logs never contain transcript or summary bodies (nor additional-instructions content).

## Preconditions

- Fresh or known log file at `~/Library/Logs/Scribe/app.log`
- Ability to run a short transcribe + summary with distinctive spoken/written phrases

## Flow

1. Note current log size / rotate if needed for a clean window.
2. Transcribe a short clip containing a unique phrase; generate a summary with unique instructions if testing that path.
3. Search the log for that phrase and for substantial summary text.

## Expected behavior

- Log may contain paths, model ids, durations, status transitions, exception types.
- Log must **not** contain the transcript body, summary body, or additional-instructions body.
- Length/hash style diagnostics (`chars=%d`) are acceptable when present.

## Edge cases

- Error paths and cancel paths must also avoid dumping content.
- History save must not cause content logging.

## Related docs / tests

- [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) (authoritative), [TESTING.md](../../TESTING.md) § C–D
- [LOCAL_DATA.md](../../LOCAL_DATA.md) logs section
