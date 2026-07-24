#!/usr/bin/env bash
# Build macOS arm64 .app for Scribe.
#
# MLX + mlx-whisper do not package reliably with a fully frozen PyInstaller
# bundle. This script builds a real .app that embeds the UI/backend and launches
# via a Mach-O stub + the project virtualenv (so Finder double-click works).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Prefer Xcode.app SDK (avoids CLT MacOSX26 + older swiftc mismatch).
# shellcheck disable=SC1091
source "$ROOT/scripts/use-xcode-toolchain.sh"

chmod +x "$ROOT/scripts/read-version.sh" 2>/dev/null || true
APP_VERSION="$("$ROOT/scripts/read-version.sh")"
echo "==> App version $APP_VERSION"
echo "==> SDKROOT=${SDKROOT:-}"

ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
  echo "This app targets Apple Silicon (arm64). Current arch: $ARCH" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/.venv"
APP_NAME="Scribe"
MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-14.0}"
export MACOSX_DEPLOYMENT_TARGET
DIST_DIR="$ROOT/dist"
APP_DIR="$DIST_DIR/$APP_NAME.app"
CONTENTS="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"
ASSETS_DIR="$ROOT/assets"
ICON_SRC="$ROOT/icon.png"
ICNS_PATH="$ASSETS_DIR/AppIcon.icns"

echo "==> Ensuring Python venv and dependencies"
if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
if [[ ! -f "$VENV_DIR/.deps-installed" ]] || [[ "$ROOT/requirements.txt" -nt "$VENV_DIR/.deps-installed" ]]; then
  pip install --upgrade pip
  pip install -r "$ROOT/requirements.txt"
  touch "$VENV_DIR/.deps-installed"
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "Virtualenv python not found at $VENV_DIR/bin/python" >&2
  exit 1
fi

echo "==> Building frontend"
if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  (cd "$ROOT/frontend" && npm install)
fi
(cd "$ROOT/frontend" && npm run build)

echo "==> Building app icon (.icns)"
mkdir -p "$ASSETS_DIR"
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
elif [[ -f "$ICNS_PATH" ]]; then
  echo "Using existing $ICNS_PATH"
else
  echo "Missing $ICON_SRC and $ICNS_PATH" >&2
  exit 1
fi

echo "==> Compiling Mach-O launcher (required for Finder double-click)"
mkdir -p "$ROOT/native/build"
"${SCRIBE_CLANG:-clang}" -O2 -arch arm64 \
  -mmacosx-version-min="$MACOSX_DEPLOYMENT_TARGET" \
  -isysroot "${SDKROOT:?SDKROOT not set — install Xcode.app}" \
  -o "$ROOT/native/build/Scribe" \
  "$ROOT/native/launcher.c"

echo "==> Compiling AudioRecorder (ScreenCaptureKit mic + system audio)"
"${SCRIBE_SWIFTC:-swiftc}" -O -parse-as-library \
  -sdk "${SDKROOT:?SDKROOT not set — install Xcode.app}" \
  -target "arm64-apple-macosx${MACOSX_DEPLOYMENT_TARGET}" \
  -o "$ROOT/native/build/AudioRecorder" \
  "$ROOT/native/AudioRecorder.swift" \
  -framework ScreenCaptureKit \
  -framework AVFoundation \
  -framework CoreMedia \
  -framework Foundation

echo "==> Assembling $APP_NAME.app"
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES/backend" "$RESOURCES/frontend"

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
"$VENV_DIR/bin/python" -c "
from pathlib import Path
import sys
sys.path.insert(0, '$ROOT/backend')
from profile_config import write_profile_json
write_profile_json(Path('$RESOURCES') / 'profile.json', 'standard')
write_profile_json(Path('$RESOURCES') / 'backend' / 'profile.json', 'standard')
"
cp -R "$ROOT/frontend/dist" "$RESOURCES/frontend/dist"
cp "$ICNS_PATH" "$RESOURCES/AppIcon.icns"
printf '%s\n' "$VENV_DIR/bin/python" > "$RESOURCES/venv_python"

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
  <string>local.scribe.app</string>
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
  <string>13.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>NSMicrophoneUsageDescription</key>
  <string>Scribe records your microphone together with system audio for local transcription.</string>
  <key>NSAudioCaptureUsageDescription</key>
  <string>Scribe captures system audio for local transcription only.</string>
  <key>NSScreenCaptureDescription</key>
  <string>Scribe uses screen-capture permission to record system audio. Video is not saved.</string>
</dict>
</plist>
EOF

# Clear quarantine so Finder can open unsigned local builds without Gatekeeper friction.
xattr -cr "$APP_DIR" 2>/dev/null || true

# Optional PyInstaller onedir artifact for experimentation (not the primary .app).
if [[ "${WITH_PYINSTALLER:-0}" == "1" ]]; then
  echo "==> Also building experimental PyInstaller onedir (may fail with MLX)"
  pip install -r "$ROOT/requirements-dev.txt"
  pyinstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "ScribePyInstaller" \
    --paths "$ROOT/backend" \
    --add-data "$ROOT/frontend/dist:frontend/dist" \
    --collect-all mlx \
    --collect-all mlx_whisper \
    --collect-all huggingface_hub \
    --hidden-import mlx \
    --hidden-import mlx_whisper \
    --hidden-import webview \
    "$ROOT/backend/app.py" || echo "PyInstaller build failed (expected with MLX); primary .app is still available."
fi

echo "==> Built: $APP_DIR"
echo "Open with: open \"$APP_DIR\""
echo "Or double-click the app in Finder."
