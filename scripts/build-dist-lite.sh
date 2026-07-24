#!/usr/bin/env bash
# Convenience wrapper: lightweight Scribe Lite build (M1 / 8GB-friendly).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec env PROFILE=lite "$ROOT/scripts/build-dist.sh" "$@"
