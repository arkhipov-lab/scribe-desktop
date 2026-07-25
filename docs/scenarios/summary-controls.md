# Scenario: Summary controls

## Goal

User shapes summary output via preset, length, language-related settings, and additional instructions; prefs persist locally.

## Preconditions

- Transcript available for regenerate experiments
- Access to **Processing options** / summary controls

## Flow

1. Open Processing options.
2. Change summary preset and/or length; optionally set additional instructions.
3. Generate / Regenerate summary.
4. Quit and relaunch; confirm preferences restored from `settings.json`.

## Expected behavior

- Output shape follows the selected preset/length intent.
- Settings stored in `~/Library/Application Support/Scribe/settings.json` without transcript/summary bodies.
- Additional-instructions text is **not** logged.
- Model lists come from the bridge/catalog — UI does not invent HF ids.

## Edge cases

- Empty additional instructions → default preset behavior.
- Separate transcript vs summary language may still be roadmap ([ROADMAP.md](../../ROADMAP.md)) — do not assume shipped unless UI exposes it.

## Related docs / tests

- [LOCAL_DATA.md](../../LOCAL_DATA.md), [TESTING.md](../../TESTING.md) § D
- [PRODUCT.md](../../PRODUCT.md) design principles
