# Architectural Decision Records

Key decisions and their rationale for Scribe. When in doubt about *why* something is designed a certain way, check here first.

Format for new entries:

```
## Title
**Status:** Proposed | Accepted | Deprecated | Superseded
**Context:** What problem or question prompted this decision?
**Decision:** What was decided?
**Reason:** Why this approach over alternatives?
**Consequences:** Trade-offs and follow-up implications.
```

---

## Why Scribe is macOS Apple Silicon only

**Status:** Accepted

**Context:** Transcription and summary use Apple’s MLX stack. Packaging and the ScreenCaptureKit recorder assume modern macOS arm64.

**Decision:** Support **macOS on Apple Silicon (arm64) only**. No Windows, Linux, or Intel Mac targets.

**Reason:** MLX is the performance and packaging path that matches the product promise. Dual-arch or cross-OS support would multiply native helpers, ffmpeg bundles, and model backends without serving the current personal-utility goal.

**Consequences:**

- Scripts refuse non-arm64 hosts (`run-dev.sh`, dist builds)
- Agents must reject or gate x86_64 / non-macOS work unless product goals change
- See [SYSTEM-REQUIREMENTS.md](SYSTEM-REQUIREMENTS.md)

---

## Why processing is fully local

**Status:** Accepted

**Context:** Meeting audio and notes are sensitive. Cloud STT/LLM APIs are convenient but break the privacy promise.

**Decision:** Audio, transcripts, and summaries are processed **only on the local Mac**. No cloud transcription/summary upload; no accounts or team sync for core features.

**Reason:** Trust is the product differentiator. Users can run after models are cached without sending meeting content off-device.

**Consequences:**

- Network is expected mainly for one-time Hugging Face model download
- Do not add remote AI APIs for core features without an explicit product decision and docs overhaul
- Authoritative policy: [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md)

---

## Why React runs inside pywebview

**Status:** Accepted

**Context:** Need a modern UI without rewriting the desktop shell in SwiftUI, and without a browser-only app that cannot own local ML and filesystem safely.

**Decision:** Ship a React + Vite SPA inside **pywebview**, with Python owning the window and bridge.

**Reason:** Fast UI iteration, familiar web tooling, and a single Python process for MLX, ffmpeg, and recording orchestration.

**Consequences:**

- UI has no direct filesystem/ML access — only `window.pywebview.api`
- Bridge readiness and “Desktop bridge is not available” must be handled in UX
- See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Why the Python Api bridge owns filesystem and ML authority

**Status:** Accepted

**Context:** A WebView UI could be mistaken for a security boundary. Paths, permissions, and model loads must be centralized.

**Decision:** The Python `Api` class in `backend/app.py` is the authority for file paths, recording, transcription, summary, settings, and history. The React layer is UX only.

**Reason:** Keeps permissions, temp cleanup, logging policy, and ML lifecycle in one place; simplifies the local-only contract.

**Consequences:**

- New capabilities need new `Api` methods + matching `frontend/src/vite-env.d.ts` types
- Heavy work must run on background threads; UI polls `get_state`

---

## Why MLX Whisper and MLX LM are used

**Status:** Accepted

**Context:** Need high-quality on-device STT and summarization on Apple Silicon without shipping CUDA stacks.

**Decision:** Use **mlx-whisper** for transcription and **mlx-lm** (Qwen2.5 Instruct 4-bit variants) for summary.

**Reason:** Native Metal/MLX performance on arm64 Macs; fits the local-only product; aligns with hardware-tier defaults (small/medium Whisper, 1.5B/3B summary).

**Consequences:**

- Platform lock-in to Apple Silicon (accepted)
- First-run downloads into HF/MLX cache; RAM pressure requires memory release between stages

---

## Why model ids and token caps live in `backend/model_catalog.py`

**Status:** Accepted

**Context:** Scattering HF ids and token budgets across UI and scripts causes drift and unsafe experiments.

**Decision:** One runtime catalog in `backend/model_catalog.py`; hardware defaults in `backend/hardware.py`; UI consumes bridge lists/settings only.

