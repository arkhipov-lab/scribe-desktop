"""Local notes summary via mlx-lm (Qwen2.5 Instruct)."""

from __future__ import annotations

import gc
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from logger import get_logger, log_exception
from model_catalog import (
    DEFAULT_SUMMARY_ID,
    summary_hf_id,
    summary_token_profile,
    normalize_summary_model_id,
)
from summary_presets import (
    DEFAULT_PRESET_ID,
    DEFAULT_SUMMARY_LENGTH,
    SummaryPreset,
    get_preset,
    normalize_summary_length,
    token_limits,
)

DEFAULT_SUMMARY_MODEL = summary_hf_id(DEFAULT_SUMMARY_ID)

StatusCallback = Callable[[str, str], None]

_model_lock = threading.Lock()
_model = None
_tokenizer = None
_loaded_model_id: str | None = None

# Localized meeting-notes headings so smaller models stay on-rails.
_MEETING_SECTION_HEADINGS: dict[str, tuple[str, ...]] = {
    "en": ("Overview", "Decisions", "Action items", "Open questions"),
    "ru": ("Обзор", "Решения", "Задачи", "Открытые вопросы"),
    "uk": ("Огляд", "Рішення", "Задачі", "Відкриті питання"),
    "de": ("Überblick", "Entscheidungen", "Aufgaben", "Offene Fragen"),
    "fr": ("Aperçu", "Décisions", "Actions", "Questions ouvertes"),
    "es": ("Resumen", "Decisiones", "Acciones", "Preguntas abiertas"),
    "it": ("Panoramica", "Decisioni", "Azioni", "Domande aperte"),
    "pt": ("Visão geral", "Decisões", "Ações", "Perguntas em aberto"),
    "pl": ("Przegląd", "Decyzje", "Zadania", "Otwarte pytania"),
    "tr": ("Genel bakış", "Kararlar", "Aksiyonlar", "Açık sorular"),
    "zh": ("概览", "决定", "待办", "未决问题"),
    "ja": ("概要", "決定事項", "アクション", "未解決の質問"),
    "ko": ("개요", "결정", "할 일", "미해결 질문"),
}

_MAX_EXTRA_INSTRUCTIONS = 800


@dataclass(frozen=True)
class SummaryResult:
    text: str
    duration_seconds: float


