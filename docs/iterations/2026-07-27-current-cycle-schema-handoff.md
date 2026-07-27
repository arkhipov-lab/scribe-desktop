# Iteration: Current-Cycle Schema And Structured Handoff

**Status:** shipped
**Date started:** 2026-07-27
**Date completed:** 2026-07-28
**Commit:** `27e36d1150d827d54cdecbbe724074fc3e1a64cb`

## Approved Scope

**Goal:** Add a minimal structured schema for `.ai/state/current-cycle.json` and a structured `handoff` section so the AI Native SDLC can enforce the next-role contract more reliably.

**Hypothesis:** If agents and the validator share a machine-checked current-cycle shape plus an explicit `handoff.next_role`, invalid phase/gate transitions and missing implementation summaries become detectable before QA/commit.

**In scope:**
- Create `.ai/org/schemas/current-cycle.schema.json`
- Add required `handoff` object (`next_role`, `reason`, `required_inputs`, `blocked_by`, `latest_artifacts`)
- Make `scripts/ai-cycle-validate.sh` schema-aware via stdlib Python helper (no new package deps)
- Add handoff consistency checks (review / QA / commit-ready / retrospective / terminal)
- Require `artifacts.latest_implementation_summary` when `review_gate=clean`
- Update workflow/skill docs that need the handoff contract
- Iteration ledger + current-cycle set to `phase=review` for independent review

**Out of scope:**
- `review-findings.schema.json`, `metrics.schema.json`, `retrospective.schema.json`, `product-analysis.schema.json`
- Structured review findings sidecar
- Full JSON Schema dependency / CI integration
- process-auditor skill, Product Owner console, project onboarding modes
- Actual automated Cursor execution
- Scribe product behavior changes

**Human approval:**
- Source: chat — implementation task “Current-Cycle Schema And Structured Handoff”
- Date: 2026-07-27

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | feature-manager / implementation task | approved scope in this ledger | done |
| Implementation prompt prepared | feature-manager | task prompt in chat | done |
| Implementation pending | Cursor / implementation agent | awaiting summary | done |
| Implementation summary received | feature-manager records summary | this ledger Implementation Summary | done |
| Review ready → Review | Codex | loop 1: 0 High, 1 Medium, 2 Low | done |
| Triage / auto-fix | review-triage | R1–R3 auto-fix applied 2026-07-27; pending re-review | done |
| Fix pass | implementation-agent | R1 pending_re_review handoff; R2 $ref FAIL; R3 blank line | done |
| Re-review | Codex | loop 2 clean — R1–R3 verified fixed; 0 new findings | done |
| Triage / auto-fix (loop 2) | review-triage | review gate clean; route to supervisor-qa | done |
| Supervisor QA | supervisor-qa | plan generated 2026-07-28; human passed 2026-07-28 | done |
| Commit prep | commit-manager | commit `27e36d1` created 2026-07-28 | done |
| Retrospective | iteration-retrospective | completed 2026-07-28; P-009 done; P-002 narrowed | done |

## Implementation Phase

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | done | Task prompt recorded |
| Implementation pending | done | Summary received |
| Implementation summary received | done | Review may begin |

## Implementation Summary

- Files changed:
  - `.ai/org/schemas/current-cycle.schema.json` (new)
  - `scripts/ai-cycle-schema-check.py` (new stdlib subset validator)
  - `scripts/ai-cycle-validate.sh` (schema + handoff consistency)
  - `.ai/state/current-cycle.json` (new iteration + `handoff`)
  - `.ai/org/schemas.md`, `.ai/org/workflows.md`
  - `.ai/skills/feature-manager.md`, `codex-review.md`, `review-triage.md`, `supervisor-qa.md`, `commit-manager.md`, `iteration-retrospective.md`
  - `docs/workflows/iteration-ledger.md`, `feature-development-pipeline.md`, `README.md`
  - `docs/iterations/2026-07-27-current-cycle-schema-handoff.md`
