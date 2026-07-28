# Testing

Scribe does not yet have a large automated test suite. Validate changes with the smoke checks below. Prefer the smallest check that covers what you touched.

## Automated / scripted checks available today

| Check | How |
| --- | --- |
| Frontend typecheck + production build | `(cd frontend && npm run build)` (`tsc --noEmit` + Vite) |
| Dist runtime smoke | Built into `scripts/build-dist.sh` (import mlx stack, mel spectrogram, optional torch absence) |
| Mach-O min OS | `scripts/assert-macho-minos.sh` (invoked by dist build) |

There is no CI matrix documented in-repo yet. Treat the checklists here as the source of truth for agents and humans.

---

## Manual smoke: development app

Run:

```bash
./scripts/run-dev.sh
```

### A. Shell & bridge

1. Window opens with the Scribe UI.
2. No persistent “Desktop bridge is not available” error.
3. Transcript language control populates. Summary language lives under Processing options (defaults from UI locale).
4. Toolbar / actions buttons, language selects, and segmented controls share the same height as icon buttons; product textareas are not user-resizable.
5. Log file appears/updates at `~/Library/Logs/Scribe/app.log`.

### B. File ingest

1. **Select** a short `.m4a` / `.mp3` / `.wav` / `.mp4` / `.mov`.
2. **Drop** a supported file onto the window (native drop).
3. Unsupported extension shows a clear error (not a crash).
4. Choosing a new file clears prior transcript/summary as expected.

### C. Transcription

1. Pick transcript language (try at least `en` and one other you care about). Optionally open Processing options and set a different **summary language**.
2. Click **Transcribe**.
3. First run may download the Whisper model — wait; status should show loading/transcribing.
4. Transcript appears; elapsed timer behaves.
5. **Cancel** mid-run returns to a sane idle/ready state.
6. Confirm the log contains path/status lines but **not** the transcript body.
7. Edit the transcript as plain text; confirm edits survive a short wait and appear in Copy/Export; regenerating summary uses the edited text. Transcribe again fully replaces the transcript. See [docs/scenarios/editable-transcript.md](docs/scenarios/editable-transcript.md).
8. Open the **Copy** menu: Copy transcript / Copy summary / Copy action items work for available content and are disabled when missing; copy works from either results tab. See [docs/scenarios/partial-copy.md](docs/scenarios/partial-copy.md).

### D. Summary

1. After a transcript exists, summary should run when auto-summary is on (or via Generate/Regenerate).
2. Change preset / length / additional instructions and regenerate — output shape should follow the preset.
3. With a different summary language than transcript language (set under Processing options), regenerate and confirm notes follow the summary-language intent.
4. With auto-summary off, transcription completes without starting summary; Generate still works.
5. Preferences survive relaunch (`~/Library/Application Support/Scribe/settings.json`), including transcript language and summary language (when seeded or overridden).
6. Cancel summary does not corrupt the existing transcript.
7. Log must not contain summary text or additional-instructions body.
8. After editing the transcript, summary does not auto-restart; manual Generate/Regenerate overwrites the summary from the current transcript.
9. Open the **Copy** menu: **Copy summary** copies the full notes; **Copy action items** is enabled only when a non-empty Action items section exists (disabled when the heading is missing or empty). See [docs/scenarios/partial-copy.md](docs/scenarios/partial-copy.md).

### E. Recording

