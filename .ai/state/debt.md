# AI Development System Debt And Planned Work Register

Durable register for accepted/deferred debt and planned process/product work.

Record debt here when a review finding, QA failure, retrospective issue, or process gap is explicitly accepted or deferred instead of fixed in the current iteration. Do not rely on chat history to remember debt.

Keep categories separate:

- **Debt** is an accepted/deferred issue from review, QA, retrospective, or a known process failure.
- **Planned process work** is future AI-organization improvement that was intentionally out of scope.
- **Planned product work** is a Product Owner follow-up captured from QA or planning so it is not lost before the next product-analyst / roadmap-planner cycle. It does not block the current commit gate.
- High and Medium review findings must not be accepted as debt before commit unless the pipeline is explicitly changed by the human.

## Open Debt

| ID | Title | Source iteration | Severity | Type | Reason accepted or deferred | Owner role | Revisit condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Closed Debt

| ID | Title | Source iteration | Closed by | Notes |
| --- | --- | --- | --- | --- |

## Planned Product Work

| ID | Title | Source iteration | Priority | Type | Why planned | Owner role | Start condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PP-2026-07-27-001 | Summary language default = system language; move control into Processing options | `2026-07-27-separate-languages` | P2 | product_followup | QA pass feedback: primary flow should not force summary-language choice; default from system/UI language; advanced users change it under Processing options. Technically feasible now; explicitly out of this iteration. | product-analyst / roadmap-planner | Next product planning after separate-languages ships | planned |
| PP-2026-07-27-002 | Reduce language selectors in direct flow; auto-detect transcript language from audio | `2026-07-27-separate-languages` | P3 | product_followup | QA pass feedback: long-term desire to remove language pickers from the main path; Whisper-style auto language detect for transcript; summary language handled via PP-001 pattern. Needs product slice + ML/UX investigation. | product-analyst / roadmap-planner | After PP-001 or when PO prioritizes hands-off language UX | planned |

## Planned Process Work

| ID | Title | Source iteration | Priority | Type | Why planned | Owner role | Start condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-2026-07-26-001 | Cycle validator | `2026-07-26-ai-memory-foundation` | P2 | process_roadmap | Mandatory memory should exist before gates are enforced by scripts. | feature-manager | Start of enforceable gates work | done |
| P-2026-07-26-002 | Structured role output schemas | `2026-07-26-ai-memory-foundation` | P2 | process_roadmap | Markdown remains the primary record until validator scripts or other machine consumers exist. | feature-manager | First validator/schema consumer is introduced | planned |
| P-2026-07-26-003 | Retrospective role | `2026-07-26-ai-memory-foundation` | P1 | process_roadmap | Durable memory is needed before retrospectives can reliably compare iteration evidence. | feature-manager | After at least one complete ledger-backed iteration | done |
| P-2026-07-27-001 | Product analyst role | `2026-07-27-backlog-intelligence` | P2 | process_roadmap | Roadmap planning should use scenarios, debt, metrics, and retrospectives, not roadmap order alone. | feature-manager | Backlog intelligence stage | done |
| P-2026-07-27-002 | Reusable process layer split | `2026-07-27-reusable-layer` | P3 | process_roadmap | Process mechanics should be portable without carrying Scribe-specific product/repo assumptions. | feature-manager | Reusable layer stage | done |
| P-2026-07-27-003 | Full reusable package extraction | `2026-07-27-reusable-layer` | P3 | process_roadmap | Initial adapters exist; full extraction should wait until another repository actually consumes the process. | feature-manager | First cross-repo adoption attempt | planned |
