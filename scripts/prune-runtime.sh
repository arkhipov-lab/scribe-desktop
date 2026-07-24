#!/usr/bin/env bash
# Prune a bundled CPython tree for smaller .app size (safe for runtime).
# Usage: prune-runtime.sh <python-root>   e.g. .../Resources/python
set -euo pipefail

PY_ROOT="${1:?python root required}"
SITE="$PY_ROOT/lib"
if [[ ! -d "$SITE" ]]; then
  echo "No lib/ under $PY_ROOT" >&2
  exit 1
fi

echo "==> Pruning runtime under $PY_ROOT"

# Bytecode / caches
find "$PY_ROOT" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
find "$PY_ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true

# Only remove known-safe test trees (never touch numpy/scipy internals).
while IFS= read -r -d '' dir; do
  case "$dir" in
    */numpy/*|*/scipy/*|*/numba/*) continue ;;
  esac
  rm -rf "$dir"
done < <(find "$SITE" -type d \( \
  -name 'PyObjCTest' -o \
  -name 'idle_test' \
\) -print0 2>/dev/null || true)

# Drop packaging-only tools if present (not needed at app runtime).
# Keep setuptools — some packages still resolve entry points via it.
for pkg in pip wheel pyinstaller pyinstaller_hooks_contrib _pyinstaller_hooks_contrib build; do
  find "$SITE" -maxdepth 4 -type d \( -name "$pkg" -o -name "${pkg}-*" \) -prune -exec rm -rf {} + 2>/dev/null || true
done

echo "==> Prune done"
