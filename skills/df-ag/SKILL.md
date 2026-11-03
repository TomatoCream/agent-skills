---
name: df-ag
description: Append to or update the user's global context file, ~/.omp/agent/AGENTS.md (shared with Claude Code via ~/.claude/CLAUDE.md and Codex via ~/.codex/AGENTS.md). Use when the user says "add to global", "add to global agents", "remember this globally", "put this in AGENTS.md", "update the global agents file", or gives a durable instruction, environment fact, or workflow that should apply to every session.
---

# Maintain the global AGENTS.md

One file holds global agent instructions for this machine:
`~/.omp/agent/AGENTS.md`. `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` are
symlinks to it, and omp loads it at native user scope in every session.

Your job: take what the user wants remembered globally and either **append** a new
section or **update** the existing one, without duplicating anything and without
making the file tool-specific or transient.

## 1. Read before writing

```bash
sed -n '1,200p' ~/.omp/agent/AGENTS.md
```

Current section order (keep it):

1. Title + tool entry-point list
2. `## Self-Improving Behavior`
3. `## Code Explanation Style`
4. `## Context and Skill Wiring`
5. `## Environment`

## 2. Decide: update or append

Search before adding:

```bash
grep -n -i '<topic keywords>' ~/.omp/agent/AGENTS.md
```

- **Update** when the file already states the topic, even under a different
  heading. Rewrite the existing sentences in place, delete what is now false, keep
  the heading. Never end up with two sections that say the same thing.
- **Append** only for a genuinely new topic. Insert a new `## ` section by topic:
  environment facts → inside `## Environment`; paths, symlinks, provider wiring →
  inside `## Context and Skill Wiring`; behavioral rules → a new section after
  `## Code Explanation Style`, before `## Context and Skill Wiring`.
- **Never** touch the title or the tool entry-point list unless the user is
  changing which tools exist.

## 3. Write rules

Edit the source of truth path, `~/.omp/agent/AGENTS.md`. Writing through a symlink
is the same file, but never replace a link with a regular file.

Content must be:

- **Durable** — true across sessions and projects, not a snapshot of current work.
  Project state belongs in the project's `AGENTS.md`, not here.
- **Tool-agnostic** — no Claude-only hooks, slash commands, or model names unless
  the instruction applies only to that tool and says so.
- **Imperative and specific** — "staging DB is at port 5433", not "be careful with
  ports"; "run `just test`", not "run the tests".
- **Deduplicated** — one authoritative statement per rule; extend the old sentence
  instead of adding a near-copy.
- **Secret-free** — record the pattern, never a token, key, or password.
- **Terse** — sentences, not paragraphs; the file is injected into every prompt.
  Keep the whole file under ~150 lines; if it grows past that, prune stale entries
  rather than adding more prose.

Preserve the user's wording for existing rules when only adding around them.

## 4. Verify

```bash
grep -n '<new or changed phrase>' ~/.omp/agent/AGENTS.md ~/.claude/CLAUDE.md ~/.codex/AGENTS.md
readlink -f ~/.claude/CLAUDE.md ~/.codex/AGENTS.md
```

All three paths must resolve to `~/.omp/agent/AGENTS.md` and show the change. If a
link is broken, recreate it with `ln -sfn ../.omp/agent/AGENTS.md <path>`; never
copy the file over the link. A broken link plus a regular file means the shared
context silently diverged — report it.

For a live check that a fresh session sees it:

```bash
cd /tmp && omp -p 'Quote the first line under the <heading> section of your global instructions.' --no-tools --no-session --model deepseek
```

## 5. Report

State the path, whether you appended or updated (name the section), and the line
range changed. One or two lines. Do not reprint the whole file.
