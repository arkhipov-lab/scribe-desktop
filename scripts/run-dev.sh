#!/usr/bin/env bash
# Development launcher for Scribe (macOS arm64).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
  echo "This app targets Apple Silicon (arm64). Current arch: $ARCH" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/.venv"
FRONTEND_DIR="$ROOT/frontend"
DEV_URL="${DEV_URL:-http://127.0.0.1:5173}"
USE_VITE_DEV="${USE_VITE_DEV:-1}"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [[ ! -f "$VENV_DIR/.deps-installed" ]] || [[ "$ROOT/requirements.txt" -nt "$VENV_DIR/.deps-installed" ]]; then
  echo "Installing Python dependencies…"
  pip install --upgrade pip
  pip install -r "$ROOT/requirements.txt"
  touch "$VENV_DIR/.deps-installed"
else
  echo "Python dependencies already installed."
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Installing frontend dependencies…"
  (cd "$FRONTEND_DIR" && npm install)
else
  echo "Frontend dependencies already installed."
fi

export PATH="/opt/homebrew/bin:${PATH}"

echo "Ensuring AudioRecorder helper is built…"
mkdir -p "$ROOT/native/build"
MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-14.0}"
export MACOSX_DEPLOYMENT_TARGET
if [[ ! -x "$ROOT/native/build/AudioRecorder" ]] || [[ "$ROOT/native/AudioRecorder.swift" -nt "$ROOT/native/build/AudioRecorder" ]]; then
  swiftc -O -parse-as-library \
    -target "arm64-apple-macosx${MACOSX_DEPLOYMENT_TARGET}" \
    -o "$ROOT/native/build/AudioRecorder" \
    "$ROOT/native/AudioRecorder.swift" \
    -framework ScreenCaptureKit \
    -framework AVFoundation \
    -framework CoreMedia \
    -framework Foundation
fi

cleanup() {
  if [[ -n "${VITE_PID:-}" ]] && kill -0 "$VITE_PID" 2>/dev/null; then
    kill "$VITE_PID" 2>/dev/null || true
    wait "$VITE_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ "$USE_VITE_DEV" == "1" ]]; then
  echo "Starting Vite dev server…"
  (cd "$FRONTEND_DIR" && npm run dev -- --host 127.0.0.1 --port 5173) &
  VITE_PID=$!

  echo "Waiting for $DEV_URL …"
  for _ in $(seq 1 60); do
    if curl -fsS "$DEV_URL" >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "$VITE_PID" 2>/dev/null; then
      echo "Vite failed to start." >&2
      exit 1
    fi
    sleep 0.25
  done

  echo "Launching desktop app (dev UI)…"
  cd "$ROOT/backend"
  python app.py --dev-url "$DEV_URL"
else
  echo "Building frontend…"
  (cd "$FRONTEND_DIR" && npm run build)
  echo "Launching desktop app (production UI)…"
  cd "$ROOT/backend"
  python app.py
fi
