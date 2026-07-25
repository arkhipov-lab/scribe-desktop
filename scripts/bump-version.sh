#!/usr/bin/env bash
# Bump VERSION from conventional commits since the last v* tag (or repo root).
#
# Usage:
#   ./scripts/bump-version.sh              # print planned bump (no write)
#   ./scripts/bump-version.sh --apply      # write VERSION (+ package.json)
#   ./scripts/bump-version.sh --commit     # apply + git commit + annotated tag
#   ./scripts/bump-version.sh --force patch|minor|major
#
# Env:
#   SKIP_VERSION_BUMP=1   no-op exit 0
#   VERSION_FILE=path     override VERSION path
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_VERSION_BUMP:-0}" == "1" ]]; then
  echo "SKIP_VERSION_BUMP=1 — skipping"
  exit 0
fi

VERSION_FILE="${VERSION_FILE:-$ROOT/VERSION}"
MODE="plan" # plan | apply | commit
FORCE_LEVEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) MODE="apply"; shift ;;
    --commit) MODE="commit"; shift ;;
    --force)
      FORCE_LEVEL="${2:-}"
      if [[ ! "$FORCE_LEVEL" =~ ^(major|minor|patch)$ ]]; then
        echo "Usage: --force major|minor|patch" >&2
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "$VERSION_FILE" ]]; then
  echo "VERSION file missing: $VERSION_FILE" >&2
  exit 1
fi

CURRENT="$(tr -d '[:space:]' < "$VERSION_FILE")"
if [[ ! "$CURRENT" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid VERSION '$CURRENT' (expected MAJOR.MINOR.PATCH)" >&2
  exit 1
fi

last_tag="$(git describe --tags --match 'v[0-9]*' --abbrev=0 2>/dev/null || true)"
if [[ -n "$last_tag" ]]; then
  BASE="${last_tag#v}"
  RANGE="${last_tag}..HEAD"
else
  BASE="$CURRENT"
  RANGE=""
fi

if [[ ! "$BASE" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid base version from tag '$last_tag' → '$BASE'" >&2
  exit 1
fi

IFS=. read -r MAJOR MINOR PATCH <<<"$BASE"

# Score: 0=none, 1=patch, 2=minor, 3=major
score=0

classify_message() {
  local msg="$1"
  local first
  # First non-empty line (subjects only from tformat:%s; still safe if body is passed)
  first="$(printf '%s\n' "$msg" | awk 'NF { print; exit }')"
  [[ -n "$first" ]] || return 0

  # Ignore our own release commits
  if printf '%s\n' "$first" | grep -qE '^chore\(release\)(:|!)'; then
    return 0
  fi

  if printf '%s\n' "$msg" | grep -qiE '^BREAKING([ -]CHANGE)?([[:space:]]|:|$)'; then
    score=3
    return 0
  fi

  # type!: or type(scope)!:
  if printf '%s\n' "$first" | grep -qE '^(feat|fix|perf|refactor|chore|docs|test|ci|build|style|revert)(\([^)]+\))?!:'; then
    score=3
    return 0
  fi

  if printf '%s\n' "$first" | grep -qE '^feat(\([^)]+\))?:'; then
    if (( score < 2 )); then score=2; fi
    return 0
  fi

  if printf '%s\n' "$first" | grep -qE '^(fix|perf|refactor|chore|docs|test|ci|build|style|revert)(\([^)]+\))?:'; then
    if (( score < 1 )); then score=1; fi
    return 0
  fi
}

# Subjects via tformat:%s — one line per commit, no inter-commit newline/NUL hazards
# from git log --format=%B%x00 (which left a leading \n on every commit after the first).
log_subjects() {
  if [[ -n "$RANGE" ]]; then
    git log --pretty=tformat:%s "$RANGE" 2>/dev/null || true
  else
    git log --pretty=tformat:%s HEAD 2>/dev/null || true
  fi
}

# Full bodies for BREAKING CHANGE footers (tformat + %x00 = record terminator, not separator)
log_bodies() {
  if [[ -n "$RANGE" ]]; then
    git log --pretty=tformat:%B%x00 "$RANGE" 2>/dev/null || true
  else
    git log --pretty=tformat:%B%x00 HEAD 2>/dev/null || true
  fi
}

if [[ -n "$FORCE_LEVEL" ]]; then
  case "$FORCE_LEVEL" in
    major) score=3 ;;
    minor) score=2 ;;
    patch) score=1 ;;
  esac
else
  while IFS= read -r subject || [[ -n "${subject:-}" ]]; do
    [[ -z "${subject:-}" ]] && continue
    classify_message "$subject"
  done < <(log_subjects)

  while IFS= read -r -d '' body || [[ -n "${body:-}" ]]; do
    if printf '%s\n' "$body" | grep -qiE '^BREAKING([ -]CHANGE)?([[:space:]]|:|$)'; then
      score=3
      break
    fi
  done < <(log_bodies)
fi

if [[ "$score" -eq 0 ]]; then
  echo "No conventional commits requiring a bump (VERSION=$CURRENT, base=$BASE, tag=${last_tag:-none})"
  exit 0
fi

case "$score" in
  3) NEW="$((MAJOR + 1)).0.0"; LEVEL="major" ;;
  2) NEW="${MAJOR}.$((MINOR + 1)).0"; LEVEL="minor" ;;
  1) NEW="${MAJOR}.${MINOR}.$((PATCH + 1))"; LEVEL="patch" ;;
  *)
    echo "Internal error: bad score $score" >&2
    exit 1
    ;;
