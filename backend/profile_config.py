"""Single-product app identity (Scribe)."""

from __future__ import annotations

import json
from pathlib import Path

APP_NAME = "Scribe"
DMG_BASENAME = "Scribe"
BUNDLE_ID = "local.scribe.app"


def get_app_name() -> str:
    return APP_NAME


def write_app_json(path: Path) -> None:
    """Bake minimal identity metadata into the .app Resources."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "app_name": APP_NAME,
                "bundle_id": BUNDLE_ID,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
