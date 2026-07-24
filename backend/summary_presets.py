"""Summary preset definitions for local note generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryPreset:
    id: str
    label: str
    sections: tuple[str, ...]
    instruction: str


# Section titles are English templates; meeting_notes also has localized headings
# in summarizer._SECTION_HEADINGS for common languages.
PRESETS: tuple[SummaryPreset, ...] = (
    SummaryPreset(
        id="meeting_notes",
        label="Meeting notes",
        sections=("Overview", "Decisions", "Action items", "Open questions"),
        instruction=(
            "Summarize as structured meeting notes. Capture what happened, "
            "decisions, concrete next steps, and unresolved questions."
        ),
    ),
    SummaryPreset(
        id="action_items",
        label="Action items only",
        sections=("Action items",),
        instruction=(
            "Extract only concrete next steps. Prefer owner and deadline when "
            "mentioned. Skip narrative overview."
        ),
    ),
    SummaryPreset(
        id="executive",
        label="Executive summary",
        sections=("Summary", "Key decisions", "Risks"),
        instruction=(
            "Write a brief executive brief for leadership. Emphasize outcomes, "
            "decisions, and material risks. Keep it short."
        ),
    ),
    SummaryPreset(
        id="customer_interview",
        label="Customer interview",
        sections=("Context", "Pain points", "Needs", "Quotes", "Follow-ups"),
        instruction=(
            "Structure notes from a customer or user interview. Prefer "
            "verbatim short quotes when useful. Do not invent quotes."
        ),
    ),
    SummaryPreset(
        id="lecture",
        label="Lecture / research notes",
        sections=("Main ideas", "Details", "Examples", "Open questions"),
        instruction=(
            "Capture learning notes: core ideas, supporting detail, examples, "
            "and questions to revisit later."
        ),
    ),
    SummaryPreset(
        id="cleaned_transcript",
        label="Cleaned transcript",
        sections=("Cleaned transcript",),
        instruction=(
            "Produce a lightly cleaned transcript: fix obvious filler and false "
            "starts, keep meaning and speaker intent. Do not add analysis "
            "sections beyond the cleaned text."
        ),
    ),
)

DEFAULT_PRESET_ID = "meeting_notes"
_PRESET_BY_ID = {p.id: p for p in PRESETS}

SUMMARY_LENGTHS = ("short", "normal", "detailed")
DEFAULT_SUMMARY_LENGTH = "normal"

# Relative to profile summary_max_tokens / summary_merge_tokens.
LENGTH_TOKEN_SCALE: dict[str, float] = {
    "short": 0.55,
    "normal": 1.0,
    "detailed": 1.45,
}


def get_preset(preset_id: str | None) -> SummaryPreset:
    key = (preset_id or "").strip() or DEFAULT_PRESET_ID
    return _PRESET_BY_ID.get(key, _PRESET_BY_ID[DEFAULT_PRESET_ID])


def normalize_preset_id(preset_id: str | None) -> str:
    return get_preset(preset_id).id


def normalize_summary_length(value: str | None) -> str:
    key = (value or "").strip().lower()
    if key in LENGTH_TOKEN_SCALE:
        return key
    return DEFAULT_SUMMARY_LENGTH


def presets_for_api() -> list[dict[str, str]]:
    return [{"id": p.id, "label": p.label} for p in PRESETS]


def token_limits(
    *,
    base_max: int,
    base_merge: int,
    length: str,
) -> tuple[int, int]:
    scale = LENGTH_TOKEN_SCALE.get(normalize_summary_length(length), 1.0)
    max_tokens = max(120, int(round(base_max * scale)))
    merge_tokens = max(160, int(round(base_merge * scale)))
    return max_tokens, merge_tokens
