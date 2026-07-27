# Reusable Workflow

Reusable iteration flow:

```text
product-analyst
  -> roadmap-planner
  -> human approval
  -> feature-manager          # sole normal post-approval entrypoint
    -> implementation prompt prepared (internal handoff)
    -> implementation pending
    -> implementation summary received
    -> review ready
  -> codex-review
  -> review-triage            # auto-fix policy
  -> supervisor-qa
  -> human QA decision
  -> commit-manager
  -> human commit approval
  -> iteration-retrospective
  -> next planning input
```

`cursor-implementation-prompt` is an internal/specialized handoff artifact generator used by feature-manager — not an alternative Product Owner-facing next step.

## Durable State

Every approved iteration needs:

- a ledger under `docs/iterations/`;
- current phase and gates in `.ai/state/current-cycle.json`;
- accepted/deferred debt and planned process work in `.ai/state/debt.md`;
- product follow-ups / wishes in `.ai/state/product-followups.md` (global curated register; ledger holds per-iteration capture notes).

Ledger/current-cycle should be able to record:

- implementation handoff prepared;
- implementation pending;
- implementation summary received;
- auto-fix pass generated / applied;
- Low findings auto-fixed;
- Low findings accepted/deferred without human involvement when policy allows;
- human involvement reason when human input was required.

## Gates

- No implementation without approved scope.
- No review while implementation is still pending (summary required).
- No supervisor QA without clean review/triage.
- No commit preparation without QA passed or explicitly skipped.
- No commit with unresolved High or Medium findings.
- Low findings: auto-fix or policy accept/defer per review-triage for **clearly non-product** items; **product-facing Lows must never be silently deferred** and need human judgment (when in doubt, ask).
- Product wishes are not review debt and do not block commit unless Product Owner re-scopes.
- No forbidden artifacts staged.
- No commit without explicit human approval.

Run the cycle status and cycle validator commands defined by the repo validation adapter (`.ai/repo/validation.md`): status when resuming work; validator after state edits, before supervisor QA, and before commit preparation.