- Behavior changed:
  - Validator loads schema and fails on missing required fields / invalid enums.
  - `current-cycle.handoff` is required and is the structured source for who acts next.
  - Phase-specific handoff rules enforce next_role for review/QA/commit-ready/retrospective/terminal states.
  - `review_gate=clean` requires a non-null `artifacts.latest_implementation_summary`.
  - Metrics may be `null` until evidence exists (no fake zeroes).
- Assumptions:
  - Lightweight schema subset is enough; no `jsonschema` package.
  - Feature-manager remains the normal post-approval orchestrator; `cursor-implementation-prompt` stays internal.
  - Terminal phases are `shipped`, `cancelled`, `rejected` and must use `handoff.next_role=none`.
- Verification reported by implementer:
  - Active: `scripts/ai-cycle-status.sh` + `scripts/ai-cycle-validate.sh` → pass (`phase=review`, `handoff.next_role=codex-review`)
  - Synthetic negatives via `AI_CYCLE_STATE` → all fail as expected:
    - invalid phase
    - missing required `handoff`
    - terminal `shipped` + `next_role=codex-review`
    - non-terminal `review` + `next_role=none`
    - `retrospective` without commit hash
    - `review_gate=clean` with `latest_implementation_summary=null`
  - Synthetic positive: valid `shipped` + `next_role=none` + commit hash → pass
  - `git diff --check` → pass
- Remaining work:
  - Independent Codex review → triage → supervisor QA → commit (human approval) → retrospective
- Documentation updates:
  - Schema/workflow/skill docs describe handoff updates at phase transitions

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | Medium | `scripts/ai-cycle-validate.sh:85-95` | `review_gate=pending_re_review` treated as progressed, so `phase=review` next-role constraint is skipped; `next_role=commit-manager` can pass during re-review | fixed |
| R2 | Low | `scripts/ai-cycle-schema-check.py:21-34` | Unresolved `$ref` raises traceback instead of clean schema FAIL | fixed |
| R3 | Low | `docs/workflows/iteration-ledger.md:58-59` | Missing blank line before `---` after schema sentence | fixed |

## Triage Decisions

- Review loop: 2 (re-review clean)
- Loop 1: R1 Medium + R2/R3 Low auto-fixed; no human involvement.
- Loop 2: 0 High, 0 Medium, 0 Low new; R1–R3 verified fixed.
- Blocking open findings: none.
- Scope: matches process-only slice; no Scribe product files; no unrelated ROADMAP leakage.
- Human involvement: none required for triage.
- Resolution (2026-07-28): review gate clean; triage clean; route to `Use supervisor-qa.`

## Supervisor QA

**Plan:** generated 2026-07-28 (see below).
**Outcome:** passed 2026-07-28 by human Product Owner; no new product follow-ups.

# Supervisor QA — Current-Cycle Schema And Structured Handoff

## Goal

Confirm that the AI development cycle now has a machine-checked `current-cycle` shape plus a structured `handoff` (who acts next), that invalid handoff/phase combinations fail validation, and that **Scribe the product app is unchanged** by this process-only slice.

## Environment

- No Scribe app launch required (docs/process-only slice).
- Work from the repo root.
- Useful commands: `scripts/ai-cycle-status.sh`, `scripts/ai-cycle-validate.sh`, `git diff --check`, `git status --short`.

## Test data

- Active ledger: `docs/iterations/2026-07-27-current-cycle-schema-handoff.md`
- Current cycle: `.ai/state/current-cycle.json`
- Schema: `.ai/org/schemas/current-cycle.schema.json`
- Scripts: `scripts/ai-cycle-validate.sh`, `scripts/ai-cycle-schema-check.py`

## Happy path

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open Approved Scope in the active ledger | Goal is schema + structured handoff for current-cycle; Scribe product behavior is out of scope. |
| 2 | Open Implementation Summary + Review/Triage | Schema/validator/docs landed; loop 2 clean; R1–R3 fixed; no open High/Medium. |
| 3 | Open `.ai/state/current-cycle.json` | Has required `handoff` (`next_role`, `reason`, `required_inputs`, `blocked_by`, `latest_artifacts`); phase/gates show QA-ready / clean review. |
| 4 | Confirm schema file exists | `.ai/org/schemas/current-cycle.schema.json` is present. |
| 5 | Run `bash scripts/ai-cycle-status.sh` | Shows this iteration; **Next role** reflects handoff; validation passes. |
| 6 | Run `bash scripts/ai-cycle-validate.sh` | Passes for the active state. |
| 7 | Spot-check a skill/workflow doc (e.g. feature-manager or pipeline) | Mentions updating `handoff` on phase transitions; terminal `next_role=none`; human checkpoints use `human-product-owner`. |

