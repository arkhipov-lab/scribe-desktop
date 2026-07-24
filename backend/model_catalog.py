"""Allowed Whisper / summary models for runtime selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelOption:
    id: str
    label: str
    huggingface_id: str
    hint: str


# IDs stay stable in settings.json; HF ids can evolve later.
WHISPER_MODELS: tuple[ModelOption, ...] = (
    ModelOption(
        id="small",
        label="Small",
        huggingface_id="mlx-community/whisper-small-mlx",
        hint="Faster, lower memory",
    ),
    ModelOption(
        id="medium",
        label="Medium",
        huggingface_id="mlx-community/whisper-medium-mlx",
        hint="Better accuracy, more memory",
    ),
)

SUMMARY_MODELS: tuple[ModelOption, ...] = (
    ModelOption(
        id="1.5b",
        label="1.5B",
        huggingface_id="mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        hint="Lighter notes model",
    ),
    ModelOption(
        id="3b",
        label="3B",
        huggingface_id="mlx-community/Qwen2.5-3B-Instruct-4bit",
        hint="Higher-quality notes",
    ),
)

# chunk_chars, max_tokens, merge_tokens — tighter caps on the smaller model.
_SUMMARY_TOKEN_PROFILES: dict[str, tuple[int, int, int]] = {
    "1.5b": (5000, 700, 900),
    "3b": (7000, 900, 1100),
}

_WHISPER_BY_ID = {m.id: m for m in WHISPER_MODELS}
_SUMMARY_BY_ID = {m.id: m for m in SUMMARY_MODELS}

DEFAULT_WHISPER_ID = "medium"
DEFAULT_SUMMARY_ID = "3b"
WEAK_WHISPER_ID = "small"
WEAK_SUMMARY_ID = "1.5b"


def normalize_whisper_id(value: str | None) -> str:
    key = (value or "").strip().lower()
    if key in _WHISPER_BY_ID:
        return key
    # Accept accidental full HF ids from older experiments.
    for option in WHISPER_MODELS:
        if key == option.huggingface_id.lower():
            return option.id
    return DEFAULT_WHISPER_ID


def normalize_summary_model_id(value: str | None) -> str:
    key = (value or "").strip().lower()
    if key in _SUMMARY_BY_ID:
        return key
    for option in SUMMARY_MODELS:
        if key == option.huggingface_id.lower():
            return option.id
    return DEFAULT_SUMMARY_ID


def whisper_hf_id(model_id: str | None) -> str:
    return _WHISPER_BY_ID[normalize_whisper_id(model_id)].huggingface_id


def summary_hf_id(model_id: str | None) -> str:
    return _SUMMARY_BY_ID[normalize_summary_model_id(model_id)].huggingface_id


def whisper_options_for_api() -> list[dict[str, str]]:
    return [
        {"id": m.id, "label": m.label, "hint": m.hint, "huggingface_id": m.huggingface_id}
        for m in WHISPER_MODELS
    ]


def summary_model_options_for_api() -> list[dict[str, str]]:
    return [
        {"id": m.id, "label": m.label, "hint": m.hint, "huggingface_id": m.huggingface_id}
        for m in SUMMARY_MODELS
    ]


def summary_token_profile(summary_model_id: str | None) -> tuple[int, int, int]:
    """chunk_chars, max_tokens, merge_tokens for the selected summary model."""
    sid = normalize_summary_model_id(summary_model_id)
    return _SUMMARY_TOKEN_PROFILES.get(sid, _SUMMARY_TOKEN_PROFILES[DEFAULT_SUMMARY_ID])
