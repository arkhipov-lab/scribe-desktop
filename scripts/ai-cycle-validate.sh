#!/usr/bin/env bash
# Validate the AI development cycle state before phase transitions or commit prep.
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="${AI_CYCLE_STATE:-$ROOT/.ai/state/current-cycle.json}"

errors=0

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  errors=$((errors + 1))
}

ok() {
  printf 'OK: %s\n' "$*"
}

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    fail "jq is required for AI cycle validation"
    return 1
  fi
}

jq_raw() {
  jq -r "$1" "$STATE_FILE"
}

is_truthy() {
  [[ "$1" == "true" ]]
}

is_clean_review_status() {
  [[ "$1" == "clean" ]]
}

is_qa_complete_status() {
  [[ "$1" == "passed" || "$1" == "skipped" || "$1" == "explicitly_skipped" ]]
}

check_state_json() {
  if [[ ! -f "$STATE_FILE" ]]; then
    fail "state file missing: $STATE_FILE"
    return
  fi

  if jq empty "$STATE_FILE" >/dev/null 2>&1; then
    ok "current-cycle.json is valid JSON"
  else
    fail "current-cycle.json is not valid JSON: $STATE_FILE"
  fi
}

check_ledger_exists() {
  local ledger_path ledger_abs
  ledger_path="$(jq_raw '.iteration.ledger_path // ""')"

  if [[ -z "$ledger_path" || "$ledger_path" == "null" ]]; then
    fail "iteration.ledger_path is missing"
    return
  fi

  ledger_abs="$ROOT/$ledger_path"
  if [[ -f "$ledger_abs" ]]; then
    ok "ledger exists: $ledger_path"
  else
    fail "ledger file missing: $ledger_path"
  fi
}

check_commit_gate_order() {
  local commit_allowed review_gate triage_status supervisor_qa scope_approved implementation_finished
  local errors_before=$errors
  commit_allowed="$(jq_raw '.gates.commit_allowed // false')"
  review_gate="$(jq_raw '.gates.review_gate // ""')"
  triage_status="$(jq_raw '.gates.triage_status // ""')"
  supervisor_qa="$(jq_raw '.gates.supervisor_qa // ""')"
  scope_approved="$(jq_raw '.gates.scope_approved // false')"
  implementation_finished="$(jq_raw '.gates.implementation_finished // false')"

  if ! is_truthy "$commit_allowed"; then
    ok "commit gate is closed"
    return
  fi

  if ! is_truthy "$scope_approved"; then
    fail "commit_allowed=true requires gates.scope_approved=true"
  fi
  if ! is_truthy "$implementation_finished"; then
    fail "commit_allowed=true requires gates.implementation_finished=true"
  fi
  if ! is_clean_review_status "$review_gate"; then
    fail "commit_allowed=true requires gates.review_gate=clean (found: $review_gate)"
  fi
  if ! is_clean_review_status "$triage_status"; then
    fail "commit_allowed=true requires gates.triage_status=clean (found: $triage_status)"
  fi
  if ! is_qa_complete_status "$supervisor_qa"; then
    fail "commit_allowed=true requires supervisor QA passed/skipped (found: $supervisor_qa)"
  fi

  if (( errors == errors_before )); then
    ok "commit_allowed prerequisites satisfied"
  fi
}

check_phase_gates() {
  local phase scope_approved implementation_finished review_gate triage_status supervisor_qa committed
  phase="$(jq_raw '.phase // ""')"
  scope_approved="$(jq_raw '.gates.scope_approved // false')"
  implementation_finished="$(jq_raw '.gates.implementation_finished // false')"
  review_gate="$(jq_raw '.gates.review_gate // ""')"
  triage_status="$(jq_raw '.gates.triage_status // ""')"
  supervisor_qa="$(jq_raw '.gates.supervisor_qa // ""')"
  committed="$(jq_raw '.gates.committed // false')"

  case "$phase" in
    planned|implementation-prompt|implementing)
      if ! is_truthy "$scope_approved"; then
        fail "phase=$phase requires gates.scope_approved=true"
      else
        ok "phase=$phase has approved scope"
      fi
      ;;
    review|fixing)
      if ! is_truthy "$implementation_finished"; then
        fail "phase=$phase requires gates.implementation_finished=true"
      else
        ok "phase=$phase has completed implementation"
      fi
      ;;
    QA)
      if ! is_clean_review_status "$review_gate"; then
        fail "phase=QA requires gates.review_gate=clean (found: $review_gate)"
      fi
      if ! is_clean_review_status "$triage_status"; then
        fail "phase=QA requires gates.triage_status=clean (found: $triage_status)"
      fi
      if is_clean_review_status "$review_gate" && is_clean_review_status "$triage_status"; then
        ok "phase=QA has clean review and triage gates"
      fi
      ;;
    commit-ready)
      if ! is_clean_review_status "$review_gate"; then
        fail "phase=commit-ready requires gates.review_gate=clean (found: $review_gate)"
      fi
      if ! is_clean_review_status "$triage_status"; then
        fail "phase=commit-ready requires gates.triage_status=clean (found: $triage_status)"
      fi
      if ! is_qa_complete_status "$supervisor_qa"; then
        fail "phase=commit-ready requires supervisor QA passed/skipped (found: $supervisor_qa)"
      fi
      ;;
    shipped)
      if ! is_truthy "$committed"; then
        fail "phase=shipped requires gates.committed=true"
      else
        ok "phase=shipped has committed=true"
      fi
      ;;
    cancelled)
      ok "phase=cancelled is terminal"
      ;;
    *)
      fail "unknown phase: $phase"
      ;;
  esac
}

