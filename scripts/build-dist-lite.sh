#!/usr/bin/env bash
# Deprecated: Scribe ships as a single build with runtime model selection.
# Kept so older docs/hooks keep working.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "==> build-dist-lite.sh is deprecated — building standard Scribe.app instead" >&2
exec "$ROOT/scripts/build-dist.sh" "$@"
