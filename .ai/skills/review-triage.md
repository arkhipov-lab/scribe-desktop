# Review Triage

## Purpose

Interpret review findings, decide whether another Cursor iteration is required, detect scope creep, and route to supervisor QA or fix. Does not implement fixes or commit.

---

## Invocation

```
Use review-triage.
```

---

## Automatic Context Loading

| Source | Purpose |
|--------|---------|
| Latest review output | Findings + readiness |
| Latest Cursor implementation summary | Expected scope / verification |
| Approved slice | In / out of scope |
| [ROADMAP.md](../../ROADMAP.md) | Later-iteration leakage |
| [PRODUCT.md](../../PRODUCT.md) / [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) | Invariant violations |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration, review gate, phase |
| [`.ai/state/debt.md`](../state/debt.md) | Previously accepted/deferred findings |
| [`.ai/state/product-followups.md`](../state/product-followups.md) | Product wishes — **not** review debt; do not triage as findings |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Review findings and implementation summary |
| Previously accepted Lows | Avoid re-litigation |

---

## Preconditions

- A review exists for the current iteration (`Use codex-review.` first if missing)
- Implementation summary exists
- Active ledger and current-cycle state exist

---

## Responsibilities

| Severity | Rule |
|----------|------|
| **High** | Must fix via AI — generate Cursor fix prompt immediately |
| **Medium** | Must fix via AI before commit — generate Cursor fix prompt |
| **Low** | If cheap → generate AI fix prompt; else ask human to **request AI fix** or **explicitly accept/defer** as debt |

```
Review received
  → High/Medium? → AI fix prompt → Cursor → re-review
  → Low only? → human requests AI fix OR accepts/defers (never hand-edits)
  → clean → supervisor-qa → manual product QA → commit-manager
```

### Scope creep

Flag unrelated files, later ROADMAP features, drive-by refactors, product behavior not in the slice. **Stop** and ask human to have AI revert or expand officially.

### Docs

Update when public Api/UX/architecture behavior changes. Do not churn docs for pure refactors. Missing docs flagged Medium → include in fix prompt.

### Prevent endless Low loops

At most one dedicated Low AI-fix pass; then human accepts or defers. Do not full re-review for Low-only polish unless High/Medium were also fixed. Human never clears Lows by editing the tree.

### Update durable memory

- Record triage decisions in the active ledger
- Update `.ai/state/current-cycle.json` with the next phase/gate state
- Add accepted or deferred **review findings** to `.ai/state/debt.md` with revisit conditions
- Do **not** put Product Owner wishes, future UX ideas, or deferred roadmap opportunities into `debt.md` — those belong in `.ai/state/product-followups.md` (usually captured at Supervisor QA or planning, not triage)

---

## Non-responsibilities

- Does not implement, commit, silently accept Lows, or run the review itself
- Does not ask the human to hand-edit code or docs

---

## Output Contract

```markdown
## Review triage — <iteration name>

### Blocking (must fix)
| # | Severity | File | Issue | Action |
|---|----------|------|-------|--------|
| 1 | Medium | `path:line` | ... | Include in AI fix prompt |

### Non-blocking (Low)
| # | File | Issue | Recommendation |
|---|------|-------|----------------|
| 1 | `path:line` | ... | AI fix prompt / ask human accept or defer |

### Scope check
- [ ] Matches iteration scope
- [ ] No unrelated changes
- Notes: ...

### Documentation check
- [ ] Public surface reflected in docs
- Notes: ...

### Privacy / bridge check
- [ ] No content logging / upload introduced
- [ ] vite-env.d.ts synced if Api changed
- Notes: ...

### Next step
- [ ] Write Cursor fix prompt
- [ ] Ask human: request AI fix vs accept/defer each Low
- [ ] Invoke supervisor-qa

### State updates
- Ledger:
- Current cycle:
- Debt register:
```

---

## Human Checkpoints

Required before accepting/deferring Lows, proceeding after scope creep, skipping QA, or recommending commit.

When only Low findings remain, **stop and ask** whether to request an AI fix or accept/defer each one. Do not suggest the human edit files themselves.

---

## When review is clean

If no High/Medium and Low items are fixed via AI or explicitly accepted/deferred:

1. Confirm Cursor verification summary is complete
2. Invoke `Use supervisor-qa.` to generate the manual QA plan
3. Wait for the human to execute **product** QA and report pass/fail
4. After QA passes (or human explicitly skips), invoke `Use commit-manager.`
5. Ask human for commit approval
