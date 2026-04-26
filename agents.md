# AGENTS.md

This directory contains agent skills for coding agents (opencode, claude-code, etc.).

## Repository Structure

```
.agents/
├── skills/              # All skills (loaded by agents)
│   ├── df-*/           # Personal skills (df- prefix required)
│   ├── tavily-*/       # Tavily web search/integration skills
│   ├── brainstorming   # From obra/superpowers
│   └── ...
├── install.org         # Idempotent installation instructions
├── agents.md           # This file
└── .skill-lock.json    # Lock file tracking installed skills
```

## Skills Overview

Skills are loaded from the `skills/` directory. Each skill is a `SKILL.md` file with YAML front matter:

```markdown
---
name: skill-name
description: When to use this skill and what it does
---

# Skill Name

## Content...
```

### Skill Name Conventions

- **Personal skills**: MUST be prefixed with `df-` (e.g., `df-skill-creator`, `df-treefmt-nix`)
- **External skills**: Use source prefix (e.g., `tavily-search`, `brainstorming`)

### Skill Sources

| Source | Skills |
|--------|--------|
| `obra/superpowers` | brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, systematic-debugging, test-driven-development, verification-before-completion, using-git-worktrees, finishing-a-development-branch, receiving-code-review, requesting-code-review, writing-skills, using-superpowers, create-skill-from-repo |
| `tavily-ai/skills` | tavily-search, tavily-extract, tavily-map, tavily-crawl, tavily-best-practices, tavily-cli, tavily-research |
| `199-biotechnologies/claude-deep-research-skill` | deep-research |
| `vercel-labs/skills` | find-skills |
| `context7` | context7 |
| `karpathy/autoresearch` | autoresearch |
| Local | create-skill-from-repo, df-src-ref-sops-nix, df-src-ref-nix-openclaw, df-ref-nixarr, df-low-latency-java |

## Related Documentation

- `install.org` — Installation instructions for all skills and required tools
- Individual skill SKILL.md files — Usage documentation
- `skills/*/references/` — Additional reference material
