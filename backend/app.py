"""Desktop shell: pywebview + React UI + mlx-whisper bridge."""

from __future__ import annotations

import base64
import mimetypes
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any

import webview

from logger import get_logger, log_exception, setup_logging
from languages import DEFAULT_LANGUAGE, WHISPER_LANGUAGES, languages_for_api, normalize_language
from macos_app import configure_macos_app
from memory import release_ml_memory
from profile_config import get_app_name
from recorder import CaptureRecorder, RecorderError, delete_path_quiet, is_temp_recording
from settings import ensure_settings_file, merge_settings, summary_language_persisted
from summarizer import (
    SummaryError,
    generate_session_title,
    summarize_transcript,
)
from summary_presets import presets_for_api
from model_catalog import (
    summary_hf_id,
    summary_model_options_for_api,
    whisper_hf_id,
    whisper_options_for_api,
)
from hardware import probe_hardware
from history import (
    delete_session as history_delete_session,
    list_sessions as history_list_sessions,
    load_session,
    update_session_summary,
    update_session_title,
    update_session_transcript,
    upsert_after_transcript,
)
from transcriber import (
    SUPPORTED_EXTENSIONS,
    TranscribeError,
    find_ffmpeg,
    transcribe_file,
    validate_audio_path,
)
from version import get_app_version

APP_NAME = get_app_name()
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 860

# Inline playback for WebView (file:// often blocked from http:// Vite origin).
_MAX_PLAYBACK_INLINE_BYTES = 80 * 1024 * 1024


def _format_export_notes(*, transcript: str, summary: str, fmt: str) -> str:
    """Build export body. Never log the returned text."""
    parts: list[str] = []
    as_md = fmt == "md"
    if transcript:
        if as_md:
            parts.append(f"## Transcript\n\n{transcript}")
        else:
            parts.append(f"Transcript\n==========\n\n{transcript}")
    if summary:
        if as_md:
            parts.append(f"## Summary\n\n{summary}")
        else:
            parts.append(f"Summary\n=======\n\n{summary}")
    return "\n\n".join(parts).rstrip() + "\n"


def _backend_dir() -> Path:
    return Path(__file__).resolve().parent


def _project_root() -> Path:
    # PyInstaller / bundled app: resources next to executable
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return _backend_dir().parent


def resolve_ui_url(dev_url: str | None = None) -> str:
    if dev_url:
        return dev_url

    candidates: list[Path] = []

    env_root = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if env_root:
        candidates.append(Path(env_root) / "frontend" / "dist" / "index.html")

    candidates.extend(
        [
            _project_root() / "frontend" / "dist" / "index.html",
            _backend_dir().parent / "frontend" / "dist" / "index.html",
            Path.cwd() / "frontend" / "dist" / "index.html",
        ]
    )

    if getattr(sys, "frozen", False):
        meipass = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        candidates.insert(0, meipass / "frontend" / "dist" / "index.html")
        exe = Path(sys.executable).resolve()
        resources = exe.parent.parent / "Resources"
        candidates.insert(0, resources / "frontend" / "dist" / "index.html")

    for path in candidates:
        if path.is_file():
            return path.resolve().as_uri()

    raise FileNotFoundError(
        "Frontend build not found. Run the Vite build or ./scripts/run-dev.sh first."
    )


