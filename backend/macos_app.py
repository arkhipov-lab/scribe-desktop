"""macOS menu-bar identity and About panel (packaged .app)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from logger import get_logger, log_exception

# Shown under the version line in the system About panel.
ABOUT_BLURB = "On-device transcription and notes. Nothing leaves your Mac."


def _app_bundle_root() -> Path | None:
    """Return …/Scribe.app when launched from a packaged bundle."""
    root = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if root:
        resources = Path(root).resolve()
        # …/Scribe.app/Contents/Resources
        if resources.name == "Resources" and resources.parent.name == "Contents":
            return resources.parent.parent
    return None


def configure_macos_app(*, app_name: str, version: str) -> None:
    """
    Make the menu bar say Scribe and fill the standard About panel.

    Best results when launched from Scribe.app (SCRIBE_ROOT set). Dev `python app.py`
    may still show limited branding because mainBundle is Python.app.
    """
    if sys.platform != "darwin":
        return

    try:
        from AppKit import NSApplication, NSImage
        from Foundation import NSBundle, NSDictionary, NSProcessInfo
    except ImportError:
        return

    try:
        NSProcessInfo.processInfo().setProcessName_(app_name)
    except Exception:
        log_exception("Failed to set macOS process name")

    copyright_line = ABOUT_BLURB
    get_info = f"{app_name} {version} — {ABOUT_BLURB}"

    # Prefer keys from the real .app Info.plist when present.
    bundle_path = _app_bundle_root()
    if bundle_path is not None:
        plist_file = bundle_path / "Contents" / "Info.plist"
        if plist_file.is_file():
            try:
                packaged = NSDictionary.dictionaryWithContentsOfFile_(str(plist_file))
                if packaged:
                    copyright_line = str(
                        packaged.get("NSHumanReadableCopyright") or copyright_line
                    )
                    get_info = str(packaged.get("CFBundleGetInfoString") or get_info)
                    version = str(
                        packaged.get("CFBundleShortVersionString") or version
                    )
                    app_name = str(packaged.get("CFBundleName") or app_name)
            except Exception:
                log_exception("Failed to read packaged Info.plist")

    try:
        info = NSBundle.mainBundle().infoDictionary()
        if info is not None:
            info["CFBundleName"] = app_name
            info["CFBundleDisplayName"] = app_name
            info["CFBundleShortVersionString"] = version
            info["CFBundleVersion"] = version
            info["CFBundleGetInfoString"] = get_info
            info["NSHumanReadableCopyright"] = copyright_line
    except Exception:
        log_exception("Failed to patch mainBundle infoDictionary for About")

    try:
        app = NSApplication.sharedApplication()
        icon_path = None
        if bundle_path is not None:
            candidate = bundle_path / "Contents" / "Resources" / "AppIcon.icns"
            if candidate.is_file():
                icon_path = candidate
        if icon_path is not None:
            image = NSImage.alloc().initWithContentsOfFile_(str(icon_path))
            if image is not None:
                app.setApplicationIconImage_(image)
    except Exception:
        log_exception("Failed to set macOS application icon")

    get_logger().info(
        "macOS app identity configured (name=%s version=%s bundled=%s)",
        app_name,
        version,
        bundle_path is not None,
    )
