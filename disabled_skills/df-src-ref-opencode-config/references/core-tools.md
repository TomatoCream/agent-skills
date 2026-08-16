---
description: Enable, disable, and configure AI tools available to the model.
source: https://opencode.ai/docs/config/
---

# Tools Configuration

Manage which tools an LLM can use.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "write": false,
    "bash": false
  }
}
```

## Disabling Tools

Set a tool to `false` to disable it entirely. Common patterns:

```json
{
  "tools": {
    "write": false,
    "edit": false,
    "bash": false
  }
}
```

## Per-Agent Tool Control

Disable tools for specific agents (e.g., review-only agents):

```jsonc
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```
