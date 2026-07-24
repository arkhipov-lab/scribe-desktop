# Testing

Scribe does not yet have a large automated test suite. Validate changes with the smoke checks below. Prefer the smallest check that covers what you touched.

## Automated / scripted checks available today

| Check | How |
| --- | --- |
| Frontend typecheck + production build | `(cd frontend && npm run build)` (`tsc --noEmit` + Vite) |
| Dist runtime smoke | Built into `scripts/build-dist.sh` (import mlx stack, mel spectrogram, optional torch absence) |
| Mach-O min OS | `scripts/assert-macho-minos.sh` (invoked by dist build) |
| Profile helper | `profile_config.reset_profile_cache()` exists for tests; no pytest suite checked in yet |

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
3. Language dropdown populates.
4. Log file appears/updates at `~/Library/Logs/Scribe/app.log`.

### B. File ingest

1. **Select** a short `.m4a` / `.mp3` / `.wav` / `.mp4` / `.mov`.
2. **Drop** a supported file onto the window (native drop).
3. Unsupported extension shows a clear error (not a crash).
4. Choosing a new file clears prior transcript/summary as expected.

### C. Transcription

1. Pick language (try at least `en` and one other you care about).
2. Click **Transcribe**.
3. First run may download the Whisper model — wait; status should show loading/transcribing.
4. Transcript appears; elapsed timer behaves.
5. **Cancel** mid-run returns to a sane idle/ready state.
6. Confirm the log contains path/status lines but **not** the transcript body.

### D. Summary

1. After a transcript exists, summary should run (auto and/or via regenerate if exposed).
2. Output has structured notes (overview / decisions / actions / open questions — localized headings when language matches).
3. Cancel summary does not corrupt the existing transcript.
4. Log must not contain summary text.

### E. Recording

1. Click **Record**; grant Mic + Screen & System Audio if prompted.
2. After granting Screen Recording, **quit and relaunch** the app, then record again.
3. Speak + play system audio (e.g. a video call or local media).
4. Stop → a file is ready for transcription.
5. Confirm a WAV under `~/Library/Caches/Scribe/recordings/` during/after capture.
6. Selecting another file deletes the previous owned temp recording.

### F. ffmpeg

- Dev/local: `check_ffmpeg` / transcription fails clearly if Homebrew ffmpeg is missing.
- Dist: transcription uses bundled `Resources/bin/ffmpeg` without Homebrew on the target Mac.

---

## Manual smoke: profiles

| Profile | How to run | Expect |
| --- | --- | --- |
| Standard | default, or `SCRIBE_PROFILE=standard` | Medium Whisper + 3B summary model ids in UI/info |
| Lite | `SCRIBE_PROFILE=lite ./scripts/run-dev.sh` | Small Whisper + 1.5B; lower peak RAM |

On 8 GB hardware, prefer Lite for full-pipeline smoke to avoid swap thrash.

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
PROFILE=lite MAKE_DMG=1 ./scripts/build-dist.sh
# or standard — slower / heavier models on first use
```

1. Build finishes with smoke steps green (including post-prune).
2. `dist/*.app` size is in the expected ballpark (~hundreds of MB for the app; models separate).
3. Open the DMG, drag to Applications (or run from `dist/` directly).
4. Gatekeeper: right-click → Open works.
5. On a **clean** user (or after clearing HF cache if testing download): first Transcribe downloads models, second run is offline-capable.
6. Recording permissions still prompt via Info.plist usage strings.
7. Confirm bundled ffmpeg is **arm64** and minos ≤ 14 (`otool` / dist asserts).

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
| `profile_config.py` / dist scripts | Both profiles’ app names + model ids; dist smoke |
| `logger.py` | Still no transcript/summary in log file |
| Packaging scripts | Dist build + launch on a second machine if possible |

---

## Failure triage

1. Read `~/Library/Logs/Scribe/app.log`.
2. Confirm arch (`arm64`), ffmpeg, and `native/build/AudioRecorder`.
3. For OOM-like failures on 8 GB: switch to Lite / shorter audio.
4. For Gatekeeper issues: unsigned ad-hoc builds need Open Anyway — not a code bug.

When adding automated tests later, prefer fast unit tests around path validation, profile loading, and language normalization before full ML integration tests.
