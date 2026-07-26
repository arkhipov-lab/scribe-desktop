# AI Product Development Cycle

**Status:** Initial operating model for Scribe — expected to evolve through use.

This document describes the recurring development cycle for one product increment in **Scribe**.

It is inspired by Scrum as a **stable starting point for process design**. It does **not** implement Scrum literally. Time-boxed ceremonies are not the primary abstraction. The important part is the **sequence of responsibilities and feedback loops**.

---

## Purpose

This is the complete product-level cycle around one increment:

- planning;
- engineering delivery;
- engineering review;
- product validation;
- retrospective;
- analytics;
- process evolution;
- next-priority selection.

The human participates as **Product Owner**.

AI roles handle planning support, engineering, review, QA preparation, analytics, and process evaluation.

This is **not** a “give AI a specification and wait for a finished application” model.

See [docs/MANIFEST.md](../MANIFEST.md).

---

## Core principle

```
Product direction
    ↓
Planning
    ↓
Engineering delivery
    ↓
Product validation / demo
    ↓
Engineering retrospective
    ↓
Product retrospective
    ↓
Analytics and process evolution
    ↓
Grooming / next priority
    ↺
```

Do not invent ceremony for ceremony’s sake. Keep a step only while it improves product value, delivery reliability, or process learning.

---

## Initial conditions

At the beginning of a cycle, assume:

- product vision exists ([PRODUCT.md](../../PRODUCT.md));
- roadmap and scenarios exist ([ROADMAP.md](../../ROADMAP.md), [docs/scenarios/](../scenarios/));
- technical truth docs exist ([ARCHITECTURE.md](../../ARCHITECTURE.md), [AI_PIPELINE.md](../../AI_PIPELINE.md), [LOCAL_DATA.md](../../LOCAL_DATA.md), [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md));
- decisions are recorded when needed ([DECISIONS.md](../../DECISIONS.md));
- previous iteration results are available when applicable.

Every approved iteration must also have durable process state:

- an iteration ledger under [`docs/iterations/`](../iterations/);
- current phase and gate status in [`.ai/state/current-cycle.json`](../../.ai/state/current-cycle.json);
- accepted or deferred debt in [`.ai/state/debt.md`](../../.ai/state/debt.md).

Create or update these artifacts at phase transitions. Do not treat chat history as durable cycle memory.

The process must **not** assume a perfect specification. [ROADMAP.md](../../ROADMAP.md) is a hypothesis.

---

## The development cycle

### 1. Product direction and planning

Identify the highest-value next product slice; compare alternatives; preserve human ownership of priorities.

**Role:** [roadmap-planner](../../.ai/skills/roadmap-planner.md)

**Output:** A bounded, human-approved product slice: goal, in scope, out of scope, hypothesis, acceptance signals. After approval, create or update the iteration ledger and `.ai/state/current-cycle.json`.

### 2. Engineering delivery

Translate the approved slice into engineering work; implement; independent review; fix blocking findings; run verification and technical smoke checks.

**Implementation:** [Feature Development Pipeline](./feature-development-pipeline.md)

During process-building, the human may still inspect engineering outputs to calibrate trust ([MANIFEST.md](../MANIFEST.md)).

### 3. Product validation / demo

The human reviews the **product**, not the code: observable user actions in Scribe (file/record → transcribe → summary → export/history as relevant).

| Step | Focus |
|------|--------|
| Supervisor QA (pipeline) | Does the approved slice behave as specified before commit? |
| Product validation / demo (this cycle) | Did the increment deliver expected user value? Should direction change? |

### 4. Engineering retrospective

Separate from product validation. Analyze review-cycle count, defects, rework, scope creep, failed verification, and expensive AI-role behavior.

### 5. Product retrospective

Did the user receive meaningful value? Did assumptions in PRODUCT, ROADMAP, or scenarios change? Should planned work be postponed?

### 6. Continuous analytics

Primary dimensions: task completion, elapsed time, AI resource use. Secondary: human effort, review loops, defects, rework, abandoned work.

Distinguish **observed facts** from **AI estimates**. Measurement does not replace Product Owner decisions.

