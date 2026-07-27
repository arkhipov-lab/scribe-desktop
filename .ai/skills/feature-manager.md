# Feature Manager

## Purpose

Orchestrate the AI-assisted feature development loop for Scribe: plan slices, write bounded prompts for Cursor and the reviewer, triage findings, and prepare commits. Does not implement code directly.

**After Product Owner approves a bounded slice, `Use feature-manager.` is the single normal user-facing entrypoint.** The Cursor implementation prompt is an internal handoff artifact produced by this orchestrator (via [cursor-implementation-prompt.md](./cursor-implementation-prompt.md)), not an alternative next step for the Product Owner.

---

## Invocation

```
Use feature-manager.
```

For a single specialized step when already mid-cycle, invoke that skill (e.g. `Use codex-review.`, `Use review-triage.`). Do **not** present `Use cursor-implementation-prompt.` as a normal Product Owner next action.

---

## Automatic Context Loading

| Document | Purpose |
|----------|---------|
| [PRODUCT.md](../../PRODUCT.md) | Vision / non-goals |
| [DECISIONS.md](../../DECISIONS.md) | ADRs |
| [ROADMAP.md](../../ROADMAP.md) | Hypothesis backlog |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Layers |
| [LOCAL_DATA.md](../../LOCAL_DATA.md) | Local data |
| [AI_PIPELINE.md](../../AI_PIPELINE.md) | Pipeline invariants |
| [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) | Privacy |
| [TESTING.md](../../TESTING.md) | Smoke matrix |
| [AGENTS.md](../../AGENTS.md) | Agent rules |
| [docs/scenarios/](../../docs/scenarios/) | Behavior specs |
| [`.ai/org/`](../org/) | Reusable roles, workflow, metrics, and schema targets |
| [`.ai/product/`](../product/) | Product invariants, roadmap, and scenario adapters |
| [`.ai/repo/`](../repo/) | Stack, validation commands, and forbidden paths |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration, phase, and gate state |
| [`.ai/state/debt.md`](../state/debt.md) | Accepted/deferred debt |
| [`.ai/state/product-followups.md`](../state/product-followups.md) | Product wishes — not debt; do not route into debt register |
| [docs/iterations/](../../docs/iterations/) | Active and previous iteration ledgers |
| Latest summaries / reviews / git tree | Cycle state |

When docs conflict, stop and ask the human.

---

## Preconditions

- Docs exist
- **New cycle:** run product-analyst first when choosing next work from roadmap/debt/metrics, then roadmap-planner; wait for human approval
- **After scope approval:** create or update the iteration ledger and `.ai/state/current-cycle.json` before implementation prompt generation
- **Review/fix:** implementation summary exists (`gates.implementation_finished=true`); do not start review while implementation is still pending
- **Supervisor QA:** review gate clean
- **Commit:** review gate clean; QA passed or explicitly skipped

---

## Responsibilities

### New implementation cycle (mandatory)

1. Run [product-analyst.md](./product-analyst.md) when choosing the next iteration from roadmap/debt/metrics
2. Run [roadmap-planner.md](./roadmap-planner.md)
3. Wait for human approval
4. Create/update the active ledger under `docs/iterations/` and `.ai/state/current-cycle.json`
5. Prepare the implementation handoff (internal): generate Cursor prompt via [cursor-implementation-prompt.md](./cursor-implementation-prompt.md); record **implementation prompt prepared** and set phase so **implementation is pending**
6. When Cursor / the implementation agent returns a summary, record it in the ledger and current-cycle (files, behavior, assumptions, verification, remaining work, docs); set `gates.implementation_finished=true` and phase to `review`
7. Only then: `Use codex-review.`

### Implementation phase model

```
scope approved
  → implementation prompt prepared
  → implementation pending
  → implementation summary received
  → review ready
  → codex-review
```

Do **not** imply review can begin before implementation has actually completed. Do **not** expose internal handoff mechanics (“After Cursor finishes, share the summary here…”) as Product Owner instructions before implementation has happened — orchestrate the handoff; the PO checkpoint after approval is waiting for engineering delivery, not operating the prompt pipeline.

### Review and fix loop (auto-fix policy)

8. `Use review-triage.`
9. Apply the **auto-fix policy** (see below and [review-triage.md](./review-triage.md)):
   - **High / Medium:** generate bounded AI fix prompt automatically; re-implement → re-review. Ask the human only if the fix needs product direction change, scope expansion, privacy-promise change, or a risky architectural decision. Medium debt remains disallowed unless the human explicitly changes the gate.
   - **Low, first review loop:** automatically include all cheap / local / non-product Lows in the same AI fix pass. Do **not** ask whether to fix obvious doc drift, naming, output-contract mismatch, small copy mismatch, or local consistency issues. Ask only if a Low changes product behavior, expands scope, or creates a meaningful product/UX tradeoff.
   - **Low, second or later review loop:** if new Lows are cheap and local **and clearly non-product**, auto-fix once more; if minor / repetitive / style-only / not worth another loop **and clearly non-product**, record as accepted/deferred Low debt with reason and revisit condition — do not block QA/commit. **Hard rule: product-facing Lows (including possible product ambiguity mislabeled as style-only) must never be silently deferred** — ask the Product Owner; when in doubt, do not silent-defer.
