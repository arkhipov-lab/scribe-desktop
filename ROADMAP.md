# Roadmap

Forward-looking ideas for Scribe. **Not a commitment** — order and scope may change. Agents should not implement these unless explicitly asked.

## Suggested priority

1. **Summary presets + additional instructions + summary length** — high value, limited app restructuring  
2. **Editable results + export** — everyday workflow polish  
3. **Local history** — sessions without cloud  
4. Everything else below

---

## P1 — Summary controls

Today the summary prompt is fixed in `backend/summarizer.py` (Overview / Decisions / Action items / Open questions), and length is only tuned per build profile (`summary_max_tokens` / `summary_merge_tokens` in `profile_config.py`). One UI language drives both Whisper and the summarizer.

### Configurable summary presets

Modes such as:

- Meeting notes (current default shape)
- Action items only
- Executive summary
- Customer interview
- Lecture / research notes
- Raw cleaned transcript

### Additional instructions (not a free-form system prompt)

UI field that the backend mixes into `_single_prompt` / `_chunk_prompt` / `_merge_prompt`, e.g.:

- highlight risks  
- keep it as short as possible  
- format like a Slack message  
- keep technical terms in English  

Avoid letting users fully replace the system prompt so smaller local models stay on-rails.

### Persist preferences locally

Example path:

```text
~/Library/Application Support/Scribe/settings.json
```

Store at least:

- last transcript language  
- last summary language (once split — see below)  
- selected summary preset  
- additional instructions  
- summary length preference  
- auto-summary on/off  

Still local-only; no sync. See [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md).

### Summary length control

UI presets that scale tokens relative to the build profile:

- Short  
- Normal  
- Detailed  

### Separate transcript language vs summary language

Allow e.g. transcribe in Russian, summarize in English (and the reverse). Whisper language and summary output language should be independent controls.

### Technical shape (when implementing P1)

- [ ] Represent presets as data, e.g. `SummaryPreset(id, label, sections, instruction)` instead of hard-wiring section logic only inside prompt helpers  
- [ ] Optional markdown post-process: drop duplicate headings, ensure expected sections, empty sections → localized “None”, then optional checklist UI  
- [ ] Keep advanced model knobs (Whisper/summary model, chunk size, raw token caps) behind an **Advanced** panel — easy to tank performance otherwise  

---

## P2 — Editable results & export

- [ ] Edit transcript and summary in-app before copy/export  
- [ ] Export `.md` and `.txt` (PDF optional later)  
- [ ] `.srt` / `.vtt` once timestamps exist  
- [ ] Partial copy actions: Copy transcript / Copy summary / Copy action items  
- [ ] Dedicated Action items view — parse the markdown section into a task list  

---

## P3 — Local session history

On-disk only (no cloud):

- [ ] Recent sessions with date, file name, languages, transcript, summary  
- [ ] Optional path to a saved audio copy when the user exported one  
- [ ] Open / delete / re-summarize from history  

---

## UX (general)

- [ ] Clearer first-run onboarding (permissions order, model download progress, Lite vs Standard)  
- [ ] Richer progress for long files (phase + rough percent where feasible)  
- [ ] Better empty / error / cancel states and retry affordances  
- [ ] Keyboard shortcuts for record, transcribe, copy  
- [ ] Optional appearance aligned with system (without flattening the current visual identity)  
- [ ] In-app link to log folder / “copy diagnostics” (metadata only)  
- [ ] Explicit offline indicator once models are cached  
- [ ] Side-by-side transcript ↔ summary navigation  

---

## Models & advanced settings

- [ ] Safe preset picker (e.g. tiny / small / medium) with RAM warnings  
- [ ] Heuristic Lite vs Standard suggestion from reported memory  
- [ ] Advanced: Whisper model, summary model, chunk size, output tokens (hidden by default)  

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
- [ ] CI building Lite + Standard on arm64 runners  
- [ ] Reproducible build attestations (profile, commit, Python tag)  

---

## Reliability & tests

- [ ] Unit tests for path validation, profiles, language normalization, presets  
- [ ] Headless smoke for Api state machine (no ML)  
- [ ] Optional integration harness with tiny fixture audio  
- [ ] Memory regression checks for Lite on 8 GB–class machines  
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
