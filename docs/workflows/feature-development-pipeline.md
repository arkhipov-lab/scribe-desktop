# Feature Development Pipeline

AI-assisted workflow for building Scribe features in a controlled, reviewable loop.

## Purpose

This pipeline keeps AI-based development:

- **Controlled** — scope is explicit before any code changes
- **Reviewable** — every iteration passes through an independent review gate
- **Aligned** — implementation is checked against product documentation, not ad-hoc assumptions

The assistant (agent manager) orchestrates the loop.

| Role | Responsibility |
| --- | --- |
| **Cursor** | Implementation agent — writes/edits code and docs within approved scope |
| **Codex** | Independent engineering reviewer — critiques the working tree; not the product owner |
| **Human** | Customer, Product Owner, supervisor QA, product reviewer, commit approver — **never** hand-edits the repo |

**No auto-commit** without explicit human approval. **No hand-written code/doc fixes** by the human — request an AI fix or explicitly accept/defer debt.

### Skill invocation

Each pipeline step is a self-contained skill in [`.ai/skills/`](../../.ai/skills/).

| Step | Prompt |
|------|--------|
| Analyze next work | `Use product-analyst.` |
| Plan next slice | `Use roadmap-planner.` |
| Orchestrate cycle | `Use feature-manager.` |
| Review changes | `Use codex-review.` |
| Triage findings | `Use review-triage.` |
| Generate manual QA plan | `Use supervisor-qa.` |
| Prepare commit | `Use commit-manager.` |
| Run retrospective | `Use iteration-retrospective.` |

See [`.ai/skills/README.md`](../../.ai/skills/README.md).

---

## Roles

### Human — Product Owner / supervisor / commit approver

- Decides roadmap direction and approves iteration scope
- Runs supervisor QA (observable product behavior) or explicitly skips it
- Accepts, rejects, or **defers** Low findings as debt — does **not** edit code to clear them
- May **request an AI fix** (Cursor via a bounded fix prompt) for any severity
- Approves commits
- Owns all product decisions (including privacy / platform scope)
- Does **not** write or patch code/docs by hand in this experiment

### Assistant / Agent Manager

- Invokes pipeline skills with one-line prompts
- **Must** run `product-analyst` when choosing next work from roadmap/debt/metrics, then `roadmap-planner`, before every new implementation cycle
- Writes bounded prompts for Cursor and Codex after human approval
- Triages review findings and writes fix prompts
- Does **not** silently change product scope
- Does **not** commit without human approval

### Cursor — implementation agent

- Implements requested changes within defined scope (code and docs)
- Runs verification commands
- Reports changed files, behavior, assumptions, and remaining work

### Codex — independent engineering reviewer

- Reviews the full uncommitted working tree (unstaged, staged, and untracked — not `git diff` alone)
- Reports findings with severity: High / Medium / Low
- Checks scope, architecture, product alignment, Scribe invariants, and verification evidence
- Does **not** replace human product review / supervisor QA

---

## Workflow Steps

```
product-analyst
        │
        ▼
Human reviews analysis
        │
        ▼
roadmap-planner
        │
        ▼
Human approves scope
        │
        ▼
feature pipeline → Cursor implements → Codex reviews → review-triage
        │                                    │
        │                         High/Medium? → AI fix → re-review
        │                                    │
        ▼                                    ▼
supervisor-qa → human product QA → commit-manager (human approves) → iteration-retrospective → next
```

### Step detail

1. **Analyze next work** — `Use product-analyst.` Compare ROADMAP, scenarios, debt, recent metrics, and retrospective evidence.
2. **Plan next slice** — `Use roadmap-planner.` Human approves before proceeding.
3. **Generate implementation prompt** — `Use feature-manager.` or `Use cursor-implementation-prompt.`
4. **Cursor implements** — within scope; run verification.
5. **Review** — `Use codex-review.` (Codex = engineering review only.)
6. **Triage** — `Use review-triage.`
7. **If High/Medium** — AI fix prompt → Cursor; return to step 4.
8. **If only Low** — human **requests an AI fix** or **explicitly accepts/defers** each as debt (human never edits the tree).
9. **Supervisor QA** — `Use supervisor-qa.`
10. **Manual product QA** — human pass/fail (or explicit skip). This is product review, not code review.
11. **Commit** — `Use commit-manager.` Human approves before commit is created.
12. **Retrospective** — `Use iteration-retrospective.` Record metrics, rework, repeated failures, and next planning input.
13. **Implementation summary** — for the next cycle.
14. **Next iteration** — return to step 1.

---

## Mandatory State Updates

Every step must read:

- [`.ai/state/current-cycle.json`](../../.ai/state/current-cycle.json) for the active iteration, phase, and gate status;
- the active ledger under [`docs/iterations/`](../iterations/);
- [`.ai/state/debt.md`](../../.ai/state/debt.md) for accepted/deferred debt.

Every phase transition must update the active ledger and `current-cycle.json`.

| Transition | Required state update |
| --- | --- |
| Human approves scope | Create ledger; set phase to `implementation-prompt` or `implementing` |
| Cursor finishes implementation | Record files, behavior, assumptions, verification; set phase to `review` |
| Codex review completes | Orchestrator/review-triage records findings and counts; set review gate |
| Triage completes | Record blocking and non-blocking decisions; update debt for accepted/deferred items |
| Supervisor QA generated / executed | Record plan, pass/fail/skip, and human decision |
| Commit prepared / created | Record staging hygiene, message, approval, and commit hash; set `phase=retrospective`, `status=retrospective`, `committed=true` |
| Retrospective completed | Record metrics, repeated failures, process recommendations, and next planning input; set `phase=shipped` / `status=shipped` |
| Iteration cancelled | Record cancellation reason and stop the cycle |

