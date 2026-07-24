"""Local user preferences (no cloud sync)."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from hardware import probe_hardware
from languages import DEFAULT_LANGUAGE, normalize_language
from logger import get_logger, log_exception
from model_catalog import (
    DEFAULT_SUMMARY_ID,
    DEFAULT_WHISPER_ID,
    WEAK_SUMMARY_ID,
    WEAK_WHISPER_ID,
    normalize_summary_model_id,
    normalize_whisper_id,
)
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
_defaults_logged = False


def recommended_model_defaults() -> dict[str, Any]:
    hw = probe_hardware()
    if hw.tier == "strong":
        return {
            "whisper_model": DEFAULT_WHISPER_ID,
            "summary_model": DEFAULT_SUMMARY_ID,
            "auto_summary": True,
            "performance_tier": hw.tier,
            "hardware_reason": hw.reason,
        }
    return {
        "whisper_model": WEAK_WHISPER_ID,
        "summary_model": WEAK_SUMMARY_ID,
        "auto_summary": False,
        "performance_tier": hw.tier,
        "hardware_reason": hw.reason,
    }


def default_settings() -> dict[str, Any]:
    rec = recommended_model_defaults()
    return {
        "language": DEFAULT_LANGUAGE,
        "summary_preset": DEFAULT_PRESET_ID,
        "additional_instructions": "",
        "summary_length": DEFAULT_SUMMARY_LENGTH,
        "auto_summary": bool(rec["auto_summary"]),
        "whisper_model": str(rec["whisper_model"]),
        "summary_model": str(rec["summary_model"]),
        "performance_tier": str(rec["performance_tier"]),
        "hardware_reason": str(rec["hardware_reason"]),
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

    # Missing model keys → hardware recommendation (first launch / migration).
    if "whisper_model" in raw:
        whisper_model = normalize_whisper_id(str(raw.get("whisper_model") or ""))
    else:
        whisper_model = base["whisper_model"]

    if "summary_model" in raw:
        summary_model = normalize_summary_model_id(str(raw.get("summary_model") or ""))
    else:
        summary_model = base["summary_model"]

    if "auto_summary" in raw:
        auto = raw.get("auto_summary")
        auto_summary = auto if isinstance(auto, bool) else bool(auto)
    else:
        auto_summary = base["auto_summary"]

    return {
        "language": language,
        "summary_preset": normalize_preset_id(str(raw.get("summary_preset", ""))),
        "additional_instructions": _clamp_instructions(
            str(raw.get("additional_instructions", "") or "")
        ),
        "summary_length": normalize_summary_length(
            str(raw.get("summary_length", "") or "")
        ),
        "auto_summary": auto_summary,
        "whisper_model": whisper_model,
        "summary_model": summary_model,
        "performance_tier": base["performance_tier"],
        "hardware_reason": base["hardware_reason"],
    }


def load_settings() -> dict[str, Any]:
    global _defaults_logged
    with _lock:
        if not SETTINGS_PATH.is_file():
            defaults = default_settings()
            if not _defaults_logged:
                get_logger().info(
                    "No settings.json yet — using %s defaults (%s)",
                    defaults["performance_tier"],
                    defaults["hardware_reason"],
                )
                _defaults_logged = True
            return defaults
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            log_exception("Failed to read settings.json")
            return default_settings()
        return normalize_settings(data if isinstance(data, dict) else None)


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_settings(settings)
    # Do not persist ephemeral hardware probe fields.
    to_store = {
        "language": normalized["language"],
        "summary_preset": normalized["summary_preset"],
        "additional_instructions": normalized["additional_instructions"],
        "summary_length": normalized["summary_length"],
        "auto_summary": normalized["auto_summary"],
        "whisper_model": normalized["whisper_model"],
        "summary_model": normalized["summary_model"],
    }
    with _lock:
        try:
            SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
            tmp = SETTINGS_PATH.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(to_store, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            tmp.replace(SETTINGS_PATH)
        except OSError:
            log_exception("Failed to write settings.json")
            get_logger().warning("Could not persist settings to %s", SETTINGS_PATH)
            return normalized
    get_logger().info(
        "Settings saved (whisper=%s summary=%s preset=%s length=%s auto_summary=%s)",
        normalized["whisper_model"],
        normalized["summary_model"],
        normalized["summary_preset"],
        normalized["summary_length"],
        normalized["auto_summary"],
    )
    return normalized


def ensure_settings_file() -> dict[str, Any]:
    """Create settings.json on first launch so hardware defaults stick."""
    with _lock:
        exists = SETTINGS_PATH.is_file()
    current = load_settings()
    if not exists:
        return save_settings(current)
    # Persist newly introduced model keys if an older settings file omitted them.
    raw: dict[str, Any] = {}
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return save_settings(current)
    if "whisper_model" not in raw or "summary_model" not in raw or "auto_summary" not in raw:
        return save_settings({**raw, **{
            "whisper_model": current["whisper_model"],
            "summary_model": current["summary_model"],
            "auto_summary": current["auto_summary"],
        }})
    return current


def merge_settings(patch: dict[str, Any] | None) -> dict[str, Any]:
    current = load_settings()
    if not isinstance(patch, dict):
        return current
    merged = {**current, **patch}
    return save_settings(merged)
