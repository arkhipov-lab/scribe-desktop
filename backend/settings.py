"""Local user preferences (no cloud sync)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from languages import DEFAULT_LANGUAGE, normalize_language
from logger import get_logger, log_exception
from summary_presets import (
    DEFAULT_PRESET_ID,
    DEFAULT_SUMMARY_LENGTH,
    normalize_preset_id,
    normalize_summary_length,
)

SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "Scribe"
SETTINGS_PATH = SUPPORT_DIR / "settings.json"

_MAX_INSTRUCTIONS = 800

_lock = threading.Lock()


def default_settings() -> dict[str, Any]:
    return {
        "language": DEFAULT_LANGUAGE,
        "summary_preset": DEFAULT_PRESET_ID,
        "additional_instructions": "",
        "summary_length": DEFAULT_SUMMARY_LENGTH,
        "auto_summary": True,
    }


def _clamp_instructions(text: str) -> str:
    cleaned = (text or "").replace("\x00", "").strip()
    if len(cleaned) > _MAX_INSTRUCTIONS:
        return cleaned[:_MAX_INSTRUCTIONS]
    return cleaned


def normalize_settings(raw: dict[str, Any] | None) -> dict[str, Any]:
    base = default_settings()
    if not isinstance(raw, dict):
        return base

    language = raw.get("language", base["language"])
    try:
        language = normalize_language(str(language))
    except ValueError:
        language = base["language"]

    auto = raw.get("auto_summary", base["auto_summary"])
    if not isinstance(auto, bool):
        auto = bool(auto)

    return {
        "language": language,
        "summary_preset": normalize_preset_id(str(raw.get("summary_preset", ""))),
        "additional_instructions": _clamp_instructions(
            str(raw.get("additional_instructions", "") or "")
        ),
        "summary_length": normalize_summary_length(
            str(raw.get("summary_length", "") or "")
        ),
        "auto_summary": auto,
    }


def load_settings() -> dict[str, Any]:
    with _lock:
        if not SETTINGS_PATH.is_file():
            return default_settings()
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            log_exception("Failed to read settings.json")
            return default_settings()
        return normalize_settings(data if isinstance(data, dict) else None)


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_settings(settings)
    with _lock:
        try:
            SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
            tmp = SETTINGS_PATH.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            tmp.replace(SETTINGS_PATH)
        except OSError:
            log_exception("Failed to write settings.json")
            get_logger().warning("Could not persist settings to %s", SETTINGS_PATH)
            return normalized
    get_logger().info(
        "Settings saved (preset=%s length=%s auto_summary=%s)",
        normalized["summary_preset"],
        normalized["summary_length"],
        normalized["auto_summary"],
    )
    return normalized


def merge_settings(patch: dict[str, Any] | None) -> dict[str, Any]:
    current = load_settings()
    if not isinstance(patch, dict):
        return current
    merged = {**current, **patch}
    return save_settings(merged)
