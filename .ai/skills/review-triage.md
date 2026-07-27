# Review Triage

## Purpose

Interpret review findings, decide whether another Cursor iteration is required, detect scope creep, and route to supervisor QA or fix. Does not implement fixes or commit.

Applies the **auto-fix policy** so routine findings do not require human approval before every fix.

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
| Review loop count | First vs second+ loop for Low policy |

---

## Preconditions

- A review exists for the current iteration (`Use codex-review.` first if missing)
- Implementation summary exists (`gates.implementation_finished=true`)
- Active ledger and current-cycle state exist

---

## Auto-fix policy

### High findings

- Must be fixed via AI before QA/commit.
- Generate a bounded AI fix prompt automatically.
- Human approval required only if the fix requires product direction change, scope expansion, privacy promise change, or a risky architectural decision.

### Medium findings

- Must be fixed via AI before QA/commit.
- Generate a bounded AI fix prompt automatically.
- Human approval required only if the fix requires product direction change, scope expansion, or accepting Medium debt (Medium debt remains disallowed unless the human explicitly changes the gate).

### Low findings — first review loop

- Automatically fix all cheap / local / non-product Low findings in the same AI fix pass.
- Do **not** ask the human whether to fix obvious doc drift, naming, output contract mismatch, small copy mismatch, or local consistency issues.
- Human approval required only if a Low finding changes product behavior, expands scope, or creates a meaningful product/UX tradeoff.

### Low findings — second or later review loop

- If new Low findings are cheap and local **and clearly non-product**, auto-fix once more.
- If Low findings are minor, repetitive, style-only, or not worth another loop **and clearly non-product**:
  - record as accepted/deferred Low debt with reason and revisit condition;
  - do not block QA/commit;
  - do not ask the human for routine non-product polish.
- **Hard rule — product-facing Low cannot be silently deferred:**
  - If a Low changes product behavior, expands scope, creates a meaningful product/UX tradeoff, or could be product ambiguity mislabeled as “style-only,” **do not** accept/defer it as debt without Product Owner judgment.
  - When in doubt whether a Low is product-facing, **do not silently defer** — ask the Product Owner (or auto-fix only if cheap and clearly non-product).

### Product wishes are not review findings

- Product Owner wishes, QA follow-ups, and future UX ideas go to `.ai/state/product-followups.md`.
- They must not be routed through review debt or used to block commit unless the Product Owner explicitly re-scopes the current iteration.

```
Review received
  → High/Medium? → auto AI fix prompt → Cursor → re-review
       (ask human only for product/scope/privacy/architecture conflicts)
  → First-loop cheap Lows? → include in same auto AI fix pass
  → Product-facing Low / UX tradeoff / product ambiguity? → ask human (never silent defer)
  → Second+ loop cheap non-product Lows? → auto-fix once more
  → Second+ loop minor non-product Lows? → record Low debt; continue
  → clean (no open High/Medium; Lows fixed or policy-deferred) → supervisor-qa
```

### Scope creep

Flag unrelated files, later ROADMAP features, drive-by refactors, product behavior not in the slice. **Stop** and ask human to have AI revert or expand officially.

### Docs

Update when public Api/UX/architecture behavior changes. Do not churn docs for pure refactors. Missing docs flagged Medium → include in auto fix prompt.

### Prevent endless Low loops

- First loop: auto-fix cheap Lows with any High/Medium fix pass (or a dedicated Low pass if Lows-only).
- Second+ loop: auto-fix cheap new **non-product** Lows once more, or accept/defer minor **non-product** Lows as debt under policy without human ask.
- **Never** silently defer a product-facing Low (or a Low that might be product ambiguity) as debt.
- Do not full re-review for Low-only polish unless High/Medium were also fixed in that pass.
- Human never clears Lows by editing the tree.

### Update durable memory

- Record triage decisions in the active ledger, including:
  - auto-fix pass generated / applied;
  - Low findings auto-fixed;
  - Low findings accepted/deferred without human involvement when policy allows;
  - human involvement reason when human input was required.
- Update `.ai/state/current-cycle.json` with the next phase/gate state **and** `handoff` (`next_role` typically `supervisor-qa` when clean, `implementation-agent` / fix path when dirty, or `human-product-owner` when a product decision is required)
- Add accepted or deferred **review findings** to `.ai/state/debt.md` with revisit conditions
- Do **not** put Product Owner wishes, future UX ideas, or deferred roadmap opportunities into `debt.md` — those belong in `.ai/state/product-followups.md` (usually captured at Supervisor QA or planning, not triage)

---

## Responsibilities

| Severity | Rule |
|----------|------|
| **High** | Must fix via AI — generate Cursor fix prompt automatically |
| **Medium** | Must fix via AI before commit — generate Cursor fix prompt automatically |
| **Low (first loop, cheap)** | Auto-include in AI fix pass — do not ask |
| **Low (product-facing / tradeoff / ambiguity)** | Ask human — **never silently defer as debt** |
| **Low (second+ loop, cheap, non-product)** | Auto-fix once more |
| **Low (second+ loop, minor, clearly non-product)** | Accept/defer as Low debt with reason — do not block QA |

---

## Non-responsibilities

- Does not implement, commit, silently accept High/Medium, silently defer product-facing Lows, or run the review itself
- Does not ask the human to hand-edit code or docs
- Does not ask the human to approve routine auto-fixable findings

---

## Output Contract

```markdown
## Review triage — <iteration name>

### Review loop
- Loop number: <1 / 2 / …>
- Auto-fix policy applied: <summary>

### Blocking (must fix)
| # | Severity | File | Issue | Action |
|---|----------|------|-------|--------|
| 1 | Medium | `path:line` | ... | Include in auto AI fix prompt |

### Low findings
| # | File | Issue | Disposition |
|---|------|-------|-------------|
| 1 | `path:line` | ... | Auto-fix / ask human (reason) / accept-defer as debt (reason) |

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
- [ ] Write Cursor fix prompt (auto)
- [ ] Ask human — only if product/scope/privacy/architecture/product-facing Low
- [ ] Record Low debt under second+ loop policy
- [ ] Invoke supervisor-qa

### Human involvement
- Required: yes/no
- Reason (if yes): ...

### State updates
- Ledger:
- Current cycle:
- Debt register:
- Product follow-ups (if any wishes captured — not as debt):
```

---

## Human Checkpoints

Required before:

- Product direction / scope expansion / privacy-promise / risky architecture fixes
- Accepting Medium or High as debt (normally disallowed)
- Product-facing Low findings or meaningful product/UX tradeoffs
- Proceeding after scope creep
- Skipping QA
- Recommending commit

Do **not** stop to ask whether to fix routine High/Medium or cheap first-loop Low findings.

Never suggest the human edit files themselves.

---

## When review is clean

If no High/Medium remain and Low items are fixed via AI or accepted/deferred under policy:

1. Confirm Cursor verification summary is complete
2. Invoke `Use supervisor-qa.` to generate the manual QA plan
3. Wait for the human to execute **product** QA and report pass/fail
4. After QA passes (or human explicitly skips), invoke `Use commit-manager.`
5. Ask human for commit approval
