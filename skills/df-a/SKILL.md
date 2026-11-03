---
name: df-a
description: Append to or update the current project's AGENTS.md (repo-root context file, not the global one). Use when the user says "add to project agents", "remember this in the repo", "document this in AGENTS.md", "write project conventions", "update the project agents file", or after a discovery about build/test commands, architecture, or repo conventions that should apply to every future session in this repository.
---

# Maintain the project AGENTS.md

Project context lives in the repository's own `AGENTS.md`. Global instructions
(`~/.omp/agent/AGENTS.md`, maintained by `df-ag`) are already injected into every
session — a project file must not repeat them.

## 1. Find the target file

```bash
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
ls -l "$root/AGENTS.md" "$root/CLAUDE.md" "$root/.omp/AGENTS.md" 2>/dev/null
```

- Write `"$root/AGENTS.md"` — the file omp's ancestor walk and Claude Code both pick
  up. Never write the global `~/.omp/agent/AGENTS.md` from this skill.
- If only `CLAUDE.md` exists, move its content to `AGENTS.md` and leave
  `CLAUDE.md` as a relative symlink to `AGENTS.md`, so both tools read one file.
  Say that you did this.
- If `.omp/AGENTS.md` exists, it is the native project context file; treat it as the
  target instead of creating a second file.

## 2. Read before writing

```bash
sed -n '1,200p' "$root/AGENTS.md"
grep -n '^#' "$root/AGENTS.md"
```

Keep the existing section order and headings. With no file yet, create only the
sections you can fill with verified facts:

```markdown
# AGENTS.md

## Overview        — what this repo is, in 1-3 sentences
## Commands        — exact build/test/lint/run commands, verified by running them
## Layout          — directories and what lives where
## Conventions     — naming, error handling, test structure, import rules
## Gotchas         — traps, env requirements, known-flaky steps
```

## 3. Decide: update or append

- **Update** whenever the topic already appears, under any heading. Replace false
  sentences, keep the heading, no second section on the same topic.
- **Append** a section only for a new topic, placed by the order above; extend an
  existing section when it is close enough.
- Never add `## Active Context` unless the user asks for session handoff state; if
  present, keep it under 20 lines and prune stale entries.

## 4. Content rules

- **Repo-specific only** — commands, paths, versions, owners, constraints. Anything
  true of every repo belongs in the global file; suggest it there instead.
- **Verified** — run the command before documenting it; never copy commands from a
  README without confirming they work.
- **Durable** — no current-branch state, no "today we changed X", no TODOs for work
  in flight.
- **Specific** — `pnpm test -- --runInBand`, not "run the tests".
- **Secret-free** — no tokens, credentials, or customer data; describe the pattern.
- **Terse** — imperative sentences; keep the file under ~150 lines. Prune stale
  entries instead of adding prose.

## 5. Verify

```bash
grep -n '<new or changed phrase>' "$root/AGENTS.md"
grep -c '^## ' "$root/AGENTS.md"   # no duplicate headings
wc -l "$root/AGENTS.md"
```

If `CLAUDE.md` should mirror it: `ln -sfn AGENTS.md "$root/CLAUDE.md"` and confirm
`readlink -f "$root/CLAUDE.md"` points at `AGENTS.md`.

## 6. Report

Repository, path, appended or updated (with section name), and line range. One or
two lines; do not reprint the file.
