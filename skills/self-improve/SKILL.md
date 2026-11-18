---
name: self-improve
description: >
  Invoke when a session ends, after significant work, or when the user says
  "wrap up", "what did we learn", "save context", or "self-improve".
  Also invoke when you notice the user correcting you, re-explaining context,
  or manually handling something you should have done.
user-invocable: true
argument-hint: "[review | dream | init]"
---

# Self-Improving Context System

You are running a self-improvement cycle. Your goal: make the NEXT session
smarter by capturing what THIS session taught you.

## Mode: `$0`

- **No argument / `review`** — Full session review. Extract learnings, update active context, update memory.
- **`dream`** — Consolidation mode. Prune stale entries, resolve contradictions, merge duplicates in learnings and memory.
- **`init`** — Bootstrap a new project. Create `LEARNINGS.md` and seed CLAUDE.md Active Context section.

---

## 1. REVIEW Mode (default)

### Step 1: Detect What Happened

Scan the conversation for these signals:

**Manual Interventions** (highest priority — you MISSED something):
- User corrected you: "no", "not that", "don't", "actually", "wrong", "stop"
- User did something manually that you should have done
- User re-explained context you should have remembered
- User pasted config/URLs/credentials-free details you needed

**Discoveries** (important context to persist):
- Business context: why something exists, who owns it, deadlines
- Environment details: URLs, ports, service names, how to run/test
- Architecture decisions: why X not Y, constraints, tradeoffs
- Repo conventions: patterns, naming, file structure, test approaches
- Current work: what branch, what MR, what's being tested, what's blocked

**Patterns** (skill-level improvements):
- Approaches that worked well (repeat these)
- Approaches that failed (avoid these)
- Tool/library quirks discovered
- Build/test/deploy steps that weren't obvious

### Step 2: Extract Learnings

For each signal found, write a structured learning:

```
**[YYYY-MM-DD] — [category]**
- Observation: [what specifically happened]
- Action: [what to do or avoid next time]
- Confidence: [high / medium / low]
```

Rules for good learnings:
- SPECIFIC: "Payment API v3 needs HMAC in Authorization header, not body" not "be careful with the API"
- ACTIONABLE: a future session reading this cold knows exactly what to do
- DATED: for staleness detection
- NO DUPLICATES: if it's already in LEARNINGS.md, update the existing entry

### Step 3: Write to LEARNINGS.md

Read `LEARNINGS.md` in the project root (create if missing using the template below).

Append new entries to the appropriate section:
- **Patterns That Work** — successful approaches
- **Mistakes to Avoid** — failures and why
- **Codebase Conventions** — non-obvious project patterns
- **Environment & Config** — how to run, test, deploy
- **Business Context** — why things exist, who owns what, deadlines
- **Open Questions** — unresolved items

If an entry contradicts an existing one, UPDATE the existing entry with the new info and today's date.

### Step 4: Update Active Context (CLAUDE.md or AGENTS.md)

Detect which context file this project uses:
- **OpenCode projects**: look for `AGENTS.md` in the project root
- **Claude Code projects**: look for `CLAUDE.md` in the project root
- If both exist, update both. If neither exists, skip this step (use `init` to bootstrap).

Find the `## Active Context` section in whichever file applies.

Update it with the MOST IMPORTANT current state:
- What branch/MR is active and why
- What's being tested or built right now
- Any blockers or constraints discovered this session
- Environment state that affects work (services running, feature flags, etc.)

Rules:
- Keep under 20 lines. Remove outdated entries to make room.
- Only the most currently-relevant info. This is a "what am I doing RIGHT NOW" section.
- NEVER modify sections above Active Context (those are static, human-maintained).

### Step 5: Update Memory (if significant)

If the session revealed something that transcends this project (a personal preference,
a tool behavior, a workflow pattern), write it to auto memory using the standard
memory system conventions.

### Step 6: Report

Tell the user what you captured:
- Number of learnings added/updated
- Active Context changes
- Memory updates (if any)
- Any open questions flagged

---

## 2. DREAM Mode (consolidation)

