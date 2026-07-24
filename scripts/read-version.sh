#!/usr/bin/env bash
# Print the project semver from VERSION (repo root).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="${VERSION_FILE:-$ROOT/VERSION}"

if [[ ! -f "$VERSION_FILE" ]]; then
  echo "VERSION file missing: $VERSION_FILE" >&2
  exit 1
fi

# Trim whitespace / newlines
tr -d '[:space:]' < "$VERSION_FILE"
