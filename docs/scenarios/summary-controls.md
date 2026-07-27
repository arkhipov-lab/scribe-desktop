# Scenario: Summary controls

## Goal

User shapes summary output via preset, length, independent summary language, and additional instructions; prefs persist locally. Transcript (Whisper) language and summary language are separate controls.

## Preconditions

- Transcript available for regenerate experiments
- Access to transcript/summary language controls and **Processing options**

## Flow

1. Set **Transcript language** and **Summary language** independently (e.g. Russian transcript, English summary).
2. Open Processing options.
3. Change summary preset and/or length; optionally set additional instructions.
4. Generate / Regenerate summary.
5. Quit and relaunch; confirm preferences restored from `settings.json` (both language fields).

## Expected behavior

- Whisper uses transcript language; summary prompts and section headings use summary language.
- Output shape follows the selected preset/length intent.
- Settings stored in `~/Library/Application Support/Scribe/settings.json` without transcript/summary bodies.
- Missing `summary_language` in an older settings file seeds from `language` until the user changes it.
- Additional-instructions text is **not** logged.
- Model lists come from the bridge/catalog — UI does not invent HF ids.

## Edge cases

- Empty additional instructions → default preset behavior.
- Older history sessions without `summary_language` fall back to stored transcript `language` when opened.
- Changing summary language does not clear an existing transcript; regenerate uses the new summary language.

## Future (not current acceptance)

Product Owner follow-ups from iteration `2026-07-27-separate-languages` (see ROADMAP + `.ai/state/product-followups.md` `PP-2026-07-27-001` / `002`):

- Default summary language from system language; move summary-language control into Processing options.
- Longer-term: fewer language selectors on the main path; auto-detect transcript language from audio.

## Related docs / tests

- [LOCAL_DATA.md](../../LOCAL_DATA.md), [TESTING.md](../../TESTING.md) § C / § D
- [PRODUCT.md](../../PRODUCT.md) design principles
