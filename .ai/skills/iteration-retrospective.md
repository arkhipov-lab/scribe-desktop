# Iteration Retrospective

## Purpose

Analyze a post-commit iteration (or an explicitly cancelled/rejected terminal iteration) using durable evidence. Produce metrics, repeated-failure analysis, and at most one or two evidence-backed process improvements. This role evaluates the process, not product direction and not code correctness.

---

## Invocation

```
Use iteration-retrospective.
```

---

## Automatic Context Loading

| Source | Purpose |
| --- | --- |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Scope, handoffs, findings, QA, verification, metrics |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration, phase, gate state, metrics |
| [`.ai/state/debt.md`](../state/debt.md) | Accepted/deferred debt and planned process work |
| [`.ai/state/product-followups.md`](../state/product-followups.md) | Whether QA/planning wishes were captured (not debt) |
| [`.ai/org/`](../org/) | Reusable roles, workflow, metrics, and schema targets |
| [`.ai/product/`](../product/) | Product-specific context to distinguish product vs process lessons |
| [`.ai/repo/`](../repo/) | Repo-specific validation and forbidden-path context |
| Recent ledgers in [docs/iterations/](../../docs/iterations/) | Repeated failure pattern comparison |
| Latest review / triage / QA / commit summary | Evidence for rework and outcomes |
| [docs/workflows/iteration-ledger.md](../../docs/workflows/iteration-ledger.md) | Metrics and ledger contract |
| [docs/workflows/ai-product-development-cycle.md](../../docs/workflows/ai-product-development-cycle.md) | Product/process cycle context |
| [AI_CONVENTION.md](../../AI_CONVENTION.md) | AI development system goals |
| [AI_SYSTEM_ROADMAP.md](../../AI_SYSTEM_ROADMAP.md) | Process roadmap context |

Run `scripts/ai-cycle-status.sh` first when resuming an existing cycle. Run `scripts/ai-cycle-validate.sh` before finalizing retrospective state updates.

---

## Preconditions

- Active ledger and `.ai/state/current-cycle.json` exist
- Implementation summary exists
- Review and triage have completed, **or** the iteration was explicitly cancelled / rejected
- Final retrospective requires a recorded commit hash in the ledger and `current-cycle` **or** an explicit cancelled/rejected terminal state (no commit)
- Supervisor QA outcome is passed, failed, or skipped (for shipped paths); cancelled/rejected paths record why QA did not complete
- Metrics have enough evidence to distinguish observed facts from estimates

Do not run a final retrospective before commit unless the iteration is explicitly cancelled or rejected. If evidence is missing, record the gap as a finding in the retrospective instead of inventing certainty.

---

## Responsibilities

- Fill or correct the ledger Metrics section
- Separate **observed** metrics from **estimated** metrics
- Analyze what created rework, delay, or human routine effort
- Compare recent ledgers for repeated failures, not one-off annoyances
- Identify weak prompts, missing context, weak gates, or missing docs/tests
- Recommend at most two process improvements, only when evidence supports them
- Record process debt or planned process work in `.ai/state/debt.md` when appropriate
- Record whether product follow-ups from QA/planning were captured in `.ai/state/product-followups.md` (and the ledger follow-ups section); do not file product wishes as debt
- Update the active ledger Retrospective section and current-cycle state
- After a successful post-commit retrospective, set `phase=shipped`, `iteration.status=shipped`, and `gates.retrospective` complete (keep `committed=true` and the commit hash); set `handoff.next_role=none` (terminal). Next-cycle planning starts from a fresh or reset current-cycle record, not by leaving a non-`none` role on a shipped iteration.

---

## Non-responsibilities

- Does not approve product direction
- Does not review code correctness
- Does not prepare or create commits
- Does not add process ceremony without evidence
- Does not silently edit PRODUCT, ROADMAP, DECISIONS, or major process docs without human approval

---

## Metrics Rules

Use **observed** when the value comes from git history, commands, ledger entries, review outputs, QA outcomes, or explicit human decisions.

Use **estimated** for approximate token use, inferred human effort, partial elapsed time, or any value reconstructed from incomplete evidence.

Never mix the source label into the value. Keep value, source type, and evidence separate.

---

## Output Contract

```markdown
# Iteration Retrospective — <iteration name>

## Outcome

- **Status:** shipped / rejected / cancelled / pending
- **Commit:** <hash / pending / n/a>
- **QA:** passed / failed / skipped / pending

## Metrics

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

## Rework Analysis

- **What caused rework:**
- **What avoided rework:**
- **Human routine effort:**

## Repeated Failure Analysis

| Pattern | Evidence | Repeated? | Recommended response |
| --- | --- | --- | --- |
| ... | ... | yes/no/unknown | none / docs / skill / gate / test |

## Process Recommendations

1. <recommendation or "No process change recommended">
2. <optional second recommendation>

## Debt / Planned Work Updates

- **Debt register:**
- **Planned process work:**
- **Product follow-ups captured:** yes/no — IDs if any

## Next Planning Input

<short input for roadmap-planner / product-analyst>

## State Updates

- Ledger:
- Current cycle:
- Debt register:
```

---

## Human Checkpoints

Human approval is required before major process changes, roadmap edits, product direction changes, or accepting new non-Low debt. The retrospective may propose changes; it does not authorize them.
