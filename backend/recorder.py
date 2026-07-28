"""Audio recorder: microphone + system audio via ScreenCaptureKit helper."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from logger import get_logger, log_exception
from output_route import OutputRouteInfo, classify_default_output_route
from transcriber import find_ffmpeg

CACHE_DIR = Path.home() / "Library" / "Caches" / "Scribe" / "recordings"

# Dual-track .m4a from AudioRecorder: stream 0 = system, stream 1 = mic.
_SYSTEM_TRACK = "0:a:0"
_MIC_TRACK = "0:a:1"

# Clamp mic gain when level-matching toward system (dB).
_LEVEL_MATCH_GAIN_MIN_DB = -12.0
_LEVEL_MATCH_GAIN_MAX_DB = 24.0
# Only analyze this many seconds for mean_volume (start of file) so Stop stays light.
_LEVEL_MATCH_DETECT_WINDOW_S = 30.0


def _keep_raw_recording() -> bool:
    """Dev/QA: keep pre-mix .m4a when SCRIBE_KEEP_RAW_RECORDING is truthy."""
    return os.environ.get("SCRIBE_KEEP_RAW_RECORDING", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


class RecorderError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _project_native_build() -> Path:
    return Path(__file__).resolve().parent.parent / "native" / "build" / "AudioRecorder"


def find_audio_recorder_binary() -> Path | None:
    candidates: list[Path] = []

    env = os.environ.get("SCRIBE_ROOT") or os.environ.get("LOCAL_TRANSCRIBER_ROOT")
    if env:
        root = Path(env)
        candidates.append(root / "AudioRecorder")
        candidates.append(root.parent / "MacOS" / "AudioRecorder")

    # Bundled .app layout: Resources/../MacOS/AudioRecorder
    here = Path(__file__).resolve()
    candidates.extend(
        [
            here.parent.parent / "MacOS" / "AudioRecorder",
            here.parent.parent.parent / "MacOS" / "AudioRecorder",
            _project_native_build(),
        ]
    )

    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK):
            return path
    return None


def ensure_cache_dir() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def delete_path_quiet(path: str | Path | None) -> None:
    if not path:
        return
    try:
        p = Path(path)
        if p.is_file():
            p.unlink()
    except OSError:
        log_exception(f"Failed to delete temp recording: {path}")


class CaptureRecorder:
    """Owns a running AudioRecorder subprocess and produces a mixed WAV."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen[str] | None = None
        self._raw_path: Path | None = None
        self._started_at: float | None = None
        self._stderr_chunks: list[str] = []
        self.logger = get_logger()

    @property
    def is_recording(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    @property
    def started_at(self) -> float | None:
        return self._started_at

    def start(self) -> Path:
        if self.is_recording:
            raise RecorderError("Recording is already in progress.")

        binary = find_audio_recorder_binary()
        if binary is None:
            raise RecorderError(
                "Audio recorder helper is missing. Run ./scripts/build.sh or compile native/AudioRecorder.swift."
            )

        ensure_cache_dir()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        raw_path = CACHE_DIR / f"recording-{stamp}.m4a"
        self._raw_path = raw_path

        self.logger.info("Starting AudioRecorder binary=%s output=%s", binary, raw_path)
        try:
            self._proc = subprocess.Popen(
                [str(binary), "--output", str(raw_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            log_exception("Failed to launch AudioRecorder")
            raise RecorderError(f"Could not start recorder: {exc}") from exc

        # Prevent stderr pipe deadlock while waiting for READY / recording.
        assert self._proc.stderr is not None
        self._stderr_chunks = []

        def _drain_stderr() -> None:
            try:
                assert self._proc is not None and self._proc.stderr is not None
                for line in self._proc.stderr:
                    self._stderr_chunks.append(line)
            except Exception:
                pass

        threading.Thread(target=_drain_stderr, daemon=True, name="recorder-stderr").start()

        # Wait for READY (permission prompts may delay this).
        assert self._proc.stdout is not None
        deadline = time.time() + 60
        ready = False
        while time.time() < deadline:
            if self._proc.poll() is not None:
                err = "".join(self._stderr_chunks)
                self._proc = None
                message = self._friendly_launch_error(err)
                raise RecorderError(message)
            line = self._proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            if line.strip() == "READY":
                ready = True
                break
            if line.startswith("ERROR:"):
                self._terminate_quiet()
                raise RecorderError(line.replace("ERROR:", "", 1).strip() or "Recorder failed to start.")

        if not ready:
            self._terminate_quiet()
            raise RecorderError(
                "Timed out waiting for the recorder. Grant Microphone and Screen & System Audio "
                "Recording permissions, then restart the app."
            )

        self._started_at = time.time()
        return raw_path

    def stop(self) -> Path:
        proc = self._proc
        raw_path = self._raw_path
        if proc is None:
            # Process may have already exited after a previous stop attempt;
            # try to salvage an existing mix/raw file.
            if raw_path is not None:
                mixed_candidate = raw_path.with_suffix(".wav")
                if mixed_candidate.is_file() and mixed_candidate.stat().st_size > 64:
                    self._raw_path = None
                    self._started_at = None
                    return mixed_candidate
                if raw_path.is_file() and raw_path.stat().st_size > 64:
                    mixed = self._mix_to_wav(raw_path)
                    self._dispose_raw_after_mix(raw_path)
                    self._raw_path = None
                    self._started_at = None
                    return mixed
            raise RecorderError("No active recording.")

        self.logger.info("Stopping AudioRecorder")

        # Prefer signal stop; also send STOP on stdin for compatibility.
        try:
            proc.send_signal(signal.SIGTERM)
        except (OSError, ProcessLookupError, ValueError):
            pass
        try:
            if proc.stdin and proc.poll() is None:
                proc.stdin.write("STOP\n")
                proc.stdin.flush()
        except OSError:
            pass

        # stderr is drained by a background thread — do not use communicate().
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            self._cleanup_proc()
            raise RecorderError("Recorder did not stop in time.") from None

        stdout = ""
        try:
            if proc.stdout:
                stdout = proc.stdout.read() or ""
        except OSError:
            pass
        stderr = "".join(self._stderr_chunks)
        code = proc.returncode
        self._cleanup_proc()
        if stdout:
            self.logger.info("AudioRecorder stdout: %s", stdout.strip()[:500])
        if stderr:
            self.logger.info("AudioRecorder stderr: %s", stderr.strip()[:500])

        if code not in (0, None):
            message = self._friendly_launch_error(stderr or stdout or "")
            # Still try to salvage if any audio was written.
            if raw_path is not None and raw_path.is_file() and raw_path.stat().st_size > 64:
                try:
                    mixed = self._mix_to_wav(raw_path)
                    self._dispose_raw_after_mix(raw_path)
                    self._raw_path = None
                    self._started_at = None
                    return mixed
                except RecorderError:
                    pass
            delete_path_quiet(raw_path)
            raise RecorderError(message)

        if raw_path is None or not raw_path.is_file() or raw_path.stat().st_size < 64:
            delete_path_quiet(raw_path)
            raise RecorderError(
                "Recording produced an empty file. Check Microphone and Screen Recording permissions."
            )

        mixed = self._mix_to_wav(raw_path)
        self._dispose_raw_after_mix(raw_path)
        self._raw_path = None
        self._started_at = None
        return mixed

    def cancel(self) -> None:
        if self._proc is None:
            return
        self._terminate_quiet()
        delete_path_quiet(self._raw_path)
        self._raw_path = None
        self._started_at = None

    def _dispose_raw_after_mix(self, raw_path: Path) -> None:
        if _keep_raw_recording():
            self.logger.info("Keeping pre-mix raw recording path=%s", raw_path)
            return
        delete_path_quiet(raw_path)

    def _mix_to_wav(self, raw_path: Path) -> Path:
        ffmpeg = find_ffmpeg()
        if ffmpeg is None:
            raise RecorderError("ffmpeg not found. Install ffmpeg with: brew install ffmpeg")

        out = raw_path.with_suffix(".wav")
        route = classify_default_output_route()
        mode = route.finalize_mode
        self.logger.info(
            "Recording finalize route_class=%s mode=%s transport=%s data_source=%s reason=%s",
            route.route_class.value,
            mode,
            route.transport,
            route.data_source or "none",
            route.reason,
        )

        if mode == "mic_only":
            if self._ffmpeg_extract_track(ffmpeg, raw_path, out, _MIC_TRACK):
                return out
            self.logger.warning(
                "Mic-only finalize failed; falling back to level-match amix "
                "(will not drop remote)"
            )
            route = OutputRouteInfo(
                route_class=route.route_class,
                transport=route.transport,
                data_source=route.data_source,
                device_id=route.device_id,
                reason=f"{route.reason}+mic_extract_fallback",
            )

        if self._ffmpeg_level_match_amix(ffmpeg, raw_path, out, route):
            return out

        # Dual-track path failed — salvage any single stream rather than delete.
        if self._ffmpeg_extract_track(ffmpeg, raw_path, out, _SYSTEM_TRACK):
            self.logger.warning("Finalize fell back to system track only")
            return out
        if self._ffmpeg_extract_track(ffmpeg, raw_path, out, _MIC_TRACK):
            self.logger.warning("Finalize fell back to mic track only")
            return out

        cmd_single = [
            str(ffmpeg),
            "-y",
            "-i",
            str(raw_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(out),
        ]
        single = subprocess.run(cmd_single, capture_output=True, text=True)
        if single.returncode != 0 or not out.is_file() or out.stat().st_size <= 64:
            self.logger.error("ffmpeg finalize failed: %s", (single.stderr or "")[:500])
            raise RecorderError("Could not finalize the recording audio.")
        return out

    def _ffmpeg_extract_track(
        self,
        ffmpeg: Path,
        raw_path: Path,
        out: Path,
        track: str,
    ) -> bool:
        cmd = [
            str(ffmpeg),
            "-y",
            "-i",
            str(raw_path),
            "-map",
            track,
            "-ac",
            "1",
            "-ar",
            "16000",
            str(out),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0 and out.is_file() and out.stat().st_size > 64

    def _ffmpeg_level_match_amix(
        self,
        ffmpeg: Path,
        raw_path: Path,
        out: Path,
        route: OutputRouteInfo,
    ) -> bool:
        """amix(level_match(mic), system). Track 0 = system, track 1 = mic."""
        gain_db = self._mic_level_match_gain_db(ffmpeg, raw_path)
        self.logger.info(
            "Recording level-match mic_gain_db=%.1f route_class=%s",
            gain_db,
            route.route_class.value,
        )
        filter_complex = (
            f"[{_SYSTEM_TRACK}]aformat=channel_layouts=mono[sys];"
            f"[{_MIC_TRACK}]aformat=channel_layouts=mono,volume={gain_db:.2f}dB[mic];"
            f"[sys][mic]amix=inputs=2:duration=longest:normalize=0[mix]"
        )
        cmd = [
            str(ffmpeg),
            "-y",
            "-i",
            str(raw_path),
            "-filter_complex",
            filter_complex,
            "-map",
            "[mix]",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(out),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and out.is_file() and out.stat().st_size > 64:
            return True

        # Plain amix without level match (still keeps both tracks).
        self.logger.warning(
            "Level-match amix failed; retrying plain amix (%s)",
            (result.stderr or "")[:300],
        )
        cmd_plain = [
            str(ffmpeg),
            "-y",
            "-i",
            str(raw_path),
            "-filter_complex",
            f"[{_SYSTEM_TRACK}][{_MIC_TRACK}]amix=inputs=2:duration=longest:normalize=0",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(out),
        ]
        plain = subprocess.run(cmd_plain, capture_output=True, text=True)
        return plain.returncode == 0 and out.is_file() and out.stat().st_size > 64

    def _mic_level_match_gain_db(self, ffmpeg: Path, raw_path: Path) -> float:
        """Gain (dB) so mic mean volume approaches system mean; clamped.

        Means are estimated from the first ``_LEVEL_MATCH_DETECT_WINDOW_S``
        seconds only so long recordings do not stall Stop on full-file decode.
        """
        window_s = _LEVEL_MATCH_DETECT_WINDOW_S
        sys_mean = self._volumedetect_mean_db(ffmpeg, raw_path, _SYSTEM_TRACK, window_s)
        mic_mean = self._volumedetect_mean_db(ffmpeg, raw_path, _MIC_TRACK, window_s)
        if sys_mean is None or mic_mean is None:
            self.logger.info(
                "Level-match skipped (volumedetect unavailable) window_s=%.1f",
                window_s,
            )
            return 0.0
        raw_gain = sys_mean - mic_mean
        gain = max(_LEVEL_MATCH_GAIN_MIN_DB, min(_LEVEL_MATCH_GAIN_MAX_DB, raw_gain))
        self.logger.info(
            "Level-match window_s=%.1f system_db=%.1f mic_db=%.1f "
            "raw_gain_db=%.1f clamped_db=%.1f",
            window_s,
            sys_mean,
            mic_mean,
            raw_gain,
            gain,
        )
        return gain

    def _volumedetect_mean_db(
        self,
        ffmpeg: Path,
        raw_path: Path,
        track: str,
        window_s: float = _LEVEL_MATCH_DETECT_WINDOW_S,
    ) -> float | None:
        # Cap decode: analyze from the start of the file only (stable, cheap).
        cmd = [
            str(ffmpeg),
            "-i",
            str(raw_path),
            "-t",
            f"{window_s:.3f}",
            "-map",
            track,
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        text = (result.stderr or "") + (result.stdout or "")
        match = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", text)
        if not match:
            return None
        try:
            return float(match.group(1))
        except ValueError:
            return None

    def _terminate_quiet(self) -> None:
        proc = self._proc
        if proc is None:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
        except OSError:
            pass
        self._cleanup_proc()

    def _cleanup_proc(self) -> None:
        self._proc = None

    @staticmethod
    def _friendly_launch_error(raw: str) -> str:
        text = (raw or "").strip()
        lower = text.lower()
        if "denied" in lower or "not authorized" in lower or "tcc" in lower:
            return (
                "Permission denied. In System Settings → Privacy & Security, allow "
                "Microphone and Screen & System Audio Recording for Scribe, then restart."
            )
        if text:
            # Keep it short for UI.
            first = text.splitlines()[0]
            if first.startswith("ERROR:"):
                first = first.replace("ERROR:", "", 1).strip()
            return first[:300] or "Recording failed."
        return "Recording failed. See the log for details."


def is_temp_recording(path: str | Path | None) -> bool:
    if not path:
        return False
    try:
        resolved = Path(path).resolve()
        return CACHE_DIR.resolve() in resolved.parents or resolved.parent == CACHE_DIR.resolve()
    except OSError:
        return False