class Api:
    """JavaScript API exposed to the React UI."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._summary_cancel = threading.Event()
        self._worker: threading.Thread | None = None
        self._summary_worker: threading.Thread | None = None
        prefs = ensure_settings_file()
        self._state: dict[str, Any] = {
            "status": "idle",
            "message": "Drop an audio file, select a file, or record notes.",
            "file_path": None,
            "file_name": None,
            "language": prefs["language"],
            "summary_language": prefs["summary_language"],
            "summary_language_persisted": summary_language_persisted(),
            "transcript": "",
            "transcript_epoch": 0,
            "summary": "",
            "summary_status": "idle",
            "summary_error": None,
            "error": None,
            "elapsed_seconds": 0.0,
            "started_at": None,
            "summary_preset": prefs["summary_preset"],
            "additional_instructions": prefs["additional_instructions"],
            "summary_length": prefs["summary_length"],
            "auto_summary": prefs["auto_summary"],
            "whisper_model": prefs["whisper_model"],
            "summary_model": prefs["summary_model"],
            "performance_tier": prefs.get("performance_tier"),
            "hardware_reason": prefs.get("hardware_reason"),
            "session_id": None,
            "session_title": None,
            "history_sidebar_open": bool(prefs.get("history_sidebar_open", True)),
            "used_language": None,
            "used_summary_language": None,
            "used_whisper_model": None,
            "used_summary_model": None,
            "used_summary_preset": None,
            "used_summary_length": None,
            "used_has_extra_instructions": False,
        }
        self._timer_stop = threading.Event()
        self._timer_thread: threading.Thread | None = None
        self._recorder = CaptureRecorder()
        self._owned_temp_path: str | None = None
        self.logger = get_logger()

    def _prefs_from_state(self) -> dict[str, Any]:
        snap = self._snapshot()
        return {
            "language": snap.get("language") or DEFAULT_LANGUAGE,
            "summary_language": snap.get("summary_language")
            or DEFAULT_LANGUAGE,
            "summary_preset": snap.get("summary_preset"),
            "additional_instructions": snap.get("additional_instructions") or "",
            "summary_length": snap.get("summary_length"),
            "auto_summary": bool(snap.get("auto_summary", True)),
            "whisper_model": snap.get("whisper_model"),
            "summary_model": snap.get("summary_model"),
            "history_sidebar_open": bool(snap.get("history_sidebar_open", True)),
        }

    def _apply_prefs(self, prefs: dict[str, Any]) -> None:
        self._update(
            language=prefs["language"],
            summary_language=prefs["summary_language"],
            summary_language_persisted=summary_language_persisted(),
            summary_preset=prefs["summary_preset"],
            additional_instructions=prefs["additional_instructions"],
            summary_length=prefs["summary_length"],
            auto_summary=prefs["auto_summary"],
            whisper_model=prefs["whisper_model"],
            summary_model=prefs["summary_model"],
            history_sidebar_open=bool(prefs.get("history_sidebar_open", True)),
            performance_tier=prefs.get("performance_tier"),
            hardware_reason=prefs.get("hardware_reason"),
        )

    def _snapshot(self) -> dict[str, Any]:
        with self._lock:
            data = dict(self._state)
            started = data.get("started_at")
            if started and data["status"] in {
                "loading_model",
                "transcribing",
                "recording",
            }:
                data["elapsed_seconds"] = round(time.time() - float(started), 1)
            return data

    def _update(self, **kwargs: Any) -> None:
        with self._lock:
            if "transcript" in kwargs and "transcript_epoch" not in kwargs:
                kwargs = {
                    **kwargs,
                    "transcript_epoch": int(self._state.get("transcript_epoch") or 0) + 1,
                }
            self._state.update(kwargs)

    def _discard_owned_temp(self, *, keep: str | None = None) -> None:
        owned = self._owned_temp_path
        if not owned:
            return
        if keep and Path(owned).resolve() == Path(keep).resolve():
            return
        delete_path_quiet(owned)
        self._owned_temp_path = None

    def _persist_after_transcript(self, transcript: str) -> None:
        snap = self._snapshot()
        language = str(snap.get("language") or DEFAULT_LANGUAGE)
        whisper_model = str(snap.get("whisper_model") or "")
        # Reflect what actually ran, even if history write fails.
        self._update(
            used_language=language,
            used_summary_language=None,
            used_whisper_model=whisper_model,
            used_summary_model=None,
            used_summary_preset=None,
            used_summary_length=None,
            used_has_extra_instructions=False,
        )
        try:
            entry = upsert_after_transcript(
                session_id=snap.get("session_id"),
                transcript=transcript,
                audio_path=snap.get("file_path"),
                source_name=snap.get("file_name"),
                language=language,
                whisper_model=whisper_model,
                clear_summary=True,
            )
            self._update(
                session_id=entry["id"],
                session_title=entry.get("title"),
            )
        except Exception:
            log_exception("Failed to persist history after transcript")

    def _persist_summary(self, summary: str) -> None:
        snap = self._snapshot()
        summary_model = str(snap.get("summary_model") or "")
        summary_preset = str(snap.get("summary_preset") or "")
        summary_length = str(snap.get("summary_length") or "")
        summary_language = str(
            snap.get("summary_language") or snap.get("language") or DEFAULT_LANGUAGE
        )
        has_extra = bool(str(snap.get("additional_instructions") or "").strip())
        self._update(
            used_summary_language=summary_language,
            used_summary_model=summary_model,
            used_summary_preset=summary_preset,
            used_summary_length=summary_length,
            used_has_extra_instructions=has_extra,
        )
        sid = snap.get("session_id")
        if not sid:
            return
        try:
            entry = update_session_summary(
                str(sid),
                summary,
                summary_model=summary_model,
                summary_preset=summary_preset,
                summary_length=summary_length,
                summary_language=summary_language,
                has_extra_instructions=has_extra,
            )
            if entry:
                self._update(session_title=entry.get("title") or snap.get("session_title"))
        except Exception:
            log_exception("Failed to persist history summary")

    def _refresh_session_title(self, transcript: str, *, unload_after: bool) -> None:
        snap = self._snapshot()
        sid = snap.get("session_id")
        if not sid:
            return
        language = str(snap.get("language") or DEFAULT_LANGUAGE)
        language_name = WHISPER_LANGUAGES.get(language, language)
        fallback = str(snap.get("file_name") or "New Transcript")
        if fallback.lower().endswith((".wav", ".m4a", ".mp3", ".mp4", ".mov")):
            fallback = Path(fallback).stem or "New Transcript"
        summary_hf = summary_hf_id(str(snap.get("summary_model") or ""))
        try:
            title = generate_session_title(
                transcript,
                language_name=language_name,
                model=summary_hf,
                fallback=fallback,
                unload_after=unload_after,
            )
            entry = update_session_title(str(sid), title)
            if entry:
                self._update(session_title=entry.get("title"))
        except Exception:
            log_exception("Failed to refresh history title")

    def get_state(self) -> dict[str, Any]:
        return self._snapshot()

    def update_transcript(
        self, text: Any = None, based_on_epoch: Any = None
    ) -> dict[str, Any]:
        """Persist user-edited plain-text transcript (does not clear summary)."""
        if text is None or not isinstance(text, str):
            return self._snapshot() | {"ok": False, "error": "Invalid transcript."}
        state = self._snapshot()
        if state["status"] in {"loading_model", "transcribing", "recording"}:
            return state | {
                "ok": False,
                "error": "Cannot edit transcript while transcription or recording is running.",
            }
        current_epoch = int(state.get("transcript_epoch") or 0)
        if based_on_epoch is not None:
            try:
                expected = int(based_on_epoch)
            except (TypeError, ValueError):
                return state | {"ok": False, "error": "Invalid transcript epoch."}
            if expected != current_epoch:
                return state | {
                    "ok": False,
                    "error": "Transcript changed; edit discarded.",
                }
        cleaned = text.replace("\x00", "")
        self._update(transcript=cleaned)
        sid = self._snapshot().get("session_id")
        if sid:
            try:
                entry = update_session_transcript(str(sid), cleaned)
                if entry:
                    self._update(session_title=entry.get("title") or state.get("session_title"))
            except Exception:
                log_exception("Failed to persist edited transcript to history")
        self.logger.info(
            "Transcript updated by user: chars=%s session=%s epoch=%s",
            len(cleaned),
            sid or "none",
            int(self._snapshot().get("transcript_epoch") or 0),
        )
        return self._snapshot() | {"ok": True}

    def get_supported_extensions(self) -> list[str]:
        return sorted(SUPPORTED_EXTENSIONS)

    def get_model_name(self) -> str:
        snap = self._snapshot()
        return whisper_hf_id(str(snap.get("whisper_model") or ""))

    def get_summary_model_name(self) -> str:
        snap = self._snapshot()
        return summary_hf_id(str(snap.get("summary_model") or ""))

    def get_app_info(self) -> dict[str, str]:
        snap = self._snapshot()
        return {
            "app_name": APP_NAME,
            "version": get_app_version(),
            "whisper_model": whisper_hf_id(str(snap.get("whisper_model") or "")),
            "summary_model": summary_hf_id(str(snap.get("summary_model") or "")),
            "performance_tier": str(snap.get("performance_tier") or ""),
            "hardware_reason": str(snap.get("hardware_reason") or ""),
        }

    def _clear_summary_fields(self) -> None:
        self._summary_cancel.set()
        self._update(
            summary="",
            summary_status="idle",
            summary_error=None,
        )
    def check_ffmpeg(self) -> dict[str, Any]:
        path = find_ffmpeg()
        if path is None:
            return {
                "ok": False,
                "path": None,
                "message": "ffmpeg not found. Install ffmpeg with: brew install ffmpeg",
            }
        return {"ok": True, "path": str(path), "message": ""}

    def select_file(self) -> dict[str, Any]:
        window = webview.active_window()
        if window is None and webview.windows:
            window = webview.windows[0]
        if window is None:
            return {"ok": False, "error": "Window is not ready."}

        # pywebview requires: "Description (*.ext;*.ext2)" — description may only
        # contain word chars and spaces (no '/', '-', etc.).
        file_types = (
            "Audio Video (*.m4a;*.mp3;*.wav;*.mp4;*.mov)",
            "All files (*.*)",
        )
        try:
            result = window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=file_types,
            )
        except ValueError as exc:
            self.logger.error("File dialog filter error: %s", exc)
            return self._snapshot() | {
                "ok": False,
                "error": "Could not open the file dialog.",
            }
        if not result:
            return self._snapshot() | {"ok": False, "cancelled": True}

        path = result[0] if isinstance(result, (list, tuple)) else str(result)
        return self.set_file_path(str(path))

    def save_audio_copy(self) -> dict[str, Any]:
        """Copy the current audio file to a user-chosen path. Does not change ownership/deletion."""
        state = self._snapshot()
        src = state.get("file_path")
        if not src:
            return state | {"ok": False, "error": "No audio file to save."}
        if state["status"] == "recording":
            return state | {"ok": False, "error": "Stop recording before saving."}

        source = Path(str(src)).expanduser().resolve()
        if not source.is_file():
            return state | {"ok": False, "error": "Current audio file is missing."}

        window = webview.active_window()
        if window is None and webview.windows:
            window = webview.windows[0]
        if window is None:
            return state | {"ok": False, "error": "Window is not ready."}

        suffix = source.suffix.lower() or ".wav"
        suggested = source.name or f"recording{suffix}"
        file_types = (
            f"Audio (*.{suffix.lstrip('.')})",
            "All files (*.*)",
        )
        try:
            result = window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=suggested,
                file_types=file_types,
            )
        except ValueError as exc:
            self.logger.error("Save dialog filter error: %s", exc)
            return state | {"ok": False, "error": "Could not open the save dialog."}

        if not result:
            return state | {"ok": False, "cancelled": True}

        dest_raw = result[0] if isinstance(result, (list, tuple)) else str(result)
        dest = Path(str(dest_raw)).expanduser()
        if not dest.suffix:
            dest = dest.with_suffix(suffix)

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        except OSError as exc:
            log_exception("Failed to save audio copy")
            return state | {
                "ok": False,
                "error": f"Could not save the file: {exc.strerror or exc}",
            }

        self.logger.info("Saved audio copy: %s -> %s", source, dest)
        self._update(message=f"Saved copy: {dest.name}", error=None)
        return self._snapshot() | {
            "ok": True,
            "saved_path": str(dest),
        }

    def get_playback_src(self) -> dict[str, Any]:
        """Return a playable audio source for the current file (never log bytes)."""
        state = self._snapshot()
        raw = state.get("file_path")
        if not raw:
            return {"ok": False, "error": "No audio file to play."}
        path = Path(str(raw)).expanduser().resolve()
        if not path.is_file():
            return {"ok": False, "error": "Audio file is missing."}

        mime, _ = mimetypes.guess_type(str(path))
        suffix = path.suffix.lower()
        if not mime:
            mime = {
                ".wav": "audio/wav",
                ".mp3": "audio/mpeg",
                ".m4a": "audio/mp4",
                ".mp4": "audio/mp4",
                ".mov": "video/quicktime",
            }.get(suffix, "application/octet-stream")

        try:
            size = path.stat().st_size
        except OSError as exc:
            log_exception("Failed to stat audio for playback")
            return {
                "ok": False,
                "error": f"Could not read the audio file: {exc.strerror or exc}",
            }

        if size <= 0:
            return {"ok": False, "error": "Audio file is empty."}
        if size > _MAX_PLAYBACK_INLINE_BYTES:
            return {
                "ok": False,
                "error": "This file is too large to preview in-app. Use Save copy to open it elsewhere.",
            }

        try:
            raw_bytes = path.read_bytes()
        except OSError as exc:
            log_exception("Failed to read audio for playback")
            return {
                "ok": False,
                "error": f"Could not read the audio file: {exc.strerror or exc}",
            }

        encoded = base64.b64encode(raw_bytes).decode("ascii")
        self.logger.info(
            "Prepared playback src: path=%s mime=%s bytes=%s",
            path,
            mime,
            size,
        )
        return {
            "ok": True,
            "mime": mime,
            "data_base64": encoded,
            "size": size,
        }

    def export_notes(self) -> dict[str, Any]:
        """Save transcript and/or summary via a Save dialog (.md or .txt)."""
        state = self._snapshot()
        transcript = str(state.get("transcript") or "").strip()
        summary = str(state.get("summary") or "").strip()
        if not transcript and not summary:
            return state | {"ok": False, "error": "Nothing to export yet."}

        window = webview.active_window()
        if window is None and webview.windows:
            window = webview.windows[0]
        if window is None:
            return state | {"ok": False, "error": "Window is not ready."}

        stem = "scribe-notes"
        file_name = state.get("file_name")
        if file_name:
            stem = Path(str(file_name)).stem or stem
        suggested = f"{stem}-notes.md"
        file_types = (
            "Markdown (*.md)",
            "Plain text (*.txt)",
        )
        try:
            result = window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=suggested,
                file_types=file_types,
            )
        except ValueError as exc:
            self.logger.error("Export dialog filter error: %s", exc)
            return state | {"ok": False, "error": "Could not open the save dialog."}

        if not result:
            return state | {"ok": False, "cancelled": True}

        dest_raw = result[0] if isinstance(result, (list, tuple)) else str(result)
        dest = Path(str(dest_raw)).expanduser()
        suffix = dest.suffix.lower()
        if suffix not in {".md", ".txt"}:
            dest = dest.with_suffix(".md")
            suffix = ".md"

        body = _format_export_notes(transcript=transcript, summary=summary, fmt=suffix[1:])
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")
        except OSError as exc:
            log_exception("Failed to export notes")
            return state | {
                "ok": False,
                "error": f"Could not save the file: {exc.strerror or exc}",
            }

        self.logger.info(
            "Exported notes: path=%s format=%s has_transcript=%s has_summary=%s",
            dest,
            suffix,
            bool(transcript),
            bool(summary),
        )
        self._update(message=f"Exported: {dest.name}", error=None)
        return self._snapshot() | {
            "ok": True,
            "saved_path": str(dest),
        }

    def set_file_path(self, file_path: str) -> dict[str, Any]:
        if self._snapshot()["status"] == "recording":
            return self._snapshot() | {
                "ok": False,
                "error": "Stop recording before selecting another file.",
            }
        if str(self._snapshot().get("transcript") or "").strip():
            return self._snapshot() | {
                "ok": False,
                "error": "Audio is locked after transcription. Start a New Transcript to replace it.",
            }
        try:
            path = validate_audio_path(file_path)
        except TranscribeError as exc:
            self._update(error=exc.message, status="error", message=exc.message)
            return self._snapshot() | {"ok": False, "error": exc.message}

        self._discard_owned_temp(keep=str(path))
        self._owned_temp_path = str(path) if is_temp_recording(path) else None

        self._clear_summary_fields()
        self._update(
            status="ready",
            message=f"Ready: {path.name}",
            file_path=str(path),
            file_name=path.name,
            transcript="",
            error=None,
            elapsed_seconds=0.0,
            started_at=None,
            session_id=None,
            session_title=None,
        )
        self.logger.info("File selected: %s", path)
        return self._snapshot() | {"ok": True}

    def start_recording(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] in {"loading_model", "transcribing", "recording"}:
            return state | {"ok": False, "error": "Cannot start recording right now."}
        if str(state.get("transcript") or "").strip():
            return state | {
                "ok": False,
                "error": "Audio is locked after transcription. Start a New Transcript to record again.",
            }

        ffmpeg = self.check_ffmpeg()
        if not ffmpeg["ok"]:
            self._update(
                status="error",
                error=ffmpeg["message"],
                message=ffmpeg["message"],
            )
            return self._snapshot() | {"ok": False, "error": ffmpeg["message"]}

        try:
            self._recorder.start()
        except RecorderError as exc:
            self._update(status="error", error=exc.message, message=exc.message)
            return self._snapshot() | {"ok": False, "error": exc.message}
        except Exception:
            log_exception("Unexpected recorder start failure")
            message = "Could not start recording. See the log for details."
            self._update(status="error", error=message, message=message)
            return self._snapshot() | {"ok": False, "error": message}

        self._update(
            status="recording",
            message="Recording microphone and system audio…",
            error=None,
            transcript="",
            summary="",
            summary_status="idle",
            summary_error=None,
            elapsed_seconds=0.0,
            started_at=time.time(),
        )
        return self._snapshot() | {"ok": True}

    def stop_recording(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] != "recording":
            return state | {"ok": False, "error": "Nothing is recording."}

        self._update(message="Finalizing recording…")
        try:
            mixed = self._recorder.stop()
        except RecorderError as exc:
            self._update(
                status="error",
                error=exc.message,
                message=exc.message,
                started_at=None,
            )
            return self._snapshot() | {"ok": False, "error": exc.message}
        except Exception:
            log_exception("Unexpected recorder stop failure")
            message = "Could not finalize recording. See the log for details."
            self._update(status="error", error=message, message=message, started_at=None)
            return self._snapshot() | {"ok": False, "error": message}

        # Leave "recording" before adopting the file — set_file_path rejects
        # selections while status is still recording.
        self._update(
            status="idle",
            message="Processing recording…",
            started_at=None,
            elapsed_seconds=0.0,
        )
        return self.set_file_path(str(mixed))

    def set_language(self, language: str) -> dict[str, Any]:
        try:
            lang = normalize_language(language)
        except ValueError:
            return self._snapshot() | {
                "ok": False,
                "error": "Unsupported language. Choose a language from the list.",
            }
        prefs = merge_settings({**self._prefs_from_state(), "language": lang})
        self._apply_prefs(prefs)
        return self._snapshot() | {"ok": True}

    def get_languages(self) -> list[dict[str, str]]:
        return languages_for_api()

    def get_summary_presets(self) -> list[dict[str, str]]:
        return presets_for_api()

    def get_whisper_models(self) -> list[dict[str, str]]:
        return whisper_options_for_api()

    def get_summary_models(self) -> list[dict[str, str]]:
        return summary_model_options_for_api()

    def get_hardware_info(self) -> dict[str, Any]:
        hw = probe_hardware()
        return {
            "memory_gb": hw.memory_gb,
            "chip_generation": hw.chip_generation,
            "chip_name": hw.chip_name,
            "tier": hw.tier,
            "reason": hw.reason,
        }

    def get_settings(self) -> dict[str, Any]:
        return self._prefs_from_state()

    def update_settings(self, patch: dict[str, Any] | None = None) -> dict[str, Any]:
        if not isinstance(patch, dict):
            return self._snapshot() | {"ok": False, "error": "Invalid settings."}
        allowed = {
            "language",
            "summary_language",
            "summary_preset",
            "additional_instructions",
            "summary_length",
            "auto_summary",
            "whisper_model",
            "summary_model",
            "history_sidebar_open",
        }
        clean = {k: patch[k] for k in allowed if k in patch}
        if not clean:
            return self._snapshot() | {"ok": False, "error": "No settings to update."}
        prefs = merge_settings({**self._prefs_from_state(), **clean})
        self._apply_prefs(prefs)
        return self._snapshot() | {"ok": True}

    def start_transcription(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] in {"loading_model", "transcribing", "recording"}:
            return state | {"ok": False, "error": "Transcription already running."}

        file_path = state.get("file_path")
        if not file_path:
            self._update(
                status="error",
                error="No file selected.",
                message="No file selected.",
            )
            return self._snapshot() | {"ok": False, "error": "No file selected."}

        ffmpeg = self.check_ffmpeg()
        if not ffmpeg["ok"]:
            self._update(
                status="error",
                error=ffmpeg["message"],
                message=ffmpeg["message"],
            )
            return self._snapshot() | {"ok": False, "error": ffmpeg["message"]}

        self._cancel.clear()
        self._clear_summary_fields()
        self._update(
            status="loading_model",
            message="Preparing transcription…",
            transcript="",
            error=None,
            elapsed_seconds=0.0,
            started_at=time.time(),
        )
        self._start_elapsed_timer()

        language = self._snapshot().get("language") or DEFAULT_LANGUAGE
        whisper_id = str(self._snapshot().get("whisper_model") or "")
        whisper_hf = whisper_hf_id(whisper_id)
        self.logger.info(
            "UI requested transcription: path=%s language=%s model=%s",
            file_path,
            language,
            whisper_hf,
        )

        def worker() -> None:
            def on_status(status: str, message: str) -> None:
                if self._cancel.is_set():
                    return
                self._update(status=status, message=message, error=None)

            try:
                result = transcribe_file(
                    str(file_path),
                    str(language),
                    model=whisper_hf,
                    on_status=on_status,
                    should_cancel=self._cancel.is_set,
                )
                if self._cancel.is_set():
                    self._update(
                        status="ready" if file_path else "idle",
                        message="Transcription cancelled.",
                        error=None,
                        started_at=None,
                    )
                    return

                self._update(
                    status="completed",
                    message="Transcription complete.",
                    transcript=result.text,
                    error=None,
                    elapsed_seconds=round(result.duration_seconds, 1),
                    started_at=None,
                )
                self._persist_after_transcript(result.text)
                release_ml_memory("before summary")
                if bool(self._snapshot().get("auto_summary", True)):
                    self._begin_summary(result.text)
                else:
                    self._refresh_session_title(result.text, unload_after=True)
                    self._update(
                        message="Transcription complete.",
                        summary_status="idle",
                    )
            except TranscribeError as exc:
                if "cancelled" in exc.message.lower():
                    snap = self._snapshot()
                    self._update(
                        status="ready" if snap.get("file_path") else "idle",
                        message="Transcription cancelled.",
                        error=None,
                        started_at=None,
                    )
                else:
                    self._update(
                        status="error",
                        message=exc.message,
                        error=exc.message,
                        started_at=None,
                    )
            except Exception:
                log_exception("Unexpected transcription failure")
                self._update(
                    status="error",
                    message="Transcription failed. See the log for details.",
                    error="Transcription failed. See the log for details.",
                    started_at=None,
                )
            finally:
                self._stop_elapsed_timer()

        self._worker = threading.Thread(target=worker, daemon=True, name="transcribe")
        self._worker.start()
        return self._snapshot() | {"ok": True}

    def cancel_transcription(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] not in {"loading_model", "transcribing"}:
            return state | {"ok": False, "error": "Nothing to cancel."}
        self._cancel.set()
        self._update(message="Cancelling…")
        self.logger.info("Cancel requested")
        return self._snapshot() | {"ok": True}

    def start_summary(self) -> dict[str, Any]:
        """Regenerate summary from the current transcript."""
        state = self._snapshot()
        if state["summary_status"] in {"loading_model", "summarizing"}:
            return state | {"ok": False, "error": "Summary already running."}
        transcript = (state.get("transcript") or "").strip()
        if not transcript:
            return state | {"ok": False, "error": "No transcript to summarize."}
        self._begin_summary(transcript)
        return self._snapshot() | {"ok": True}

    def cancel_summary(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["summary_status"] not in {"loading_model", "summarizing"}:
            return state | {"ok": False, "error": "Nothing to cancel."}
        self._summary_cancel.set()
        self._update(summary_error=None)
        self.logger.info("Summary cancel requested")
        return self._snapshot() | {"ok": True}

    def _begin_summary(self, transcript: str) -> None:
        self._summary_cancel.clear()
        self._update(
            summary="",
            summary_status="loading_model",
            summary_error=None,
        )
        snap = self._snapshot()
        language = str(
            snap.get("summary_language") or snap.get("language") or DEFAULT_LANGUAGE
        )
        language_name = WHISPER_LANGUAGES.get(language, language)
        preset_id = str(snap.get("summary_preset") or "")
        additional = str(snap.get("additional_instructions") or "")
        summary_length = str(snap.get("summary_length") or "")
        summary_model_id = str(snap.get("summary_model") or "")
        summary_hf = summary_hf_id(summary_model_id)
        self.logger.info(
            "Starting summary worker (%s chars, language=%s preset=%s length=%s model=%s)",
            len(transcript),
            language_name,
            preset_id or "meeting_notes",
            summary_length or "normal",
            summary_hf,
        )

        def worker() -> None:
            def on_status(status: str, message: str) -> None:
                if self._summary_cancel.is_set():
                    return
                # Keep transcription status untouched; only update summary fields.
                # Surface progress lightly in the main message when idle/completed.
                current = self._snapshot()
                patch: dict[str, Any] = {
                    "summary_status": status,
                    "summary_error": None,
                }
                if current.get("status") in {"completed", "ready"}:
                    patch["message"] = message
                self._update(**patch)

            try:
                result = summarize_transcript(
                    transcript,
                    language=language,
                    language_name=language_name,
                    preset_id=preset_id,
                    additional_instructions=additional,
                    summary_length=summary_length,
                    model=summary_hf,
                    on_status=on_status,
                    should_cancel=self._summary_cancel.is_set,
                    unload_after=False,
                )
                if self._summary_cancel.is_set():
                    self._update(
                        summary_status="idle",
                        summary="",
                        summary_error=None,
                        message="Summary cancelled.",
                    )
                    release_ml_memory("after cancelled summary")
                    return
                self._update(
                    summary=result.text,
                    summary_status="completed",
                    summary_error=None,
                    message="Transcription complete. Summary ready.",
                )
                self._persist_summary(result.text)
                self._refresh_session_title(transcript, unload_after=True)
            except SummaryError as exc:
                release_ml_memory("after summary error")
                if "cancelled" in exc.message.lower():
                    self._update(
                        summary_status="idle",
                        summary="",
                        summary_error=None,
                        message="Summary cancelled.",
                    )
                else:
                    self._update(
                        summary_status="error",
                        summary_error=exc.message,
                        message=exc.message,
                    )
                # Still try a title if we have a session from transcript.
                if self._snapshot().get("session_id") and "cancelled" not in exc.message.lower():
                    self._refresh_session_title(transcript, unload_after=True)
            except Exception:
                release_ml_memory("after summary failure")
                log_exception("Unexpected summary failure")
                message = "Summarization failed. See the log for details."
                self._update(
                    summary_status="error",
                    summary_error=message,
                    message=message,
                )
                if self._snapshot().get("session_id"):
                    self._refresh_session_title(transcript, unload_after=True)

        self._summary_worker = threading.Thread(
            target=worker, daemon=True, name="summarize"
        )
        self._summary_worker.start()

    def list_sessions(self) -> list[dict[str, Any]]:
        try:
            return history_list_sessions()
        except Exception:
            log_exception("Failed to list history sessions")
            return []

    def open_session(self, session_id: str) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] in {"loading_model", "transcribing", "recording"}:
            return state | {"ok": False, "error": "Finish the current job before opening history."}
        if state["summary_status"] in {"loading_model", "summarizing"}:
            return state | {"ok": False, "error": "Finish the summary before opening history."}

        payload = load_session(str(session_id or ""))
        if payload is None:
            return self._snapshot() | {"ok": False, "error": "Session not found."}

        meta = payload["meta"]
        audio = payload.get("audio_path")
        source = payload.get("source_path")
        file_path = None
        for candidate in (audio, source):
            if candidate and Path(str(candidate)).is_file():
                file_path = str(Path(str(candidate)).resolve())
                break

        self._cancel.set()
        self._summary_cancel.set()
        self._discard_owned_temp()
        # History audio is not a disposable temp recording.
        self._owned_temp_path = None

        transcript = str(payload.get("transcript") or "")
        summary = str(payload.get("summary") or "")
        file_name = meta.get("source_name")
        if file_path and not file_name:
            file_name = Path(file_path).name

        status = "completed" if transcript.strip() else ("ready" if file_path else "idle")
        message = (
            f"Opened: {meta.get('title') or file_name or 'session'}"
            if transcript.strip() or file_path
            else "Session opened."
        )
        self._update(
            status=status,
            message=message,
            file_path=file_path,
            file_name=file_name,
            language=meta.get("language") or self._snapshot().get("language"),
            summary_language=(
                meta.get("summary_language")
                or meta.get("language")
                or self._snapshot().get("summary_language")
                or self._snapshot().get("language")
            ),
            transcript=transcript,
            summary=summary,
            summary_status="completed" if summary.strip() else "idle",
            summary_error=None,
            error=None,
            elapsed_seconds=0.0,
            started_at=None,
            session_id=meta.get("id"),
            session_title=meta.get("title"),
            summary_preset=meta.get("summary_preset") or self._snapshot().get("summary_preset"),
            summary_length=meta.get("summary_length") or self._snapshot().get("summary_length"),
            whisper_model=meta.get("whisper_model") or self._snapshot().get("whisper_model"),
            summary_model=meta.get("summary_model") or self._snapshot().get("summary_model"),
            used_language=meta.get("language"),
            used_summary_language=meta.get("summary_language") or meta.get("language"),
            used_whisper_model=meta.get("whisper_model"),
            used_summary_model=meta.get("summary_model"),
            used_summary_preset=meta.get("summary_preset"),
            used_summary_length=meta.get("summary_length"),
            used_has_extra_instructions=bool(meta.get("has_extra_instructions")),
        )
        self.logger.info("Opened history session id=%s", meta.get("id"))
        return self._snapshot() | {"ok": True}

    def delete_session(self, session_id: str) -> dict[str, Any]:
        sid = str(session_id or "").strip()
        if not sid:
            return self._snapshot() | {"ok": False, "error": "Missing session id."}
        ok = history_delete_session(sid)
        if not ok:
            return self._snapshot() | {"ok": False, "error": "Could not delete session."}
        if self._snapshot().get("session_id") == sid:
            self._discard_owned_temp()
            self._update(
                status="idle",
                message="Drop an audio file, select a file, or record notes.",
                file_path=None,
                file_name=None,
                transcript="",
                summary="",
                summary_status="idle",
                summary_error=None,
                error=None,
                elapsed_seconds=0.0,
                started_at=None,
                session_id=None,
                session_title=None,
                used_language=None,
                used_summary_language=None,
                used_whisper_model=None,
                used_summary_model=None,
                used_summary_preset=None,
                used_summary_length=None,
                used_has_extra_instructions=False,
            )
        return self._snapshot() | {"ok": True}

    def clear_result(self) -> dict[str, Any]:
        file_path = self._snapshot().get("file_path")
        self._clear_summary_fields()
        self._update(
            transcript="",
            error=None,
            status="ready" if file_path else "idle",
            message=(
                f"Ready: {Path(file_path).name}"
                if file_path
                else "Drop an audio file, select a file, or record notes."
            ),
            elapsed_seconds=0.0,
            started_at=None,
        )
        return self._snapshot() | {"ok": True}

    def reset_for_another_file(self) -> dict[str, Any]:
        self._cancel.set()
        self._summary_cancel.set()
        if self._recorder.is_recording:
            self._recorder.cancel()
        self._discard_owned_temp()
        self._update(
            status="idle",
            message="Drop an audio file, select a file, or record notes.",
            file_path=None,
            file_name=None,
            transcript="",
            summary="",
            summary_status="idle",
            summary_error=None,
            error=None,
            elapsed_seconds=0.0,
            started_at=None,
            session_id=None,
            session_title=None,
            used_language=None,
            used_summary_language=None,
            used_whisper_model=None,
            used_summary_model=None,
            used_summary_preset=None,
            used_summary_length=None,
            used_has_extra_instructions=False,
        )
        return self._snapshot() | {"ok": True}

    def _start_elapsed_timer(self) -> None:
        self._stop_elapsed_timer()
        self._timer_stop = threading.Event()

        def tick() -> None:
            while not self._timer_stop.wait(0.5):
                snap = self._snapshot()
                if snap["status"] not in {"loading_model", "transcribing", "recording"}:
                    break

        self._timer_thread = threading.Thread(target=tick, daemon=True)
        self._timer_thread.start()

    def _stop_elapsed_timer(self) -> None:
        if hasattr(self, "_timer_stop"):
            self._timer_stop.set()


def main(dev_url: str | None = None) -> None:
    setup_logging()
    logger = get_logger()
    configure_macos_app(app_name=APP_NAME, version=get_app_version())
    # Eager-import DOM helpers. Finder-launched local .app bundles that point at a
    # project .venv under ~/Documents can hit macOS TCC on *late* imports from
    # site-packages; importing here keeps drop-binding (and the JS bridge path)
    # from failing after the window is already up.
    try:
        from webview.dom import DOMEventHandler  # noqa: F401
        from webview.dom import event as _webview_dom_event  # noqa: F401
    except Exception:
        log_exception("Eager webview.dom import failed")

    api = Api()
    url = resolve_ui_url(dev_url)
    snap = api.get_state()
    logger.info(
        "Starting %s (whisper=%s summary=%s tier=%s)",
        APP_NAME,
        whisper_hf_id(str(snap.get("whisper_model") or "")),
        summary_hf_id(str(snap.get("summary_model") or "")),
        snap.get("performance_tier") or "unknown",
    )
    logger.info("Loading UI from %s", url)

    window = webview.create_window(
        APP_NAME,
        url=url,
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(640, 560),
        background_color="#F3F1EC",
    )

    def bind_native_drop(win: webview.Window) -> None:
        """Match pywebview's official drag/drop example (document-level handlers)."""
        from webview.dom import DOMEventHandler, _dnd_state

        def on_drag(_event: dict[str, Any]) -> None:
            return None

        def on_drop(event: dict[str, Any]) -> None:
            try:
                files = event.get("dataTransfer", {}).get("files", []) or []
                path: str | None = None
                if files:
                    first = files[0]
                    path = first.get("pywebviewFullPath") or first.get("path")

                # Fallback if serialization missed the injected path.
                if not path and _dnd_state.get("paths"):
                    path = str(_dnd_state["paths"][0][1])
                    _dnd_state["paths"].clear()

                if path:
                    api.set_file_path(path)
                else:
                    logger.warning(
                        "Drop received without file path (files=%s dnd=%s)",
                        files,
                        _dnd_state.get("paths"),
                    )
            except Exception:
                log_exception("Native drop handler failed")

        def attach() -> None:
            try:
                doc = win.dom.document
                doc.events.dragenter += DOMEventHandler(on_drag, True, True)
                doc.events.dragstart += DOMEventHandler(on_drag, True, True)
                doc.events.dragover += DOMEventHandler(on_drag, True, True, debounce=500)
                doc.events.drop += DOMEventHandler(on_drop, True, True)
                logger.info("Native drop binding attached")
            except Exception:
                log_exception("Failed to bind native drop handler")

        # Must bind after each page load: navigation replaces the JS context.
        win.events.loaded += attach

    webview.start(bind_native_drop, window, debug=bool(dev_url))


if __name__ == "__main__":
    # Optional: python app.py --dev-url http://127.0.0.1:5173
    args = sys.argv[1:]
    url: str | None = None
    if "--dev-url" in args:
        idx = args.index("--dev-url")
        if idx + 1 < len(args):
            url = args[idx + 1]
    elif "--dev" in args:
        url = "http://127.0.0.1:5173"
    main(dev_url=url)