**Reason:** Single source of truth for what users can pick; easier packaging and safer token budgets for map-reduce.

**Consequences:**

- Do not hard-code model ids or token caps in the React UI
- Catalog/docs updates belong together when options change

---

## Why summary uses map-reduce for long transcripts

**Status:** Accepted

**Context:** Long meetings exceed practical single-context summarization for the local models and token caps in use.

**Decision:** Short transcripts use a single pass; long transcripts use **chunk → summarize → merge** (map-reduce) in `backend/summarizer.py`.

**Reason:** Preserves useful notes without requiring a huge context window; cancel can occur between stages.

**Consequences:**

- More stages and status complexity; cooperative cancel is not mid-token
- Advanced knobs (chunk size, raw caps) stay gated — see [ROADMAP.md](ROADMAP.md)

---

## Why recording uses a Swift ScreenCaptureKit helper

**Status:** Accepted

**Context:** Users want mic **and** system audio (calls, local media) without installing virtual audio devices like BlackHole.

**Decision:** Ship a compiled Swift **AudioRecorder** helper using ScreenCaptureKit (+ AVFoundation), launched from Python and mixed with ffmpeg.

**Reason:** System audio capture on modern macOS requires this permission family; a small native helper keeps Python focused on orchestration.

**Consequences:**

- Microphone + Screen & System Audio permissions; restart after granting Screen Recording
- Video frames are **not** persisted — copy must stay honest
- Temp WAVs under `~/Library/Caches/Scribe/recordings/`

---

## Why logs exclude transcript and summary bodies

**Status:** Accepted

**Context:** Debug logs are the easiest place to accidentally leak meeting content to disk or support channels.

**Decision:** Logging allows paths, statuses, durations, model ids, and safe error metadata — **never** transcript/summary text (or additional-instructions bodies).

**Reason:** Matches the privacy promise; support can still triage with metadata and lengths.

**Consequences:**

- Agents and contributors must not “log the transcript for debugging”
- See [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) and [docs/scenarios/privacy-logging.md](docs/scenarios/privacy-logging.md)

---

## Why dist uses embedded Python instead of fully frozen PyInstaller

**Status:** Accepted

**Context:** Fully freezing MLX + dynamic imports + HF assets with PyInstaller is brittle on macOS.

**Decision:** Dist builds prefer a **relocatable embedded CPython** plus copied backend sources and bundled ffmpeg (`build-dist.sh`), not a single frozen binary as the primary ship path.

**Reason:** More reliable imports and native dylibs; still self-contained for sharing. Local `build.sh` may keep using project `.venv` for developer convenience.

**Consequences:**

- Dist app size is hundreds of MB before models; models still download once per machine
- Do not commit `dist/` or `.cache/`
- Details: [BUILDING.md](BUILDING.md)

---

## Why local history is filesystem-based

**Status:** Accepted

**Context:** Users need recent sessions without cloud sync or a database server.

**Decision:** Store sessions as folders under `~/Library/Application Support/Scribe/history/` (`meta.json`, `transcript.md`, `summary.md`, optional audio) plus a light `index.json`.

**Reason:** Transparent, user-inspectable, easy to delete; no SQLite/ORM surface for MVP-scale personal history.

**Consequences:**

- Documented in [LOCAL_DATA.md](LOCAL_DATA.md); not a relational schema
- Optional audio copy may skip very large files
- No multi-device sync (non-goal)

---

## Template for future decisions

Copy this block when adding a new decision:

```
## [Title]
**Status:** Proposed
**Context:**
**Decision:**
**Reason:**
**Consequences:**
```

---

## Related Documents

- [PRODUCT.md](PRODUCT.md) — product principles
- [ARCHITECTURE.md](ARCHITECTURE.md) — system structure
- [AI_PIPELINE.md](AI_PIPELINE.md) — processing pipeline
- [LOCAL_DATA.md](LOCAL_DATA.md) — on-disk and in-memory data
- [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) — privacy and logging authority
- [BUILDING.md](BUILDING.md) — packaging authority