Run this periodically (weekly or when LEARNINGS.md exceeds ~100 entries).

### Phase 1: Orient
Read LEARNINGS.md and the Active Context section from whichever file the project uses (`AGENTS.md` for OpenCode, `CLAUDE.md` for Claude Code). Inventory what exists.

### Phase 2: Prune
- Remove entries referencing deleted files, deprecated APIs, or completed work
- Remove entries older than 60 days with confidence: low
- Remove entries contradicted by newer entries

### Phase 3: Consolidate
- Merge duplicate/overlapping entries into single authoritative statements
- Promote patterns that appeared 3+ times to the project's conventions section (`AGENTS.md` or `CLAUDE.md`) — ask user first
- Convert relative dates to absolute dates
- Move resolved Open Questions to appropriate sections or delete

### Phase 4: Index
- Ensure LEARNINGS.md stays under ~150 entries
- Ensure Active Context stays under 20 lines
- Ensure each entry is still specific and actionable (remove vague ones)

Report what changed: entries pruned, merged, promoted.

---

## 3. INIT Mode (bootstrap)

Create the self-improving infrastructure for a new project.

### Step 1: Create LEARNINGS.md

```markdown
# Project Learnings

> Auto-maintained by the self-improve skill. Read at session start, updated at session end.

## Patterns That Work
<!-- Approaches that produced good results -->

## Mistakes to Avoid
<!-- Failed approaches and why they failed -->

## Codebase Conventions
<!-- Non-obvious project patterns and naming conventions -->

## Environment & Config
<!-- How to run, test, deploy. Service URLs, ports, tools needed -->

## Business Context
<!-- Why things exist, who owns what, deadlines, constraints -->

## Open Questions
<!-- Unresolved items needing investigation -->
```

### Step 2: Add Active Context to the project's AI context file

Detect the project's tooling:
- If `AGENTS.md` exists → it's an **OpenCode** project. Append to `AGENTS.md`.
- If `CLAUDE.md` exists → it's a **Claude Code** project. Append to `CLAUDE.md`.
- If neither exists → ask the user which tool they use, then create the appropriate file.

Append to the detected file (before any existing dynamic sections):

```markdown

## Active Context
<!-- AI assistant maintains this section. Keep under 20 lines. -->
<!-- Updated automatically by /self-improve. Remove stale entries. -->
```

If creating a new file from scratch (OpenCode / AGENTS.md):

```markdown
# [Project Name]

## Conventions
<!-- Add project conventions here -->

## Active Context
<!-- AI assistant maintains this section. Keep under 20 lines. -->
<!-- Updated automatically by /self-improve. Remove stale entries. -->
```

If creating a new file from scratch (Claude Code / CLAUDE.md):

```markdown
# [Project Name]

## Conventions
<!-- Add project conventions here -->

## Active Context
<!-- Claude maintains this section. Keep under 20 lines. -->
<!-- Updated automatically by /self-improve. Remove stale entries. -->
```

### Step 3: Confirm
Tell the user the system is bootstrapped and what to expect:
- LEARNINGS.md will accumulate knowledge across sessions
- Active Context will track current work state
- Run `/self-improve` at session end or it triggers automatically
- Run `/self-improve dream` weekly to consolidate

---

## LEARNINGS.md Template for New Entries

Always use this format when appending:

```
**[YYYY-MM-DD] — [Environment & Config]**
- Observation: staging DB is at postgres://staging.internal:5432/myapp
- Action: use this connection string for integration tests, not localhost
- Confidence: high
```

---

## Anti-Patterns (DO NOT)

- DO NOT add vague entries: "be careful with X" is useless
- DO NOT bloat Active Context beyond 20 lines
- DO NOT modify static sections of `CLAUDE.md` / `AGENTS.md` (Architecture, Conventions) without user permission
- DO NOT duplicate what's already in LEARNINGS.md — update the existing entry
- DO NOT record sensitive data (passwords, tokens, keys) — only record the PATTERN
- DO NOT record things derivable from code/git — only record non-obvious knowledge
- DO NOT record debugging solutions — the fix is in the code; record the PATTERN that caused the bug