check_shipped_commit_hash() {
  local phase status commit
  phase="$(jq_raw '.phase // ""')"
  status="$(jq_raw '.iteration.status // ""')"
  commit="$(jq_raw '.artifacts.commit // ""')"

  if [[ "$phase" != "shipped" && "$status" != "shipped" ]]; then
    ok "iteration is not shipped"
    return
  fi

  if [[ -z "$commit" || "$commit" == "null" || "$commit" == "pending" ]]; then
    fail "shipped iteration must record artifacts.commit"
    return
  fi

  if [[ "$commit" =~ ^[0-9a-fA-F]{7,40}$ ]]; then
    ok "shipped iteration records commit hash"
  else
    fail "shipped iteration commit does not look like a git hash: $commit"
  fi
}

check_unresolved_findings() {
  local ledger_path ledger_abs unresolved
  ledger_path="$(jq_raw '.iteration.ledger_path // ""')"
  ledger_abs="$ROOT/$ledger_path"

  if [[ ! -f "$ledger_abs" ]]; then
    return
  fi

  unresolved="$(
    awk -F'|' '
      BEGIN { found = 0 }
      /^\|[[:space:]]*R[0-9]+[[:space:]]*\|/ {
        severity = $3
        # Markdown table rows end with "|"; status is the last non-empty field
        # so finding text may contain "|" without shifting the status column.
        status = $(NF-1)
        if (status == "" && NF >= 2) {
          status = $(NF-2)
        }
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", severity)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", status)
        severity_l = tolower(severity)
        status_l = tolower(status)
        if ((severity_l == "high" || severity_l == "medium") &&
            status_l !~ /^(fixed|resolved|closed|clean)([[:space:]]|$|\()/) {
          print $0
          found = 1
        }
      }
      END { exit found ? 1 : 0 }
    ' "$ledger_abs"
  )"

  if [[ -n "$unresolved" ]]; then
    fail "ledger has unresolved High/Medium findings:"
    printf '%s\n' "$unresolved" >&2
  else
    ok "no unresolved High/Medium findings in ledger"
  fi
}

check_forbidden_paths() {
  local forbidden_regex staged changed
  forbidden_regex='(^|/)(dist|\.cache|\.venv|node_modules|recordings)(/|$)|^frontend/dist(/|$)|^native/build(/|$)|^ai-md-condidates(/|$)'

  staged="$(git -C "$ROOT" diff --cached --name-only 2>/dev/null | grep -E "$forbidden_regex" || true)"
  if [[ -n "$staged" ]]; then
    fail "forbidden paths are staged:"
    printf '%s\n' "$staged" >&2
  else
    ok "no forbidden paths staged"
  fi

  changed="$(
    git -C "$ROOT" status --short --untracked-files=all 2>/dev/null \
      | awk '{ $1=""; sub(/^ /, ""); print }' \
      | grep -E "$forbidden_regex" || true
  )"
  if [[ -n "$changed" ]]; then
    fail "forbidden paths are present in working tree changes:"
    printf '%s\n' "$changed" >&2
  else
    ok "no forbidden paths in working tree changes"
  fi
}

main() {
  require_jq
  if (( errors == 0 )); then
    check_state_json
  fi
  if (( errors == 0 )); then
    check_ledger_exists
    check_phase_gates
    check_commit_gate_order
    check_shipped_commit_hash
    check_unresolved_findings
    check_forbidden_paths
  fi

  if (( errors > 0 )); then
    printf '\nAI cycle validation failed with %d issue(s).\n' "$errors" >&2
    exit 1
  fi

  printf '\nAI cycle validation passed.\n'
}

main "$@"
