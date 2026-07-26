# AI Development System Roadmap

This roadmap is about the AI development system, not Scribe's user-facing feature roadmap.

Scribe remains the proving ground. The product goal here is a working AI organization that can replace routine development-team effort while keeping the human as Product Owner and final approver.

---

# Strategic Direction

Move from a documented workflow to a stateful, measurable, self-improving operating system for AI-assisted product development.

The immediate priority is not adding more agents. The priority is adding:

- durable memory;
- metrics;
- enforceable gates;
- retrospectives;
- debt tracking;
- process auditing;
- reusable process layers.

---

# P1 - Durable Iteration Memory

## Iteration ledger

Create a durable record for every product iteration.

Purpose:

- preserve approved scope;
- preserve handoffs between roles;
- preserve review findings and triage decisions;
- preserve supervisor QA result;
- preserve verification evidence;
- connect commits back to product intent;
- provide input for future roadmap planning.

Recommended artifact:

- `docs/iterations/YYYY-MM-DD-<slug>.md`, or
- `.ai/state/iterations/YYYY-MM-DD-<slug>.json` when machine validation becomes useful.

See [docs/workflows/iteration-ledger.md](docs/workflows/iteration-ledger.md).

## Current-cycle state

Track the current phase and gate status.

Purpose:

- prevent agents from skipping roadmap planning, review, QA, or approval;
- make the next allowed step obvious;
- reduce repeated context reconstruction.

Possible artifact:

- `.ai/state/current-cycle.json`

---

# P1 - Metrics And Retrospectives

## Iteration metrics

Record at least:

- elapsed time;
- agent turns;
- approximate token use where available;
- review loop count;
- High / Medium / Low finding counts;
- QA pass, fail, or skipped;
- human decisions required;
- shipped, rejected, or deferred outcome.

Separate observed facts from AI estimates.

## Retrospective role

Add an `iteration-retrospective` skill.

Responsibilities:

- analyze what created rework;
- identify weak prompts or missing context;
- detect repeated findings;
- decide whether docs, skills, gates, or tests should change;
- propose one or two process improvements only when evidence supports them.

Retrospective output should feed the next roadmap planning cycle.

---

# P1 - Debt Register

Accepted or deferred findings need their own durable register.

Purpose:

- stop accepted Low findings from disappearing;
- prevent repeated debate about already accepted debt;
- make revisit conditions explicit;
- separate product debt from engineering debt and process debt.

Possible artifact:

- `.ai/state/debt.md`, or
- `.ai/state/debt.json`

Minimum fields:

- title;
- source iteration;
- severity;
- type: product / engineering / process;
- reason accepted or deferred;
- owner role;
- revisit condition;
- status.

---

# P2 - Enforceable Gates

## Cycle validator

Add a lightweight validator that checks whether the next phase is allowed.

Examples:

- no implementation prompt without approved scope;
- no supervisor QA without clean review gate;
- no commit preparation without QA pass or explicit QA skip;
- no commit with unresolved High or Medium findings;
- no accepted Low without explicit human decision;
- no staged forbidden artifacts.

Possible artifacts:

- `scripts/ai-cycle-status.sh`
- `scripts/ai-cycle-validate.sh`

The first version can be simple and markdown-based. It should become stricter only when repeated failures justify it.

## Structured output contracts

Current skills use markdown templates. That is useful for humans, but weak for automation.

Future versions should define machine-readable schemas for:

- roadmap recommendation;
- implementation summary;
- review findings;
- triage decisions;
- QA outcome;
- commit preparation;
- retrospective;
- metrics.

---

# P2 - Process Audit

Add a `process-auditor` role that reviews the iteration process, not the code.

Responsibilities:

- detect excessive human involvement;
- detect unnecessary AI loops;
- detect recurring handoff failures;
- check whether scope control worked;
- check whether process changes are justified by evidence;
- flag ceremony that does not improve product value or reliability.

The process auditor should run after several iterations or after a failed / expensive iteration, not after every trivial change.

---

# P2 - Product Analytics And Backlog Intelligence

Add a `product-analyst` or `backlog-groomer` role.

Responsibilities:

- compare roadmap candidates by user value, effort, risk, and enablement;
- identify stale roadmap items;
- connect scenarios to roadmap gaps;
- separate product work from engineering and process debt;
- recommend whether the next iteration should build product value, reduce risk, or improve the AI development system itself.

This role supports the human Product Owner. It does not own product direction.

---

# P3 - Reusable Process Package

Split the process into layers so it can leave the Scribe repository later.

Target structure:

```text
.ai/org/
  roles/
  workflows/
  metrics/
  schemas/

.ai/product/
  invariants.md
  roadmap.md
  scenarios/

.ai/repo/
  stack.md
  validation.md
  forbidden-paths.md
```

Reusable:

- role boundaries;
- handoff contracts;
- review gates;
- iteration ledger;
- metrics;
- retrospective and audit process.

Product-specific:

- vision;
- roadmap;
- scenarios;
- acceptance criteria;
- privacy or platform promises.

Repo-specific:

- stack;
- commands;
- paths;
- build and test rules;
- forbidden artifacts.

---

# Success Signal

The AI development system is improving when a small iteration can move from approved product slice to commit-ready state with:

- no hand-written human repo edits;
- clear scope preservation;
- independent engineering review;
- product-facing QA;
- recorded human decisions;
- known cost;
- recorded debt;
- useful retrospective;
- a better-informed next planning step.

The system is failing when the human must reconstruct state, repeat standing rules, manually clear process gaps, or decide routine engineering questions that were already delegated.

