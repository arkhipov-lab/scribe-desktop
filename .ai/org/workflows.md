# Reusable Workflow

Reusable iteration flow:

```text
product-analyst
  -> roadmap-planner
  -> human approval
  -> feature-manager / implementation prompt
  -> implementation
  -> codex-review
  -> review-triage
  -> supervisor-qa
  -> human QA decision
  -> commit-manager
  -> human commit approval
  -> iteration-retrospective
  -> next planning input
```

## Durable State

Every approved iteration needs:

- a ledger under `docs/iterations/`;
- current phase and gates in `.ai/state/current-cycle.json`;
- accepted/deferred debt and planned process work in `.ai/state/debt.md`;
- product follow-ups / wishes in `.ai/state/product-followups.md` (global curated register; ledger holds per-iteration capture notes).

## Gates

- No implementation without approved scope.
- No supervisor QA without clean review/triage.
- No commit preparation without QA passed or explicitly skipped.
- No commit with unresolved High or Medium findings.
- No accepted/deferred Low without explicit human decision.
- No forbidden artifacts staged.
- No commit without explicit human approval.

Run the cycle status and cycle validator commands defined by the repo validation adapter (`.ai/repo/validation.md`): status when resuming work; validator after state edits, before supervisor QA, and before commit preparation.

