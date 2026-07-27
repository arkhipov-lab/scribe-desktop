# Commit Manager

## Purpose

Final step before landing an iteration: verify the review gate, run final checks, prepare a commit summary and message, and **request human approval before creating the commit**.

---

## Invocation

```
Use commit-manager.
```

---

## Automatic Context Loading

| Source | Purpose |
|--------|---------|
| Latest review + triage | Gate status, accepted Lows |
| Implementation summary | Behavior, files, verification |
| Supervisor QA plan + outcome | Pass / fail / explicit skip |
| Approved slice | Scope match |
| [`.ai/state/current-cycle.json`](../state/current-cycle.json) | Active iteration, gate state, QA status |
| [`.ai/state/debt.md`](../state/debt.md) | Accepted/deferred debt that must be recorded before commit |
| [`.ai/state/product-followups.md`](../state/product-followups.md) | QA/planning wishes — confirm captured here (not in debt) when notes mention them |
| Active ledger in [docs/iterations/](../../docs/iterations/) | Full iteration record and handoffs |
| [`.ai/org/`](../org/) | Reusable gate and workflow rules |
| [`.ai/product/`](../product/) | Product-layer constraints for scope check |
| [`.ai/repo/`](../repo/) | Validation commands and forbidden-path adapter |
| [`.ai/repo/forbidden-paths.md`](../repo/forbidden-paths.md) | Forbidden staging paths source |
| Git working tree | `git status`, `git diff`, `git diff --cached` |
| [CONTRIBUTING.md](../../CONTRIBUTING.md) | Conventional Commits / what not to commit |

---

## Preconditions

- No unresolved High/Medium
- Lows fixed or accepted/deferred **under review-triage auto-fix policy** (reason documented in ledger/debt); product-facing Lows require Product Owner judgment — never silently deferred
- Supervisor QA **passed** or **explicitly skipped** (record skip)
- Verification reported
- Active ledger and current-cycle state are up to date through QA
- `scripts/ai-cycle-validate.sh` passes
- Human has **not** yet authorized the commit in the current message — prepare first

---

## Responsibilities

### Check gate

Run `scripts/ai-cycle-validate.sh`. If it fails, stop and route to review-triage / codex-review / supervisor-qa or state repair. Do not prepare a commit.

### Run final verification

Relevant checks only:

- [ ] `(cd frontend && npm run build)` if frontend/TS touched
- [ ] `./scripts/run-dev.sh` smoke for affected flows
- [ ] `USE_VITE_DEV=0 ./scripts/run-dev.sh` if needed
- [ ] Packaging builds **only** if packaging-related
- [ ] Confirm no transcript/summary logging if ML/logging touched

### Prepare artifacts

1. Commit summary (Output Contract)
2. Suggested Conventional Commits message
3. Changed files with one-line purpose
4. Accepted Lows + QA skip notes
5. If Supervisor QA / ledger notes mention product wishes, confirm they are in `.ai/state/product-followups.md` and the ledger Product Follow-ups section — **not** in `debt.md`
6. Update the active ledger and `.ai/state/current-cycle.json` to `commit-ready` with `handoff.next_role=human-product-owner` (commit approval) or `commit-manager` while prep is still in progress
7. **Ask for explicit commit approval** — do not commit until requested

### Exclude from commit

Follow the forbidden-path policy in [`.ai/repo/forbidden-paths.md`](../repo/forbidden-paths.md). Never stage:

- `dist/`, `.cache/`, `.venv/`, `node_modules/`, `frontend/dist/`, `native/build/`
- logs, recordings, HF caches, secrets
- **`ai-md-condidates/`** — never stage additions, modifications, **or** deletions unless the human **explicitly** asks to include that folder

### Staging check (required)

Before asking for commit approval, verify:

```bash
git status --short --untracked-files=all
git diff --cached --name-only
```

Confirm **no** path under `ai-md-condidates/` is staged. If any candidate path is staged, unstage it and report that fact in the commit preparation output.

### After commit (only when human approved)

Record the commit hash in the active ledger and update `.ai/state/current-cycle.json` to post-commit retrospective state: `phase=retrospective`, `iteration.status=retrospective`, `gates.committed=true`, `artifacts.commit=<hash>`, and `handoff.next_role=iteration-retrospective`. Then route to `Use iteration-retrospective.` The retrospective role sets `phase=shipped` / `status=shipped` and `handoff.next_role=none` after it completes.

---

## Non-responsibilities

- Does **not** commit without explicit human approval in the current message
- Does **not** bypass review or QA (unless QA explicitly skipped)
- Does **not** silently accept High/Medium, or silently defer product-facing Lows
- Does **not** re-ask the human about routine policy-deferred non-product Lows already recorded by triage

---

## Output Contract

````markdown
## Commit preparation — <iteration name>

### Review gate
- High/Medium: none unresolved
- Low: <fixed / accepted with reasons>

### Supervisor QA
- Status: <passed / skipped with reason>
- Notes: ...

### Changed files

| File | Purpose |
|------|---------|
| `path` | ... |

### Staging hygiene

- [ ] No `ai-md-condidates/` paths staged (additions, modifications, or deletions)
- [ ] No `dist/`, `.cache/`, recordings, secrets, or other forbidden artifacts staged

### Behavior implemented

- ...

### Documentation changes

- ...

### Known limitations

- ...

### Accepted Low findings (if any)

| Finding | Reason accepted |
|---------|-----------------|
| ... | ... |

### Verification results

| Check | Result |
|-------|--------|
| `(cd frontend && npm run build)` | pass/fail/skipped |
| `./scripts/run-dev.sh` smoke | ... |
| `scripts/ai-cycle-validate.sh` | pass/fail |

### Suggested commit message

```
<type>(<scope>): <short description>

<optional body — why, not what>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `build`, `ci`, `perf`, `style`, `revert`

### Approval needed

Human must explicitly request the commit before it is created.

### State updates

- Ledger:
- Current cycle:
- Debt register:
````

When the human approves, create the commit per repo conventions ([CONTRIBUTING.md](../../CONTRIBUTING.md)) and produce the post-commit summary.

---

## Human Checkpoints

Required:

- Before skipping supervisor QA
- Before every commit
- Before accepting or deferring **product-facing** Lows / meaningful UX tradeoffs (routine non-product Lows are handled by triage auto-fix / policy defer)

---

## Rules

| Rule | Detail |
|------|--------|
| Human approval | Required for every commit |
| High/Medium block | Never commit with open blockers |
| Low / QA skip | Lows: fixed or accepted/deferred under policy with documented reason; product-facing Lows need human judgment. QA skip must be explicit |
| Message format | Conventional Commits |
| Scope | Only current iteration files |
| Candidate folder | Never stage `ai-md-condidates/` unless human explicitly requests |
