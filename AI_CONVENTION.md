# AI Development System Convention

This document records the product convention behind this repository's AI-organization experiment.

Scribe is the application being built. The broader product being designed here is the **AI development system**: a set of roles, workflows, records, and gates that can replace routine work normally done by developers, reviewers, QA assistants, release assistants, and product-operations support.

This is not a claim that an AI team magically knows what the human wants. The human remains the product author, Product Owner, supervisor, and final approver. The system exists to reduce the amount of routine execution and coordination the human must perform.

---

# Core Product Thesis

The goal is not a better coding prompt.

The goal is an **AI engineering organization** that can carry a small product iteration from approved scope to commit-ready state while preserving:

- human ownership of product direction;
- independent review;
- observable QA;
- durable decision history;
- measurable cost;
- controlled scope;
- explicit approval before irreversible steps.

The system is successful when the human spends most effort on:

- deciding what matters;
- accepting or rejecting product behavior;
- clarifying product intent;
- approving commits and major process changes.

The system is not successful if the human still has to:

- manually patch code or docs;
- reconstruct iteration history from chat;
- remember accepted debt;
- police every role transition by hand;
- repeatedly explain the same repository invariants;
- perform routine engineering review that a specialized AI role could perform.

---

# What The System Can Replace

The target is routine, bounded work that current AI tools can realistically perform with verification:

- implementation of approved slices;
- code review against explicit architecture and product constraints;
- review triage and fix-prompt generation;
- manual QA plan generation;
- release and commit preparation;
- backlog comparison and iteration planning support;
- process analytics and retrospectives;
- debt tracking;
- workflow hygiene checks.

The target is not replacement of product authorship.

The system must not pretend to own:

- product vision;
- final priority calls;
- acceptance of user value;
- privacy promise changes;
- major roadmap direction;
- commit approval.

---

# Human Role

The human is not an engineer inside this experiment.

The human acts as:

- customer;
- Product Owner;
- product reviewer;
- supervisor QA executor;
- process direction owner;
- commit approver.

The human may describe requirements, accept or reject behavior, defer debt, request an AI fix, and approve commits.

The human must not hand-edit durable code or documentation in the repository. If something needs changing, an AI agent makes the change.

---

# AI Organization Model

The system should not collapse into one general-purpose agent that plans, implements, reviews, and accepts its own work.

Specialization exists because accountability matters:

- planning must not review its own plan;
- implementation must not approve its own implementation;
- review must not decide product value;
- QA must validate observable behavior, not source code;
- commit preparation must not bypass review or human approval.

Roles can evolve, but role boundaries must stay explicit.

---

# Current Strength

This repository already has a strong initial process:

- a manifest for product/process principles;
- an AI product development cycle;
- an engineering feature pipeline;
- role-specific skills for planning, implementation prompts, review, triage, QA, and commit preparation;
- scenario documents as acceptance references;
- Scribe-specific invariants for local-only processing, logging, platform scope, and bridge contracts.

That is enough to run controlled iterations.

It is not yet enough to make the AI organization reliably self-improving.

---

# Current Gap

The process is mostly procedural. It says how to conduct an iteration.

The next stage is to make the system stateful and measurable. It should know:

- which iteration is active;
- which scope was approved;
- which role produced which artifact;
- which findings are open;
- which Low findings were accepted or deferred;
- which QA checks passed or failed;
- how many review loops occurred;
- how much time and AI resource the iteration consumed;
- which failures repeated across iterations;
- what should change in the workflow next.

Without durable state, the system depends too much on chat context and human memory.

---

# Operating Standard

Every process improvement should be judged by one question:

> Does this reduce human routine effort or improve the quality of decisions in a later iteration?

If yes, it belongs in the system.

If no, it is bureaucracy.

---

# Relationship To Scribe

Scribe is the product under development and the proving ground for the AI development system.

The AI development system should become reusable outside Scribe by separating:

- reusable organization mechanics;
- product-specific constraints and goals;
- repository-specific engineering details.

Scribe-specific rules remain authoritative for this repository. Reusable process rules should be documented so they can later move into a product-independent layer.

