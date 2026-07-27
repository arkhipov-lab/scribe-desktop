# AI Development Workflow

Current version: **v1.0** (adapted for Scribe)

Status: Stable starting point — expect evolution through use.

## Portable layers

The process is split into reusable and project-specific layers:

- [`.ai/org/`](../../.ai/org/) — reusable AI organization roles, workflows, metrics, gates, and schema targets;
- [`.ai/product/`](../../.ai/product/) — Scribe product invariants, roadmap, and scenarios;
- [`.ai/repo/`](../../.ai/repo/) — Scribe stack, validation commands, and forbidden paths.

Existing root docs remain canonical for Scribe. The `.ai/*` layer files are adapters that make the process easier to port to another repository.

## Mandatory iteration memory

Every approved product or process iteration must have durable memory before implementation starts:

- a ledger in [`docs/iterations/`](../iterations/);
- current phase and gate state in [`.ai/state/current-cycle.json`](../../.ai/state/current-cycle.json);
- accepted or deferred debt in [`.ai/state/debt.md`](../../.ai/state/debt.md);
- product follow-ups / wishes in [`.ai/state/product-followups.md`](../../.ai/state/product-followups.md).

Agents must read these artifacts at the start of each workflow step and update them when the phase changes. Chat history is supporting context, not the source of truth.

## Cycle validator

Use the lightweight validator when checking or advancing cycle state:

```bash
scripts/ai-cycle-status.sh
scripts/ai-cycle-validate.sh
```

Run `scripts/ai-cycle-status.sh` when resuming work or before choosing the next workflow action. Run `scripts/ai-cycle-validate.sh` after state edits, before supervisor QA, and before commit preparation.

The validator checks JSON validity, ledger existence, phase gates, unresolved High/Medium findings, QA/commit prerequisites, shipped commit hashes, and forbidden paths.

## Operating model

[AI Product Development Cycle](./ai-product-development-cycle.md) — product-level loop: planning → engineering delivery → demo → retrospectives → analytics → process evolution → next priority.

[Iteration Ledger](./iteration-ledger.md) — durable per-iteration memory: approved scope, role handoffs, findings, QA outcome, metrics, debt, retrospective, and commit link.

[AI Development System Convention](../../AI_CONVENTION.md) — product convention for the broader AI development system.

[AI Development System Roadmap](../../AI_SYSTEM_ROADMAP.md) — roadmap for turning the workflow into a stateful, measurable AI organization.

## Pipeline

[Feature Development Pipeline](./feature-development-pipeline.md) — engineering delivery inside the product cycle (bounded prompts, review, QA, commit).

## Skills

Self-contained skills in [`.ai/skills/`](../../.ai/skills/). Invoke with a one-line prompt:

| Prompt | Skill |
|--------|-------|
| `Use product-analyst.` | Evidence-based next-work analysis |
| `Use roadmap-planner.` | Next slice recommendation |
| `Use feature-manager.` | Full cycle orchestration |
| `Use codex-review.` | Working-tree review |
| `Use review-triage.` | Finding interpretation |
| `Use supervisor-qa.` | Manual QA plan for Product Owner |
| `Use commit-manager.` | Pre-commit preparation |
| `Use iteration-retrospective.` | Metrics, retrospective, repeated-failure analysis |

See [`.ai/skills/README.md`](../../.ai/skills/README.md) for the full index.

## Scribe verification (quick reference)

| Change type | Typical check |
| --- | --- |
| Frontend / TS | `(cd frontend && npm run build)` |
| General smoke | `./scripts/run-dev.sh` |
| Production UI smoke | `USE_VITE_DEV=0 ./scripts/run-dev.sh` |
| Packaging | `./scripts/build.sh` or `./scripts/build-dist.sh` — full dist **only** for packaging-related work |

Authoritative smoke matrix: [TESTING.md](../../TESTING.md).

## When to modify

This workflow should only be modified when:

- repeated friction is observed;
- a new AI role appears;
- a recurring manual activity is identified.

Otherwise development effort should focus on product features.

Major process changes require human approval ([MANIFEST.md](../MANIFEST.md)).
