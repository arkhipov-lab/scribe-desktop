"""Local hardware probe for recommended model defaults (no network)."""

from __future__ import annotations

import platform
import re
import subprocess
from dataclasses import dataclass
from typing import Literal

from logger import get_logger, log_exception

PerformanceTier = Literal["strong", "weak"]


@dataclass(frozen=True)
class HardwareInfo:
    memory_gb: float | None
    chip_generation: int | None
    chip_name: str | None
    tier: PerformanceTier
    reason: str


def _sysctl(name: str) -> str | None:
    try:
        result = subprocess.run(
            ["sysctl", "-n", name],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = (result.stdout or "").strip()
    return value or None


def _memory_gb() -> float | None:
    raw = _sysctl("hw.memsize")
    if not raw:
        return None
    try:
        return int(raw) / (1024**3)
    except ValueError:
        return None


def _parse_chip(text: str | None) -> tuple[str | None, int | None]:
    if not text:
        return None, None
    cleaned = text.strip()
    match = re.search(r"\bM(\d+)\b", cleaned, flags=re.IGNORECASE)
    if not match:
        return cleaned or None, None
    return cleaned, int(match.group(1))


def _chip_from_brand() -> tuple[str | None, int | None]:
    brand = _sysctl("machdep.cpu.brand_string")
    name, gen = _parse_chip(brand)
    if gen is not None:
        return name, gen
    # Fallback: some builds only expose a marketing name via system_profiler.
    try:
        result = subprocess.run(
            ["system_profiler", "SPHardwareDataType", "-json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout:
            import json

            data = json.loads(result.stdout)
            entries = data.get("SPHardwareDataType") or []
            if entries:
                chip = str(entries[0].get("chip_type") or entries[0].get("cpu_type") or "")
                return _parse_chip(chip)
    except Exception:
        log_exception("system_profiler hardware probe failed")
    return name, gen


def recommend_tier(
    *,
    memory_gb: float | None,
    chip_generation: int | None,
) -> tuple[PerformanceTier, str]:
    """
    Prefer safer defaults on low RAM. Otherwise follow chip generation:
    M3+ → strong, M2 and older → weak (per product policy).
    """
    if memory_gb is not None and memory_gb < 12:
        return "weak", f"low memory ({memory_gb:.0f} GB)"
    if chip_generation is not None:
        if chip_generation >= 3:
            return "strong", f"Apple M{chip_generation}"
        return "weak", f"Apple M{chip_generation}"
    if memory_gb is not None and memory_gb >= 16:
        return "strong", f"memory ({memory_gb:.0f} GB), chip unknown"
    return "weak", "conservative default"


def probe_hardware() -> HardwareInfo:
    if platform.machine() != "arm64":
        return HardwareInfo(
            memory_gb=None,
            chip_generation=None,
            chip_name=None,
            tier="weak",
            reason="non-Apple-Silicon host",
        )

    memory_gb = _memory_gb()
    chip_name, chip_generation = _chip_from_brand()
    tier, reason = recommend_tier(
        memory_gb=memory_gb,
        chip_generation=chip_generation,
    )
    try:
        get_logger().info(
            "Hardware probe: tier=%s memory_gb=%s chip=%s reason=%s",
            tier,
            f"{memory_gb:.1f}" if memory_gb is not None else "unknown",
            chip_name or "unknown",
            reason,
        )
    except Exception:
        pass
    return HardwareInfo(
        memory_gb=memory_gb,
        chip_generation=chip_generation,
        chip_name=chip_name,
        tier=tier,
        reason=reason,
    )
