"""Classify the macOS default audio *output* route for recording finalize.

Used to choose mic-only (speakers / open air) vs leveled mic+system amix
(headphones / private listen). Detection failures → ``unknown`` so callers
never drop remote audio by mistake.

Logs and return values carry route class / transport codes only — never
device audio.
"""

from __future__ import annotations

import ctypes
from ctypes import Structure, byref, c_uint32
from dataclasses import dataclass
from enum import Enum
from typing import Literal


def _fourcc(code: str) -> int:
    raw = code.encode("ascii")
    if len(raw) != 4:
        raise ValueError(f"fourcc must be 4 chars, got {code!r}")
    return int.from_bytes(raw, "big")


def _fourcc_str(value: int) -> str:
    try:
        return value.to_bytes(4, "big").decode("ascii")
    except Exception:
        return f"0x{value:08x}"


class AudioObjectPropertyAddress(Structure):
    _fields_ = [
        ("mSelector", c_uint32),
        ("mScope", c_uint32),
        ("mElement", c_uint32),
    ]


# Core Audio four-char codes
_K_AUDIO_OBJECT_SYSTEM_OBJECT = 1
_SEL_DEFAULT_OUTPUT = _fourcc("dOut")
_SEL_TRANSPORT = _fourcc("tran")
_SEL_DATA_SOURCE = _fourcc("ssrc")
_SCOPE_GLOBAL = _fourcc("glob")
_SCOPE_OUTPUT = _fourcc("outp")

_TRANSPORT_BUILTIN = _fourcc("bltn")
_TRANSPORT_BLUETOOTH = _fourcc("blue")
_TRANSPORT_BLUETOOTH_LE = _fourcc("blea")
_TRANSPORT_USB = _fourcc("usb ")
_TRANSPORT_HDMI = _fourcc("hdmi")
_TRANSPORT_DISPLAYPORT = _fourcc("dpt ")
_TRANSPORT_AIRPLAY = _fourcc("airp")
_TRANSPORT_VIRTUAL = _fourcc("virt")
_TRANSPORT_AGGREGATE = _fourcc("grup")

_DATA_INTERNAL_SPEAKERS = _fourcc("ispk")
_DATA_HEADPHONES = _fourcc("hdpn")


class OutputRouteClass(str, Enum):
    """Coarse class for finalize branching."""

    SPEAKERS = "speakers"
    HEADPHONES = "headphones"
    UNKNOWN = "unknown"


FinalizeMode = Literal["mic_only", "level_match_amix"]


@dataclass(frozen=True)
class OutputRouteInfo:
    route_class: OutputRouteClass
    transport: str
    data_source: str | None
    device_id: int | None
    reason: str

    @property
    def finalize_mode(self) -> FinalizeMode:
        # Speakers / open air: mic already has remote bleed — do not amix.
        if self.route_class is OutputRouteClass.SPEAKERS:
            return "mic_only"
        # Headphones + unknown: keep system track (never drop remote).
        return "level_match_amix"


def _coreaudio() -> ctypes.CDLL | None:
    try:
        return ctypes.CDLL(
            "/System/Library/Frameworks/CoreAudio.framework/CoreAudio"
        )
    except OSError:
        return None


def _get_u32(
    core: ctypes.CDLL,
    object_id: int,
    selector: int,
    scope: int,
) -> int | None:
    addr = AudioObjectPropertyAddress(selector, scope, 0)
    value = c_uint32(0)
    size = c_uint32(ctypes.sizeof(c_uint32))
    status = core.AudioObjectGetPropertyData(
        c_uint32(object_id),
        byref(addr),
        c_uint32(0),
        None,
        byref(size),
        byref(value),
    )
    if status != 0:
        return None
    return int(value.value)


