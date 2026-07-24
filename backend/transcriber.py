"""Local audio transcription via mlx-whisper."""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from logger import get_logger, log_exception
from languages import normalize_language as _normalize_language_code
from profile_config import get_profile

DEFAULT_MODEL = get_profile().whisper_model

SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".mov"}

HOMEBREW_FFMPEG = Path("/opt/homebrew/bin/ffmpeg")

StatusCallback = Callable[[str, str], None]


@dataclass(frozen=True)
class TranscribeResult:
    text: str
    duration_seconds: float


class TranscribeError(Exception):
    """User-facing transcription error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def find_ffmpeg() -> Path | None:
    """Prefer ffmpeg bundled inside the .app, then PATH / Homebrew."""
    root = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if root:
        bundled = Path(root) / "bin" / "ffmpeg"
        if bundled.is_file() and os.access(bundled, os.X_OK):
            return bundled

    which = shutil.which("ffmpeg")
    if which:
        return Path(which)
    if HOMEBREW_FFMPEG.is_file():
        return HOMEBREW_FFMPEG
    return None


def ensure_ffmpeg() -> Path:
    path = find_ffmpeg()
    if path is None:
        raise TranscribeError(
            "ffmpeg not found. Install ffmpeg with: brew install ffmpeg"
        )
    return path


def validate_audio_path(file_path: str) -> Path:
    if not file_path or not file_path.strip():
        raise TranscribeError("No file selected.")

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise TranscribeError("File does not exist.")
    if not path.is_file():
        raise TranscribeError("Selected path is not a file.")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise TranscribeError(
            f"Unsupported format '{suffix}'. Supported: {supported}"
        )
    return path


def normalize_language(language: str) -> str:
    try:
        return _normalize_language_code(language)
    except ValueError as exc:
        raise TranscribeError("Unsupported language. Choose a language from the list.") from exc


def _friendly_error(exc: BaseException) -> str:
    text = str(exc).lower()
    name = type(exc).__name__.lower()

    if "ffmpeg" in text:
        return "ffmpeg not found. Install ffmpeg with: brew install ffmpeg"
    if any(token in text for token in ("out of memory", "memoryerror", "oom")):
        return "Not enough memory to run transcription. Try a shorter file."
    if "memoryerror" in name:
        return "Not enough memory to run transcription. Try a shorter file."
    if any(
        token in text
        for token in (
            "failed to download",
            "connection",
            "huggingface",
            "hf hub",
            "repo",
            "404",
            "cannot find",
            "no such file",
        )
    ) and "model" in text:
        return "Could not load the transcription model. Check your network and try again."
    if "model" in text and any(
        token in text for token in ("download", "load", "hub", "cache")
    ):
        return "Could not load the transcription model. Check your network and try again."
    return "Transcription failed. See the log for details."


def is_model_cached(model: str = DEFAULT_MODEL) -> bool:
    """Best-effort check whether the HF/MLX model cache is complete."""
    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    if not cache_root.exists():
        return False
    # HF hub folder names look like models--org--name
    safe = model.replace("/", "--")
    candidates = [
        cache_root / f"models--{safe}",
        cache_root / safe,
    ]
    for candidate in candidates:
        if not candidate.is_dir():
            continue
        # Interrupted downloads leave *.incomplete blobs — treat as not cached.
        if any(candidate.rglob("*.incomplete")):
            return False
        snapshots = candidate / "snapshots"
        if not snapshots.is_dir():
            continue
        for snap in snapshots.iterdir():
            if snap.is_dir() and any(p.is_file() for p in snap.rglob("*")):
                return True
    return False


def transcribe_file(
    file_path: str,
    language: str,
    *,
    model: str = DEFAULT_MODEL,
    on_status: StatusCallback | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> TranscribeResult:
    """
    Run local transcription.

    on_status(status, message) is called for UI updates.
    should_cancel() may be polled between stages; mid-model cancel is cooperative.
    """
    logger = get_logger()
    path = validate_audio_path(file_path)
    lang = normalize_language(language)
    ensure_ffmpeg()

    if should_cancel and should_cancel():
        raise TranscribeError("Transcription cancelled.")

    def emit(status: str, message: str) -> None:
        if on_status:
            on_status(status, message)

    logger.info("Transcription requested: path=%s language=%s model=%s", path, lang, model)

    # mlx_whisper.transcribe() also downloads/loads the model — keep the honest
    # status until that call returns (no premature "Transcribing…" / "Model loaded").
    needs_download = not is_model_cached(model)
    if needs_download:
        emit(
            "loading_model",
            "Downloading the transcription model. This happens only once.",
        )
        logger.info("Model not cached; download may start: %s", model)
    else:
        emit("loading_model", "Loading transcription model…")
        logger.info("Loading model from local cache: %s", model)

    started = time.perf_counter()

    try:
        import mlx_whisper
    except ImportError as exc:
        log_exception("Failed to import mlx_whisper")
        raise TranscribeError(
            "mlx-whisper is not installed. Run ./scripts/run-dev.sh first."
        ) from exc

    if should_cancel and should_cancel():
        raise TranscribeError("Transcription cancelled.")

    if not needs_download:
        emit("transcribing", "Transcribing locally…")
    logger.info("Starting transcription for %s", path)

    try:
        result = mlx_whisper.transcribe(
            str(path),
            path_or_hf_repo=model,
            language=lang,
            verbose=False,
        )
    except TranscribeError:
        raise
    except Exception as exc:
        log_exception("Transcription failed")
        raise TranscribeError(_friendly_error(exc)) from exc

    if should_cancel and should_cancel():
        raise TranscribeError("Transcription cancelled.")

    text = ""
    if isinstance(result, dict):
        text = str(result.get("text") or "").strip()
    else:
        text = str(result).strip()

    elapsed = time.perf_counter() - started
    logger.info("Transcription finished in %.1fs (chars=%d)", elapsed, len(text))
    try:
        from memory import release_ml_memory

        release_ml_memory("after transcription")
    except Exception:
        pass
    return TranscribeResult(text=text, duration_seconds=elapsed)
