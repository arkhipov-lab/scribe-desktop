# Iteration Ledger

Status: mandatory operating record for the AI development system.

This document defines the durable memory each approved iteration must leave behind.

The ledger exists because chat is not a reliable source of truth. Future agents should be able to understand what happened, what was accepted, what was deferred, and what the next cycle should know without reconstructing the whole conversation.

---

# Purpose

The iteration ledger records:

- approved product scope;
- handoffs between AI roles;
- implementation phase states (prompt prepared, pending, summary received);
- implementation summary;
- review findings;
- triage decisions including auto-fix passes;
- QA plan and outcome;
- human approvals and **human involvement reason** when human input was required mid-loop;
- verification evidence;
- accepted or deferred debt;
- product follow-ups / wishes captured this iteration;
- metrics;
- retrospective notes;
- commit link.

The ledger is not bureaucracy. It is memory for the AI organization.

---

# Recommended Location

Use one file per approved iteration:

```text
docs/iterations/YYYY-MM-DD-<short-slug>.md
```

The active iteration must also be reflected in:

```text
.ai/state/current-cycle.json
.ai/state/debt.md
.ai/state/product-followups.md
```

`current-cycle.handoff` is the structured source for who acts next. Every phase transition in this ledger must be mirrored in `current-cycle.json` **including** an updated `handoff` (`next_role`, `reason`, `required_inputs`, `blocked_by`, `latest_artifacts`). Terminal states use `next_role=none`. Human checkpoints use `next_role=human-product-owner`.

If richer machine validation becomes important, add parallel structured iteration files later:

```text
.ai/state/iterations/YYYY-MM-DD-<short-slug>.json
```

Schema for the active cycle lives at `.ai/org/schemas/current-cycle.schema.json` and is enforced by `scripts/ai-cycle-validate.sh`.

---

# When To Create

Create the ledger entry immediately after the human approves an iteration scope and before implementation starts.

Update it at each phase transition:

1. scope approved;
2. implementation handoff prepared (prompt recorded; implementation pending);
3. implementation summary received (review ready);
4. review completed;
5. auto-fix pass generated / applied (when applicable);
6. triage completed;
7. QA plan generated;
8. human QA passed, failed, or was explicitly skipped;
9. commit prepared;
10. commit approved and created;
11. retrospective completed.

If an iteration is cancelled, record why and stop updating it.

Agents must read the active ledger at the start of each workflow step and update it at phase transitions. Chat history may explain a decision, but the ledger records it durably.

---

# Required Template

