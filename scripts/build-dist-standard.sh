#!/usr/bin/env bash
# Convenience wrapper: standard quality Scribe build (M3+ / 16GB+).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec env PROFILE=standard "$ROOT/scripts/build-dist.sh" "$@"