## Edge cases

| Case | Action | Expected result |
|------|--------|-----------------|
| Bad handoff on re-review | Mentally confirm / optionally ask agent to re-show: `phase=review` + `review_gate=pending_re_review` + `next_role=commit-manager` | Validator must **fail**. |
| Clean review without summary | Mentally confirm: `review_gate=clean` with missing `latest_implementation_summary` | Validator must **fail**. |
| Terminal shipped role | Mentally confirm: `phase=shipped` with `next_role` other than `none` | Validator must **fail**. |
| Product isolation | `git status --short` / changed paths | No required Scribe product changes under `frontend/`, `backend/`, or `native/` for this slice. |

## Regression checks

| Area | Action | Expected result |
|------|--------|-----------------|
| Prior cycle memory | Debt + product-followups registers still exist | Registers present; product wishes still separate from debt. |
| Forbidden paths | Working tree | No `dist/`, `.venv`, `node_modules`, etc. staged/changed for this work. |
| Whitespace | `git diff --check` | Passes. |

## Out of scope

- Other role schemas (review-findings, metrics, retrospective, product-analysis)
- CI integration / full JSON Schema package dependency
- Process-auditor skill, Product Owner console, automated Cursor execution
- Any Scribe transcription/summary/recording behavior

## Pass criteria

- [ ] Scope matches the process-only schema/handoff slice
- [ ] Active cycle validate + status pass
- [ ] `handoff` is present and status shows next role
- [ ] Review/triage clean with R1–R3 fixed
- [ ] No unintended Scribe product file changes required for the slice
- [ ] `git diff --check` pass (or equivalent cleanliness)

## Fail criteria

- Active validator fails on the real cycle state
- `handoff` missing or docs still treat chat as the only next-role source
- Open High/Medium findings remain
- Slice silently changed Scribe product behavior / shipped unrelated ROADMAP work

## Notes

- Accepted/fixed Lows: R2 (schema `$ref` error reporting), R3 (markdown blank line) — both fixed; do not re-litigate.
- Fixed Medium: R1 (`pending_re_review` must hand off to `codex-review`).
- Product wishes heard during QA (if any) — capture after pass in `.ai/state/product-followups.md`; do not treat as fail criteria.
- Suggested order: scope → status/validate → isolation spot-check → edge-case confirmations.

## Commit Preparation

**Prepared:** 2026-07-28
**Commit:** `27e36d1150d827d54cdecbbe724074fc3e1a64cb` created 2026-07-28 after explicit human approval.

Suggested message (used):

```
feat(ai-process): add current-cycle schema and structured handoff

Make cycle state machine-checkable and encode who acts next so invalid
phase/gate/handoff transitions fail before QA or commit.
```

Files: schema, stdlib schema checker, validator handoff checks, current-cycle + ledger, workflow/skill docs.

### Changed files (summary)

| File | Purpose |
|------|---------|
| `.ai/org/schemas/current-cycle.schema.json` | Minimal current-cycle + handoff schema |
| `scripts/ai-cycle-schema-check.py` | Stdlib subset schema validator |
| `scripts/ai-cycle-validate.sh` | Schema + handoff consistency checks |
| `scripts/ai-cycle-status.sh` | Show next role / handoff reason |
| `.ai/state/current-cycle.json` | Active iteration + handoff |
| `docs/iterations/2026-07-27-current-cycle-schema-handoff.md` | Iteration ledger |
| `.ai/org/schemas.md`, `.ai/org/workflows.md` | Schema/handoff contract |
| Skills + `docs/workflows/*` | Handoff updates at phase transitions |

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| review_loops | 2 | observed | Loop 1 findings + auto-fix; loop 2 re-review clean |
| human_decisions | 2 | observed | Supervisor QA pass + commit approval (no review-loop asks) |
| high_findings | 0 | observed | Review records |
| medium_findings | 1 | observed | R1 (fixed loop 1) |
| low_findings | 2 | observed | R2, R3 (fixed loop 1) |
| qa_outcome | passed | observed | Human Product Owner 2026-07-28 |
| outcome | shipped | observed | Commit `27e36d1` + retrospective complete |

