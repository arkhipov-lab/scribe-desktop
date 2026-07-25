# AI Development Workflow

Current version: **v1.0** (adapted for Scribe)

Status: Stable starting point — expect evolution through use.

## Operating model

[AI Product Development Cycle](./ai-product-development-cycle.md) — product-level loop: planning → engineering delivery → demo → retrospectives → analytics → process evolution → next priority.

## Pipeline

[Feature Development Pipeline](./feature-development-pipeline.md) — engineering delivery inside the product cycle (bounded prompts, review, QA, commit).

## Skills

Self-contained skills in [`.ai/skills/`](../../.ai/skills/). Invoke with a one-line prompt:

| Prompt | Skill |
|--------|-------|
| `Use roadmap-planner.` | Next slice recommendation |
| `Use feature-manager.` | Full cycle orchestration |
| `Use codex-review.` | Working-tree review |
| `Use review-triage.` | Finding interpretation |
| `Use supervisor-qa.` | Manual QA plan for Product Owner |
| `Use commit-manager.` | Pre-commit preparation |

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
