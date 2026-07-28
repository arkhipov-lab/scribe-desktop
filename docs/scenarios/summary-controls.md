# Scenario: Summary controls

## Goal

User shapes summary output via preset, length, summary language (under Processing options), and additional instructions; prefs persist locally. Transcript (Whisper) language stays in the primary flow; summary language defaults from the resolved UI locale and can be overridden under Processing options.

## Preconditions

- Transcript available for regenerate experiments
- Access to transcript language control and **Processing options**

## Flow

1. Confirm the primary flow shows **Transcript language** only (no summary-language control beside Transcribe).
2. Open Processing options; set **Summary language** independently if needed (e.g. Russian transcript, English summary).
3. Change summary preset and/or length; optionally set additional instructions.
4. Generate / Regenerate summary.
5. Quit and relaunch; confirm preferences restored from `settings.json` (both language fields when summary language was set or seeded).

## Expected behavior

- Whisper uses transcript language; summary prompts and section headings use summary language.
- On first launch (or when `summary_language` is absent from settings), summary language is seeded from the resolved UI locale (`en` / `ru` / system→navigator), mapped to a Whisper language code with fallback `en`.
- Already-persisted `summary_language` values are preserved (not rewritten from transcript language or from later UI locale changes).
- Output shape follows the selected preset/length intent.
- Settings stored in `~/Library/Application Support/Scribe/settings.json` without transcript/summary bodies.
- Additional-instructions text is **not** logged.
- Model lists come from the bridge/catalog — UI does not invent HF ids.

## Edge cases

- Empty additional instructions → default preset behavior.
- Older history sessions without `summary_language` fall back to stored transcript `language` when opened.
- Changing summary language does not clear an existing transcript; regenerate uses the new summary language.
- Changing UI locale after summary language is persisted does not auto-rewrite summary language.

## Future (not current acceptance)

Product Owner follow-up `PP-2026-07-27-002` (see ROADMAP + `.ai/state/product-followups.md`):

- Longer-term: fewer language selectors on the main path; auto-detect transcript language from audio when reliable on-device.

## Related docs / tests

- [LOCAL_DATA.md](../../LOCAL_DATA.md), [TESTING.md](../../TESTING.md) § A / § C / § D
- [PRODUCT.md](../../PRODUCT.md) design principles
