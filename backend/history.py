"""Local session history (on-disk transcripts, summaries, optional audio)."""

from __future__ import annotations

import json
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logger import get_logger, log_exception
from settings import SUPPORT_DIR

HISTORY_ROOT = SUPPORT_DIR / "history"
INDEX_PATH = HISTORY_ROOT / "index.json"
SESSIONS_DIR = HISTORY_ROOT / "sessions"

# Skip copying huge media into Application Support; texts still save.
_MAX_AUDIO_BYTES = 400 * 1024 * 1024
_TITLE_MAX = 80

_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_dirs() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _session_dir(session_id: str) -> Path:
    return SESSIONS_DIR / session_id


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _atomic_write_json(path: Path, data: Any) -> None:
    _atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        log_exception("Failed to read history JSON")
        return None


def _load_index() -> list[dict[str, Any]]:
    _ensure_dirs()
    raw = _read_json(INDEX_PATH)
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict) and item.get("id")]


def _save_index(entries: list[dict[str, Any]]) -> None:
    _ensure_dirs()
    _atomic_write_json(INDEX_PATH, entries)


def _fallback_title(source_name: str | None) -> str:
    # Shown until the local LLM title arrives; filename is only a last-resort fallback.
    if source_name:
        stem = Path(str(source_name)).stem.strip()
        if stem:
            return stem[:_TITLE_MAX]
    return "New Transcript"


def sanitize_title(raw: str | None, *, fallback: str) -> str:
    text = (raw or "").replace("\x00", "").strip()
    text = text.strip("\"'`“”‘’ \t\n\r")
    # First line only; models sometimes add extra fluff.
    if "\n" in text:
        text = text.split("\n", 1)[0].strip()
    if text.lower().startswith("title:"):
        text = text[6:].strip()
    if len(text) > _TITLE_MAX:
        text = text[:_TITLE_MAX].rstrip()
    return text or fallback


def _index_entry_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": meta["id"],
        "title": meta.get("title") or "Untitled session",
        "created_at": meta.get("created_at"),
        "updated_at": meta.get("updated_at"),
        "source_name": meta.get("source_name"),
        "has_audio": bool(meta.get("has_audio")),
        "has_transcript": bool(meta.get("has_transcript")),
        "has_summary": bool(meta.get("has_summary")),
        "language": meta.get("language"),
    }


def _find_audio(session_path: Path) -> Path | None:
    for path in sorted(session_path.glob("audio.*")):
        if path.is_file():
            return path
    return None


def list_sessions() -> list[dict[str, Any]]:
    with _lock:
        entries = _load_index()
    # Newest first.
    entries.sort(key=lambda e: str(e.get("updated_at") or e.get("created_at") or ""), reverse=True)
    return entries


def load_session(session_id: str) -> dict[str, Any] | None:
    sid = (session_id or "").strip()
    if not sid:
        return None
    with _lock:
        session_path = _session_dir(sid)
        meta_path = session_path / "meta.json"
        meta = _read_json(meta_path)
        if not isinstance(meta, dict):
            return None
        transcript = ""
        summary = ""
        t_path = session_path / "transcript.md"
        s_path = session_path / "summary.md"
        if t_path.is_file():
            transcript = t_path.read_text(encoding="utf-8")
        if s_path.is_file():
            summary = s_path.read_text(encoding="utf-8")
        audio = _find_audio(session_path)
        return {
            "meta": meta,
            "transcript": transcript,
            "summary": summary,
            "audio_path": str(audio) if audio else None,
            "source_path": meta.get("source_path"),
        }


def delete_session(session_id: str) -> bool:
    sid = (session_id or "").strip()
    if not sid:
        return False
    with _lock:
        entries = _load_index()
        entries = [e for e in entries if e.get("id") != sid]
        _save_index(entries)
        session_path = _session_dir(sid)
        if session_path.is_dir():
            try:
                shutil.rmtree(session_path)
            except OSError:
                log_exception("Failed to delete history session dir")
                return False
        get_logger().info("Deleted history session id=%s", sid)
        return True


def update_session_title(session_id: str, title: str) -> dict[str, Any] | None:
    sid = (session_id or "").strip()
    if not sid:
        return None
    with _lock:
        session_path = _session_dir(sid)
        meta_path = session_path / "meta.json"
        meta = _read_json(meta_path)
        if not isinstance(meta, dict):
            return None
        fallback = _fallback_title(meta.get("source_name"))
        meta["title"] = sanitize_title(title, fallback=fallback)
        meta["updated_at"] = _now_iso()
        _atomic_write_json(meta_path, meta)
        entries = _load_index()
        found = False
        for i, entry in enumerate(entries):
            if entry.get("id") == sid:
                entries[i] = _index_entry_from_meta(meta)
                found = True
                break
        if not found:
            entries.insert(0, _index_entry_from_meta(meta))
        _save_index(entries)
        get_logger().info("Updated history title id=%s", sid)
        return _index_entry_from_meta(meta)


