# Building & distribution

How to produce macOS `.app` bundles and DMGs for Scribe. Prefer this doc over packing every packaging detail into the README.

**Build machine:** Apple Silicon (arm64) macOS. Dist builds target **macOS 14 Sonoma+**.

## Choose the right script

| Script | Output | Relocatable? | When to use |
| --- | --- | --- | --- |
| `./scripts/build.sh` | `dist/Scribe.app` | **No** — launches via project `.venv` | Daily local Finder launch on *this* machine |
| `./scripts/build-dist.sh` | `.app` + optional `.dmg` | **Yes** — embedded CPython + deps + ffmpeg | Sharing with others / moving the app |
| `./scripts/build-dist-standard.sh` | Standard profile wrapper | Yes | Quality build (medium Whisper + 3B summary) |
| `./scripts/build-dist-lite.sh` | Lite profile wrapper | Yes | 8 GB–friendly build (small Whisper + 1.5B summary) |

Do **not** commit `dist/` or `.cache/`.

---

## Local `.app` (`build.sh`)

```bash
./scripts/build.sh
open "dist/Scribe.app"
```

What it does:

- Ensures `.venv` + Python deps
- Builds the frontend (`npm run build`)
- Generates `assets/AppIcon.icns` from root `icon.png` (1024×1024)
- Compiles `native/launcher.c` → Mach-O stub
- Assembles `dist/Scribe.app` that still depends on the repo’s `.venv`

Keep the repo folder after building. If you move the project, rebuild.

Optional experimental PyInstaller artifact:

```bash
WITH_PYINSTALLER=1 ./scripts/build.sh
```

A fully frozen MLX + PyInstaller bundle is brittle (native dylibs, dynamic imports, HF assets). Prefer `build-dist.sh` for anything you ship.

---

## Self-contained dist (`build-dist.sh`)

Requires Homebrew tooling on the **build** machine (ffmpeg resolution helpers, icon tools, etc.). The **shipped** app embeds a compatible ffmpeg binary — end users do not need Homebrew.

### Profiles

| | Standard | Lite |
| --- | --- | --- |
| Command | `./scripts/build-dist-standard.sh` or `PROFILE=standard ./scripts/build-dist.sh` | `./scripts/build-dist-lite.sh` or `PROFILE=lite ./scripts/build-dist.sh` |
| App name | **Scribe** | **Scribe Lite** |
| Bundle ID | `local.scribe.app` | `local.scribe.lite.app` |
| Artifacts | `dist/Scribe.app`, `dist/Scribe-<version>.dmg` | `dist/Scribe Lite.app`, `dist/Scribe-Lite-<version>.dmg` |
| Whisper | medium | small |
| Summary | Qwen2.5-3B-Instruct-4bit | Qwen2.5-1.5B-Instruct-4bit |

Hardware guidance: [SYSTEM-REQUIREMENTS-STANDARD.md](SYSTEM-REQUIREMENTS-STANDARD.md), [SYSTEM-REQUIREMENTS-LITE.md](SYSTEM-REQUIREMENTS-LITE.md).

### Useful knobs

| Variable | Default | Meaning |
| --- | --- | --- |
| `PROFILE` | `standard` | `standard` or `lite` |
| `MAKE_DMG` | `1` | Set `0` to skip DMG creation |
| `FORCE_RUNTIME` | `0` | Rebuild cached embedded Python + site-packages |
| `PYTHON_BIN` | `python3` | Host Python for the *build helper* venv |
| `MACOSX_DEPLOYMENT_TARGET` | `14.0` | Compile / wheel compatibility floor |
| `MAX_MINOS_MAJOR` | `14` | Mach-O min OS assert for shipped binaries |
| `FFMPEG_SRC` | auto | Override ffmpeg binary used for bundling |

App / DMG version comes from the repo-root [`VERSION`](VERSION) file (semver). It is written into `Info.plist` (`CFBundleShortVersionString` / `CFBundleVersion`), baked into the bundle as `Resources/VERSION`, and used in the DMG filename (`Scribe-1.2.3.dmg`, `Scribe-Lite-1.2.3.dmg`).

