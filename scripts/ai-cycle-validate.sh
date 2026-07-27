#!/usr/bin/env bash
# Validate the AI development cycle state before phase transitions or commit prep.
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="${AI_CYCLE_STATE:-$ROOT/.ai/state/current-cycle.json}"
SCHEMA_FILE="${AI_CYCLE_SCHEMA:-$ROOT/.ai/org/schemas/current-cycle.schema.json}"
SCHEMA_CHECK="$ROOT/scripts/ai-cycle-schema-check.py"

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

looks_like_commit_hash() {
  [[ "$1" =~ ^[0-9a-fA-F]{7,40}$ ]]
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

check_schema() {
  if [[ ! -f "$SCHEMA_FILE" ]]; then
    fail "schema file missing: $SCHEMA_FILE"
    return
  fi
  if [[ ! -f "$SCHEMA_CHECK" ]]; then
    fail "schema checker missing: $SCHEMA_CHECK"
    return
  fi

  local output
  if output="$(python3 "$SCHEMA_CHECK" "$STATE_FILE" "$SCHEMA_FILE" 2>&1)"; then
    ok "current-cycle.json matches schema"
  else
    printf '%s\n' "$output" >&2
    fail "current-cycle.json failed schema validation"
  fi
}

artifact_present() {
  local value="$1"
  [[ -n "$value" && "$value" != "null" ]]
}

review_or_triage_progressed() {
  local review_gate="$1"
  local triage_status="$2"
  # pending_re_review is not progressed — re-review still requires codex-review.
  case "$review_gate" in
    clean|dirty|blocked|skipped) return 0 ;;
  esac
  case "$triage_status" in
    fix_required|fix_applied|clean|blocked|skipped) return 0 ;;
  esac
  return 1
}

check_handoff_consistency() {
  local phase next_role review_gate triage_status supervisor_qa committed commit
  local impl_summary errors_before=$errors
  phase="$(jq_raw '.phase // ""')"
  next_role="$(jq_raw '.handoff.next_role // ""')"
  review_gate="$(jq_raw '.gates.review_gate // ""')"
  triage_status="$(jq_raw '.gates.triage_status // ""')"
  supervisor_qa="$(jq_raw '.gates.supervisor_qa // ""')"
  committed="$(jq_raw '.gates.committed // false')"
  commit="$(jq_raw '.artifacts.commit // ""')"
  impl_summary="$(jq_raw '.artifacts.latest_implementation_summary // ""')"

  if [[ -z "$next_role" || "$next_role" == "null" ]]; then
    fail "handoff.next_role is missing"
    return
  fi

  case "$phase" in
    shipped|cancelled|rejected)
      if [[ "$next_role" != "none" ]]; then
        fail "phase=$phase requires handoff.next_role=none (found: $next_role)"
      fi
      ;;
    *)
      if [[ "$next_role" == "none" ]]; then
        fail "phase=$phase is non-terminal and cannot use handoff.next_role=none"
      fi
      ;;
  esac

  case "$phase" in
    review)
      if [[ "$review_gate" == "pending_re_review" ]]; then
        if [[ "$next_role" != "codex-review" ]]; then
          fail "phase=review with review_gate=pending_re_review requires handoff.next_role=codex-review (found: $next_role)"
        fi
      elif ! review_or_triage_progressed "$review_gate" "$triage_status"; then
        if [[ "$next_role" != "codex-review" && "$next_role" != "review-triage" ]]; then
          fail "phase=review with pending review/triage requires handoff.next_role=codex-review or review-triage (found: $next_role)"
        fi
      fi
      ;;
    QA)
      if ! is_clean_review_status "$review_gate"; then
        fail "phase=QA requires gates.review_gate=clean (found: $review_gate)"
      fi
      if ! is_clean_review_status "$triage_status"; then
        fail "phase=QA requires gates.triage_status=clean (found: $triage_status)"
      fi
      if [[ "$next_role" != "supervisor-qa" && "$next_role" != "human-product-owner" ]]; then
        fail "phase=QA requires handoff.next_role=supervisor-qa or human-product-owner (found: $next_role)"
      fi
      ;;
    commit-ready)
      if ! is_qa_complete_status "$supervisor_qa"; then
        fail "phase=commit-ready requires supervisor QA passed/skipped (found: $supervisor_qa)"
      fi
      if [[ "$next_role" != "commit-manager" && "$next_role" != "human-product-owner" ]]; then
        fail "phase=commit-ready requires handoff.next_role=commit-manager or human-product-owner (found: $next_role)"
      fi
      ;;
    retrospective)
      if ! is_truthy "$committed"; then
        fail "phase=retrospective requires gates.committed=true"
      fi
      if [[ -z "$commit" || "$commit" == "null" || "$commit" == "pending" ]]; then
        fail "phase=retrospective requires artifacts.commit"
      elif ! looks_like_commit_hash "$commit"; then
        fail "phase=retrospective commit does not look like a git hash: $commit"
      fi
      if [[ "$next_role" != "iteration-retrospective" ]]; then
        fail "phase=retrospective requires handoff.next_role=iteration-retrospective (found: $next_role)"
      fi
      ;;
  esac

  if is_clean_review_status "$review_gate"; then
    if ! artifact_present "$impl_summary"; then
      fail "gates.review_gate=clean requires artifacts.latest_implementation_summary"
    fi
  fi

  if (( errors == errors_before )); then
    ok "handoff consistency checks passed"
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

