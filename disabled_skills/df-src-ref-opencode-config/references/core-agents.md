---
description: Configure specialized agents with custom prompts, models, and tool access.
source: https://opencode.ai/docs/config/
---

# Agents Configuration

Define specialized agents for specific tasks.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `description` | string | Human-readable description |
| `model` | string | Override default model for this agent |
| `prompt` | string | System prompt customization |
| `tools` | object | Enable/disable specific tools for this agent |

## Default Agent

```json
{
  "default_agent": "plan"
}
```

Set which agent is used when none is explicitly specified. Must be a primary agent (built-in like "build", "plan" or custom). Falls back to "build" with warning if invalid.

## Alternative: Markdown Files

Define agents using markdown files in:
- `~/.config/opencode/agents/`
- `.opencode/agents/`
