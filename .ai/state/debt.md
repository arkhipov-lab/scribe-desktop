# AI Development System Debt And Planned Work Register

Durable register for accepted/deferred debt and planned process work.

Record debt here when a review finding, QA failure, retrospective issue, or process gap is explicitly accepted or deferred instead of fixed in the current iteration. Do not rely on chat history to remember debt.

Keep categories separate:

- **Debt** is an accepted/deferred issue from review, QA, retrospective, or a known process failure.
- **Planned process work** is future AI-organization improvement that was intentionally out of scope.
- **Product follow-ups / wishes** do **not** belong here — use [`.ai/state/product-followups.md`](./product-followups.md).
- High and Medium review findings must not be accepted as debt before commit unless the pipeline is explicitly changed by the human.
- Low findings may be auto-fixed, or on a second+ review loop accepted/deferred as Low debt under the review-triage auto-fix policy (with reason and revisit condition), without requiring human involvement when the Low is not product-facing.

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
| P-2026-07-26-002 | Structured role output schemas | `2026-07-26-ai-memory-foundation` | P2 | process_roadmap | Markdown remains primary for most roles; current-cycle schema consumer shipped in `2026-07-27-current-cycle-schema-handoff`; review-findings schema + validator consumer shipped in `2026-07-28-review-findings-reconciliation`. Remaining: metrics / retrospective / product-analysis schemas when a concrete consumer needs them. | feature-manager | First validator/schema consumer introduced (done); add next schema only with a consumer | planned |
| P-2026-07-26-003 | Retrospective role | `2026-07-26-ai-memory-foundation` | P1 | process_roadmap | Durable memory is needed before retrospectives can reliably compare iteration evidence. | feature-manager | After at least one complete ledger-backed iteration | done |
| P-2026-07-27-001 | Product analyst role | `2026-07-27-backlog-intelligence` | P2 | process_roadmap | Roadmap planning should use scenarios, debt, metrics, and retrospectives, not roadmap order alone. | feature-manager | Backlog intelligence stage | done |
| P-2026-07-27-002 | Reusable process layer split | `2026-07-27-reusable-layer` | P3 | process_roadmap | Process mechanics should be portable without carrying Scribe-specific product/repo assumptions. | feature-manager | Reusable layer stage | done |
| P-2026-07-27-003 | Full reusable package extraction | `2026-07-27-reusable-layer` | P3 | process_roadmap | Initial adapters exist; full extraction should wait until another repository actually consumes the process. | feature-manager | First cross-repo adoption attempt | planned |
| P-2026-07-27-004 | Implementation-runner / handoff skill | `2026-07-27-pipeline-operator-ux` | P2 | process_roadmap | Separate implementation execution from feature-manager: accept handoff, wait for summary, record into ledger/current-cycle, mark review-ready. | feature-manager | After pipeline-operator-ux ships | planned |
| P-2026-07-27-005 | Validate product-analyst PO-readable output on next real cycle | `2026-07-27-pipeline-operator-ux` | P2 | process_validation | Contract is recommendation-first; confirm one real `Use product-analyst.` run leads with recommendation, keeps evidence in appendix, avoids excessive internal process detail. | product-analyst | Next planning cycle after this ships | done |
| P-2026-07-27-006 | Measure human review-fix involvement after auto-fix policy | `2026-07-27-pipeline-operator-ux` | P2 | process_metrics | Compare human decisions / review-loop interruptions before vs after auto-fix. Measured in `2026-07-27-editable-transcript` retrospective: R1/R2/R4 auto-fixed without asking; only product-facing R3 asked PO (Decision B). Confirms auto-fix reduces routine-Low interrupts while preserving product-facing asks. | iteration-retrospective | Next shipped iteration retrospective after this | done |
| P-2026-07-27-007 | Automate implementation → review → triage loop | `2026-07-27-pipeline-operator-ux` | P3 | process_roadmap | Docs now describe deterministic orchestration; actual Cursor execution and multi-agent looping remain a later autonomy milestone. | feature-manager | After handoff skill (P-004) and stable auto-fix evidence | planned |
| P-2026-07-27-008 | Hide cursor-implementation-prompt in PO-facing indexes / future console | `2026-07-27-pipeline-operator-ux` | P3 | process_ux | Skill is marked internal/specialized; future PO console/UI should not show it as a normal command. | feature-manager | When PO console / operator UI work starts | planned |
| P-2026-07-27-009 | Validator checks for implementation phase consistency | `2026-07-27-pipeline-operator-ux` | P2 | process_roadmap | Detect impossible states (e.g. review-ready without implementation summary; handoff/phase illegal combos). Delivered in `2026-07-27-current-cycle-schema-handoff`: schema + handoff consistency, `review_gate=clean` requires `latest_implementation_summary`, `pending_re_review`→`codex-review`. | feature-manager | After P-004 or next validator hardening slice | done |
| P-2026-07-29-001 | New backend modules must be listed in build.sh / build-dist.sh (or switch to copy-all) | `2026-07-29-recording-mix-dual-path` | P2 | process_hardening | Explicit `cp` lists omitted `output_route.py` → `.app` launched then crashed (`ModuleNotFoundError` / `kLSNoExecutableErr`); blocked Supervisor QA until hotfix. | feature-manager / implementation-agent | Next backend-module slice or packaging checklist update | planned |