State is the durable record of prior decisions. A newer explicit human instruction overrides stale or incorrect state and must be recorded back into the ledger/current-cycle state before the workflow continues.

Run `scripts/ai-cycle-status.sh` when resuming an iteration. Run `scripts/ai-cycle-validate.sh` after state edits, before supervisor QA, and before commit preparation. Validation must pass before commit prep begins.

---

## Review Gate

| Severity | Rule |
|----------|------|
| **High** | Must fix via AI before commit |
| **Medium** | Must fix via AI before commit |
| **Low** | Cheap → AI fix prompt; otherwise human may explicitly accept/defer as debt |

**Gate rule:** No High or Medium findings may remain at commit time.

Scribe-specific High examples: cloud upload of audio/text; transcript/summary logging; bridge type drift that breaks core flows; blocking ML on the UI thread.

---

## Human Checkpoints

Human approval is required before:

- Starting a new iteration
- Changing [PRODUCT.md](../../PRODUCT.md)
- Changing roadmap scope in [ROADMAP.md](../../ROADMAP.md)
- Adding major architecture decisions to [DECISIONS.md](../../DECISIONS.md)
- Accepting or deferring unresolved Low findings (AI performs any code/doc fix)
- Skipping supervisor QA (must be explicit)
- Committing
- Moving to the next major roadmap bet

Human never clears findings by editing the working tree.

---

## Scope Control

Every Cursor prompt must define:

- **In scope**
- **Out of scope**
- **Verification**
- **Documentation updates**
- **Final response format**

Do not expand scope without human approval.

---

## Verification Expectations

| Change type | Typical verification |
|-------------|---------------------|
| Frontend / TypeScript | `(cd frontend && npm run build)` |
| General desktop smoke | `./scripts/run-dev.sh` |
| Production UI in window | `USE_VITE_DEV=0 ./scripts/run-dev.sh` |
| Backend-only logic | Dev smoke of affected Api path; see [TESTING.md](../../TESTING.md) |
| Recording | Start/stop Record; WAV under `~/Library/Caches/Scribe/recordings/`; temp cleanup |
| Transcription / summary | Short file still transcribes/summarizes; cancel paths; log has no transcript body |
| Packaging | `./scripts/build.sh` or `./scripts/build-dist.sh` — **full dist only when packaging-related** |

Do **not** run full `build-dist.sh` for pure UI copy tweaks.

Cursor must report which checks ran and their results.

---

## Anti-patterns

- Implementing ROADMAP items that were not approved for this slice
- Drive-by refactors unrelated to the iteration
- Rewriting product docs unnecessarily
- Accepting AI review output without a human checkpoint
- Endless Low-finding polish loops
- Committing without verification summary
- Adding cloud sync, telemetry, or remote AI APIs “temporarily”
- Logging transcript/summary “for debugging”
- Hard-coding model ids / token caps in the UI
- Committing `dist/`, `.cache/`, recordings, or model weights

---

## Example Lifecycle: Cancel summary polish

**Goal:** Cancelling summary never clears an existing good transcript; UI returns to a sane idle state.

**Scope:** Cancel path in summarizer / Api state; UI status copy; scenario + TESTING notes if behavior was underspecified.

**Flow:**

1. Roadmap planner recommends a small cancel-summary slice over a larger diarization bet.
2. Human approves; feature manager writes a bounded Cursor prompt.
3. Cursor implements; runs `(cd frontend && npm run build)` and manual cancel smoke via `./scripts/run-dev.sh`.
4. Independent review flags missing sync between a new Api field and `vite-env.d.ts` (Medium).
5. Fix + re-review; supervisor QA plan covers cancel mid-summary and log privacy.
6. Human approves commit.

---

## Related Files

| File | Invocation |
|------|------------|
| [`.ai/skills/README.md`](../../.ai/skills/README.md) | Skill index |
| [`.ai/skills/product-analyst.md`](../../.ai/skills/product-analyst.md) | `Use product-analyst.` |
| [`.ai/skills/roadmap-planner.md`](../../.ai/skills/roadmap-planner.md) | `Use roadmap-planner.` |
| [`.ai/skills/feature-manager.md`](../../.ai/skills/feature-manager.md) | `Use feature-manager.` |
| [`.ai/skills/cursor-implementation-prompt.md`](../../.ai/skills/cursor-implementation-prompt.md) | `Use cursor-implementation-prompt.` |
| [`.ai/skills/codex-review.md`](../../.ai/skills/codex-review.md) | `Use codex-review.` |
| [`.ai/skills/review-triage.md`](../../.ai/skills/review-triage.md) | `Use review-triage.` |
| [`.ai/skills/supervisor-qa.md`](../../.ai/skills/supervisor-qa.md) | `Use supervisor-qa.` |
| [`.ai/skills/commit-manager.md`](../../.ai/skills/commit-manager.md) | `Use commit-manager.` |
| [ai-product-development-cycle.md](./ai-product-development-cycle.md) | Product-level cycle above this pipeline |