check_registers_exist() {
  local debt_path followups_path debt_abs followups_abs
  debt_path="$(jq_raw '.artifacts.debt_register // ".ai/state/debt.md"')"
  followups_path="$(jq_raw '.artifacts.product_followups_register // ".ai/state/product-followups.md"')"

  if [[ -z "$debt_path" || "$debt_path" == "null" ]]; then
    debt_path=".ai/state/debt.md"
  fi
  if [[ -z "$followups_path" || "$followups_path" == "null" ]]; then
    followups_path=".ai/state/product-followups.md"
  fi

  debt_abs="$ROOT/$debt_path"
  followups_abs="$ROOT/$followups_path"

  if [[ -f "$debt_abs" ]]; then
    ok "debt register exists: $debt_path"
  else
    fail "debt register missing: $debt_path"
  fi

  if [[ -f "$followups_abs" ]]; then
    ok "product follow-ups register exists: $followups_path"
  else
    fail "product follow-ups register missing: $followups_path"
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
    retrospective)
      local commit errors_before=$errors
      commit="$(jq_raw '.artifacts.commit // ""')"
      if ! is_truthy "$implementation_finished"; then
        fail "phase=retrospective requires gates.implementation_finished=true"
      fi
      if ! is_clean_review_status "$review_gate"; then
        fail "phase=retrospective requires gates.review_gate=clean (found: $review_gate)"
      fi
      if ! is_clean_review_status "$triage_status"; then
        fail "phase=retrospective requires gates.triage_status=clean (found: $triage_status)"
      fi
      if ! is_qa_complete_status "$supervisor_qa"; then
        fail "phase=retrospective requires supervisor QA passed/skipped (found: $supervisor_qa)"
      fi
      if ! is_truthy "$committed"; then
        fail "phase=retrospective requires gates.committed=true"
      fi
      if [[ -z "$commit" || "$commit" == "null" || "$commit" == "pending" ]]; then
        fail "phase=retrospective requires artifacts.commit"
      elif ! looks_like_commit_hash "$commit"; then
        fail "phase=retrospective commit does not look like a git hash: $commit"
      fi
      if (( errors == errors_before )); then
        ok "phase=retrospective has clean gates, committed=true, and commit hash"
      fi
      ;;
    shipped)
      if ! is_truthy "$committed"; then
        fail "phase=shipped requires gates.committed=true"
      else
        ok "phase=shipped has committed=true"
      fi
      ;;
    cancelled|rejected)
      ok "phase=$phase is terminal"
      ;;
    *)
      fail "unknown phase: $phase"
      ;;
  esac
}

check_committed_phase() {
  local phase committed commit errors_before=$errors
  phase="$(jq_raw '.phase // ""')"
  committed="$(jq_raw '.gates.committed // false')"
  commit="$(jq_raw '.artifacts.commit // ""')"

  if ! is_truthy "$committed"; then
    ok "commit not yet recorded"
    return
  fi

  if [[ "$phase" != "retrospective" && "$phase" != "shipped" ]]; then
    fail "gates.committed=true requires phase=retrospective or shipped (found: $phase)"
  fi
  if [[ -z "$commit" || "$commit" == "null" || "$commit" == "pending" ]]; then
    fail "gates.committed=true requires artifacts.commit"
  elif ! looks_like_commit_hash "$commit"; then
    fail "gates.committed=true commit does not look like a git hash: $commit"
  fi

  if (( errors == errors_before )); then
    ok "committed=true is paired with phase=$phase and commit hash"
  fi
}

check_shipped_consistency() {
  local phase status commit committed errors_before
  local phase_shipped=false status_shipped=false any_shipped_marker=false
  errors_before=$errors
  phase="$(jq_raw '.phase // ""')"
  status="$(jq_raw '.iteration.status // ""')"
  commit="$(jq_raw '.artifacts.commit // ""')"
  committed="$(jq_raw '.gates.committed // false')"

  [[ "$phase" == "shipped" ]] && phase_shipped=true
  [[ "$status" == "shipped" ]] && status_shipped=true
  # committed=true alone is not a shipped marker — post-commit retrospective uses it first.
  if [[ "$phase_shipped" == true || "$status_shipped" == true ]]; then
    any_shipped_marker=true
  fi

  if [[ "$any_shipped_marker" != true ]]; then
    ok "iteration is not shipped"
    return
  fi

  # Any shipped marker requires phase, status, and committed to agree.
  if [[ "$phase_shipped" != true ]]; then
    fail "shipped markers disagree: phase=$phase (expected shipped) with status=$status gates.committed=$committed"
  fi
  if [[ "$status_shipped" != true ]]; then
    fail "shipped markers disagree: iteration.status=$status (expected shipped) with phase=$phase gates.committed=$committed"
  fi
  if ! is_truthy "$committed"; then
    fail "shipped markers disagree: gates.committed=$committed (expected true) with phase=$phase iteration.status=$status"
  fi

  if [[ -z "$commit" || "$commit" == "null" || "$commit" == "pending" ]]; then
    fail "shipped iteration must record artifacts.commit"
  elif ! looks_like_commit_hash "$commit"; then
    fail "shipped iteration commit does not look like a git hash: $commit"
  fi

  if (( errors == errors_before )); then
    ok "shipped markers are consistent (phase, status, committed, commit hash)"
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
    check_schema
  fi
  if (( errors == 0 )); then
    check_ledger_exists
    check_registers_exist
    check_phase_gates
    check_handoff_consistency
    check_commit_gate_order
    check_committed_phase
    check_shipped_consistency
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
