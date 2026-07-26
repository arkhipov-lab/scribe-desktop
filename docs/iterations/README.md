# Iterations

Durable iteration memory for the AI development system.

Create one ledger file here for every approved product or process iteration:

```text
docs/iterations/YYYY-MM-DD-<short-slug>.md
```

The ledger records what actually happened: approved scope, role handoffs, review findings, QA outcome, verification, debt, metrics, retrospective notes, and commit link.

Do not rely on chat history as the source of truth for an active or completed iteration. Future agents should be able to open this folder, `.ai/state/current-cycle.json`, and `.ai/state/debt.md` to understand the current process state.

