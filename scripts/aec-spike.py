#!/usr/bin/env python3
"""Offline AEC spike for Scribe clean-mix Phase 3 (not a product default).

Usage:
  SCRIBE_AEC_SPIKE=1 python3 scripts/aec-spike.py \\
    --input ~/Library/Caches/Scribe/recordings/recording-….m4a \\
    --outdir /tmp/scribe-aec-spike

Expects a dual-track AAC/M4A (system = 0:a:0, mic = 0:a:1) as produced by
AudioRecorder, or pass --mic / --ref WAV/PCM paths.

Uses Homebrew SpeexDSP (BSD-3-Clause). Does not modify the Record product path.
Never logs or prints meeting audio samples — paths and timings only.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path


SAMPLE_RATE = 16_000
# ~20 ms frames at 16 kHz
FRAME_SIZE = 320
# ~200 ms filter (Speex docs: 100–500 ms typical)
FILTER_LENGTH = 3200


def _speex_lib() -> ctypes.CDLL:
    prefix = Path(os.environ.get("SPEEXDSP_PREFIX", "/opt/homebrew/opt/speexdsp"))
    candidates = [
        prefix / "lib" / "libspeexdsp.dylib",
        Path("/usr/local/opt/speexdsp/lib/libspeexdsp.dylib"),
    ]
    for path in candidates:
        if path.is_file():
            return ctypes.CDLL(str(path))
    raise FileNotFoundError(
        "libspeexdsp not found. Install with: brew install speexdsp"
    )


class SpeexAEC:
    def __init__(self, frame_size: int = FRAME_SIZE, filter_length: int = FILTER_LENGTH) -> None:
        self.frame_size = frame_size
        self.lib = _speex_lib()
        self.lib.speex_echo_state_init.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.speex_echo_state_init.restype = ctypes.c_void_p
        self.lib.speex_echo_state_destroy.argtypes = [ctypes.c_void_p]
        self.lib.speex_echo_state_destroy.restype = None
        self.lib.speex_echo_cancellation.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_int16),
        ]
        self.lib.speex_echo_cancellation.restype = None
        self.lib.speex_echo_ctl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        self.lib.speex_echo_ctl.restype = ctypes.c_int

        self.state = self.lib.speex_echo_state_init(frame_size, filter_length)
        if not self.state:
            raise RuntimeError("speex_echo_state_init failed")
        # SPEEX_ECHO_SET_SAMPLING_RATE = 24
        rate = ctypes.c_int(SAMPLE_RATE)
        self.lib.speex_echo_ctl(self.state, 24, ctypes.byref(rate))

    def close(self) -> None:
        if self.state:
            self.lib.speex_echo_state_destroy(self.state)
            self.state = None

    def process(self, mic: bytes, ref: bytes) -> bytes:
        if len(mic) != len(ref):
            raise ValueError("mic and ref PCM must be same length")
        if len(mic) % 2 != 0:
            raise ValueError("PCM length must be even (int16)")

        n_samples = len(mic) // 2
        out = bytearray()
        mic_i16 = memoryview(mic).cast("h")
        ref_i16 = memoryview(ref).cast("h")

        frame = self.frame_size
        for i in range(0, n_samples - frame + 1, frame):
            rec = (ctypes.c_int16 * frame)(*mic_i16[i : i + frame])
            play = (ctypes.c_int16 * frame)(*ref_i16[i : i + frame])
            dest = (ctypes.c_int16 * frame)()
            self.lib.speex_echo_cancellation(self.state, rec, play, dest)
            out.extend(struct.pack(f"<{frame}h", *dest))

        # Drop incomplete trailing frame (document in spike notes).
        return bytes(out)

    def __enter__(self) -> SpeexAEC:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        first = err[0] if err else f"exit {proc.returncode}"
        raise RuntimeError(f"command failed: {cmd[0]}: {first[:200]}")


def _ffmpeg() -> str:
    for candidate in ("/opt/homebrew/bin/ffmpeg", "ffmpeg"):
        path = Path(candidate) if candidate.startswith("/") else None
        if path and path.is_file():
            return str(path)
        found = subprocess.run(["which", candidate], capture_output=True, text=True)
        if found.returncode == 0 and found.stdout.strip():
            return found.stdout.strip()
    raise FileNotFoundError("ffmpeg not found")


def extract_track(ffmpeg: str, src: Path, stream_index: int, dest_wav: Path) -> None:
    dest_wav.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-map",
            f"0:a:{stream_index}",
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(dest_wav),
        ]
    )


def read_pcm16(path: Path) -> bytes:
    with wave.open(str(path), "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError(f"expected mono s16le WAV: {path}")
        if wf.getframerate() != SAMPLE_RATE:
            raise ValueError(f"expected {SAMPLE_RATE} Hz: {path}")
        return wf.readframes(wf.getnframes())


def write_pcm16(path: Path, pcm: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)
    # Touch metadata only in logs via caller.


def mix_wavs(ffmpeg: str, mic: Path, system: Path, out: Path) -> None:
    _run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(mic),
            "-i",
            str(system),
            "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0",
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            str(out),
        ]
    )


def align_pair(mic: bytes, ref: bytes) -> tuple[bytes, bytes]:
    n = min(len(mic), len(ref))
    n -= n % 2
    return mic[:n], ref[:n]


def main() -> int:
    if os.environ.get("SCRIBE_AEC_SPIKE", "").strip() not in ("1", "true", "yes", "on"):
        print(
            "Refusing to run: set SCRIBE_AEC_SPIKE=1 to acknowledge this is a local spike "
            "(not product Record path).",
            file=sys.stderr,
        )
        return 2

    parser = argparse.ArgumentParser(description="Scribe offline SpeexDSP AEC spike")
    parser.add_argument("--input", type=Path, help="Dual-track .m4a from AudioRecorder")
    parser.add_argument("--mic", type=Path, help="Mic WAV (mono s16le 16 kHz)")
    parser.add_argument("--ref", type=Path, help="System/reference WAV (mono s16le 16 kHz)")
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("/tmp/scribe-aec-spike"),
        help="Output directory for split / cleaned / mixed WAV paths",
    )
    parser.add_argument(
        "--system-index",
        type=int,
        default=0,
        help="Audio stream index for system track in --input (default 0)",
    )
    parser.add_argument(
        "--mic-index",
        type=int,
        default=1,
        help="Audio stream index for mic track in --input (default 1)",
    )
    parser.add_argument("--filter-ms", type=int, default=200, help="Speex filter length in ms")
    parser.add_argument(
        "--ref-delay-ms",
        type=int,
        default=0,
        help="Delay AEC reference (system) by N ms: pad ref start with silence (mixes stay undelayed)",
    )
    args = parser.parse_args()

    outdir: Path = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    ffmpeg = _ffmpeg()

    mic_wav = outdir / "mic.wav"
    sys_wav = outdir / "system.wav"

    if args.input:
        if not args.input.is_file():
            print(f"input missing: {args.input}", file=sys.stderr)
            return 1
        print(f"split input={args.input} -> {outdir}")
        extract_track(ffmpeg, args.input, args.system_index, sys_wav)
        extract_track(ffmpeg, args.input, args.mic_index, mic_wav)
    elif args.mic and args.ref:
        mic_wav = args.mic
        sys_wav = args.ref
    else:
        print("Provide --input dual-track m4a or both --mic and --ref", file=sys.stderr)
        return 2

    mic_pcm = read_pcm16(mic_wav)
    ref_pcm = read_pcm16(sys_wav)
    mic_pcm, ref_pcm = align_pair(mic_pcm, ref_pcm)
    # Undelayed system for mix_plain / mix_aec / system_aligned listen compares.
    # Delay applies only to the AEC reference input (room path lag vs digital system).
    mix_sys_pcm = ref_pcm
    aec_ref_pcm = ref_pcm
    if args.ref_delay_ms > 0:
        delay_samples = int(SAMPLE_RATE * (args.ref_delay_ms / 1000.0))
        # Acoustic path: system in room arrives later on mic → delay ref so it
        # aligns with bleed in mic (pad start of ref with silence).
        aec_ref_pcm = (b"\x00\x00" * delay_samples) + ref_pcm
        mic_pcm, aec_ref_pcm = align_pair(mic_pcm, aec_ref_pcm)
        mix_sys_pcm, _ = align_pair(mix_sys_pcm, mic_pcm)
        print(f"ref_delay_ms={args.ref_delay_ms} delay_samples={delay_samples}")
    duration_s = (len(mic_pcm) // 2) / SAMPLE_RATE
    print(
        f"pcm samples={len(mic_pcm) // 2} duration_s={duration_s:.2f} "
        f"frame={FRAME_SIZE} filter_ms={args.filter_ms}"
    )

    filter_length = max(FRAME_SIZE, int(SAMPLE_RATE * (args.filter_ms / 1000.0)))
    t0 = time.perf_counter()
    with SpeexAEC(frame_size=FRAME_SIZE, filter_length=filter_length) as aec:
        cleaned = aec.process(mic_pcm, aec_ref_pcm)
    elapsed = time.perf_counter() - t0
    print(f"aec_wall_s={elapsed:.3f} realtime_factor={duration_s / elapsed if elapsed else 0:.1f}x")

    cleaned_wav = outdir / "mic_aec.wav"
    write_pcm16(cleaned_wav, cleaned)
    print(f"wrote cleaned_mic={cleaned_wav} bytes={cleaned_wav.stat().st_size}")

    plain_mix = outdir / "mix_plain.wav"
    aec_mix = outdir / "mix_aec.wav"
    # Re-write aligned mic + undelayed system for fair plain/AEC mix compares
    aligned_mic = outdir / "mic_aligned.wav"
    write_pcm16(aligned_mic, mic_pcm)
    aligned_sys = outdir / "system_aligned.wav"
    write_pcm16(aligned_sys, mix_sys_pcm)
    mix_wavs(ffmpeg, aligned_mic, aligned_sys, plain_mix)
    mix_wavs(ffmpeg, cleaned_wav, aligned_sys, aec_mix)
    print(f"wrote plain_mix={plain_mix}")
    print(f"wrote aec_mix={aec_mix}")
    print(
        "library=SpeexDSP reason=Homebrew/BSD-3, ctypes spike, no product dep; "
        "WebRTC AEC3 deferred to integrate if Speex inadequate on fixtures"
    )
    print("Listen: mic.wav vs mic_aec.wav; mix_plain.wav vs mix_aec.wav (A/C fixtures).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
