#!/usr/bin/env bash
# Build both dist profiles (relocatable .app + versioned DMG) into dist/.
# Used by the post-merge hook after a local version bump on main.
#
# Env:
#   SKIP_RELEASE_BUILD=1        no-op
#   SCRIBE_RELEASE_BUILD_FG=1   run in foreground (default: background)
#   MAKE_DMG=1                  passed through (default 1)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_RELEASE_BUILD:-0}" == "1" ]]; then
  echo "SKIP_RELEASE_BUILD=1 — skipping dist builds"
  exit 0
fi

chmod +x \
  "$ROOT/scripts/build-dist.sh" \
  "$ROOT/scripts/build-dist-standard.sh" \
  "$ROOT/scripts/build-dist-lite.sh" \
  "$ROOT/scripts/read-version.sh" \
  "$ROOT/scripts/bundle-ffmpeg.sh" \
  "$ROOT/scripts/prune-runtime.sh" \
  "$ROOT/scripts/ensure-compatible-ffmpeg.sh" \
  "$ROOT/scripts/assert-macho-minos.sh" 2>/dev/null || true

VERSION="$("$ROOT/scripts/read-version.sh")"
LOG_DIR="$ROOT/.cache"
LOG_FILE="$LOG_DIR/release-build.log"
mkdir -p "$LOG_DIR" "$ROOT/dist"

run_builds() {
  echo "==> Local release build for v${VERSION}"
  echo "==> $(date '+%Y-%m-%d %H:%M:%S') starting standard + lite dist builds"
  MAKE_DMG="${MAKE_DMG:-1}" "$ROOT/scripts/build-dist-standard.sh"
  MAKE_DMG="${MAKE_DMG:-1}" "$ROOT/scripts/build-dist-lite.sh"
  echo "==> $(date '+%Y-%m-%d %H:%M:%S') done"
  echo "==> Artifacts:"
  ls -lh "$ROOT/dist/Scribe.app" "$ROOT/dist/Scribe Lite.app" \
    "$ROOT/dist/Scribe-${VERSION}.dmg" "$ROOT/dist/Scribe-Lite-${VERSION}.dmg" 2>/dev/null || \
    ls -lh "$ROOT/dist"/*"${VERSION}"* "$ROOT/dist"/*.app 2>/dev/null || true
}

if [[ "${SCRIBE_RELEASE_BUILD_FG:-0}" == "1" ]]; then
  run_builds
  exit 0
fi

# Background so git merge/pull returns quickly; builds can take a long time.
{
  echo "======== $(date '+%Y-%m-%d %H:%M:%S') release-build-local v${VERSION} ========"
  if run_builds; then
    echo "======== $(date '+%Y-%m-%d %H:%M:%S') SUCCESS ========"
  else
    echo "======== $(date '+%Y-%m-%d %H:%M:%S') FAILED (exit $?) ========"
    exit 1
  fi
} >>"$LOG_FILE" 2>&1 &
pid=$!
echo "post-merge: dist builds started in background (pid $pid)"
echo "  log: $LOG_FILE"
echo "  expect: dist/Scribe.app, dist/Scribe Lite.app,"
echo "          dist/Scribe-${VERSION}.dmg, dist/Scribe-Lite-${VERSION}.dmg"
echo "  foreground instead: SCRIBE_RELEASE_BUILD_FG=1"
echo "  skip builds:        SKIP_RELEASE_BUILD=1"