def classify_default_output_route() -> OutputRouteInfo:
    """Probe the system default output device and classify the route.

    Conservative rules (product Ideal):
    - Built-in + internal speakers → speakers (mic-only finalize)
    - Built-in + headphones jack, or Bluetooth / BLE → headphones (mix)
    - USB / HDMI / DisplayPort / AirPlay / aggregate / virtual / errors →
      unknown (headphones-style mix; do not mic-only)
    """
    core = _coreaudio()
    if core is None:
        return OutputRouteInfo(
            route_class=OutputRouteClass.UNKNOWN,
            transport="none",
            data_source=None,
            device_id=None,
            reason="coreaudio_unavailable",
        )

    try:
        device_id = _get_u32(
            core, _K_AUDIO_OBJECT_SYSTEM_OBJECT, _SEL_DEFAULT_OUTPUT, _SCOPE_GLOBAL
        )
        if device_id is None or device_id == 0:
            return OutputRouteInfo(
                route_class=OutputRouteClass.UNKNOWN,
                transport="none",
                data_source=None,
                device_id=None,
                reason="no_default_output",
            )

        transport = _get_u32(core, device_id, _SEL_TRANSPORT, _SCOPE_GLOBAL)
        if transport is None:
            return OutputRouteInfo(
                route_class=OutputRouteClass.UNKNOWN,
                transport="unknown",
                data_source=None,
                device_id=device_id,
                reason="transport_unavailable",
            )

        transport_s = _fourcc_str(transport)
        data_source = _get_u32(core, device_id, _SEL_DATA_SOURCE, _SCOPE_OUTPUT)
        if data_source is None:
            # Some devices expose data source on global scope.
            data_source = _get_u32(core, device_id, _SEL_DATA_SOURCE, _SCOPE_GLOBAL)
        data_source_s = _fourcc_str(data_source) if data_source is not None else None

        if transport in (_TRANSPORT_BLUETOOTH, _TRANSPORT_BLUETOOTH_LE):
            return OutputRouteInfo(
                route_class=OutputRouteClass.HEADPHONES,
                transport=transport_s,
                data_source=data_source_s,
                device_id=device_id,
                reason="bluetooth_private",
            )

        if transport == _TRANSPORT_BUILTIN:
            if data_source == _DATA_HEADPHONES:
                return OutputRouteInfo(
                    route_class=OutputRouteClass.HEADPHONES,
                    transport=transport_s,
                    data_source=data_source_s,
                    device_id=device_id,
                    reason="builtin_headphones",
                )
            if data_source == _DATA_INTERNAL_SPEAKERS:
                return OutputRouteInfo(
                    route_class=OutputRouteClass.SPEAKERS,
                    transport=transport_s,
                    data_source=data_source_s,
                    device_id=device_id,
                    reason="builtin_speakers",
                )
            return OutputRouteInfo(
                route_class=OutputRouteClass.UNKNOWN,
                transport=transport_s,
                data_source=data_source_s,
                device_id=device_id,
                reason="builtin_unknown_source",
            )

        # USB / HDMI / DP / AirPlay / virtual / aggregate: ambiguous
        # (headset vs room speakers / TV). Prefer mix so remote is kept.
        reason_map = {
            _TRANSPORT_USB: "usb_ambiguous",
            _TRANSPORT_HDMI: "hdmi_ambiguous",
            _TRANSPORT_DISPLAYPORT: "displayport_ambiguous",
            _TRANSPORT_AIRPLAY: "airplay_ambiguous",
            _TRANSPORT_VIRTUAL: "virtual_ambiguous",
            _TRANSPORT_AGGREGATE: "aggregate_ambiguous",
        }
        reason = reason_map.get(transport, f"transport_{transport_s}")
        return OutputRouteInfo(
            route_class=OutputRouteClass.UNKNOWN,
            transport=transport_s,
            data_source=data_source_s,
            device_id=device_id,
            reason=reason,
        )
    except Exception:
        return OutputRouteInfo(
            route_class=OutputRouteClass.UNKNOWN,
            transport="error",
            data_source=None,
            device_id=None,
            reason="probe_exception",
        )
