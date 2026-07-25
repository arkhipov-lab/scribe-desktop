# Scenario: Cancel summary

## Goal

User can cancel summary generation without destroying an existing good transcript.

## Preconditions

- Transcript already present
- Summary started (auto or Generate), preferably on a longer transcript (map-reduce)

## Flow

1. Start summary.
2. Cancel while summarizing.
3. Confirm transcript still available; optionally Generate again.

## Expected behavior

- Existing transcript remains intact.
- Summary pane does not present a false “complete” result for a cancelled job.
- UI returns to a sane state; re-generate works.
- Log has no summary body.

## Edge cases

- Cancel between map-reduce stages vs near completion — both must be safe.
- Auto-summary cancelled → user can still Generate later.

## Related docs / tests

- [AI_PIPELINE.md](../../AI_PIPELINE.md), [TESTING.md](../../TESTING.md) § D
- [DECISIONS.md](../../DECISIONS.md) map-reduce decision
