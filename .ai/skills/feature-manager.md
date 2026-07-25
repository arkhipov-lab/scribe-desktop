# Feature Manager

## Purpose

Orchestrate the AI-assisted feature development loop for Scribe: plan slices, write bounded prompts for Cursor and the reviewer, triage findings, and prepare commits. Does not implement code directly.

---

## Invocation

```
Use feature-manager.
```

For a single step, invoke the specialized skill (e.g. `Use roadmap-planner.`, `Use codex-review.`).

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
| Latest summaries / reviews / git tree | Cycle state |

When docs conflict, stop and ask the human.

---

## Preconditions

- Docs exist
- **New cycle:** run roadmap-planner first; wait for human approval
- **Review/fix:** implementation summary exists
- **Supervisor QA:** review gate clean
- **Commit:** review gate clean; QA passed or explicitly skipped

---

## Responsibilities

### New implementation cycle (mandatory)

1. Run [roadmap-planner.md](./roadmap-planner.md)
2. Wait for human approval
3. Generate Cursor prompt via [cursor-implementation-prompt.md](./cursor-implementation-prompt.md)
4. After implementation: `Use codex-review.`

### Review and fix loop

5. `Use review-triage.`
6. High/Medium → bounded fix prompt → re-implement → re-review
7. Low only → ask human to **request an AI fix** or **explicitly accept/defer** each as debt (human never edits the tree)

### Supervisor QA and commit

8. `Use supervisor-qa.` → human manual QA
9. `Use commit-manager.` only after QA pass or explicit skip
10. Implementation summary after commit

### Scope preservation

- Match approved slice only
- Flag out-of-scope work from Cursor summaries
- Never bundle unrelated ROADMAP items silently

---

## Non-responsibilities

- Does **not** implement code, auto-commit, or silently accept Lows
- Does **not** override PRODUCT / SECURITY-PRIVACY / DECISIONS
- Does **not** skip roadmap-planner on a new cycle

---

## Output Contract

Produce the artifact for the **current phase only** (unless human asked for status overview):

- Planning → roadmap recommendation verbatim + approval question
- Implementation prompt → [cursor-implementation-prompt.md](./cursor-implementation-prompt.md) template
- Review → findings per [codex-review.md](./codex-review.md)
- Fix prompt → bounded list of findings only
- Supervisor QA → [supervisor-qa.md](./supervisor-qa.md)
- Commit → [commit-manager.md](./commit-manager.md)

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
| High or Medium findings | Write AI fix prompt → Cursor fixes → new Codex review |
| Only Low findings | Ask human: request AI fix, or accept/defer each as debt (never hand-edit) |
| No findings | Invoke supervisor-qa; after human product QA passes, recommend commit |
| Scope creep detected | Stop; realign with human before more code |

---

## Human Checkpoints

Ask for explicit human approval before:

- Starting a new cycle after roadmap recommendation
- Changing scope mid-iteration
- Approving PRODUCT / ROADMAP / major DECISIONS / SECURITY-PRIVACY edits (AI still performs the edit)
- Accepting or deferring unresolved Low findings
- Skipping supervisor QA and proceeding directly to commit
- Recommending commit
- Advancing to a new major roadmap bet

Never ask the human to edit the working tree themselves — offer an AI fix prompt instead.

---

## Cycle overview

```
roadmap-planner → human approves → Cursor prompt
  → Cursor implements → Codex review → review-triage
  → (AI fix loop) → supervisor-qa → product QA (human)
  → commit-manager → summary → next
```

See [docs/workflows/feature-development-pipeline.md](../../docs/workflows/feature-development-pipeline.md).
