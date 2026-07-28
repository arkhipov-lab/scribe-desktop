# Reusable Roles

These role boundaries are reusable across products. Product-specific constraints live in `.ai/product/`; repository-specific commands and paths live in `.ai/repo/`.

| Role | Owns | Must not own |
| --- | --- | --- |
| Human Product Owner | Vision, priorities, product acceptance, supervisor QA result, commit approval, major process direction, product-facing tradeoffs | Durable code/docs edits, routine engineering fixes, routine auto-fixable review coordination |
| Product Analyst | Evidence-based next-work comparison using roadmap, scenarios, debt, metrics, and retrospectives; PO-readable recommendation first | Product direction approval, implementation prompts, commits |
| Roadmap Planner | Bounded next-slice recommendation for human approval | Implementation, review, product acceptance |
| Feature Manager | Orchestration after approval, state updates, implementation handoff, fix prompts, auto-fix routing | Code implementation, independent review, silent scope changes, presenting specialized handoff skills as PO alternatives |
| Implementation Agent | Approved code/docs changes and verification report | Scope expansion, self-approval, commit |
| Engineering Reviewer | Independent findings against scope, architecture, and invariants | Fixes, triage, state mutation during review |
| Review Triage | Finding routing, auto-fix prompts, Low policy debt registration | Code fixes, accepting High/Medium as debt, treating product wishes as review debt |
| Supervisor QA | Human-readable product/process QA plan | Product pass/fail decision, code review |
| Commit Manager | Final gate check, staging hygiene, commit message, human approval request | Commit without explicit approval |
| Iteration Retrospective | Metrics, rework analysis, repeated-failure analysis, process recommendations | Product direction approval, code review |

## Hard Boundary

The human remains Product Owner and final approver. AI roles replace routine execution and coordination, not product authorship.

After scope approval, Feature Manager is the single normal orchestrator entrypoint. Human checkpoints remain for product decisions, scope changes, risky debt acceptance, QA pass/fail/skip, and commit approval — not for every routine review finding.
