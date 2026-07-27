# Product Follow-Ups And Wishes

Durable register for Product Owner wishes, QA follow-ups, and future product opportunities.

These items are **not** review debt and do **not** block the current commit gate unless the Product Owner explicitly changes the current iteration scope.

## What belongs here

- Product Owner wishes from Supervisor QA (including “pass with follow-ups”)
- Deferred product ideas from planning
- Future UX / product opportunities
- Product questions that need later validation

## What does not belong here

- High / Medium review findings (fix or explicit debt in `.ai/state/debt.md`)
- Accepted engineering / process debt (`.ai/state/debt.md`)
- Planned process / AI-organization work (`.ai/state/debt.md` Planned Process Work)
- Implementation tasks already approved for the current slice

## Open Follow-Ups

| ID | Title | Source iteration | Source phase | Type | Why captured | Product value | Suggested owner | Revisit condition | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PP-2026-07-27-002 | Reduce language selectors in direct flow; auto-detect transcript language from audio | `2026-07-27-separate-languages` | Supervisor QA | Product opportunity | Long-term desire to remove language pickers from the main path; needs UX/ML feasibility investigation. | Medium | product-analyst / roadmap-planner | After PP-001 ships or when PO prioritizes hands-off language UX | open |

## Closed / Converted

| ID | Title | Converted to | Closed by | Notes |
| --- | --- | --- | --- | --- |
| PP-2026-07-27-001 | Summary language default = system language; move control into Processing options | `2026-07-27-summary-language-ux` | commit-manager prep 2026-07-27 | Shipped in summary-language UX slice; close on commit/ship |