class SummaryError(Exception):
    """User-facing summarization error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def is_summary_model_cached(model: str = DEFAULT_SUMMARY_MODEL) -> bool:
    """True only when the HF cache looks complete (no interrupted downloads)."""
    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    safe = model.replace("/", "--")
    candidate = cache_root / f"models--{safe}"
    if not candidate.is_dir():
        return False
    if any(candidate.rglob("*.incomplete")):
        return False
    snapshots = candidate / "snapshots"
    if not snapshots.is_dir():
        return False
    return any(
        snap.is_dir() and any(p.is_file() for p in snap.rglob("*"))
        for snap in snapshots.iterdir()
    )


def _friendly_error(exc: BaseException) -> str:
    text = str(exc).lower()
    if any(token in text for token in ("download", "connection", "hub", "network", "http")):
        return "Could not download the summary model. Check your network and try again."
    if "mlx" in text and "import" in text:
        return "mlx-lm is not installed. Run ./scripts/run-dev.sh first."
    return "Summarization failed. See the log for details."


def unload_summary_model() -> None:
    """Drop cached summary weights to free RAM between jobs."""
    global _model, _tokenizer, _loaded_model_id
    with _model_lock:
        _model = None
        _tokenizer = None
        _loaded_model_id = None
    gc.collect()


def _load_model(model_id: str | None = None):
    global _model, _tokenizer, _loaded_model_id
    model_id = model_id or DEFAULT_SUMMARY_MODEL
    with _model_lock:
        if _model is not None and _loaded_model_id == model_id:
            return _model, _tokenizer
        try:
            from mlx_lm import load
        except ImportError as exc:
            raise SummaryError(
                "mlx-lm is not installed. Run ./scripts/run-dev.sh first."
            ) from exc
        get_logger().info("Loading summary model: %s", model_id)
        _model, _tokenizer = load(model_id)
        _loaded_model_id = model_id
        return _model, _tokenizer


def _chat_prompt(tokenizer, user_content: str) -> str:
    messages = [{"role": "user", "content": user_content}]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
    return user_content


def _generate(model, tokenizer, user_content: str, *, max_tokens: int) -> str:
    from mlx_lm import generate

    prompt = _chat_prompt(tokenizer, user_content)
    raw = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        verbose=False,
    )
    return str(raw).strip()


def _uses_compact_prompts(model_hf_id: str) -> bool:
    """Smaller 1.5B model needs shorter, stricter prompt scaffolding."""
    return normalize_summary_model_id(model_hf_id) == "1.5b"


def _split_chunks(text: str, size: int) -> list[str]:
    text = text.strip()
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # Prefer breaking on paragraph / sentence boundaries.
            window = text[start:end]
            break_at = max(window.rfind("\n\n"), window.rfind(". "), window.rfind(" "))
            if break_at > size // 3:
                end = start + break_at + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks or [text]


def _section_headings(preset: SummaryPreset, language: str) -> tuple[str, ...]:
    if preset.id == "meeting_notes":
        code = (language or "").strip().lower()
        return _MEETING_SECTION_HEADINGS.get(code, _MEETING_SECTION_HEADINGS["en"])
    return preset.sections


def _headings_phrase(sections: tuple[str, ...]) -> str:
    return " / ".join(f"## {title}" for title in sections)


def _structure_block(sections: tuple[str, ...], *, compact: bool) -> str:
    lines: list[str] = []
    for title in sections:
        lines.append(f"## {title}")
        if compact:
            lines.append("- short bullets, or none")
        else:
            lines.append("- concise bullets grounded in the transcript, or none")
        lines.append("")
    return "\n".join(lines).rstrip()


def _extra_block(additional_instructions: str) -> str:
    text = (additional_instructions or "").replace("\x00", "").strip()
    if not text:
        return ""
    if len(text) > _MAX_EXTRA_INSTRUCTIONS:
        text = text[:_MAX_EXTRA_INSTRUCTIONS]
    return f"Additional user preferences (follow if compatible):\n{text}\n\n"


def _language_instruction(
    language_name: str,
    *,
    language: str,
    sections: tuple[str, ...],
    compact: bool,
) -> str:
    name = (language_name or "").strip() or "English"
    headings = _headings_phrase(sections)
    if compact:
        return (
            f"CRITICAL LANGUAGE RULE: Write the ENTIRE answer in {name} only. "
            f"Do not write English prose. Do not mix languages. "
            f"Use these exact markdown headings: {headings}."
        )
    return (
        f"Write the entire summary in {name}. "
        f"Use these exact markdown headings: {headings}."
    )


def _single_prompt(
    transcript: str,
    language_name: str,
    *,
    language: str,
    preset: SummaryPreset,
    additional_instructions: str,
    compact: bool,
) -> str:
    name = (language_name or "").strip() or "English"
    sections = _section_headings(preset, language)
    extra = _extra_block(additional_instructions)
    lang_rule = _language_instruction(
        name, language=language, sections=sections, compact=compact
    )
    structure = _structure_block(sections, compact=compact)
    if compact:
        return (
            f"You write notes from a transcript. Preset: {preset.label}.\n"
            f"{preset.instruction}\n"
            f"{lang_rule}\n"
            f"{extra}"
            "Use this exact structure:\n\n"
            f"{structure}\n\n"
            f"Be concise. Do not invent facts. Every sentence must be in {name}.\n\n"
            f"Transcript:\n{transcript}"
        )
    return (
        "You are a notes assistant. Summarize the transcript below.\n"
        f"Preset: {preset.label}. {preset.instruction}\n"
        f"{lang_rule}\n"
        f"{extra}"
        "Use this structure with markdown headings:\n\n"
        f"{structure}\n\n"
        f"Be concise. Do not invent facts that are not in the transcript. "
        f"Write the body text in {name}.\n\n"
        f"Transcript:\n{transcript}"
    )


def _chunk_prompt(
    transcript_chunk: str,
    index: int,
    total: int,
    language_name: str,
    *,
    language: str,
    preset: SummaryPreset,
    additional_instructions: str,
    compact: bool,
) -> str:
    name = (language_name or "").strip() or "English"
    sections = _section_headings(preset, language)
    section_names = ", ".join(sections)
    extra = _extra_block(additional_instructions)
    lang_rule = _language_instruction(
        name, language=language, sections=sections, compact=compact
    )
    if compact:
        return (
            f"Summarize transcript section ({index}/{total}) for later merging.\n"
            f"Preset: {preset.label}. {preset.instruction}\n"
            f"{lang_rule}\n"
            f"{extra}"
            f"Short bullets under: {section_names}.\n"
            f"Write only in {name}. Do not invent facts.\n\n"
            f"Transcript section:\n{transcript_chunk}"
        )
    return (
        "You are a notes assistant. Summarize this transcript section "
        f"({index}/{total}) for later merging.\n"
        f"Preset: {preset.label}. {preset.instruction}\n"
        f"{lang_rule}\n"
        f"{extra}"
        f"Use short bullets under: {section_names}.\n"
        f"Write in {name}. Do not invent facts.\n\n"
        f"Transcript section:\n{transcript_chunk}"
    )


def _merge_prompt(
    partials: list[str],
    language_name: str,
    *,
    language: str,
    preset: SummaryPreset,
    additional_instructions: str,
    compact: bool,
) -> str:
    name = (language_name or "").strip() or "English"
    sections = _section_headings(preset, language)
    headings = ", ".join(f"## {title}" for title in sections)
    extra = _extra_block(additional_instructions)
    lang_rule = _language_instruction(
        name, language=language, sections=sections, compact=compact
    )
    joined = "\n\n---\n\n".join(
        f"Section {i + 1}:\n{part}" for i, part in enumerate(partials)
    )
    if compact:
        return (
            f"Merge these partial notes into one clean summary in {name} only.\n"
            f"Preset: {preset.label}. {preset.instruction}\n"
            f"{lang_rule}\n"
            f"{extra}"
            f"Use markdown headings: {headings}.\n"
            f"Deduplicate. Be concise. Do not invent facts. Reply only in {name}.\n\n"
            f"Partial notes:\n{joined}"
        )
    return (
        "Merge these partial notes into one clean summary.\n"
        f"Preset: {preset.label}. {preset.instruction}\n"
        f"{lang_rule}\n"
        f"{extra}"
        f"Use markdown headings: {headings}.\n\n"
        f"Deduplicate overlapping points. Be concise. Do not invent facts. "
        f"Write in {name}.\n\n"
        f"Partial notes:\n{joined}"
    )


def summarize_transcript(
    transcript: str,
    *,
    language: str = "en",
    language_name: str | None = None,
    preset_id: str = DEFAULT_PRESET_ID,
    additional_instructions: str = "",
    summary_length: str = DEFAULT_SUMMARY_LENGTH,
    model: str = DEFAULT_SUMMARY_MODEL,
    on_status: StatusCallback | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> SummaryResult:
    """Summarize transcript text. Cooperative cancel between stages only."""
    logger = get_logger()
    text = (transcript or "").strip()
    if not text:
        raise SummaryError("No transcript to summarize.")

    display_language = (language_name or "").strip() or (language or "en").strip() or "English"
    preset = get_preset(preset_id)
    length = normalize_summary_length(summary_length)
    # Callers may pass catalog id ("3b") or a full Hugging Face id.
    raw_model = (model or "").strip() or DEFAULT_SUMMARY_MODEL
    if "/" in raw_model:
        model_hf = raw_model
        model_id = normalize_summary_model_id(raw_model)
    else:
        model_id = normalize_summary_model_id(raw_model)
        model_hf = summary_hf_id(model_id)
    chunk_chars, base_max, base_merge = summary_token_profile(model_id)
    max_tokens, merge_tokens = token_limits(
        base_max=base_max,
        base_merge=base_merge,
        length=length,
    )
    compact = _uses_compact_prompts(model_hf)

    def emit(status: str, message: str) -> None:
        if on_status:
            on_status(status, message)

    def cancelled() -> bool:
        return bool(should_cancel and should_cancel())

    started = time.time()
    logger.info(
        "Summary requested: chars=%s language=%s preset=%s length=%s model=%s cached=%s",
        len(text),
        display_language,
        preset.id,
        length,
        model_hf,
        is_summary_model_cached(model_hf),
    )

    if not is_summary_model_cached(model_hf):
        emit(
            "loading_model",
            "Downloading the summary model. This happens only once.",
        )
    else:
        emit("loading_model", "Loading summary model…")

    if cancelled():
        raise SummaryError("Summarization cancelled.")

    try:
        mlx_model, tokenizer = _load_model(model_hf)
    except SummaryError:
        raise
    except Exception as exc:
        log_exception("Failed to load summary model")
        raise SummaryError(_friendly_error(exc)) from exc

    if cancelled():
        raise SummaryError("Summarization cancelled.")

    emit("summarizing", "Writing summary…")
    chunks = _split_chunks(text, chunk_chars)
    prompt_kwargs = {
        "language": language,
        "preset": preset,
        "additional_instructions": additional_instructions,
        "compact": compact,
    }

    try:
        if len(chunks) == 1:
            summary = _generate(
                mlx_model,
                tokenizer,
                _single_prompt(chunks[0], display_language, **prompt_kwargs),
                max_tokens=max_tokens,
            )
        else:
            partials: list[str] = []
            for index, chunk in enumerate(chunks, start=1):
                if cancelled():
                    raise SummaryError("Summarization cancelled.")
                emit(
                    "summarizing",
                    f"Summarizing section {index} of {len(chunks)}…",
                )
                partial = _generate(
                    mlx_model,
                    tokenizer,
                    _chunk_prompt(
                        chunk,
                        index,
                        len(chunks),
                        display_language,
                        **prompt_kwargs,
                    ),
                    max_tokens=max_tokens,
                )
                if partial:
                    partials.append(partial)
            if cancelled():
                raise SummaryError("Summarization cancelled.")
            emit("summarizing", "Combining section notes…")
            summary = _generate(
                mlx_model,
                tokenizer,
                _merge_prompt(partials, display_language, **prompt_kwargs),
                max_tokens=merge_tokens,
            )
    except SummaryError:
        raise
    except Exception as exc:
        log_exception("Summary generation failed")
        raise SummaryError(_friendly_error(exc)) from exc

    if cancelled():
        raise SummaryError("Summarization cancelled.")

    if not summary.strip():
        raise SummaryError("The model returned an empty summary.")

    duration = time.time() - started
    logger.info("Summary complete in %.1fs (%s chars)", duration, len(summary))
    try:
        unload_summary_model()
        import mlx.core as mx

        if hasattr(mx, "clear_cache"):
            mx.clear_cache()
    except Exception:
        pass
    gc.collect()
    return SummaryResult(text=summary.strip(), duration_seconds=duration)
