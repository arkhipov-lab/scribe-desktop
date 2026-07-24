"""Build/runtime profile: standard (quality) vs lite (low memory)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppProfile:
    id: str
    app_name: str
    dmg_basename: str
    whisper_model: str
    summary_model: str
    # Slightly tighter generation on lite to reduce peak memory.
    summary_chunk_chars: int
    summary_max_tokens: int
    summary_merge_tokens: int


PROFILES: dict[str, AppProfile] = {
    "standard": AppProfile(
        id="standard",
        app_name="Scribe",
        dmg_basename="Scribe",
        whisper_model="mlx-community/whisper-medium-mlx",
        summary_model="mlx-community/Qwen2.5-3B-Instruct-4bit",
        summary_chunk_chars=7000,
        summary_max_tokens=900,
        summary_merge_tokens=1100,
    ),
    "lite": AppProfile(
        id="lite",
        app_name="Scribe Lite",
        dmg_basename="Scribe-Lite",
        whisper_model="mlx-community/whisper-small-mlx",
        summary_model="mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        summary_chunk_chars=5000,
        summary_max_tokens=700,
        summary_merge_tokens=900,
    ),
}

_cached: AppProfile | None = None


def _profile_path_candidates() -> list[Path]:
    paths: list[Path] = []
    root = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if root:
        paths.append(Path(root) / "profile.json")
    here = Path(__file__).resolve().parent
    paths.append(here / "profile.json")
    paths.append(here.parent / "profile.json")
    return paths


def _load_profile_id() -> str:
    env = (os.environ.get("SCRIBE_PROFILE") or "").strip().lower()
    if env in PROFILES:
        return env
    for path in _profile_path_candidates():
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            value = str(data.get("id") or data.get("profile") or "").strip().lower()
            if value in PROFILES:
                return value
        except Exception:
            continue
    return "standard"


def get_profile() -> AppProfile:
    global _cached
    if _cached is None:
        _cached = PROFILES[_load_profile_id()]
    return _cached


def reset_profile_cache() -> None:
    """Test helper."""
    global _cached
    _cached = None


def write_profile_json(path: Path, profile_id: str) -> None:
    profile = PROFILES[profile_id]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": profile.id,
                "app_name": profile.app_name,
                "whisper_model": profile.whisper_model,
                "summary_model": profile.summary_model,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
