# Iteration Ledger

Status: mandatory operating record for the AI development system.

This document defines the durable memory each approved iteration must leave behind.

The ledger exists because chat is not a reliable source of truth. Future agents should be able to understand what happened, what was accepted, what was deferred, and what the next cycle should know without reconstructing the whole conversation.

---

# Purpose

The iteration ledger records:

- approved product scope;
- handoffs between AI roles;
- implementation summary;
- review findings;
- triage decisions;
- QA plan and outcome;
- human approvals;
- verification evidence;
- accepted or deferred debt;
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
```

If richer machine validation becomes important, add parallel structured iteration files later:

```text
.ai/state/iterations/YYYY-MM-DD-<short-slug>.json
```

---

# When To Create

Create the ledger entry immediately after the human approves an iteration scope and before implementation starts.

Update it at each phase transition:

1. scope approved;
2. implementation finished;
3. review completed;
4. triage completed;
5. QA plan generated;
6. human QA passed, failed, or was explicitly skipped;
7. commit prepared;
8. commit approved and created;
9. retrospective completed.

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
| Implementation prompt | feature-manager / cursor-implementation-prompt | <summary/link> | pending/done |
| Implementation | Cursor | <summary/link> | pending/done |
| Review | Codex | <summary/link> | pending/done |
| Triage | review-triage | <summary/link> | pending/done |
| Supervisor QA | supervisor-qa | <summary/link> | pending/done |
| Commit prep | commit-manager | <summary/link> | pending/done |
| Retrospective | iteration-retrospective | <summary/link> | pending/done |

## Implementation Summary

- Files changed:
- Behavior changed:
- Assumptions:
- Verification reported by implementer:

## Review Findings

| ID | Severity | File | Finding | Status |
| --- | --- | --- | --- | --- |
| R1 | High/Medium/Low | `path:line` | ... | open/fixed/accepted/deferred |

## Triage Decisions

- Blocking findings:
- Low findings fixed:
- Low findings accepted or deferred:
- Scope concerns:

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

| Item | Type | Reason accepted/deferred | Revisit condition |
| --- | --- | --- | --- |
| ... | product/engineering/process | ... | ... |

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
- review skipped;
- High or Medium findings left unresolved before commit;
- Low finding accepted without explicit human decision;
- supervisor QA skipped without explicit human decision;
- commit prepared without verification evidence;
- process debt discovered but not recorded;
- product scope changed without human approval.

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
