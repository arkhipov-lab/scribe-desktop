#!/usr/bin/env bash
# Build a self-contained arm64 Scribe.app (+ optional DMG).
#
# One product build: models are chosen at runtime from Processing options.
#
# Usage:
#   ./scripts/build-dist.sh
#   MAKE_DMG=0 ./scripts/build-dist.sh
#   FORCE_RUNTIME=1 ./scripts/build-dist.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer Xcode.app SDK (avoids CLT MacOSX26 + older swiftc mismatch).
# shellcheck disable=SC1091
source "$ROOT/scripts/use-xcode-toolchain.sh"

chmod +x "$ROOT/scripts/read-version.sh" 2>/dev/null || true
APP_VERSION="$("$ROOT/scripts/read-version.sh")"
echo "==> [dist] App version $APP_VERSION"
echo "==> [dist] SDKROOT=${SDKROOT:-}"

ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
  echo "Dist builds target Apple Silicon (arm64). Current arch: $ARCH" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -n "${PROFILE:-}" && "${PROFILE}" != "standard" ]]; then
  echo "==> [dist] Ignoring PROFILE='${PROFILE}' — single Scribe build (runtime model selection)" >&2
fi
PROFILE="standard"
APP_NAME="Scribe"
DMG_BASENAME="Scribe"
BUNDLE_ID="local.scribe.app"

DIST_DIR="$ROOT/dist"
APP_DIR="$DIST_DIR/$APP_NAME.app"
CONTENTS="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"
ASSETS_DIR="$ROOT/assets"
ICON_SRC="$ROOT/icon.png"
ICNS_PATH="$ASSETS_DIR/AppIcon.icns"
CACHE_DIR="$ROOT/.cache/dist"
PYTHON_VERSION="3.13.14"
PYTHON_TAG="20260718"
PYTHON_ARCHIVE="cpython-${PYTHON_VERSION}+${PYTHON_TAG}-aarch64-apple-darwin-install_only_stripped.tar.gz"
PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PYTHON_TAG}/${PYTHON_ARCHIVE}"
RUNTIME_DIR="$CACHE_DIR/runtime"
RUNTIME_REQS="$ROOT/requirements-runtime.txt"
MAKE_DMG="${MAKE_DMG:-1}"
FORCE_RUNTIME="${FORCE_RUNTIME:-0}"
# Ship binaries that still run on macOS 14 Sonoma / 15 Sequoia (mlx wheels are 14+).
MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-14.0}"
export MACOSX_DEPLOYMENT_TARGET
COMPAT_PLATFORM="macosx_14_0_arm64"
MAX_MINOS_MAJOR="${MAX_MINOS_MAJOR:-14}"

mkdir -p "$CACHE_DIR" "$ASSETS_DIR"
chmod +x \
  "$ROOT/scripts/bundle-ffmpeg.sh" \
  "$ROOT/scripts/prune-runtime.sh" \
  "$ROOT/scripts/ensure-compatible-ffmpeg.sh" \
  "$ROOT/scripts/assert-macho-minos.sh" \
  "$ROOT/scripts/read-version.sh"

