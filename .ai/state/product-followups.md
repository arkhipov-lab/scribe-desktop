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
| PP-2026-07-27-003 | Editable summary later without a full Markdown document editor | `2026-07-27-editable-transcript` | Planning | Product opportunity | PO deferred summary editing: Markdown WYSIWYG/raw-MD dual pane is off-goal; need a later approach that is not a document editor. | Medium | product-analyst / roadmap-planner | After editable transcript ships or when PO prioritizes summary correction UX | open |
| PP-2026-07-28-001 | Fix layout in Processing / settings panel | `2026-07-28-control-height-ux` | Supervisor QA | UX polish | QA noted settings panel layout feels broken/awkward after control-height pass; needs a dedicated layout fix. | Medium | product-analyst / roadmap-planner | Next UX polish planning or when PO prioritizes settings panel | open |
| PP-2026-07-28-002 | History sidebar spacing in fullscreen; consider fixed sidebar with show/hide | `2026-07-28-control-height-ux` | Supervisor QA | UX / layout | In fullscreen the sidebar sits too close to main content; PO suggests fixed sidebar with hide/show rather than tight static spacing. | Medium | product-analyst / roadmap-planner | Next shell/layout planning or when PO prioritizes chrome | open |
| PP-2026-07-28-003 | Remove focus/outline rings from controls (textarea, buttons) | `2026-07-28-control-height-ux` | Supervisor QA | UX polish | PO: controls show outlines; prefer no visible outlines (accessibility tradeoff to decide in planning). | Medium | product-analyst / roadmap-planner | Next UX polish planning; confirm a11y stance before shipping | open |
| PP-2026-07-28-004 | Clean meeting mix (no doubled remote / broken transcript) | chat 2026-07-28 | Product bug / initiative | Major | In-app Record: remote/system audio duplicated via speakers→mic (+ track skew); own voice OK. Ideal plan lives in initiative doc — not ROADMAP detail. Phase 0+1 sync shipped (QA pass w/ follow-ups); remaining = fixed-delay acoustic bleed → Phase 3 AEC. | Critical | product-analyst / roadmap-planner → implementer | Next planning: Phase 3 AEC spike/integrate per [docs/initiatives/recording-clean-mix.md](../../docs/initiatives/recording-clean-mix.md) | open |
| PP-2026-07-28-005 | Speakers: fixed-delay remote double remains (bleed) | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / initiative | After Phase 1 sync, double still audible (louder = clear duplicate); Δ does not grow with length; Whisper OK. Needs reference AEC (Phase 3). | High | product-analyst / roadmap-planner | When planning `recording-mix-aec-spike` / `recording-mix-aec` | open |
| PP-2026-07-28-006 | Speakers overlap: user voice hard to hear under remote | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / listening | Matrix C: same double as A; near-end buried when overlapping. Likely levels + bleed; Ideal after AEC/polish. | Medium | product-analyst / roadmap-planner | With AEC integrate or Phase 4 polish | open |
| PP-2026-07-28-007 | Headphones: mic quiet vs system in mix | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / listening | No double on headphones; mic level low relative to system. Phase 4 mix polish candidate. | Medium | product-analyst / roadmap-planner | Phase 4 `recording-mix-polish` | open |

## Closed / Converted

| ID | Title | Converted to | Closed by | Notes |
| --- | --- | --- | --- | --- |
| PP-2026-07-27-001 | Summary language default = system language; move control into Processing options | `2026-07-27-summary-language-ux` | commit-manager prep 2026-07-27 | Shipped in summary-language UX slice; close on commit/ship |
