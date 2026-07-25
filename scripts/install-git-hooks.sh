#!/usr/bin/env bash
# Point this repo at .githooks/ (version bump + local dist build on pull of main).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p "$ROOT/.githooks"
chmod +x "$ROOT/.githooks/"* \
  "$ROOT/scripts/bump-version.sh" \
  "$ROOT/scripts/read-version.sh" \
  "$ROOT/scripts/release-build-local.sh" 2>/dev/null || true

current="$(git config --get core.hooksPath || true)"
desired=".githooks"
if [[ "$current" == "$desired" ]]; then
  echo "Git hooks already using $desired"
  exit 0
fi

git config core.hooksPath "$desired"
echo "Configured core.hooksPath=$desired"
