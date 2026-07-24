#!/usr/bin/env bash
# Ensure a macOS-compatible static ffmpeg is cached for dist builds.
# Homebrew ffmpeg on macOS 26+ often has minos 26 and will not run on Sequoia.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="$ROOT/.cache/dist/ffmpeg-static"
OUT="$CACHE_DIR/ffmpeg"
URL="${FFMPEG_STATIC_URL:-https://www.osxexperts.net/ffmpeg71arm.zip}"
MAX_MINOS_MAJOR="${1:-14}"

macho_minos_major() {
  local f="$1"
  local v
  v="$(otool -l "$f" 2>/dev/null | awk '
    /LC_BUILD_VERSION/ {p=1}
    p && /minos/ {print $2; exit}
    /LC_VERSION_MIN_MACOSX/ {q=1}
    q && /version/ {print $2; exit}
  ')"
  if [[ -z "$v" ]]; then
    echo "0"
    return
  fi
  echo "${v%%.*}"
}

mkdir -p "$CACHE_DIR"

if [[ -x "$OUT" ]]; then
  major="$(macho_minos_major "$OUT")"
  if [[ "$major" -le "$MAX_MINOS_MAJOR" ]]; then
    echo "$OUT"
    exit 0
  fi
  echo "Cached ffmpeg minos major=$major is too high; re-downloading…" >&2
fi

TMP="$CACHE_DIR/download"
rm -rf "$TMP"
mkdir -p "$TMP"
ZIP="$TMP/ffmpeg.zip"
curl -fL --retry 3 -o "$ZIP" "$URL"
unzip -o "$ZIP" -d "$TMP" >/dev/null
CAND="$(find "$TMP" -type f -name ffmpeg | head -1)"
if [[ -z "$CAND" || ! -f "$CAND" ]]; then
  echo "Could not find ffmpeg binary in $URL" >&2
  exit 1
fi
cp "$CAND" "$OUT"
chmod +x "$OUT"
codesign --force -s - "$OUT" >/dev/null 2>&1 || true

major="$(macho_minos_major "$OUT")"
arch="$(file "$OUT" | tr ' ' '\n' | grep -E 'arm64|x86_64' | head -1 || true)"
if [[ "$arch" != "arm64" ]]; then
  echo "Static ffmpeg is not arm64 ($arch)" >&2
  exit 1
fi
if [[ "$major" -gt "$MAX_MINOS_MAJOR" ]]; then
  echo "Static ffmpeg minos major=$major exceeds max $MAX_MINOS_MAJOR" >&2
  exit 1
fi

echo "Cached compatible ffmpeg (minos major=$major) -> $OUT" >&2
echo "$OUT"