esac

if git rev-parse "v${NEW}" >/dev/null 2>&1; then
  if [[ "$CURRENT" != "$NEW" ]]; then
    echo "Tag v${NEW} exists but VERSION is $CURRENT — syncing file"
    if [[ "$MODE" == "plan" ]]; then
      echo "Would sync VERSION → $NEW"
      exit 0
    fi
    printf '%s\n' "$NEW" > "$VERSION_FILE"
    echo "Synced VERSION to $NEW"
  else
    echo "Already released v${NEW}"
  fi
  exit 0
fi

if [[ "$CURRENT" == "$NEW" ]]; then
  echo "VERSION already $NEW (tag missing) — will tag on --commit"
  if [[ "$MODE" == "plan" ]]; then
    exit 0
  fi
  if [[ "$MODE" == "apply" ]]; then
    exit 0
  fi
  # fall through to commit/tag only
else
  echo "Bump $BASE → $NEW ($LEVEL) [current file=$CURRENT, range=${RANGE:-all}]"
fi

if [[ "$MODE" == "plan" ]]; then
  exit 0
fi

if [[ "$CURRENT" != "$NEW" ]]; then
  printf '%s\n' "$NEW" > "$VERSION_FILE"

  PKG="$ROOT/frontend/package.json"
  if [[ -f "$PKG" ]]; then
    python3 - "$PKG" "$NEW" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
data["version"] = ver
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
  fi
  echo "Wrote $VERSION_FILE (= $NEW)"
fi

if [[ "$MODE" != "commit" ]]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repo — wrote VERSION only" >&2
  exit 0
fi

PKG="$ROOT/frontend/package.json"
git add "$VERSION_FILE"
[[ -f "$PKG" ]] && git add "$PKG"

# If nothing staged (VERSION already correct), still create tag if needed
if ! git diff --cached --quiet; then
  git commit -m "chore(release): v${NEW}"
elif [[ "$(tr -d '[:space:]' < "$VERSION_FILE")" != "$NEW" ]]; then
  echo "VERSION mismatch and nothing to commit" >&2
  exit 1
fi

if ! git rev-parse "v${NEW}" >/dev/null 2>&1; then
  git tag -a "v${NEW}" -m "v${NEW}"
  echo "Tagged v${NEW}"
else
  echo "Tag v${NEW} already present"
fi
