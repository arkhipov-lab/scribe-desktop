# Codex Review

## Purpose

Review the full uncommitted working tree against Scribe documentation and the current iteration scope. Produce structured findings with severity ratings and an iteration-readiness verdict.

---

## Invocation

```
Use codex-review.
```

---

## Automatic Context Loading

| Document | When |
|----------|------|
| [PRODUCT.md](../../PRODUCT.md) | Always |
| [ROADMAP.md](../../ROADMAP.md) | Always — current slice reference |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Always |
| [LOCAL_DATA.md](../../LOCAL_DATA.md) | If data/settings/history/state touched |
| [AI_PIPELINE.md](../../AI_PIPELINE.md) | If pipeline touched |
| [DECISIONS.md](../../DECISIONS.md) | Always — relevant ADRs |
| [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) | Always for privacy-sensitive diffs |
| [TESTING.md](../../TESTING.md) | Always — verification evidence |
| [AGENTS.md](../../AGENTS.md) | Always |
| [docs/scenarios/](../../docs/scenarios/) | If user-facing flow changed |
| [BUILDING.md](../../BUILDING.md) | If packaging touched |
| [`.ai/org/`](../org/) | Reusable role/gate/metrics boundaries for process changes |
| [`.ai/product/`](../product/) | Product invariants and scenario adapters |
| [`.ai/repo/`](../repo/) | Stack, validation, and forbidden-path adapters |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration, approved scope, and gate state |
| [`.ai/state/debt.md`](../state/debt.md) | Previously accepted/deferred debt |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Role handoffs, implementation summary, verification evidence |
| Implementation summary + approved slice | Always |

Also inspect the working tree (see below).

---

## Preconditions

- Cursor implemented and reported a summary
- Active ledger and current-cycle state exist for the iteration
- Uncommitted working tree exists (or human explicitly asked to review committed state — note that)

Do **not** require a specific Node.js patch version; follow [DEVELOPMENT.md](../../DEVELOPMENT.md) / README (Node 20+).

---

## Responsibilities

### Inspect the full working tree

Do **not** rely on `git diff` alone.

```bash
git status --short --untracked-files=all
git diff
git diff --cached
```

Include unstaged, staged, and untracked files (read contents of untracked).

### Review against documentation

| Area | What to verify |
|------|----------------|
| **Local-only contract** | No audio/transcript/summary upload; no remote AI for core features |
| **Logging** | No transcript/summary/additional-instructions bodies in logs |
| **Bridge contract** | `backend/app.py` Api ↔ `frontend/src/vite-env.d.ts` |
| **Threading** | Heavy ML/IO not on pywebview main thread |
| **Model catalog** | No hard-coded HF ids / token caps in UI |
| **Platform** | No x86_64 / Windows / Linux assumptions |
| **Recording** | Permissions honesty; temp audio cleanup |
| **Packaging** | Artifacts not committed; dist only when in scope |
| **Scope control** | No unrelated refactors or ROADMAP leaps |
| **Verification** | Implementer reported appropriate checks; missing verification → Medium unless trivially safe |

### Produce findings

Cite file and line. Judge against **docs and iteration scope**, not personal style.

### Propose durable memory updates

After review, output proposed ledger/current-cycle updates for the orchestrator or review-triage role to apply. Do not edit the working tree or mutate state files as part of the review; the reviewed diff must remain stable.

---

## Non-responsibilities

- Does not implement fixes, triage, or commit
- Does not expand scope or request unrelated features
- Does not edit ledger, current-cycle state, debt register, or any other working-tree file during review

---

## Output Contract

```markdown
## Findings

### Finding N

- **Severity:** High | Medium | Low
- **File and line:** `path:line`
- **What is wrong:**
- **Why it matters:**
- **Suggested fix:**

---

## Iteration readiness

- [ ] Ready to commit (no High/Medium)
- [ ] Needs fixes (list blocking severities)
- [ ] Scope concern — needs human realignment

## Summary

<2–4 sentences>

## Proposed state updates

- Ledger:
- Current cycle:
```

### Severity guide

| Severity | Examples |
|----------|----------|
| **High** | Content upload; transcript logging; broken core ingest/transcribe; data loss of user history |
| **Medium** | Bridge type drift; missing cancel/cleanup; unverified ML path; scope creep |
| **Low** | Naming, minor copy, optional refactor, doc typo |

---

## Human Checkpoints

Skill may run without approval. After triage, human must approve Low accept/defer, commits, and scope realignment.

Do not treat the human as a second implementer: request an AI fix for code/doc changes. Codex owns engineering review; the human owns product review via supervisor QA.
