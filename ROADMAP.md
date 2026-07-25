# Roadmap

Forward-looking ideas for Scribe. **Not a commitment** — order and scope may change. Agents should not implement these unless explicitly asked.

This roadmap is a **hypothesis**. Prioritize using [PRODUCT.md](PRODUCT.md) and [docs/scenarios/](docs/scenarios/) when they conflict with checkbox order; propose roadmap edits for human approval rather than shipping low-value polish. Planning skill: [`.ai/skills/roadmap-planner.md`](.ai/skills/roadmap-planner.md).

## Suggested priority

1. **Summary presets + additional instructions + summary length** — high value, limited app restructuring  
2. **Editable results + export** — everyday workflow polish  
3. **Local history** — sessions without cloud  
4. Everything else below

---

## P1 — Summary controls

Most of this shipped (presets, length, additional instructions, auto-summary, local `settings.json`). Remaining:

### Separate transcript language vs summary language

Allow e.g. transcribe in Russian, summarize in English (and the reverse). Whisper language and summary output language should be independent controls.

### Technical leftovers

- [ ] Optional markdown post-process: drop duplicate headings, ensure expected sections, empty sections → localized “None”, then optional checklist UI  
- [ ] Keep advanced model knobs (chunk size, raw token caps) behind an **Advanced** panel — easy to tank performance otherwise  
- [ ] Separate transcript language vs summary language

---

## P2 — Editable results & export

- [ ] Edit transcript and summary in-app before copy/export  
- [x] Export `.md` and `.txt` (PDF optional later)  
- [ ] `.srt` / `.vtt` once timestamps exist  
- [ ] Partial copy actions: Copy transcript / Copy summary / Copy action items  
- [ ] Dedicated Action items view — parse the markdown section into a task list  

---

## P3 — Local session history

On-disk only (no cloud):

- [x] Recent sessions with date, file name, languages, transcript, summary  
- [x] Optional audio copy into history (skipped if file is very large)  
- [x] Open / delete / re-summarize from history  
- [x] Local LLM title after transcription (updates sidebar)  

---

## UX (general)

- [ ] Clearer first-run onboarding (permissions order, model download progress, weak vs strong defaults)  
- [ ] Richer progress for long files (phase + rough percent where feasible)  
- [ ] Better empty / error / cancel states and retry affordances  
- [ ] Keyboard shortcuts for record, transcribe, copy  
- [ ] Optional appearance aligned with system (without flattening the current visual identity)  
- [ ] In-app link to log folder / “copy diagnostics” (metadata only)  
- [ ] Explicit offline indicator once models are cached  
- [ ] Side-by-side transcript ↔ summary navigation  

---

## Models & advanced settings

- [x] Safe preset picker (e.g. small / medium Whisper, 1.5B / 3B summary) with local persistence  
- [x] Heuristic defaults from reported memory + Apple chip generation (M3+ strong; M2− / low RAM weak)  
- [ ] Advanced: chunk size, raw output tokens (hidden by default)

---

## Audio & transcription quality

- [ ] Local speaker diarization when feasible on Apple Silicon  
- [ ] Timestamps / segment navigation in the transcript  
- [ ] On-device noise-robust preprocessing options  
- [ ] Pause/resume recording; chapter markers while recording  
- [ ] Better UX for very long meetings (chunked transcription)  

---

## Packaging & distribution

- [ ] Developer ID signing + notarization  
- [ ] Privacy-preserving update feed (e.g. Sparkle), optional  
- [ ] Smaller DMGs / further runtime pruning  
- [x] Single Scribe DMG (runtime model selection)  
- [ ] CI building on arm64 runners  
- [ ] Reproducible build attestations (commit, Python tag)  

---

## Reliability & tests

- [ ] Unit tests for path validation, model ids, language normalization, presets  
- [ ] Headless smoke for Api state machine (no ML)  
- [ ] Optional integration harness with tiny fixture audio  
- [ ] Memory regression checks for Small / 1.5B on 8 GB–class machines  
- [ ] Crash reporting that strips transcript content by design  

---

## Platform (long-term / speculative)

- [ ] Sandboxed Mac App Store variant (ScreenCaptureKit + entitlements TBD)  
- [ ] Intel / other platforms — **out of scope** unless MLX alternatives and product goals change  

## Explicit non-goals (for now)

- Cloud accounts, team sync, or server-side transcription  
- Shipping user audio to third-party APIs  
- Meeting bots that join Zoom / Meet / Teams as a participant  
- Windows / Linux parity  

---

When an item ships, move the behavior into the relevant docs (`README`, `ARCHITECTURE`, `SECURITY-PRIVACY`, etc.) instead of leaving stale checkboxes here.
