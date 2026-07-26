# Cursor Implementation Prompt

## Purpose

Generate a strict, iteration-bounded prompt for Cursor to implement an approved Scribe roadmap slice. One shippable slice per cycle.

---

## Invocation

```
Use cursor-implementation-prompt.
```

(or via `Use feature-manager.` after human approves the slice)

---

## Automatic Context Loading

| Document | Purpose |
|----------|---------|
| [PRODUCT.md](../../PRODUCT.md) | Relevant vision / non-goals |
| [ROADMAP.md](../../ROADMAP.md) | Iteration reference |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Layers |
| [LOCAL_DATA.md](../../LOCAL_DATA.md) | If settings/history/state touched |
| [AI_PIPELINE.md](../../AI_PIPELINE.md) | If pipeline touched |
| [DECISIONS.md](../../DECISIONS.md) | Relevant ADRs |
| [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) | If permissions/logging/network touched |
| [TESTING.md](../../TESTING.md) | Verification baseline |
| [docs/scenarios/](../../docs/scenarios/) | If user-facing flow touched |
| [AGENTS.md](../../AGENTS.md) | Hard constraints |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Approved active iteration and current phase |
| [`.ai/state/debt.md`](../state/debt.md) | Relevant accepted/deferred debt |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Approved scope and prior handoffs |
| Approved roadmap recommendation | In/out of scope |
| Latest implementation summary | Current gaps |

---

## Preconditions

- Human approved a bounded roadmap slice
- Active iteration ledger and `.ai/state/current-cycle.json` exist
- Slice fits one review cycle

---

## Responsibilities

- Fill every Output Contract section — no empty placeholders
- Explicit In scope / Out of scope
- Scribe-appropriate verification commands
- Require final response format from Cursor
- Remind: do not commit unless asked; do not log meeting content; sync bridge types
- Require Cursor to report the exact implementation summary needed for the ledger

---

## Non-responsibilities

- Does not implement, approve scope, review, or commit
- Does not combine unrelated roadmap items

---

## Output Contract

```markdown
=========================================
CONTEXT
=========================================

Scribe — local macOS Apple Silicon transcription + notes app.
<Where this iteration fits.>

=========================================
DOCUMENTS TO READ
=========================================

- AGENTS.md
- PRODUCT.md — <sections>
- ARCHITECTURE.md — <layers>
- AI_PIPELINE.md / LOCAL_DATA.md / DECISIONS.md / SECURITY-PRIVACY.md — <if applicable>
- docs/scenarios/<name>.md — <if applicable>
- TESTING.md — relevant smoke rows
- ROADMAP.md — <reference only>
- .ai/state/current-cycle.json — active phase and approved scope
- .ai/state/debt.md — relevant accepted/deferred debt
- docs/iterations/<active-ledger>.md — approved scope and handoffs

=========================================
CURRENT STATE
=========================================

<What exists. Last slice. Known gaps.>

=========================================
GOAL
=========================================

<One clear outcome.>

=========================================
IN SCOPE
=========================================

- ...

=========================================
OUT OF SCOPE
=========================================

- ...
- Cloud sync / remote AI APIs / telemetry
- Unrelated ROADMAP items

=========================================
BACKEND REQUIREMENTS
=========================================

- <Api methods, transcriber/summarizer/recorder/history/settings>
- Background threads for heavy work
- Log metadata only
- Or: no backend changes

=========================================
FRONTEND REQUIREMENTS
=========================================

- <UI / api.ts / vite-env.d.ts sync>
- Or: no frontend changes

=========================================
NATIVE / PACKAGING REQUIREMENTS
=========================================

- <AudioRecorder / scripts — or none>
- Do not run full build-dist unless this slice is packaging-related

=========================================
UX REQUIREMENTS
=========================================

- <status, cancel, errors, permissions honesty>

=========================================
DATA / PRIVACY REQUIREMENTS
=========================================

- settings must not store transcripts/summaries
- temp recording cleanup if ingest touched
- no transcript/summary logging

=========================================
DOCUMENTATION REQUIREMENTS
=========================================

- <PRODUCT / AI_PIPELINE / LOCAL_DATA / DECISIONS / scenarios / TESTING — only if behavior changes>
- Or: no doc changes

=========================================
VERIFICATION
=========================================

Run and report:

- [ ] `(cd frontend && npm run build)` if frontend/TS touched
- [ ] `./scripts/run-dev.sh` smoke for affected flow
- [ ] `USE_VITE_DEV=0 ./scripts/run-dev.sh` if production UI packaging of frontend matters
- [ ] Recording / ML / log privacy checks from TESTING.md if those layers touched
- [ ] Packaging scripts only if packaging-related (`./scripts/build.sh` or `./scripts/build-dist.sh`)

=========================================
FINAL RESPONSE FORMAT
=========================================

Report:

1. **Files created/changed**
2. **Behavior implemented**
3. **Assumptions made**
4. **Verification results**
5. **Remaining work**
6. **Documentation changes**
7. **Ledger update details** — summary fields the agent manager should record

Do not commit unless explicitly asked.
```

---

## Human Checkpoints

Human approval of the roadmap slice is **required** before generating this prompt.

---

## Guidelines

- One iteration, one prompt
- Out of scope is mandatory
- Verification is mandatory
- Docs only when behavior changes
- If docs and request conflict, stop and report
