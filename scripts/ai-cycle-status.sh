#!/usr/bin/env bash
# Print the active AI development cycle state, then run the validator.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="${AI_CYCLE_STATE:-$ROOT/.ai/state/current-cycle.json}"
FINDINGS_FILE="${AI_CYCLE_FINDINGS:-$ROOT/.ai/state/review-findings.json}"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for AI cycle status" >&2
  exit 1
fi

if [[ ! -f "$STATE_FILE" ]]; then
  echo "AI cycle state missing: $STATE_FILE" >&2
  exit 1
fi

jq -r '
  "AI Cycle Status",
  "===============",
  "Iteration: " + (.iteration.id // "unknown") + " — " + (.iteration.name // "unknown"),
  "Phase: " + (.phase // "unknown"),
  "Status: " + (.iteration.status // "unknown"),
  "Ledger: " + (.iteration.ledger_path // "missing"),
  "Review gate: " + (.gates.review_gate // "unknown"),
  "Triage: " + (.gates.triage_status // "unknown"),
  "Supervisor QA: " + (.gates.supervisor_qa // "unknown"),
  "Commit allowed: " + ((.gates.commit_allowed // false) | tostring),
  "Next role: " + (.handoff.next_role // "unknown"),
  "Handoff reason: " + (.handoff.reason // "unknown"),
  "Metrics findings (H/M/L): " +
    ((.metrics.high_findings // "null") | tostring) + "/" +
    ((.metrics.medium_findings // "null") | tostring) + "/" +
    ((.metrics.low_findings // "null") | tostring),
  "Commit: " + (.artifacts.commit // "pending"),
  "Last updated: " + (.last_updated // "unknown")
' "$STATE_FILE"

if [[ -f "$FINDINGS_FILE" ]]; then
  echo
  jq -r '
    "Structured review findings",
    "--------------------------",
    "Findings file iteration: " + (.iteration_id // "unknown"),
    "Finding counts (H/M/L): " +
      (([.findings[] | select(.severity == "High")] | length) | tostring) + "/" +
      (([.findings[] | select(.severity == "Medium")] | length) | tostring) + "/" +
      (([.findings[] | select(.severity == "Low")] | length) | tostring),
    "Open findings: " +
      (([.findings[] | select(.status == "open")] | length) | tostring),
    "Last updated: " + (.last_updated // "unknown")
  ' "$FINDINGS_FILE"
else
  echo
  echo "Structured review findings: missing ($FINDINGS_FILE)"
fi

echo
"$ROOT/scripts/ai-cycle-validate.sh"
