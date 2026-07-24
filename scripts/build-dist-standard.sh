#!/usr/bin/env bash
# Build relocatable Scribe.app (+ versioned DMG) into dist/.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$ROOT/scripts/build-dist.sh" "$@"
