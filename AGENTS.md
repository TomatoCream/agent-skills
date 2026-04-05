# Agent Instructions

This is a personal collection of agent skills for use with Claude Code and compatible AI agents.

## What This Repo Is

Two types of Claude Code extensions live here:

- **Skills** (`skills/`) — reference guides Claude loads on demand to handle specific tasks
- **Agents** (`agents/`) — specialized subagents with their own system prompts, invokable via the `Agent` tool

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

## Agent Format

Agents are single `.md` files in `agents/` with frontmatter and a system prompt body.

```
agents/
  my-agent.md       # frontmatter + system prompt
```

### Frontmatter

```yaml
---
name: agent-name
description: Use this agent when [triggering conditions with examples]
model: sonnet        # or opus, haiku — defaults to sonnet
---
```

- `name`: letters, numbers, hyphens
- `description`: same rules as skills — "Use this agent when...", never summarizes workflow. Include `<example>` blocks showing user messages and when to dispatch the agent.
- `model`: optional. Use `opus` for complex reasoning tasks, `haiku` for fast/cheap tasks, `sonnet` for default.

The body (after frontmatter) is the agent's full system prompt. Write it as instructions to the agent, not to the user.

## Writing New Skills

Before writing any skill, invoke the `writing-skills` skill:

```
Use the writing-skills skill
```

This enforces the RED-GREEN-REFACTOR cycle: run a baseline test first, write the skill to fix observed failures, then close loopholes.

**Do not write a skill without a failing baseline test.**

## Installing

Run the install script after adding any skill or agent:

```bash
./install.sh
```

`install.sh` is **idempotent** — safe to re-run at any time. It symlinks:
- `skills/*` → `~/.claude/skills/` and `~/.config/opencode/skills/`
- `agents/*.md` → `~/.claude/agents/`

**When adding a new install target** (new tool, new config directory), update `install.sh`
to include it. The script is the single source of truth for where things get installed —
keep it complete so a fresh clone + `./install.sh` fully bootstraps the environment.

**When adding any new skill or agent**, also add a row to the appropriate table in
`tools.org` with a short "when to use" description.

## Naming Conventions

- Use hyphens, not underscores
- Verb-first / gerund form preferred: `reviewing-prs`, `deploying-nix`, `writing-nixos-modules`
- Name by what you DO, not what the topic is: `condition-based-waiting` not `async-helpers`
- Personal/private skills (not sourced from upstream registries) must use the `df-` prefix: `df-treefmt-nix`, `df-my-workflow`

## Directory Structure

```
agent-skills/
  skills/                    # One subdirectory per skill
  agents/                    # One .md file per agent
  vendor/superpowers/        # obra/superpowers submodule (reference copy)
  install.sh                 # Symlinks skills → ~/.claude/ and ~/.config/opencode/
  AGENTS.md                  # This file
  README.md
```

## Opencode Setup

Superpowers loads in opencode via the plugin system — no symlinks needed for it.
The plugin entry is in `~/.config/opencode/opencode.jsonc`:

```json
{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
}
```

The `vendor/superpowers` submodule is a local reference copy. The live opencode install
fetches directly from GitHub on restart.

Personal skills in `skills/` are symlinked to both `~/.claude/skills/` and
`~/.config/opencode/skills/` by `install.sh`.

## Repo-Specific Conventions

- All skills are personal/private workflows — not necessarily suitable for upstream contribution
- If a skill would benefit others, consider opening a PR to the upstream skills registry
- Keep skills focused: if something is project-specific, put it in that project's CLAUDE.md instead