1. Click **Record**; grant Mic + Screen & System Audio if prompted.
2. After granting Screen Recording, **quit and relaunch** the app, then record again.
3. Speak + play system audio (e.g. a video call or local media).
4. Stop → a file is ready for transcription.
5. Confirm a WAV under `~/Library/Caches/Scribe/recordings/` during/after capture.
6. Selecting another file deletes the previous owned temp recording.
7. **Mix sync QA (speakers):** remote speech should not appear as a multi-second delayed second copy. Optional: `SCRIBE_KEEP_RAW_RECORDING=1` via `open --env SCRIBE_KEEP_RAW_RECORDING=1 ./dist/Scribe.app` (preferred for TCC), then after stop split tracks with `ffprobe` / `ffmpeg -map 0:a:0` and `0:a:1` on the kept `.m4a`. Check app.log for `DIAG: session_start` / drop counts (metadata only). Headphones should be no worse than before.
8. **AEC spike (dev only, not product):** `SCRIBE_AEC_SPIKE=1 python3 scripts/aec-spike.py --input <dual.m4a> --outdir /tmp/scribe-aec-spike` after `brew install speexdsp`. Speex cancel was **not** proven in QA 2026-07-29 — tool remains for experiments. See [DEVELOPMENT.md](DEVELOPMENT.md).
9. **Clean-mix Ideal (not shipped yet):** dual-path finalize — speakers/no headphones → mic-only; headphones → mic+system with mic level match. Track [recording-clean-mix](docs/initiatives/recording-clean-mix.md) / `PP-2026-07-29-001`. Do not fail current Record for Ideal until that slice ships.

### F. ffmpeg

- Dev/local: `check_ffmpeg` / transcription fails clearly if Homebrew ffmpeg is missing.
- Dist: transcription uses bundled `Resources/bin/ffmpeg` without Homebrew on the target Mac.

---

## Manual smoke: model defaults

| Mac class | Expect on first launch |
| --- | --- |
| Strong (M3+ and enough RAM) | Whisper medium, summary 3B, auto-summary on |
| Weak (M2− or &lt;12 GB RAM) | Whisper small, summary 1.5B, auto-summary off |

Confirm values under **Processing options** and that they persist in `settings.json`.

---

## Manual smoke: local `.app`

```bash
./scripts/build.sh
open "dist/Scribe.app"
```

1. App launches from Finder.
2. Still works only while the project `.venv` path remains valid.
3. Repeat a short transcribe after launch.

---

## Manual smoke: dist package (when packaging changed)

```bash
MAKE_DMG=1 ./scripts/build-dist.sh
```

1. Build finishes with smoke steps green (including post-prune).
2. `dist/Scribe.app` size is in the expected ballpark (~hundreds of MB for the app; models separate).
3. DMG name includes `VERSION` (e.g. `Scribe-1.2.0.dmg`); `Info.plist` / `get_app_info().version` match.
4. Open the DMG, drag to Applications (or run from `dist/` directly).
5. Gatekeeper: right-click → Open works.
6. On a **clean** user (or after clearing HF cache if testing download): first Transcribe downloads models, second run is offline-capable.
7. Recording permissions still prompt via Info.plist usage strings.
8. Confirm bundled ffmpeg is **arm64** and minos ≤ 14 (`otool` / dist asserts).

Skip full dist builds for pure UI copy tweaks; run frontend build + `run-dev.sh` instead.

---

## Regression matrix (quick)

Use this when unsure what to retest:

| You changed… | Must retest |
| --- | --- |
| `frontend/src/*` | Bridge still works; UI build; core click paths |
| `backend/app.py` API | Matching TS types; get_state polling; cancel paths |
| `transcriber.py` | File validate + short transcribe + cancel + logs |
| `summarizer.py` | Short + long transcript (chunk path) + cancel |
| `recorder.py` / `AudioRecorder.swift` | Record permissions + mix + temp cleanup |
| `profile_config.py` / dist scripts | App name / identity; dist smoke |
| `model_catalog.py` / `hardware.py` | Model pickers + first-launch defaults |
| `logger.py` | Still no transcript/summary in log file |
| Packaging scripts | Dist build + launch on a second machine if possible |

---

## Failure triage

1. Read `~/Library/Logs/Scribe/app.log`.
2. Confirm arch (`arm64`), ffmpeg, and `native/build/AudioRecorder`.
3. For OOM-like failures on 8 GB: switch to Small / 1.5B and shorter audio.
4. For Gatekeeper issues: unsigned ad-hoc builds need Open Anyway — not a code bug.

When adding automated tests later, prefer fast unit tests around path validation, model id normalization, and language normalization before full ML integration tests.
