"""Desktop shell: pywebview + React UI + mlx-whisper bridge."""

from __future__ import annotations

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
from memory import release_ml_memory
from profile_config import get_profile
from recorder import CaptureRecorder, RecorderError, delete_path_quiet, is_temp_recording
from summarizer import (
    DEFAULT_SUMMARY_MODEL,
    SummaryError,
    summarize_transcript,
)
from transcriber import (
    DEFAULT_MODEL,
    SUPPORTED_EXTENSIONS,
    TranscribeError,
    find_ffmpeg,
    transcribe_file,
    validate_audio_path,
)
from version import get_app_version

_PROFILE = get_profile()
APP_NAME = _PROFILE.app_name
WINDOW_WIDTH = 880
WINDOW_HEIGHT = 760


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
        self._state: dict[str, Any] = {
            "status": "idle",
            "message": "Drop an audio file, select a file, or record notes.",
            "file_path": None,
            "file_name": None,
            "language": DEFAULT_LANGUAGE,
            "transcript": "",
            "summary": "",
            "summary_status": "idle",
            "summary_error": None,
            "error": None,
            "elapsed_seconds": 0.0,
            "started_at": None,
        }
        self._timer_stop = threading.Event()
        self._timer_thread: threading.Thread | None = None
        self._recorder = CaptureRecorder()
        self._owned_temp_path: str | None = None
        self.logger = get_logger()

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
            self._state.update(kwargs)

    def _discard_owned_temp(self, *, keep: str | None = None) -> None:
        owned = self._owned_temp_path
        if not owned:
            return
        if keep and Path(owned).resolve() == Path(keep).resolve():
            return
        delete_path_quiet(owned)
        self._owned_temp_path = None

    def get_state(self) -> dict[str, Any]:
        return self._snapshot()

    def get_supported_extensions(self) -> list[str]:
        return sorted(SUPPORTED_EXTENSIONS)

    def get_model_name(self) -> str:
        return DEFAULT_MODEL

    def get_summary_model_name(self) -> str:
        return DEFAULT_SUMMARY_MODEL

    def get_app_info(self) -> dict[str, str]:
        profile = get_profile()
        return {
            "app_name": profile.app_name,
            "profile": profile.id,
            "version": get_app_version(),
            "whisper_model": profile.whisper_model,
            "summary_model": profile.summary_model,
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

    def set_file_path(self, file_path: str) -> dict[str, Any]:
        if self._snapshot()["status"] == "recording":
            return self._snapshot() | {
                "ok": False,
                "error": "Stop recording before selecting another file.",
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
        )
        self.logger.info("File selected: %s", path)
        return self._snapshot() | {"ok": True}

    def start_recording(self) -> dict[str, Any]:
        state = self._snapshot()
        if state["status"] in {"loading_model", "transcribing", "recording"}:
            return state | {"ok": False, "error": "Cannot start recording right now."}

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
        self._update(language=lang)
        return self._snapshot() | {"ok": True}

    def get_languages(self) -> list[dict[str, str]]:
        return languages_for_api()

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
        self.logger.info(
            "UI requested transcription: path=%s language=%s", file_path, language
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
                release_ml_memory("before summary")
                self._begin_summary(result.text)
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
        language = str(self._snapshot().get("language") or DEFAULT_LANGUAGE)
        language_name = WHISPER_LANGUAGES.get(language, language)
        self.logger.info(
            "Starting summary worker (%s chars, language=%s)",
            len(transcript),
            language_name,
        )

        def worker() -> None:
            def on_status(status: str, message: str) -> None:
                if self._summary_cancel.is_set():
                    return
                # Keep transcription status untouched; only update summary fields.
                # Surface progress lightly in the main message when idle/completed.
                snap = self._snapshot()
                patch: dict[str, Any] = {
                    "summary_status": status,
                    "summary_error": None,
                }
                if snap.get("status") in {"completed", "ready"}:
                    patch["message"] = message
                self._update(**patch)

            try:
                result = summarize_transcript(
                    transcript,
                    language=language,
                    language_name=language_name,
                    on_status=on_status,
                    should_cancel=self._summary_cancel.is_set,
                )
                if self._summary_cancel.is_set():
                    self._update(
                        summary_status="idle",
                        summary="",
                        summary_error=None,
                        message="Summary cancelled.",
                    )
                    return
                self._update(
                    summary=result.text,
                    summary_status="completed",
                    summary_error=None,
                    message="Transcription complete. Summary ready.",
                )
            except SummaryError as exc:
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
            except Exception:
                log_exception("Unexpected summary failure")
                message = "Summarization failed. See the log for details."
                self._update(
                    summary_status="error",
                    summary_error=message,
                    message=message,
                )

        self._summary_worker = threading.Thread(
            target=worker, daemon=True, name="summarize"
        )
        self._summary_worker.start()

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
    logger.info(
        "Starting %s (profile=%s whisper=%s summary=%s)",
        APP_NAME,
        _PROFILE.id,
        DEFAULT_MODEL,
        DEFAULT_SUMMARY_MODEL,
    )

    api = Api()
    url = resolve_ui_url(dev_url)
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