def update_session_summary(
    session_id: str,
    summary: str,
    *,
    summary_model: str | None = None,
    summary_preset: str | None = None,
    summary_length: str | None = None,
    summary_language: str | None = None,
    has_extra_instructions: bool | None = None,
) -> dict[str, Any] | None:
    sid = (session_id or "").strip()
    if not sid:
        return None
    text = (summary or "").replace("\x00", "")
    with _lock:
        session_path = _session_dir(sid)
        meta_path = session_path / "meta.json"
        meta = _read_json(meta_path)
        if not isinstance(meta, dict):
            return None
        _atomic_write_text(session_path / "summary.md", text.rstrip() + ("\n" if text else ""))
        meta["has_summary"] = bool(text.strip())
        meta["updated_at"] = _now_iso()
        if summary_model is not None:
            meta["summary_model"] = summary_model
        if summary_preset is not None:
            meta["summary_preset"] = summary_preset
        if summary_length is not None:
            meta["summary_length"] = summary_length
        if summary_language is not None:
            meta["summary_language"] = summary_language
        if has_extra_instructions is not None:
            meta["has_extra_instructions"] = bool(has_extra_instructions)
        _atomic_write_json(meta_path, meta)
        entries = _load_index()
        for i, entry in enumerate(entries):
            if entry.get("id") == sid:
                entries[i] = _index_entry_from_meta(meta)
                break
        else:
            entries.insert(0, _index_entry_from_meta(meta))
        _save_index(entries)
        get_logger().info("Updated history summary id=%s has_summary=%s", sid, meta["has_summary"])
        return _index_entry_from_meta(meta)


def upsert_after_transcript(
    *,
    session_id: str | None,
    transcript: str,
    audio_path: str | None,
    source_name: str | None,
    language: str,
    whisper_model: str,
    clear_summary: bool = True,
) -> dict[str, Any]:
    """Create or update a session after a successful transcription. Copies audio when feasible."""
    text = (transcript or "").replace("\x00", "")
    with _lock:
        _ensure_dirs()
        sid = (session_id or "").strip() or uuid.uuid4().hex
        session_path = _session_dir(sid)
        session_path.mkdir(parents=True, exist_ok=True)
        meta_path = session_path / "meta.json"
        existing = _read_json(meta_path)
        now = _now_iso()
        if isinstance(existing, dict) and existing.get("id") == sid:
            meta = dict(existing)
            # Retranscribe: show placeholder until the new LLM title lands.
            title = "New Transcript"
            created = meta.get("created_at") or now
        else:
            meta = {"id": sid}
            title = "New Transcript"
            created = now

        _atomic_write_text(session_path / "transcript.md", text.rstrip() + "\n")
        if clear_summary:
            summary_file = session_path / "summary.md"
            if summary_file.is_file():
                summary_file.unlink()
            meta["has_summary"] = False
            meta["summary_model"] = None
            meta["summary_preset"] = None
            meta["summary_length"] = None
            meta["summary_language"] = None
            meta["has_extra_instructions"] = False

        has_audio = False
        copied_from = None
        if audio_path:
            src = Path(str(audio_path)).expanduser()
            try:
                if src.is_file():
                    size = src.stat().st_size
                    if size <= _MAX_AUDIO_BYTES:
                        # Remove prior audio.* then copy.
                        for old in session_path.glob("audio.*"):
                            try:
                                old.unlink()
                            except OSError:
                                pass
                        suffix = src.suffix.lower() or ".wav"
                        dest = session_path / f"audio{suffix}"
                        shutil.copy2(src, dest)
                        has_audio = True
                        copied_from = str(src.resolve())
                    else:
                        get_logger().info(
                            "History skip audio copy (too large) id=%s bytes=%s",
                            sid,
                            size,
                        )
                        copied_from = str(src.resolve())
            except OSError:
                log_exception("Failed to copy audio into history")

        meta.update(
            {
                "id": sid,
                "title": title,
                "created_at": created,
                "updated_at": now,
                "source_name": source_name,
                "source_path": copied_from,
                "has_audio": has_audio,
                "has_transcript": bool(text.strip()),
                "language": language,
                "whisper_model": whisper_model,
            }
        )
        if "has_summary" not in meta:
            meta["has_summary"] = False

        _atomic_write_json(meta_path, meta)
        entries = [e for e in _load_index() if e.get("id") != sid]
        entries.insert(0, _index_entry_from_meta(meta))
        _save_index(entries)
        get_logger().info(
            "History upsert after transcript id=%s has_audio=%s chars=%s",
            sid,
            has_audio,
            len(text),
        )
        return _index_entry_from_meta(meta)
