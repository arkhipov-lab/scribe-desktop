# AI Skills

Self-contained skills for the Scribe feature development pipeline. Each skill is invoked with a one-line prompt — no need to list documents, roles, or output formats.

## Invocation

| Skill | One-line prompt | Notes |
|-------|-----------------|-------|
| [roadmap-planner.md](./roadmap-planner.md) | `Use roadmap-planner.` | After product analysis / for next slice |
| [product-analyst.md](./product-analyst.md) | `Use product-analyst.` | Evidence-based next-work analysis |
| [feature-manager.md](./feature-manager.md) | `Use feature-manager.` | **Normal orchestrator after Product Owner approves scope** |
| [cursor-implementation-prompt.md](./cursor-implementation-prompt.md) | `Use cursor-implementation-prompt.` | **Internal / specialized** handoff artifact — not a normal PO next step |
| [codex-review.md](./codex-review.md) | `Use codex-review.` | After implementation summary exists |
| [review-triage.md](./review-triage.md) | `Use review-triage.` | Auto-fix policy for findings |
| [supervisor-qa.md](./supervisor-qa.md) | `Use supervisor-qa.` | Manual QA plan for Product Owner |
| [commit-manager.md](./commit-manager.md) | `Use commit-manager.` | Pre-commit preparation |
| [iteration-retrospective.md](./iteration-retrospective.md) | `Use iteration-retrospective.` | Metrics + repeated-failure analysis |

Each skill defines its own context loading, preconditions, responsibilities, output contract, and human checkpoints.

## Typical cycle

```
Use product-analyst.     → evidence-based next-work analysis (recommendation first)
Use roadmap-planner.     → bounded slice recommendation → human approves
Use feature-manager.     → sole post-approval entrypoint; prepares implementation handoff
                         → implementation pending → summary → review orchestration
Use codex-review.        → Use review-triage. (auto-fix per policy)
                         → (AI fix loop if needed)
Use supervisor-qa.       → human manual QA
Use commit-manager.      → human approves commit
Use iteration-retrospective. → metrics + repeated-failure analysis
```

After scope approval, always use `Use feature-manager.` — do not offer `Use cursor-implementation-prompt.` as an alternative normal next action.

Full pipeline: [docs/workflows/feature-development-pipeline.md](../../docs/workflows/feature-development-pipeline.md).

Product cycle (above the pipeline): [docs/workflows/ai-product-development-cycle.md](../../docs/workflows/ai-product-development-cycle.md).

## Portable layers

The AI development system is split into reusable and project-specific adapters:

- [`.ai/org/`](../org/) — reusable roles, workflow, metrics, gates, and schema targets;
- [`.ai/product/`](../product/) — Scribe product invariants, roadmap, and scenario adapters;
- [`.ai/repo/`](../repo/) — Scribe stack, validation commands, and forbidden paths.

Use `.ai/org/` for process mechanics, `.ai/product/` for product direction and constraints, and `.ai/repo/` for implementation/validation details.

## Mandatory state

Every approved iteration must have:

- an active ledger under [`docs/iterations/`](../../docs/iterations/);
- current phase and gate status in [`.ai/state/current-cycle.json`](../state/current-cycle.json);
- accepted or deferred debt in [`.ai/state/debt.md`](../state/debt.md);
- product follow-ups / wishes in [`.ai/state/product-followups.md`](../state/product-followups.md).

Each skill must read these artifacts before acting and update them when it completes a phase transition. Chat history is not durable process memory.

## Scribe invariants (all skills)

- Local-only audio/transcript/summary processing
- No transcript/summary logging
- Bridge contract: `backend/app.py` ↔ `frontend/src/vite-env.d.ts`
- Heavy ML/IO on background threads
- Model catalog not hard-coded in the UI
- macOS Apple Silicon only
- Do not commit `dist/`, `.cache/`, recordings, or model weights
- Never stage `ai-md-condidates/` (additions, modifications, or deletions) unless the human explicitly asks
- No commit without explicit human approval

## Experimental process rule (hard)

- **Human never hand-edits** code or docs in this repo
- Human roles: customer, Product Owner, supervisor QA, product reviewer, commit approver
- **Cursor** = implementation agent; **Codex** = independent engineering reviewer; human = product review / approval only
- Human checkpoints: product decisions, scope changes, risky debt, QA pass/fail/skip, commit approval — not routine auto-fixable review findings
- High/Medium: AI auto-fix before QA/commit; Low: auto-fix cheap first-loop items; second+ loop may auto-fix cheap Lows or accept/defer minor Lows as debt per [review-triage.md](./review-triage.md) — never “human will fix in the editor”

See [docs/MANIFEST.md](../../docs/MANIFEST.md).
