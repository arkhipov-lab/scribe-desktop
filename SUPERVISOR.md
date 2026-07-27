# Supervisor Guide

You are the human supervisor for Scribe.

Your role is not to implement the product. Your role is to decide what should be built, verify whether it works as a product, and approve durable changes.

Scribe runs an AI-organization experiment:

> No hand-written repository edits by the human.

All code and documentation changes are made by AI agents.

---

## Your Role

You are:

- customer;
- Product Owner;
- product reviewer;
- supervisor QA;
- commit approver.

You are not:

- implementation engineer;
- code fixer;
- routine code reviewer;
- release automation;
- emergency patch author.

---

## Hard Rule

Do **not** edit code or documentation by hand in this repository.

You may:

- describe requirements;
- choose priorities;
- approve or reject scope;
- run the app and test observable behavior;
- report QA pass/fail;
- accept or defer product-facing Low findings as debt (routine cheap Lows are auto-fixed by AI);
- request an AI fix;
- explicitly approve commits.

You must not:

- patch files manually;
- "quick-fix" review findings in the editor;
- clear Low findings yourself;
- stage unrelated artifacts;
- commit without review and QA gates;
- silently weaken Scribe's local-only / privacy promise.

If you want to change one line, ask an AI agent to change that one line.

---

## Standard Cycle

### 1. Start With Planning

Ask:

```text
Use roadmap-planner.
```

The planner should recommend a small product slice and explain:

- goal;
- user value;
- in scope;
- out of scope;
- risks;
- verification;
- opportunity cost.

Approve, modify, or reject the slice.

Example:

```text
Одобряю Option A. Scope оставить как предложено. Сформируй implementation prompt.
```

---

### 2. Generate The Implementation Prompt

Ask:

```text
Use feature-manager.
```

Feature-manager is the sole normal post-approval entrypoint. It prepares the internal Cursor implementation handoff, records that implementation is pending, and continues the cycle after the implementer returns a summary. Do not choose between feature-manager and `cursor-implementation-prompt` — the latter is an internal artifact only.

The prompt must be bounded. It should tell Cursor exactly what to read, what to change, what not to change, and what to verify.

---

### 3. Let Cursor Implement

Cursor implements the approved slice.

Do not edit files while Cursor is working.

Cursor should report:

- files changed;
- behavior implemented;
- assumptions;
- verification results;
- remaining work;
- documentation changes.

---

### 4. Run Independent Review

Ask Codex or another independent reviewer:

```text
Use codex-review.
```

or:

```text
Сделай ревью working tree.
```

The reviewer should inspect:

- unstaged changes;
- staged changes;
- untracked files;
- implementation against scope;
- Scribe invariants;
- verification evidence.

---

### 5. Triage Findings

Ask:

```text
Use review-triage.
```

Rules:

| Severity | Supervisor action |
| --- | --- |
| High | AI must fix (auto fix prompt) — ask human only for product/scope/privacy/architecture conflicts |
| Medium | AI must fix before commit (auto) — same human exceptions as High |
| Low (cheap / local / non-product) | AI auto-fixes; on second+ loop may policy-defer as Low debt with reason — do not decide every Low yourself |
| Low (product-facing / UX tradeoff) | Human judgment required — **never silently deferred** |

Do not fix findings yourself.

Examples:

```text
Use review-triage.
```

```text
Low про product copy / UX tradeoff — нужна моя оценка. Остальные cheap Lows пусть AI fixed по policy.
```

---

### 6. Run Supervisor QA

When the review gate is clean, ask:

```text
Use supervisor-qa.
```

Then run the app and test the product behavior.

Typical dev launch:

```bash
./scripts/run-dev.sh
```

If production UI behavior matters:

```bash
USE_VITE_DEV=0 ./scripts/run-dev.sh
```

You validate observable behavior, not code structure.

Report the result:

```text
Supervisor QA passed.

Checked:
- file select works
- transcription starts
- summary appears
- cancel returns to a sane state
- logs do not contain transcript/summary body
```

or:

```text
Supervisor QA failed:
- cancel summary removed the existing transcript
Expected: transcript remains visible.
Сформируй AI fix prompt.
```

---

### 7. Prepare Commit

After review is clean and supervisor QA passed or was explicitly skipped, ask:

```text
Use commit-manager.
```

Commit-manager should show:

- review gate status;
- QA status;
- changed files;
- staging hygiene;
- verification results;
- suggested commit message.

Do not approve commit until this is clear.

---

### 8. Approve Commit Explicitly

Only after commit preparation:

```text
Одобряю commit.
```

No AI agent should commit without this explicit approval.

---

## Staging Hygiene

Before any commit, confirm these are **not staged**:

```text
ai-md-condidates/
dist/
.cache/
.venv/
node_modules/
frontend/dist/
native/build/
logs
recordings
model caches
secrets
.env
```

`ai-md-condidates/` is source material only. It may exist locally, but should not be staged unless you explicitly decide otherwise.

---

## Scribe Product Invariants

Never approve changes that violate these without an explicit product decision and documentation overhaul:

- macOS Apple Silicon only;
- audio, transcript, and summary stay local;
- no cloud transcription or cloud summary APIs;
- no remote telemetry of meeting content;
- transcript and summary bodies are never logged;
- model ids and token caps come from backend catalog, not hard-coded UI;
- bridge contract stays synced between `backend/app.py` and `frontend/src/vite-env.d.ts`;
- heavy ML / IO work does not block the pywebview main thread.

---

## Useful Prompts

Planning:

```text
Use roadmap-planner.
```

Full orchestration (normal after scope approval):

```text
Use feature-manager.
```

Review:

```text
Use codex-review.
```

Triage:

```text
Use review-triage.
```

QA plan:

```text
Use supervisor-qa.
```

Commit preparation:

```text
Use commit-manager.
```

Ask for a bounded AI fix:

```text
Сформируй AI fix prompt только для этих findings. Не расширяй scope.
```

Reject implementation:

```text
Отклоняю текущую реализацию: <reason>. Предложи bounded fix или rollback через AI.
```

Accept product-facing Low as debt (never for silent style-only defer by AI alone):

```text
Product-facing Low принимаю как debt. Запиши причину и revisit condition в triage/debt.
```

---

## When In Doubt

Do not edit files manually.

Ask an AI agent to:

- explain the current state;
- propose the next slice;
- review the working tree;
- generate a QA plan;
- make a bounded fix;
- prepare a commit.

Your job is product judgment and approval.
The AI organization's job is implementation, review support, QA preparation, and commit preparation.
