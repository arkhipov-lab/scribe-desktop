#!/usr/bin/env bash
# Fail if any Mach-O under a path has LC minos major > MAX_MAJOR (default 14).
set -euo pipefail

ROOT_PATH="${1:?path required}"
MAX_MAJOR="${2:-14}"

macho_minos() {
  otool -l "$1" 2>/dev/null | awk '
    /LC_BUILD_VERSION/ {p=1}
    p && /minos/ {print $2; exit}
    /LC_VERSION_MIN_MACOSX/ {q=1}
    q && /version/ {print $2; exit}
  '
}

bad=0
while IFS= read -r -d '' f; do
  # Skip non-Mach-O quickly
  if ! file "$f" | grep -q 'Mach-O'; then
    continue
  fi
  v="$(macho_minos "$f")"
  [[ -z "$v" ]] && continue
  major="${v%%.*}"
  if [[ "$major" =~ ^[0-9]+$ ]] && [[ "$major" -gt "$MAX_MAJOR" ]]; then
    echo "INCOMPATIBLE minos=$v -> $f" >&2
    bad=1
  fi
done < <(find "$ROOT_PATH" \( -type f -perm +111 -o -name '*.dylib' -o -name '*.so' \) -print0 2>/dev/null)

if [[ "$bad" -ne 0 ]]; then
  echo "Found Mach-O binaries requiring macOS > $MAX_MAJOR.0" >&2
  exit 1
fi
echo "All scanned Mach-O binaries have minos <= $MAX_MAJOR.0"
