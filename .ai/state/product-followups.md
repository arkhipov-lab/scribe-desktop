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
| PP-2026-07-28-004 | Clean meeting mix (no doubled remote / broken transcript) | chat 2026-07-28 | Product bug / initiative | Major | In-app Record: remote duplicated via speakers→mic bleed (+ former track skew). Phase 0+1 sync shipped. AEC Speex spike: cancel not proven. **Current Ideal:** dual-path finalize (`PP-2026-07-29-001`) in [recording-clean-mix.md](../../docs/initiatives/recording-clean-mix.md). | Critical | product-analyst / roadmap-planner → implementer | Plan `recording-mix-dual-path` after aec-spike ships | open |
| PP-2026-07-28-005 | Speakers: fixed-delay remote double remains (bleed) | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / initiative | After Phase 1 sync, amix still doubles remote (bleed on mic + system). Dual-path mic-only on speakers is the PO fix candidate (`PP-2026-07-29-001`). | High | product-analyst / roadmap-planner | With `recording-mix-dual-path` | open |
| PP-2026-07-28-006 | Speakers overlap: user voice hard to hear under remote | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / listening | Matrix C under **amix**: user buried. On **mic-only** speakers path, PO heard user≈remote — dual-path may cure; re-check C after dual-path. | Medium | product-analyst / roadmap-planner | With dual-path QA matrix C | open |
| PP-2026-07-28-007 | Headphones: mic quiet vs system in mix | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / listening | Headphones branch of dual-path explicitly level-matches mic toward remote (`PP-2026-07-29-001`). | Medium | product-analyst / roadmap-planner | With `recording-mix-dual-path` headphones path | open |
| PP-2026-07-29-001 | Dual-path Record finalize: speakers→mic-only; headphones→mic+system with mic level match | `2026-07-28-recording-mix-aec-spike` | Supervisor QA / PO proposal | Product / Ideal (initiative Phase 3′) | **PO Ideal (2026-07-29):** no headphones → **mic-only**; headphones → **mic+system**, normalize mic amplitude toward remote. Speakers QA: mic-only best for Whisper; amix causes double. Headphones: mic-only would miss remote. Eng: macOS route detection + fallbacks. Tracks `PP-004`. | Critical | product-analyst / roadmap-planner | Next slice `recording-mix-dual-path` after aec-spike commit | open |
| PP-2026-07-29-002 | SpeexDSP offline AEC did not cancel speaker bleed (correct mic←system) | `2026-07-28-recording-mix-aec-spike` | Supervisor QA | Engineering / library | Spike tool OK (~150× RT); no audible cancel; mix_aec≈mix_plain. Do **not** ship Speex as default. WebRTC AEC3 only if Ideal returns to AEC+mix (backup to dual-path). | High | product-analyst / roadmap-planner | Only if PO reopens AEC integrate | open |

## Closed / Converted

| ID | Title | Converted to | Closed by | Notes |
| --- | --- | --- | --- | --- |
| PP-2026-07-27-001 | Summary language default = system language; move control into Processing options | `2026-07-27-summary-language-ux` | commit-manager prep 2026-07-27 | Shipped in summary-language UX slice; close on commit/ship |
