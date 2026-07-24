#!/usr/bin/env bash
# Copy ffmpeg + non-system dylibs into an app Resources tree and fix install names.
# Usage: bundle-ffmpeg.sh <ffmpeg-binary> <resources-dir>
# Compatible with macOS system Bash 3.2 (no associative arrays).
set -euo pipefail

SRC_FFMPEG="${1:?ffmpeg binary required}"
RESOURCES="${2:?resources dir required}"
BIN_DIR="$RESOURCES/bin"
LIB_DIR="$RESOURCES/lib"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/bundle-ffmpeg.XXXXXX")"
QUEUE="$WORK/queue"
SEEN="$WORK/seen"
mkdir -p "$BIN_DIR" "$LIB_DIR" "$SEEN"
: >"$QUEUE"

cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

cp "$SRC_FFMPEG" "$BIN_DIR/ffmpeg"
chmod +x "$BIN_DIR/ffmpeg"

is_system_lib() {
  case "$1" in
    /System/*|/usr/lib/*) return 0 ;;
    *) return 1 ;;
  esac
}

mark_seen() {
  local key
  key="$(printf '%s' "$1" | shasum -a 256 | awk '{print $1}')"
  touch "$SEEN/$key"
}

was_seen() {
  local key
  key="$(printf '%s' "$1" | shasum -a 256 | awk '{print $1}')"
  [[ -f "$SEEN/$key" ]]
}

enqueue() {
  printf '%s\n' "$1" >>"$QUEUE"
}

mark_seen "$BIN_DIR/ffmpeg"
enqueue "$BIN_DIR/ffmpeg"

IDX=1
while true; do
  CURRENT="$(sed -n "${IDX}p" "$QUEUE" || true)"
  [[ -z "${CURRENT:-}" ]] && break
  IDX=$((IDX + 1))

  while IFS= read -r dep; do
    [[ -z "$dep" ]] && continue
    is_system_lib "$dep" && continue
    [[ -e "$dep" ]] || continue
    base="$(basename "$dep")"
    dest="$LIB_DIR/$base"
    if ! was_seen "$dest"; then
      cp "$dep" "$dest"
      chmod +w "$dest" 2>/dev/null || true
      mark_seen "$dest"
      enqueue "$dest"
    fi
  done < <(otool -L "$CURRENT" | awk 'NR>1 {print $1}')
done

while IFS= read -r dep; do
  [[ -z "$dep" ]] && continue
  is_system_lib "$dep" && continue
  base="$(basename "$dep")"
  if [[ -f "$LIB_DIR/$base" ]]; then
    install_name_tool -change "$dep" "@loader_path/../lib/$base" "$BIN_DIR/ffmpeg" 2>/dev/null || true
  fi
done < <(otool -L "$BIN_DIR/ffmpeg" | awk 'NR>1 {print $1}')

for dylib in "$LIB_DIR"/*.dylib; do
  [[ -e "$dylib" ]] || continue
  base="$(basename "$dylib")"
  install_name_tool -id "@loader_path/$base" "$dylib" 2>/dev/null || true
  while IFS= read -r dep; do
    [[ -z "$dep" ]] && continue
    is_system_lib "$dep" && continue
    dep_base="$(basename "$dep")"
    if [[ -f "$LIB_DIR/$dep_base" ]]; then
      install_name_tool -change "$dep" "@loader_path/$dep_base" "$dylib" 2>/dev/null || true
    fi
  done < <(otool -L "$dylib" | awk 'NR>1 {print $1}')
done

codesign --force -s - "$BIN_DIR/ffmpeg" >/dev/null 2>&1 || true
for dylib in "$LIB_DIR"/*.dylib; do
  [[ -e "$dylib" ]] || continue
  codesign --force -s - "$dylib" >/dev/null 2>&1 || true
done

count="$(find "$LIB_DIR" -name '*.dylib' | wc -l | tr -d ' ')"
echo "Bundled ffmpeg -> $BIN_DIR/ffmpeg ($count libs)"