echo "==> [dist] Ensuring local tooling venv (for build helpers only)"
if [[ ! -d "$ROOT/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$ROOT/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"
if [[ ! -f "$ROOT/.venv/.deps-installed" ]] || [[ "$ROOT/requirements.txt" -nt "$ROOT/.venv/.deps-installed" ]]; then
  pip install --upgrade pip
  pip install -r "$ROOT/requirements.txt"
  touch "$ROOT/.venv/.deps-installed"
fi

echo "==> [dist] Building frontend"
if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  (cd "$ROOT/frontend" && npm install)
fi
(cd "$ROOT/frontend" && npm run build)

echo "==> [dist] App icon"
if [[ -f "$ICON_SRC" ]]; then
  ICONSET="$ASSETS_DIR/AppIcon.iconset"
  rm -rf "$ICONSET" "$ICNS_PATH"
  mkdir -p "$ICONSET"
  for SIZE in 16 32 128 256 512; do
    sips -z "$SIZE" "$SIZE" "$ICON_SRC" --out "$ICONSET/icon_${SIZE}x${SIZE}.png" >/dev/null
    sips -z $((SIZE * 2)) $((SIZE * 2)) "$ICON_SRC" --out "$ICONSET/icon_${SIZE}x${SIZE}@2x.png" >/dev/null
  done
  iconutil -c icns "$ICONSET" -o "$ICNS_PATH"
  rm -rf "$ICONSET"
elif [[ ! -f "$ICNS_PATH" ]]; then
  echo "Missing $ICON_SRC and $ICNS_PATH" >&2
  exit 1
fi

echo "==> [dist] Compiling launcher + AudioRecorder (minos $MACOSX_DEPLOYMENT_TARGET)"
mkdir -p "$ROOT/native/build"
"${SCRIBE_CLANG:-clang}" -O2 -arch arm64 \
  -mmacosx-version-min="$MACOSX_DEPLOYMENT_TARGET" \
  -isysroot "${SDKROOT:?SDKROOT not set — install Xcode.app}" \
  -o "$ROOT/native/build/Scribe" \
  "$ROOT/native/launcher.c"
"${SCRIBE_SWIFTC:-swiftc}" -O -parse-as-library \
  -sdk "${SDKROOT:?SDKROOT not set — install Xcode.app}" \
  -target "arm64-apple-macosx${MACOSX_DEPLOYMENT_TARGET}" \
  -o "$ROOT/native/build/AudioRecorder" \
  "$ROOT/native/AudioRecorder.swift" \
  -framework ScreenCaptureKit \
  -framework AVFoundation \
  -framework CoreMedia \
  -framework Foundation

echo "==> [dist] Fetching relocatable CPython (cached)"
PYTHON_TGZ="$CACHE_DIR/$PYTHON_ARCHIVE"
if [[ ! -f "$PYTHON_TGZ" ]]; then
  curl -fL --retry 3 -o "$PYTHON_TGZ.partial" "$PYTHON_URL"
  mv "$PYTHON_TGZ.partial" "$PYTHON_TGZ"
fi

STAMP="$RUNTIME_DIR/.stamp"
STAMP_TAG="py${PYTHON_VERSION}-${COMPAT_PLATFORM}-v1"
NEED_RUNTIME=0
if [[ "$FORCE_RUNTIME" == "1" ]]; then
  NEED_RUNTIME=1
elif [[ ! -x "$RUNTIME_DIR/python/bin/python3" ]]; then
  NEED_RUNTIME=1
elif [[ ! -f "$STAMP" ]] || [[ "$RUNTIME_REQS" -nt "$STAMP" ]]; then
  NEED_RUNTIME=1
elif [[ "$(cat "$STAMP" 2>/dev/null || true)" != "$STAMP_TAG" ]]; then
  NEED_RUNTIME=1
fi

smoke_runtime() {
  local py="$1"
  local label="$2"
  echo "==> [dist] Smoke: $label"
  "$py" - <<'PY'
import importlib

# Core app imports must work without torch.
for name in ("mlx", "mlx_whisper", "mlx_lm", "webview", "numba", "scipy"):
    importlib.import_module(name)

torch_ok = True
try:
    importlib.import_module("torch")
except ImportError:
    torch_ok = False

# mlx-whisper MLX path should not need torch.
import mlx_whisper
from mlx_whisper.audio import log_mel_spectrogram
import numpy as np

audio = np.zeros(16_000, dtype=np.float32)
_ = log_mel_spectrogram(audio)

from mlx_lm import load as _load  # noqa: F401

print("smoke ok; torch_present=", torch_ok)
if torch_ok:
    raise SystemExit(0)
PY
}

if [[ "$NEED_RUNTIME" == "1" ]]; then
  echo "==> [dist] Building cached runtime (python + runtime deps) — first time is slow"
  rm -rf "$RUNTIME_DIR"
  mkdir -p "$RUNTIME_DIR"
  tar -xzf "$PYTHON_TGZ" -C "$RUNTIME_DIR"
  if [[ ! -x "$RUNTIME_DIR/python/bin/python3" ]]; then
    echo "Standalone Python layout unexpected under $RUNTIME_DIR" >&2
    ls -la "$RUNTIME_DIR" >&2
    exit 1
  fi
  PY="$RUNTIME_DIR/python/bin/python3"
  "$PY" -m pip install --upgrade pip
  "$PY" -m pip install -r "$RUNTIME_REQS"

  echo "==> [dist] Forcing MLX wheels compatible with macOS ${MACOSX_DEPLOYMENT_TARGET}+ ($COMPAT_PLATFORM)"
  WHEEL_DIR="$CACHE_DIR/wheels-${COMPAT_PLATFORM}"
  rm -rf "$WHEEL_DIR"
  mkdir -p "$WHEEL_DIR"
  # Host pip on macOS 26 prefers macosx_26 wheels; pin the Sonoma/Sequoia builds instead.
  "$PY" -m pip download \
    mlx mlx-metal numpy scipy llvmlite numba \
    -d "$WHEEL_DIR" \
    --platform "$COMPAT_PLATFORM" \
    --python-version 3.13 \
    --implementation cp \
    --abi cp313 \
    --only-binary=:all:
  "$PY" -m pip install --force-reinstall --no-deps "$WHEEL_DIR"/*.whl

  echo "==> [dist] Attempting to drop unused torch stack (MLX path only)"
  "$PY" -m pip uninstall -y torch sympy networkx 2>/dev/null || true

  if ! smoke_runtime "$PY" "after torch uninstall"; then
    echo "==> [dist] Smoke failed without torch — restoring torch (safe fallback)"
    "$PY" -m pip install 'torch' 
    smoke_runtime "$PY" "with torch restored" || {
      echo "Runtime smoke failed even with torch restored" >&2
      exit 1
    }
  else
    echo "==> [dist] Torch stack removed successfully"
  fi

  "$ROOT/scripts/prune-runtime.sh" "$RUNTIME_DIR/python"
  smoke_runtime "$PY" "after prune" || {
    echo "Runtime smoke failed after prune" >&2
    exit 1
  }

  echo "$STAMP_TAG" >"$STAMP"
else
  echo "==> [dist] Reusing cached runtime at $RUNTIME_DIR"
fi

echo "==> [dist] Assembling $APP_NAME.app"
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES/backend" "$RESOURCES/frontend" "$RESOURCES/bin"

cp "$ROOT/native/build/Scribe" "$MACOS_DIR/Scribe"
cp "$ROOT/native/build/AudioRecorder" "$MACOS_DIR/AudioRecorder"
chmod +x "$MACOS_DIR/Scribe" "$MACOS_DIR/AudioRecorder"

cp "$ROOT/backend/app.py" "$RESOURCES/backend/"
cp "$ROOT/backend/transcriber.py" "$RESOURCES/backend/"
cp "$ROOT/backend/logger.py" "$RESOURCES/backend/"
cp "$ROOT/backend/recorder.py" "$RESOURCES/backend/"
cp "$ROOT/backend/languages.py" "$RESOURCES/backend/"
cp "$ROOT/backend/summarizer.py" "$RESOURCES/backend/"
cp "$ROOT/backend/summary_presets.py" "$RESOURCES/backend/"
cp "$ROOT/backend/settings.py" "$RESOURCES/backend/"
cp "$ROOT/backend/model_catalog.py" "$RESOURCES/backend/"
cp "$ROOT/backend/hardware.py" "$RESOURCES/backend/"
cp "$ROOT/backend/macos_app.py" "$RESOURCES/backend/"
cp "$ROOT/backend/profile_config.py" "$RESOURCES/backend/"
cp "$ROOT/backend/memory.py" "$RESOURCES/backend/"
cp "$ROOT/backend/version.py" "$RESOURCES/backend/"
cp "$ROOT/VERSION" "$RESOURCES/VERSION"
cp "$ROOT/VERSION" "$RESOURCES/backend/VERSION"
# Bake profile so the app does not depend on build-machine env at runtime.
"$ROOT/.venv/bin/python" - <<PY
from pathlib import Path
import sys
sys.path.insert(0, str(Path("$ROOT") / "backend"))
from profile_config import write_profile_json
write_profile_json(Path("$RESOURCES") / "profile.json", "$PROFILE")
print("profile:", "$PROFILE")
PY
# Also keep a copy next to backend modules for import-time discovery without SCRIBE_ROOT.
cp "$RESOURCES/profile.json" "$RESOURCES/backend/profile.json"
cp -R "$ROOT/frontend/dist" "$RESOURCES/frontend/dist"
cp "$ICNS_PATH" "$RESOURCES/AppIcon.icns"

echo "==> [dist] Copying embedded Python runtime"
rm -rf "$RESOURCES/python"
mkdir -p "$RESOURCES/python"
if command -v rsync >/dev/null 2>&1; then
  rsync -a "$RUNTIME_DIR/python/" "$RESOURCES/python/"
else
  cp -R "$RUNTIME_DIR/python/." "$RESOURCES/python/"
fi
chmod +x "$RESOURCES/python/bin/python3" || true

# Final prune on the copy (idempotent)
"$ROOT/scripts/prune-runtime.sh" "$RESOURCES/python"

echo "==> [dist] Bundling compatible ffmpeg (not Homebrew-on-macOS-26)"
FFMPEG_SRC="${FFMPEG_SRC:-}"
if [[ -z "$FFMPEG_SRC" ]]; then
  FFMPEG_SRC="$("$ROOT/scripts/ensure-compatible-ffmpeg.sh" "$MAX_MINOS_MAJOR")"
fi
"$ROOT/scripts/bundle-ffmpeg.sh" "$FFMPEG_SRC" "$RESOURCES"

FF_ARCH="$(file "$RESOURCES/bin/ffmpeg" | tr ' ' '\n' | grep -E 'arm64|x86_64' | head -1 || true)"
if [[ "$FF_ARCH" != "arm64" ]]; then
  echo "Bundled ffmpeg is not arm64 ($FF_ARCH). Refusing dist build." >&2
  exit 1
fi

echo "==> [dist] Asserting Mach-O minos <= ${MAX_MINOS_MAJOR}.0"
"$ROOT/scripts/assert-macho-minos.sh" "$MACOS_DIR" "$MAX_MINOS_MAJOR"
"$ROOT/scripts/assert-macho-minos.sh" "$RESOURCES/bin" "$MAX_MINOS_MAJOR"
if [[ -d "$RESOURCES/lib" ]]; then
  "$ROOT/scripts/assert-macho-minos.sh" "$RESOURCES/lib" "$MAX_MINOS_MAJOR"
fi
"$ROOT/scripts/assert-macho-minos.sh" "$RESOURCES/python" "$MAX_MINOS_MAJOR"

cat > "$CONTENTS/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>Scribe</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>CFBundleIdentifier</key>
  <string>${BUNDLE_ID}</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleDisplayName</key>
  <string>${APP_NAME}</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>${APP_VERSION}</string>
  <key>CFBundleVersion</key>
  <string>${APP_VERSION}</string>
  <key>CFBundleGetInfoString</key>
  <string>${APP_NAME} ${APP_VERSION} — On-device transcription and notes. Nothing leaves your Mac.</string>
  <key>NSHumanReadableCopyright</key>
  <string>On-device transcription and notes. Nothing leaves your Mac.</string>
  <key>LSMinimumSystemVersion</key>
  <string>${MACOSX_DEPLOYMENT_TARGET}</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSMicrophoneUsageDescription</key>
  <string>${APP_NAME} records your microphone together with system audio for local transcription.</string>
  <key>NSAudioCaptureUsageDescription</key>
  <string>${APP_NAME} captures system audio for local transcription only.</string>
  <key>NSScreenCaptureDescription</key>
  <string>${APP_NAME} uses screen-capture permission to record system audio. Video is not saved.</string>
</dict>
</plist>
EOF

codesign --force -s - "$MACOS_DIR/Scribe" >/dev/null 2>&1 || true
codesign --force -s - "$MACOS_DIR/AudioRecorder" >/dev/null 2>&1 || true
codesign --force -s - --deep "$APP_DIR" >/dev/null 2>&1 || true
xattr -cr "$APP_DIR" 2>/dev/null || true

echo "==> [dist] Final smoke on assembled .app"
SCRIBE_ROOT="$RESOURCES" PATH="$RESOURCES/bin:$PATH" \
  smoke_runtime "$RESOURCES/python/bin/python3" "assembled app" || {
  echo "Assembled app smoke failed" >&2
  exit 1
}

# Assert torch is absent when possible (non-fatal warning if fallback kept it)
if "$RESOURCES/python/bin/python3" -c "import torch" 2>/dev/null; then
  echo "==> [dist] NOTE: torch is still present in the bundle"
else
  echo "==> [dist] torch absent from bundle (good)"
fi

echo "==> [dist] Size audit (top site-packages)"
SP="$(echo "$RESOURCES"/python/lib/python*/site-packages)"
if [[ -d "$SP" ]]; then
  du -sh "$SP"/* 2>/dev/null | sort -hr | head -20 || true
fi
du -sh "$APP_DIR" || true

if [[ "$MAKE_DMG" == "1" ]]; then
  echo "==> [dist] Creating DMG (${DMG_BASENAME}-${APP_VERSION})"
  DMG_ROOT="$DIST_DIR/dmg-root"
  DMG_PATH="$DIST_DIR/${DMG_BASENAME}-${APP_VERSION}.dmg"
  rm -rf "$DMG_ROOT" "$DMG_PATH"
  mkdir -p "$DMG_ROOT"
  ditto "$APP_DIR" "$DMG_ROOT/$APP_NAME.app"
  ln -s /Applications "$DMG_ROOT/Applications"
  hdiutil create \
    -volname "${APP_NAME} ${APP_VERSION}" \
    -srcfolder "$DMG_ROOT" \
    -ov \
    -format UDZO \
    "$DMG_PATH"
  rm -rf "$DMG_ROOT"
  xattr -cr "$DMG_PATH" 2>/dev/null || true
  echo "==> DMG: $DMG_PATH ($(du -sh "$DMG_PATH" | awk '{print $1}'))"
fi

echo "==> Built self-contained app: $APP_DIR ($(du -sh "$APP_DIR" | awk '{print $1}')) [profile=$PROFILE version=$APP_VERSION]"
echo "Open with: open \"$APP_DIR\""
echo "Friends: mount DMG → drag to Applications → right-click Open / Open Anyway"
