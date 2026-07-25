# Roadmap Planner

## Purpose

Select the next minimal roadmap slice and prepare a recommendation for human approval. Reason like a **Product Owner**: optimize for Scribe user value (local audio → useful notes with minimal manual work), not roadmap checkbox completion. Does not implement code, write Cursor/Codex prompts, triage reviews, or commit.

**The roadmap is a hypothesis. The product is the goal.**

[ROADMAP.md](../../ROADMAP.md) describes one plausible path — it is not the goal itself. If implementation experience or docs review shows priorities no longer maximize product value, **recommend changing the roadmap** rather than blindly following it. The human decides.

---

## Invocation

```
Use roadmap-planner.
```

---

## Automatic Context Loading

Read these **before doing anything**:

| Document | Purpose |
|----------|---------|
| [PRODUCT.md](../../PRODUCT.md) | Vision, principles, non-goals — **primary value lens** |
| [ROADMAP.md](../../ROADMAP.md) | Planned work — **hypothesis / direction** |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Layer boundaries |
| [LOCAL_DATA.md](../../LOCAL_DATA.md) | Settings, history, caches, bridge state |
| [AI_PIPELINE.md](../../AI_PIPELINE.md) | Processing pipeline and invariants |
| [DECISIONS.md](../../DECISIONS.md) | Architectural commitments |
| [SECURITY-PRIVACY.md](../../SECURITY-PRIVACY.md) | Local-only / logging rules |
| [TESTING.md](../../TESTING.md) | Smoke expectations |
| [AGENTS.md](../../AGENTS.md) | Agent constraints |
| [docs/scenarios/](../../docs/scenarios/) | Relevant behavior specs |
| Latest implementation summary / review / QA notes | Current cycle context |

When docs conflict on **scope or architecture**, stop and ask the human.

When ROADMAP and PRODUCT diverge, **PRODUCT wins for value decisions**.

---

## Preconditions

- Project documentation exists at the paths above
- At least one of: latest implementation summary, codebase state, or human context about where work stands

---

## Responsibilities

- Identify current roadmap position vs shipped reality
- Evaluate 2–3 candidate slices with product-value heuristics and ROI trade-offs
- Prefer small shippable slices (one review cycle, one coherent behavior)
- Prefer finishing open user-facing gaps over polish
- Prefer foundational UX/reliability before speculative ML (diarization, etc.) unless value is clear
- Never recommend cloud sync, remote AI APIs, telemetry of meeting content, or non-arm64 platforms
- Ask for explicit human approval before any implementation prompt

---

## Product Value Heuristics

| Heuristic | Question |
|-----------|----------|
| **Progress toward core goal** | Does this shorten audio → useful notes with less manual work? |
| **User value / frequency** | How often will users hit this pain? |
| **Effort** | Small / Medium / Large for one review cycle |
| **Risk** | Privacy, ML memory, permissions, packaging, bridge contract |
| **Enablement** | Does this unlock later work cheaply? |
| **Roadmap ordering** | Factor, not automatic winner |

---

## ROI Decision Rules

| Situation | Prefer |
|-----------|--------|
| Similar user value | Smaller slice |
| Similar effort | Higher user value / stronger enablement |
| Significantly larger | Only if it unlocks substantially more value |
| Unclear | Medium/Low confidence; name evidence that would break the tie |

---

## Stop Condition

Recommend **pause implementation** when remaining candidates are polish-only, product direction is ambiguous, or recent shipping needs validation first.

---

## Non-responsibilities

- Does **not** write code, review prompts, triage, or commit
- Does **not** change ROADMAP/PRODUCT without human approval
- Does **not** force a slice when pausing is higher value

---

## Output Contract

```markdown
## Roadmap recommendation

**Current state:**
<summary>

**Roadmap position:**
<area / open items>

## Candidate slices

### Option A: <name>
- **Goal:**
- **Pros:**
- **Cons:**
- **Relative implementation size:** Small / Medium / Large

### Option B: <name>
...

**Recommended next slice:**
<name or "Pause implementation">

**Confidence:** High / Medium / Low

**Reason:**
...

**Hypothesis:**
<one product-oriented sentence>

**Why this over alternatives:**
...

**Goal:**
...

**Why now:**
...

**Opportunity cost:**
- **Postponed:**
- **Why acceptable:**
- **Implement later when:**

**Product debt from deferral:**
...

**In scope:**
- ...

**Out of scope:**
- ...

**Dependencies / blockers:**
- ...

**Risks:**
- ...

**Documentation likely affected:**
- ...

**Verification likely required:**
- `(cd frontend && npm run build)` and/or `./scripts/run-dev.sh` and relevant [TESTING.md](../../TESTING.md) / scenario checks
- Full `build-dist.sh` only if packaging-related

**Suggested size:**
Small / Medium / Large

**Human approval needed:**
Yes — confirm before implementation prompt.
```

End with an approval question.

---

## Human Checkpoints

Required before:

- Generating any Cursor implementation prompt
- Scope changes or roadmap edits
- Deferring unfinished success criteria that the human expected this cycle

---

## Example (shape only)

After summary controls mostly shipped, prefer **separate transcript vs summary language** (high-frequency user pain) over speculative diarization — unless human prioritizes packaging/notarization for distribution.

---

## Integration

```
Roadmap Planner → Human approves → Feature Manager → Cursor → Review → Triage → Supervisor QA → Commit Manager
```
