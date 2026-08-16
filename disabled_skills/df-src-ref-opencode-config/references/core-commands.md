---
description: Define custom commands with templates, descriptions, and agent assignments.
source: https://opencode.ai/docs/config/
---

# Commands Configuration

Create custom commands for repetitive tasks.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report.\nFocus on failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5"
    },
    "component": {
      "template": "Create a new React component named $ARGUMENTS with TypeScript.\nInclude proper typing and structure.",
      "description": "Create a new component"
    }
  }
}
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `template` | string | Command prompt template (use `$ARGUMENTS` for input) |
| `description` | string | Human-readable description |
| `agent` | string | Which agent to use (default: build) |
| `model` | string | Override model for this command |

## Placeholders

| Placeholder | Description |
|-------------|-------------|
| `$ARGUMENTS` | User-provided arguments to the command |

## Alternative: Markdown Files

Define commands using markdown files in:
- `~/.config/opencode/commands/`
- `.opencode/commands/`
