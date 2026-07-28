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
| PP-2026-07-28-006 | Speakers overlap: user voice hard to hear under remote | `2026-07-28-recording-mix-sync` | Supervisor QA | Product / listening | Dual-path speakers QA passed 2026-07-29; keep open only if PO later reports mic-only overlap still buried. | Low | product-analyst / roadmap-planner | Only if PO reports C still bad after dual-path | open |
| PP-2026-07-29-002 | SpeexDSP offline AEC did not cancel speaker bleed (correct mic←system) | `2026-07-28-recording-mix-aec-spike` | Supervisor QA | Engineering / library | Spike tool OK (~150× RT); no audible cancel; mix_aec≈mix_plain. Do **not** ship Speex as default. WebRTC AEC3 only if Ideal returns to AEC+mix (backup to dual-path). | High | product-analyst / roadmap-planner | Only if PO reopens AEC integrate | open |
| PP-2026-07-29-003 | Show current audio input and output devices in the UI | `2026-07-29-recording-mix-dual-path` | Supervisor QA | UX / product | After dual-path QA: PO wants visible mic input + speaker/headphones output so route/mic choice is understandable (incl. headset-with-mic cases). | Medium | product-analyst / roadmap-planner | Next Record/UX planning after dual-path ships | open |
| PP-2026-07-29-004 | Clarify / optionally prefer headset mic when a headset is default output | `2026-07-29-recording-mix-dual-path` | Supervisor QA | Product question | Today Record uses macOS **default input** (`AVCaptureDevice.default`). Headset mic is used only if macOS made it the default mic — not guaranteed by headphone output alone. Tied to `PP-2026-07-29-003`. | Medium | product-analyst / roadmap-planner | With PP-003 or dedicated mic-selection slice | open |

## Closed / Converted

| ID | Title | Converted to | Closed by | Notes |
| --- | --- | --- | --- | --- |
| PP-2026-07-27-001 | Summary language default = system language; move control into Processing options | `2026-07-27-summary-language-ux` | commit-manager prep 2026-07-27 | Shipped in summary-language UX slice |
| PP-2026-07-28-004 | Clean meeting mix (no doubled remote / broken transcript) | `2026-07-29-recording-mix-dual-path` | iteration-retrospective 2026-07-29 | Ideal P0 met on tested routes; commit `c13dd58` |
| PP-2026-07-28-005 | Speakers: fixed-delay remote double remains (bleed) | `2026-07-29-recording-mix-dual-path` | iteration-retrospective 2026-07-29 | Cured by speakers mic-only finalize |
| PP-2026-07-28-007 | Headphones: mic quiet vs system in mix | `2026-07-29-recording-mix-dual-path` | iteration-retrospective 2026-07-29 | Headphones QA passed with level-match |
| PP-2026-07-29-001 | Dual-path Record finalize | `2026-07-29-recording-mix-dual-path` | iteration-retrospective 2026-07-29 | Shipped `c13dd58`; QA 4 modes pass |
