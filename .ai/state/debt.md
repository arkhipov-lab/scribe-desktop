# AI Development System Debt And Planned Work Register

Durable register for accepted/deferred debt and planned process work.

Record debt here when a review finding, QA failure, retrospective issue, or process gap is explicitly accepted or deferred instead of fixed in the current iteration. Do not rely on chat history to remember debt.

Keep debt separate from planned process roadmap work:

- **Debt** is an accepted/deferred issue from review, QA, retrospective, or a known process failure.
- **Planned process work** is future system improvement that was intentionally out of scope, and it does not carry review severity or block the current commit gate.
- High and Medium review findings must not be accepted as debt before commit unless the pipeline is explicitly changed by the human.

## Open Debt

| ID | Title | Source iteration | Severity | Type | Reason accepted or deferred | Owner role | Revisit condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Closed Debt

| ID | Title | Source iteration | Closed by | Notes |
| --- | --- | --- | --- | --- |

## Planned Process Work

| ID | Title | Source iteration | Priority | Type | Why planned | Owner role | Start condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-2026-07-26-001 | Cycle validator | `2026-07-26-ai-memory-foundation` | P2 | process_roadmap | Mandatory memory should exist before gates are enforced by scripts. | feature-manager | Start of enforceable gates work | done |
| P-2026-07-26-002 | Structured role output schemas | `2026-07-26-ai-memory-foundation` | P2 | process_roadmap | Markdown remains the primary record until validator scripts or other machine consumers exist. | feature-manager | First validator/schema consumer is introduced | planned |
| P-2026-07-26-003 | Retrospective role | `2026-07-26-ai-memory-foundation` | P1 | process_roadmap | Durable memory is needed before retrospectives can reliably compare iteration evidence. | feature-manager | After at least one complete ledger-backed iteration | done |
| P-2026-07-27-001 | Product analyst role | `2026-07-27-backlog-intelligence` | P2 | process_roadmap | Roadmap planning should use scenarios, debt, metrics, and retrospectives, not roadmap order alone. | feature-manager | Backlog intelligence stage | done |
| P-2026-07-27-002 | Reusable process layer split | `2026-07-27-reusable-layer` | P3 | process_roadmap | Process mechanics should be portable without carrying Scribe-specific product/repo assumptions. | feature-manager | Reusable layer stage | done |
| P-2026-07-27-003 | Full reusable package extraction | `2026-07-27-reusable-layer` | P3 | process_roadmap | Initial adapters exist; full extraction should wait until another repository actually consumes the process. | feature-manager | First cross-repo adoption attempt | planned |
