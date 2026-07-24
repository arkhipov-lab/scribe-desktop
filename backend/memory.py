"""Best-effort MLX / Python memory release between pipeline stages."""

from __future__ import annotations

import gc

from logger import get_logger, log_exception


def release_ml_memory(reason: str = "") -> None:
    """Free cached models / Metal buffers when possible."""
    logger = get_logger()
    try:
        from summarizer import unload_summary_model

        unload_summary_model()
    except Exception:
        log_exception("unload_summary_model failed")

    try:
        import mlx.core as mx

        if hasattr(mx, "clear_cache"):
            mx.clear_cache()
        elif hasattr(mx, "metal") and hasattr(mx.metal, "clear_cache"):
            mx.metal.clear_cache()
    except Exception:
        # mlx may not be imported yet — fine
        pass

    gc.collect()
    if reason:
        logger.info("Released ML memory (%s)", reason)
    else:
        logger.info("Released ML memory")
