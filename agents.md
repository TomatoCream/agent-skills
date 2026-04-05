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
| Local | create-skill-from-repo |

### Personal Skills (df-* prefix)

| Skill | Description |
|-------|-------------|
| `df-commit` | Commit changes and push to remote — review diff, craft message, commit, push |
| `df-skill-creator` | Create new skills, edit/verify existing skills, run evals |
| `df-treefmt-nix` | Setting up treefmt-nix in Nix flakes, `nix fmt` / `nix flake check` |
| `df-flashcard-org` | Generate Anki flashcards in org-mode format |
| `df-think-say-approve-do` | Plan before acting — think → describe → approve → execute loop |

## Code Style Guidelines

### Skill Document Format

Every skill should follow this structure:

1. **YAML Front Matter** (required):
   ```yaml
   ---
   name: skill-name
   description: Clear description of when to trigger this skill
   ---
   ```

2. **H1 Title**: Same as skill name
3. **Overview**: 1-2 sentence summary
4. **Sections**: Logical divisions with H2 headers
5. **Formatting**: Use tables for comparisons, code blocks for examples

### Markdown Conventions

- Use ATX-style headers (`#`, `##`, `###`)
- Code blocks with language hints: ` ```bash `, ` ```python `
- Tables for structured comparisons
- Bold for key terms, emphasis for warnings
- Line length: Wrap at 120 characters when practical
- No trailing whitespace

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Skill names | kebab-case | `df-skill-creator` |
| File names | kebab-case | `root-cause-tracing.md` |
| Headers | Title Case | `## Root Cause Investigation` |
| Variables | snake_case | `skill_path` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |

### Front Matter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (kebab-case) |
| `description` | Yes | When to use this skill |
| `allowed-tools` | No | List of permitted tool prefixes |

### Error Handling

- Document expected failure modes
- Include troubleshooting sections
- Use clear warnings with **bold** headers
- Provide recovery procedures

### Best Practices

1. **Be concise**: Skills are reference guides, not tutorials
2. **Concrete examples**: Include runnable code examples
3. **Clear triggers**: State explicitly when to use the skill
4. **Process steps**: Numbered lists for sequential processes
5. **Cross-references**: Link to related skills with `skill-name` format
6. **Idempotent instructions**: Instructions should be safe to run multiple times

## Linting and Validation

Skills are validated by the `writing-skills` skill which includes:
- Schema validation against SKILL.md format
- Consistency checks (name matches filename, etc.)
- Completeness checks (required fields present)

No separate build step required — skills are plain markdown.

## Working with Skills

### Loading a Skill

Use the `skill` tool:
```
/skill skill-name
```

### Creating a New Skill

**MUST add to install.org for EVERY personal skill** — do not skip this step.

1. Create `skills/df-your-skill/SKILL.md`
2. Follow the format above
3. **Add entry to install.org Personal Skills table** — all fields required:
   - Skill name (df-*)
   - When to Use (description)
   - External Tools (even "None")
4. Commit

### Evaluating Skills

Use the `df-skill-creator` skill for iterative improvement of skills:
```
/skill df-skill-creator
```

## Related Documentation

- `install.org` — Installation instructions for all skills and required tools
- Individual skill SKILL.md files — Usage documentation
- `skills/*/references/` — Additional reference material
