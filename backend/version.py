"""Resolve app semver from baked VERSION file (build) or repo root (dev)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


def _candidates() -> list[Path]:
    paths: list[Path] = []
    root = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if root:
        paths.append(Path(root) / "VERSION")
    here = Path(__file__).resolve().parent
    paths.append(here / "VERSION")
    paths.append(here.parent / "VERSION")
    return paths


@lru_cache(maxsize=1)
def get_app_version() -> str:
    for path in _candidates():
        if not path.is_file():
            continue
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    return "0.0.0"


def reset_version_cache() -> None:
    get_app_version.cache_clear()
