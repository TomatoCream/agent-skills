---
description: Extend OpenCode with custom tools, hooks, and integrations via plugins.
source: https://opencode.ai/docs/config/
---

# Plugins Configuration

Extend OpenCode with custom tools, hooks, and integrations.

## File-Based Plugins

Place plugin files in:
- `.opencode/plugins/`
- `~/.config/opencode/plugins/`

## NPM Plugins

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "opencode-helicone-session",
    "@my-org/custom-plugin"
  ]
}
```

Plugins from npm are loaded automatically when specified in the `plugin` array.
