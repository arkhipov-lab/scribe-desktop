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
| [`.ai/state/review-findings.json`](../state/review-findings.json) | Structured findings for this iteration (propose updates; do not edit) |
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

After review, output proposed ledger / current-cycle / **review-findings.json** updates for the orchestrator or review-triage role to apply, including the next `handoff` (`next_role` typically `review-triage`, or `human-product-owner` if a product decision is required). Do not edit the working tree or mutate state files as part of the review; the reviewed diff must remain stable.

Every review output must include:

1. **Human-readable findings** for chat and the markdown ledger table.
2. **Proposed structured `review-findings.json` updates** (full finding objects or a clear patch list).
3. **Review loop number** (integer ≥ 1).
4. **Exact severity** (`High` | `Medium` | `Low`) and **exact status** (initially usually `open`).
5. **Clear owner / next role** per finding and in the handoff proposal.

Keep finding `id` values stable inside the iteration (`R1`, `R2`, …). Set `location` to `path:line` when possible; use `null` only for process-level / repo-wide findings. Do not invent debt or product-followup ids during review — triage owns those links.

---

## Non-responsibilities

- Does not implement fixes, triage, or commit
- Does not expand scope or request unrelated features
- Does not edit ledger, current-cycle state, debt register, or any other working-tree file during review

---

## Output Contract

```markdown
## Findings

### Finding N (ID: Rn)

- **Severity:** High | Medium | Low
- **Status:** open (usual at first report) | fixed | accepted_debt | deferred | not_reproducible
- **Review loop:** <integer ≥ 1>
- **File and line:** `path:line` (or `null` if process-level)
- **Owner / next role:** <role>
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

- Ledger (markdown findings table):
- Current cycle (`metrics.*_findings`, `artifacts.latest_review`, `handoff`):
- Structured review-findings.json (propose objects; do not write the file). Example finding object fields:
  - `id`: `R1`
  - `review_loop`: `1`
  - `severity`: `Medium`
  - `status`: `open`
  - `summary`: short non-empty text
  - `location`: `path:line` or `null` if process-level
  - `owner`: next role (e.g. `implementation-agent`)
  - `resolution`: `null` until triage/fix
  - `debt_id`: `null` (triage sets when `accepted_debt`)
  - `product_followup_id`: `null` (triage sets only for product wishes)
```

### Severity guide

| Severity | Examples |
|----------|----------|
| **High** | Content upload; transcript logging; broken core ingest/transcribe; data loss of user history |
| **Medium** | Bridge type drift; missing cancel/cleanup; unverified ML path; scope creep |
| **Low** | Naming, minor copy, optional refactor, doc typo |

---

## Human Checkpoints

Skill may run without approval. After triage, human is asked only for product/scope/privacy/architecture conflicts, product-facing Lows, commits, and scope realignment — not for routine auto-fixable findings.

Do not treat the human as a second implementer: request an AI fix for code/doc changes. Codex owns engineering review; the human owns product review via supervisor QA.
