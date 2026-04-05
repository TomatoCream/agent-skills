# Agent Instructions

This is a personal collection of agent skills for use with Claude Code and compatible AI agents.

## What This Repo Is

Each directory under `skills/` is one skill — a reusable reference guide that Claude loads on demand to improve how it handles specific tasks or domains.

## Skill Format

Every skill is a directory with at least one required file:

```
skills/
  skill-name/
    SKILL.md              # Required — frontmatter + content
    supporting-file.*     # Only if needed (scripts, heavy reference docs)
```

### SKILL.md frontmatter

```yaml
---
name: skill-name
description: Use when [specific triggering conditions — third person, starts with "Use when"]
---
```

Rules:
- `name`: letters, numbers, hyphens only
- `description`: max ~500 chars, describes WHEN to use (not what it does), never summarizes the skill's workflow
- Total frontmatter: max 1024 characters

## Writing New Skills

Before writing any skill, invoke the `writing-skills` skill:

```
Use the writing-skills skill
```

This enforces the RED-GREEN-REFACTOR cycle: run a baseline test first, write the skill to fix observed failures, then close loopholes.

**Do not write a skill without a failing baseline test.**

## Installing Skills

Run the install script to symlink skills into the agent skill directory:

```bash
./install.sh
```

This symlinks each `skills/<name>` directory into `~/.claude/skills/<name>`.

To install a single skill:

```bash
./install.sh skill-name
```

## Naming Conventions

- Use hyphens, not underscores
- Verb-first / gerund form preferred: `reviewing-prs`, `deploying-nix`, `writing-nixos-modules`
- Name by what you DO, not what the topic is: `condition-based-waiting` not `async-helpers`

## Directory Structure

```
agent-skills/
  skills/           # One subdirectory per skill
  install.sh        # Install script
  AGENTS.md         # This file
  README.md
```

## Repo-Specific Conventions

- All skills are personal/private workflows — not necessarily suitable for upstream contribution
- If a skill would benefit others, consider opening a PR to the upstream skills registry
- Keep skills focused: if something is project-specific, put it in that project's CLAUDE.md instead