## Debt / Follow-ups

- Advances planned process work: current-cycle schema is the first schema consumer (P-002 narrowed); P-009 marked done.
- Deferred: other role output schemas, CI wiring, findings sidecar, P-004 implementation-runner.

## Retrospective

# Iteration Retrospective — Current-Cycle Schema And Structured Handoff

## Outcome

- **Status:** shipped
- **Commit:** `27e36d1150d827d54cdecbbe724074fc3e1a64cb`
- **QA:** passed

## Metrics

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | ~1 calendar day (same evening stretch) | estimated | `date_started` 2026-07-27 → completed 2026-07-28; commit `27e36d1` at 2026-07-28 00:25 +0200 |
| Agent turns | ~11 user skill/step turns | estimated | implement → review → triage → fix → re-review → triage → QA → pass → commit-manager → commit → retrospective |
| Approx token use | not measured | estimated | no tooling report |
| Review loops | 2 | observed | ledger review/triage |
| High findings | 0 | observed | ledger |
| Medium findings | 1 | observed | R1 fixed |
| Low findings | 2 | observed | R2–R3 fixed |
| Human decisions | 2 | observed | QA pass + commit approval |
| QA outcome | passed | observed | ledger |
| Outcome | shipped | observed | commit + this retrospective |

## Rework Analysis

- **What caused rework:** Loop 1 Medium R1 — `pending_re_review` incorrectly treated as a progressed handoff escape, allowing illegal `next_role` during re-review.
- **What avoided rework:** Explicit synthetic negatives in the implementation summary; auto-fix of R1–R3 without human interrupts; process-only scope kept product surface untouched.
- **Human routine effort:** Only mandatory gates (QA + commit). Zero review-loop involvement — continues the auto-fix improvement seen in `editable-transcript` / `pipeline-operator-ux`.

## Repeated Failure Analysis

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| Asking human about routine Lows | R2/R3 auto-fixed; no ask | no (improved) | none; keep auto-fix |
| Incomplete gate escape hatch | R1 `pending_re_review` bypass | unknown (first schema/handoff slice) | gate/test — fixed this cycle; keep synthetic regression |
| Validator half-state gaps | Prior shipped-consistency + this handoff slice | yes (process hardening theme) | continue targeted validator slices only when a concrete illegal state appears |

## Process Recommendations

1. Treat structured schemas as demand-driven: keep P-002 open for other role outputs, but do not add schemas without a validator/consumer (current-cycle is enough for now).
2. When choosing process next, prefer P-004 (implementation-runner / handoff skill) — schema/handoff foundation is now in place for that work.

## Debt / Planned Work Updates

- **Debt register:** no new Open Debt
- **Planned process work:** P-009 → done; P-002 notes updated (current-cycle schema shipped; other role schemas still planned)
- **Product follow-ups captured:** yes/no — none this iteration

## Next Planning Input

Use `product-analyst` (then roadmap-planner). Compare next Scribe product candidates (e.g. editable summary approach for `PP-2026-07-27-003`, parked language auto-detect `PP-2026-07-27-002`) against process `P-2026-07-27-004` (implementation-runner). Prefer product if a bounded user-facing slice is clear; otherwise P-004 is the strongest process follow-on now that current-cycle schema/handoff exists.

## State Updates

- Ledger: retrospective filled; status shipped; metrics finalized
- Current cycle: `phase=shipped`, `handoff.next_role=none`
- Debt register: P-009 done; P-002 narrowed

## Product Follow-ups

(none this iteration)