```markdown
# Iteration: <name>

**Status:** planned / implementing / review / fixing / QA / commit-ready / retrospective / shipped / cancelled
**Date started:** YYYY-MM-DD
**Date completed:** YYYY-MM-DD or pending
**Commit:** <hash or pending>

## Approved Scope

**Goal:**

**Hypothesis:**

**In scope:**
- ...

**Out of scope:**
- ...

**Human approval:**
- Source: <chat / explicit message / other>
- Date: YYYY-MM-DD

## Role Handoffs

| Phase | Role | Artifact | Status |
| --- | --- | --- | --- |
| Planning | roadmap-planner | <summary/link> | pending/done |
| Implementation prompt prepared | feature-manager (internal: cursor-implementation-prompt) | <summary/link> | pending/done |
| Implementation pending | Cursor | awaiting summary | pending/done |
| Implementation summary received | feature-manager records Cursor summary | <summary/link> | pending/done |
| Review ready → Review | Codex | <summary/link> | pending/done |
| Triage / auto-fix | review-triage | <summary/link> | pending/done |
| Supervisor QA | supervisor-qa | <summary/link> | pending/done |
| Commit prep | commit-manager | <summary/link> | pending/done |
| Retrospective | iteration-retrospective | <summary/link> | pending/done |

## Implementation Phase

Record explicitly so agents do not start review early:

| State | Status | Notes |
| --- | --- | --- |
| Implementation handoff prepared | pending/done | Prompt artifact created/recorded |
| Implementation pending | pending/done | Waiting for implementer summary |
| Implementation summary received | pending/done | Review may begin only after this |

## Implementation Summary

- Files changed:
- Behavior changed:
- Assumptions:
- Verification reported by implementer:
- Remaining work:
- Documentation updates:

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | High/Medium/Low | `path:line` | ... | open/fixed/accepted/deferred |

## Triage Decisions

- Review loop number:
- Blocking findings:
- Auto-fix pass generated:
- Auto-fix applied:
- Low findings auto-fixed:
- Low findings accepted or deferred (with/without human; reason):
- Human involvement required: yes/no
- Human involvement reason (if any):
- Scope concerns:
- Product wishes routed to follow-ups (not debt):

## Supervisor QA

**Plan:** <link or summary>

**Outcome:** passed / failed / skipped

**Human decision:**
- Date:
- Notes:

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `(cd frontend && npm run build)` | pass/fail/skipped | ... |
| `./scripts/run-dev.sh` | pass/fail/skipped | ... |
| Other | pass/fail/skipped | ... |

## Debt

Accepted or deferred review/QA/process debt only. Product wishes go under Product Follow-ups / Wishes and in `.ai/state/product-followups.md`.

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| ... | engineering/process | ... | ... |

## Product Follow-ups / Wishes

Local capture for this iteration. Curated source of truth: `.ai/state/product-followups.md`.

| ID | Title | Source phase | Notes |
| --- | --- | --- | --- |
| ... | ... | Supervisor QA / Planning / Retrospective | Link or short note; do not treat as review debt |

## Metrics

Separate observed facts from estimates.

| Metric | Value | Source |
| --- | --- | --- |
| Elapsed time | ... | observed/estimated |
| Agent turns | ... | observed/estimated |
| Approx token use | ... | observed/estimated |
| Review loops | ... | observed |
| High findings | ... | observed |
| Medium findings | ... | observed |
| Low findings | ... | observed |
| Human decisions | ... | observed |
| QA outcome | ... | observed |
| Outcome | ... | observed |

Preferred expanded form when evidence matters:

| Metric | Value | Source type | Evidence |
| --- | --- | --- | --- |
| Elapsed time | ... | observed/estimated | ... |
| Agent turns | ... | observed/estimated | ... |
| Approx token use | ... | estimated | ... |
| Review loops | ... | observed | ... |
| High findings | ... | observed | ... |
| Medium findings | ... | observed | ... |
| Low findings | ... | observed | ... |
| Human decisions | ... | observed | ... |
| QA outcome | ... | observed | ... |
| Outcome | ... | observed | ... |

## Retrospective

**What worked:**

**What caused rework:**

**Repeated failure patterns:**

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| ... | ... | yes/no/unknown | none/docs/skill/gate/test |

**Process change recommended:**

**Next planning input:**
```

---

# Gate Rules

The ledger should make these violations obvious:

- implementation started without approved scope;
- review started while implementation was still pending (no summary received);
- review skipped;
- High or Medium findings left unresolved before commit;
- Low finding left open without AI fix or policy accept/defer;
- supervisor QA skipped without explicit human decision;
- commit prepared without verification evidence;
- process debt discovered but not recorded;
- product follow-ups from QA/planning lost in chat or filed as debt;
- product scope changed without human approval;
- human asked to approve routine auto-fixable findings without a product/scope reason.

Notes on Low findings:

- First-loop cheap Lows should be auto-fixed; no human ask required.
- Second+ loop minor Lows may be accepted/deferred as debt **without** human involvement when policy allows; record reason and revisit condition.
- Product-facing Lows still need Product Owner judgment.

---

# Metrics Guidance

Metrics are useful only when their meaning is honest.

Use:

- **observed** for facts from commands, timestamps, git history, review outputs, or explicit human decisions;
- **estimated** for token counts, inferred human effort, or partial timing.

Do not hide uncertainty. A rough estimate is useful when labelled as an estimate.

The retrospective should compare at least the active ledger and the most recent relevant ledgers before calling something a repeated failure.

---

# Relationship To Existing Workflow

The ledger complements:

- [AI Product Development Cycle](./ai-product-development-cycle.md);
- [Feature Development Pipeline](./feature-development-pipeline.md);
- [AI Development System Convention](../../AI_CONVENTION.md);
- [AI Development System Roadmap](../../AI_SYSTEM_ROADMAP.md).

The workflow describes what should happen.
The ledger records what actually happened.