10. Record accepted/deferred **review** debt in `.ai/state/debt.md`; product wishes go to `.ai/state/product-followups.md` (never as review debt, never as commit blockers unless PO re-scopes)

### Supervisor QA and commit

11. `Use supervisor-qa.` → human manual QA
12. Record QA outcome in the active ledger and current-cycle state
13. `Use commit-manager.` only after QA pass or explicit skip
14. After human-approved commit, set post-commit `phase=retrospective` (via commit-manager), then `Use iteration-retrospective.`
15. After retrospective completes (`phase=shipped`), produce the planning handoff for the next cycle

### Scope preservation

- Match approved slice only
- Flag out-of-scope work from Cursor summaries
- Never bundle unrelated ROADMAP items silently

### Durable memory

- Read `.ai/state/current-cycle.json`, `.ai/state/debt.md`, `.ai/state/product-followups.md`, and the active ledger before choosing the next action
- Run `scripts/ai-cycle-status.sh` when resuming or reporting the active cycle
- Update the ledger and current-cycle state at every phase transition (including implementation pending → summary received, and each auto-fix pass)
- Run `scripts/ai-cycle-validate.sh` after state updates that move the cycle toward QA or commit
- Treat state files as the durable record of prior decisions; a newer explicit human instruction overrides stale or incorrect state and must be recorded back into the ledger/current-cycle state
- When human input was required mid-loop, record **human involvement reason** in the ledger

---

## Non-responsibilities

- Does **not** implement code, auto-commit, or accept High/Medium as debt
- Does **not** override PRODUCT / SECURITY-PRIVACY / DECISIONS
- Does **not** skip roadmap-planner on a new cycle
- Does **not** ask the human to approve routine auto-fixable findings

---

## Output Contract

Produce the artifact for the **current phase only** (unless human asked for status overview):

- Product analysis → [product-analyst.md](./product-analyst.md) template
- Planning → roadmap recommendation verbatim + approval question
- Implementation prompt → [cursor-implementation-prompt.md](./cursor-implementation-prompt.md) template (internal handoff; next PO-visible step after delivery is review orchestration, not “choose between skills”)
- Review → findings per [codex-review.md](./codex-review.md)
- Fix prompt → bounded list of findings only (auto-generated per policy)
- Supervisor QA → [supervisor-qa.md](./supervisor-qa.md)
- Commit → [commit-manager.md](./commit-manager.md)
- Retrospective → [iteration-retrospective.md](./iteration-retrospective.md)

Every phase output must also state which ledger/current-cycle/debt updates were made or why no update was required.

### Cursor fix prompt template

```markdown
## Fix prompt — <iteration name>

**Context:** ...

**Findings to fix:**
1. [Severity] File:line — issue — suggested fix

**In scope:** Only the listed fixes.

**Out of scope:** No new features, no unrelated refactors.

**Verification:** `(cd frontend && npm run build)` and/or `./scripts/run-dev.sh` + relevant smoke.

**Final response format:**
- Files changed
- How each finding was addressed
- Verification results
- Anything still open
```

### Review loop decision

| Review outcome | Action |
|----------------|--------|
| High or Medium findings | Auto-generate AI fix prompt → Cursor fixes → new Codex review (ask human only for product/scope/privacy/architecture conflicts) |
| Cheap / local / non-product Low findings (first loop) | Include in same AI fix pass automatically |
| Product-facing Low / UX tradeoff / product ambiguity | Ask human — **never silently defer as debt**; when in doubt, ask |
| Second+ loop: cheap new non-product Lows | Auto-fix once more |
| Second+ loop: minor clearly non-product / not worth another loop | Record Low debt (reason + revisit); do not block QA |
| No open High/Medium; Lows fixed or policy-deferred | Invoke supervisor-qa; after human product QA passes, recommend commit |
| Scope creep detected | Stop; realign with human before more code |
| Product wishes / future UX ideas | Route to `.ai/state/product-followups.md` — not debt, not review findings |

---

## Human Checkpoints

Ask for explicit human approval before:

- Starting a new cycle after roadmap recommendation
- Changing scope mid-iteration
- Approving PRODUCT / ROADMAP / major DECISIONS / SECURITY-PRIVACY edits (AI still performs the edit)
- Product-facing Low findings or Lows that create meaningful product/UX tradeoffs
- Accepting Medium (or High) as debt — disallowed unless the human explicitly changes the gate
- Fixes that require product direction change, scope expansion, privacy-promise change, or risky architecture
- Skipping supervisor QA and proceeding directly to commit
- Recommending commit
- Advancing to a new major roadmap bet

Do **not** ask the human whether to fix routine High/Medium or cheap first-loop Low findings — auto-generate the fix prompt.

Never ask the human to edit the working tree themselves — offer an AI fix prompt instead.

---

## Cycle overview

```
product-analyst → roadmap-planner → human approves → feature-manager
  → (internal) implementation prompt → implementation pending
  → implementation summary → Codex review → review-triage
  → (auto AI fix loop per policy) → supervisor-qa → product QA (human)
  → commit-manager → iteration-retrospective → next planning
```

See [docs/workflows/feature-development-pipeline.md](../../docs/workflows/feature-development-pipeline.md).