See [CONTRIBUTING.md](CONTRIBUTING.md) for how `VERSION` is bumped from conventional commits.

### Local release builds (after merge bump)

On merge into `main`, if the version bump created a new `VERSION`/tag, `scripts/release-build-local.sh` builds both profiles into `dist/`:

- `Scribe.app` / `Scribe Lite.app`
- `Scribe-X.Y.Z.dmg` / `Scribe-Lite-X.Y.Z.dmg`

Default: background (log `.cache/release-build.log`). Foreground: `SCRIBE_RELEASE_BUILD_FG=1`. Skip builds: `SKIP_RELEASE_BUILD=1`.

Optional CI (`.github/workflows/release-build.yml`) can still publish the same artifacts to a GitHub Release when a `v*` tag is pushed.

Examples:

```bash
MAKE_DMG=0 PROFILE=lite ./scripts/build-dist.sh
FORCE_RUNTIME=1 ./scripts/build-dist.sh
./scripts/release-build-local.sh
```
### What the dist build embeds

Inside `Something.app/Contents/`:

```text
MacOS/Scribe              Mach-O launcher
MacOS/AudioRecorder       ScreenCaptureKit helper
Resources/backend/        Python app sources + profile.json
Resources/frontend/dist/  Built UI
Resources/python/         Relocatable CPython 3.13 + runtime deps
Resources/bin/ffmpeg      Bundled ffmpeg (+ libs as needed)
Resources/AppIcon.icns
Resources/profile.json    Baked standard|lite config
```

Models are **not** pre-baked. On first transcription/summary on each machine they download into the Hugging Face cache, then work offline.

### Runtime construction & pruning

1. Download astral-sh **python-build-standalone** (cached under `.cache/dist/`).
2. `pip install -r requirements-runtime.txt`.
3. Reinstall MLX-related wheels pinned to `macosx_14_0_arm64` so hosts on newer macOS do not ship too-new wheels.
4. Attempt to **uninstall torch** (MLX path should not need it); restore if smoke fails.
5. `scripts/prune-runtime.sh` drops caches, tests, packaging junk.
6. Smoke-import `mlx`, `mlx_whisper`, `mlx_lm`, `webview`, etc., and run a tiny mel-spectrogram check.
7. Bundle ffmpeg via `ensure-compatible-ffmpeg.sh` + `bundle-ffmpeg.sh`.
8. Assert Mach-O `minos` ≤ deployment target (`assert-macho-minos.sh`).
9. Ad-hoc codesign + clear quarantine attrs (not Developer ID notarization).

First dist build is slow; later builds reuse `.cache/dist/runtime` unless `FORCE_RUNTIME=1` or requirements change.

---

## Giving the app to someone else

1. Build with `build-dist-*.sh` (not `build.sh`).
2. Share the DMG.
3. On the other Mac:
   - Open DMG → drag app to Applications
   - First launch: right-click → **Open**, or **Privacy & Security → Open Anyway** (unsigned / ad-hoc signed)
   - Grant **Microphone** and **Screen & System Audio Recording**, then restart
   - Expect a one-time model download on first Transcribe / Summary

---

## Icon

Source: repo-root `icon.png` (1024×1024).  
Generated: `assets/AppIcon.icns` (via `sips` + `iconutil`). Iconset intermediates are gitignored.

---

## Why not a single frozen binary?

MLX stacks pull native Metal dylibs and dynamic imports; Hugging Face assets resolve at runtime. Embedding an interpreter + pruning unused torch has been more reliable than a pure PyInstaller onefile for this project.

---

## Related

- [DEVELOPMENT.md](DEVELOPMENT.md) — local loop
- [TESTING.md](TESTING.md) — packaging smoke checks
- [SECURITY-PRIVACY.md](SECURITY-PRIVACY.md) — permissions strings baked into Info.plist
