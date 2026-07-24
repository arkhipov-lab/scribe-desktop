#!/usr/bin/env bash
# Build the single dist profile (relocatable .app + versioned DMG) into dist/.
# Used by the post-merge hook after a local version bump on main.
#
# Env:
#   SKIP_RELEASE_BUILD=1        no-op
#   SCRIBE_RELEASE_BUILD_FG=1   run in foreground (default: background)
#   MAKE_DMG=1                  passed through (default 1)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/use-xcode-toolchain.sh"

if [[ "${SKIP_RELEASE_BUILD:-0}" == "1" ]]; then
  echo "SKIP_RELEASE_BUILD=1 — skipping dist builds"
  exit 0
fi

chmod +x \
  "$ROOT/scripts/build-dist.sh" \
  "$ROOT/scripts/build-dist-standard.sh" \
  "$ROOT/scripts/read-version.sh" \
  "$ROOT/scripts/bundle-ffmpeg.sh" \
  "$ROOT/scripts/prune-runtime.sh" \
  "$ROOT/scripts/ensure-compatible-ffmpeg.sh" \
  "$ROOT/scripts/assert-macho-minos.sh" \
  "$ROOT/scripts/use-xcode-toolchain.sh" 2>/dev/null || true

VERSION="$("$ROOT/scripts/read-version.sh")"
LOG_DIR="$ROOT/.cache"
LOG_FILE="$LOG_DIR/release-build.log"
mkdir -p "$LOG_DIR" "$ROOT/dist"

run_builds() {
  set -euo pipefail
  # shellcheck disable=SC1091
  source "$ROOT/scripts/use-xcode-toolchain.sh"
  echo "==> Local release build for v${VERSION}"
  echo "==> DEVELOPER_DIR=${DEVELOPER_DIR:-} SDKROOT=${SDKROOT:-}"
  echo "==> $(date '+%Y-%m-%d %H:%M:%S') starting dist build"
  MAKE_DMG="${MAKE_DMG:-1}" "$ROOT/scripts/build-dist.sh"
  echo "==> $(date '+%Y-%m-%d %H:%M:%S') verifying artifacts"
  local missing=0
  for path in \
    "$ROOT/dist/Scribe.app" \
    "$ROOT/dist/Scribe-${VERSION}.dmg"
  do
    if [[ -e "$path" ]]; then
      ls -lh "$path"
    else
      echo "Missing required artifact: $path" >&2
      missing=1
    fi
  done
  if [[ "$missing" -ne 0 ]]; then
    return 1
  fi
  echo "==> $(date '+%Y-%m-%d %H:%M:%S') done"
}

if [[ "${SCRIBE_RELEASE_BUILD_FG:-0}" == "1" ]]; then
  run_builds
  exit 0
fi

# Background so git merge/pull returns quickly; builds can take a long time.
(
  set -euo pipefail
  echo "======== $(date '+%Y-%m-%d %H:%M:%S') release-build-local v${VERSION} ========"
  run_builds
  echo "======== $(date '+%Y-%m-%d %H:%M:%S') SUCCESS ========"
) >>"$LOG_FILE" 2>&1 &
pid=$!
echo "post-merge: dist build started in background (pid $pid)"
echo "  log: $LOG_FILE"
echo "  expect: dist/Scribe.app, dist/Scribe-${VERSION}.dmg"
echo "  foreground instead: SCRIBE_RELEASE_BUILD_FG=1"
echo "  skip builds:        SKIP_RELEASE_BUILD=1"
