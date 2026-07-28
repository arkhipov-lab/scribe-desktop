# Manifest

This document is the constitution of the Scribe repository.

It is not a product brief, not a technical design, and not a how-to guide.
It states the principles that must remain true even when tools, roles, and code change.

**Audience:** future maintainers, contributors, AI agents, and future versions of this project.

---

# Why this project exists

This repository exists for two goals at once:

1. **Build Scribe** — a real personal macOS (Apple Silicon) app that turns meeting audio into on-device transcripts and useful notes.
2. **Research and evolve an AI-assisted software development process** — a living system for how humans and specialized AI roles ship software together.

Both goals are equally important.

The product is not a pretext for the process.
The process is not a side project attached to the product.
Each must remain valuable on its own, and each must improve the other.

---

# Vision

The long-term goal is not a better coding assistant.

The goal is an **AI engineering organization**: specialized roles that plan, implement, review, validate, and release — while a human remains Product Owner.

Large software products are discovered through many iterations.
They are not generated from one perfect specification.

Therefore this organization optimizes for:

- rapid feedback;
- independent engineering judgment;
- continuous product steering.

Not for one-shot code generation.

A single general-purpose agent that plans, builds, reviews, and accepts its own work collapses accountability.
Specialization exists so that judgment is independent, responsibility is narrow, and product authority stays human.

Code generation is a means.
Judgment about *what* to build, *whether* it worked, and *what to do next* remains human.

---

# Product decisions and engineering decisions

This separation is central.

## Product decisions

Owned by the human:

- vision
- priorities
- iteration acceptance
- roadmap evolution
- user value
- privacy promise changes

## Engineering decisions

Gradually owned by specialized AI roles (with human checkpoints while trust is earned):

- implementation
- architecture within accepted constraints
- reviews
- QA preparation
- release assistance

The long-term goal is not to remove the human.
The goal is to move routine engineering decisions to AI while keeping product ownership human.

If a question changes *what* the product should become, it is a product decision.
If a question changes *how* an approved outcome is delivered, it is an engineering decision.

Scribe’s non-negotiables (local-only processing, Apple Silicon only, no transcript/summary logging) are product constraints — agents must not “engineer around” them.

---

# Human role

## Experimental hard rule: no hand-written repo edits

In this repository’s AI-organization experiment, the **human does not write or edit code or docs by hand**.

| Human may | Human must not |
| --- | --- |
| Act as customer / Product Owner | Edit application code directly |
| Describe requirements and priorities | “Quick-fix” review findings in the working tree |
| Run supervisor QA / product review on the running app | Patch markdown or process docs by hand (ask an AI agent instead) |
| Accept, reject, or defer results | Bypass AI roles by committing hand-made changes |
| Request an AI agent to implement or fix | Mix product review with engineering code review |
| Explicitly approve commits | Auto-approve or silent-commit |

Any durable change to code or documentation is performed by an **AI agent**. The human steers with requirements, acceptance, and approval — not keystrokes in the repo.

## What the human owns

- Product vision ([PRODUCT.md](../PRODUCT.md))
- Priorities ([ROADMAP.md](../ROADMAP.md))
- Product validation and demo feedback
- Supervisor QA execution (observable product behavior)
- Acceptance or rejection of iterations
- Explicit approval of commits
- Evolution of the development process itself (direction; edits still via AI)
- Major documentation / process change **decisions**

**Do not overclaim autonomy.** Human approval is required for product direction, major docs/process changes, and every commit. That approval is not a license for the human to implement the change personally.

---

# Trust evolves

Engineering **judgment** moves from humans to specialized AI roles gradually. Trust is earned through repeated reliable cycles.

What does **not** wait for trust: the no-hand-edits rule above. Even while calibrating the organization, the human participates as Product Owner / supervisor / commit approver — inspecting outputs, rejecting work, and requesting AI fixes — not as a secondary implementer.

---

# AI organization

AI here is not one general assistant that does everything.

It is an organization of **specialized roles**, each with a narrow responsibility.
Roles exist so that planning is not judging its own plan, implementation is not reviewing its own work, and review is not deciding product priority.

Examples of role families:

- Planning — propose bounded next value ([`.ai/skills/roadmap-planner.md`](../.ai/skills/roadmap-planner.md))
- Implementation — deliver only the approved slice
- Review — independent critique against product and architecture truth
- QA — validate that the user-visible outcome holds
- Release / commit — prepare durable history only after explicit human approval

The exact roster may change.
The principle does not: **narrow responsibility, clear interfaces, independent evolution, human checkpoints for product decisions and commits.**

Operational docs: [docs/workflows/](workflows/), skills: [`.ai/skills/`](../.ai/skills/).

The broader convention for the AI development system is recorded in [AI_CONVENTION.md](../AI_CONVENTION.md). Its process roadmap is recorded in [AI_SYSTEM_ROADMAP.md](../AI_SYSTEM_ROADMAP.md).

---

# Product over implementation

The primary optimization target is **product value**, not code volume or technical elegance.

Every iteration should answer one question:

> What new value does the Scribe user receive?

If the answer is unclear, the iteration is not ready.

---

# Iterative development

Software evolves through many small iterations, not large leaps of faith.

Each iteration is a closed loop:

1. Planning
2. Implementation
3. Review
4. Product validation
5. Retrospective

The next iteration is chosen **after** reviewing the previous one —
not by blindly walking a checklist written months earlier.

[ROADMAP.md](../ROADMAP.md) is a **hypothesis**, not a contract. [PRODUCT.md](../PRODUCT.md) and [docs/scenarios/](scenarios/) inform prioritization.

---

# The process as a product

The development process is treated as something that can be designed, judged, and improved.

Valid deliverables of the process product include:

- a new workflow;
- a better review loop;
- a new AI role;
- a better quality gate;
- better orchestration.

A better process that ships better product value is progress.
A clever process that does not improve product value is not.

---

# How the process is judged

Process evolution asks questions such as:

- Did recent work increase product value?
- How long did iterations take?
- How much AI resource did they consume?
- How much human effort was required?
- How many review cycles were needed?
- Were privacy or local-only invariants put at risk?

Measurement informs judgment. It does not replace Product Owner decisions.

Iteration-level memory should be durable, not reconstructed from chat. Use [docs/workflows/iteration-ledger.md](workflows/iteration-ledger.md) as the expected record shape when an iteration needs persistent process history.

---

# Reusable layers

Work separates into layers so that most of the system can outlive any single product.

## Reusable

- engineering roles and review gates
- orchestration
- quality expectations
- analytics of the process itself

## Product-specific (Scribe)

- vision and non-goals ([PRODUCT.md](../PRODUCT.md))
- roadmap ([ROADMAP.md](../ROADMAP.md))
- scenarios ([docs/scenarios/](scenarios/))
- domain knowledge (local audio → transcript → notes, pywebview, MLX, ScreenCaptureKit)

**Engineering should be reusable.
Product should be replaceable.**

---

# Long-term vision

> The human behaves like a Product Owner, not like an engineer.

Nearly all human effort should go to:

- deciding what to build;
- evaluating product value;
- steering the product and the privacy promise.

Engineering decisions should gradually become the responsibility of specialized AI roles under human product authority — **without** silent commits or silent product-direction changes.

---

# Evolution

This document is expected to evolve.

When the dual goals of product and process change how we work, this Manifest should change with them — with human approval for major revisions.

Until then, treat this file as the constitution of an evolving AI engineering organization building Scribe.
