# Scenario: Weak hardware defaults

## Goal

On first launch without `settings.json`, weaker Macs get lighter model defaults and auto-summary off; stronger Macs get heavier defaults and auto-summary on.

## Preconditions

- No existing `~/Library/Application Support/Scribe/settings.json` (back up then remove to re-probe)
- Know approximate machine class (see [SYSTEM-REQUIREMENTS.md](../../SYSTEM-REQUIREMENTS.md))

## Flow

1. Remove settings file (if testing probe).
2. Launch `./scripts/run-dev.sh`.
3. Open **Processing options**; note Whisper, summary model, auto-summary.
4. Confirm `settings.json` written with those choices.

## Expected behavior

| Mac class | Expect |
| --- | --- |
| Strong (M3+ with enough RAM) | Whisper medium, summary 3B, auto-summary on |
| Weak (M2− or &lt;~12 GB RAM) | Whisper small, summary 1.5B, auto-summary off |

- User can override afterward; overrides persist.
- Defaults come from `backend/hardware.py` + catalog — not hard-coded only in the UI.

## Edge cases

- Borderline RAM → follow probe implementation; document observed tier if surprising.
- 8 GB machines should prefer Small / 1.5B for full-pipeline smoke even if user later enables heavier models.

## Related docs / tests

- [SYSTEM-REQUIREMENTS.md](../../SYSTEM-REQUIREMENTS.md), [TESTING.md](../../TESTING.md) model defaults
- [LOCAL_DATA.md](../../LOCAL_DATA.md), [DECISIONS.md](../../DECISIONS.md) catalog decision