### 7. Process evolution

Adjust roles, handoffs, or gates based on recurring friction — not every minor inconvenience. Major process changes need human approval.

### 8. Grooming and next-priority selection

Re-evaluate candidates using validation, retrospectives, analytics, and updated risks. Input to the next planning cycle.

---

## Three feedback loops

### Product loop

**Question:** What should be built next?

**Inputs:** product validation, product retrospective, [PRODUCT.md](../../PRODUCT.md), [ROADMAP.md](../../ROADMAP.md), scenarios.

### Engineering loop

**Question:** How can approved work be delivered more reliably?

**Inputs:** implementation, review, QA, defects, rework.

### Organization / process loop

**Question:** How should the AI organization itself change?

**Inputs:** role performance, handoff failures, resource use, repeated friction.

---

## Human role

### Responsible for

- product vision and priorities;
- approval of the next slice;
- product validation / demo (product review — not code review);
- supervisor QA execution on observable behavior;
- accepting delivered value or requesting AI fixes;
- approving commits;
- approving major process changes.

### Must not

- Hand-edit code or documentation in the repository;
- Clear review findings by patching the working tree;
- Silent commits or silent product-direction changes;
- Weaken the local-only / no-content-logging promise without explicit decision.

### Role separation

| Role | Who |
|------|-----|
| Implementation | Cursor (AI) |
| Engineering review | Codex (AI) |
| Product review / supervisor QA / commit approval | Human |

See [docs/MANIFEST.md](../MANIFEST.md) experimental hard rule.

---

## Cycle output

Durable outputs such as: shipped or rejected increment; Product Owner notes; retrospectives; analytics summary; updated roadmap candidates; context for next planning. These belong in the iteration ledger and state files, not only in chat.

Only update documentation when understanding or behavior actually changes.

---

## Stop and continuation conditions

- current product goal achieved;
- Product Owner changes or cancels the goal;
- time or token budget exhausted;
- further work has lower expected value than pause;
- blockers require human input.

A single commit is not necessarily completion of a product goal.

---

## Relation to the feature-development pipeline

| Layer | Document | Responsibility |
|-------|----------|----------------|
| **Product cycle (this doc)** | [ai-product-development-cycle.md](./ai-product-development-cycle.md) | Direction, wrapper, demo, retrospectives, analytics, grooming |
| **Engineering delivery** | [feature-development-pipeline.md](./feature-development-pipeline.md) | Bounded prompts, implementation, review, triage, supervisor QA, commit |

| Need | Skill / doc |
|------|-------------|
| Next slice | [roadmap-planner](../../.ai/skills/roadmap-planner.md) |
| Orchestration | [feature-manager](../../.ai/skills/feature-manager.md) |
| Implementation prompt | [cursor-implementation-prompt](../../.ai/skills/cursor-implementation-prompt.md) |
| Independent review | [codex-review](../../.ai/skills/codex-review.md) |
| Triage | [review-triage](../../.ai/skills/review-triage.md) |
| Manual QA plan | [supervisor-qa](../../.ai/skills/supervisor-qa.md) |
| Commit preparation | [commit-manager](../../.ai/skills/commit-manager.md) |
| Skill index | [`.ai/skills/README.md`](../../.ai/skills/README.md) |

---

## Reusable vs product-specific

| Reusable across projects | Specific to Scribe |
|--------------------------|--------------------|
| Cycle sequence and three feedback loops | Vision and local-only meeting-notes promise |
| Human as Product Owner; specialized AI roles | [PRODUCT.md](../../PRODUCT.md), [ROADMAP.md](../../ROADMAP.md), scenarios |
| Plan → implement → independent review → QA → commit | pywebview bridge, MLX Whisper/LM, ScreenCaptureKit recorder |
| Analytics dimensions | Privacy logging rules, Apple Silicon-only constraints |
| Process evolution from measured friction | Concrete packaging and model-catalog constraints |

---

## Evolution note

Prefer evidence from repeated cycles over theoretical completeness.

When process changes are accepted, update this document, [README.md](./README.md), and relevant skills under [`.ai/skills/`](../../.ai/skills/).
