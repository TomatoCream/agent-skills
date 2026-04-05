---
description: OpenCode configuration file formats, locations, and precedence order for merging settings from multiple sources.
source: https://opencode.ai/docs/config/
---

# Config Format & Locations

OpenCode supports **JSON** and **JSONC** (JSON with Comments) formats for configuration.

## File Format

```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "server": {
    "port": 4096
  }
}
```

## Config Precedence (Merged, Not Replaced)

Settings from multiple config sources are **combined** — later configs override earlier ones only for conflicting keys.

| Order | Source | Path |
|-------|--------|------|
| 1 | Remote | `.well-known/opencode` (org defaults) |
| 2 | Global | `~/.config/opencode/opencode.json` |
| 3 | Custom | `OPENCODE_CONFIG` env var |
| 4 | Project | `opencode.json` in project root |
| 5 | Directories | `.opencode/` directories |
| 6 | Inline | `OPENCODE_CONFIG_CONTENT` env var |
| 7 | Managed | `/Library/Application Support/opencode/` (macOS), `/etc/opencode/` (Linux) |
| 8 | MDM | macOS `.mobileconfig` via MDM (highest priority, not overridable) |

**Key insight**: Non-conflicting settings from all configs are preserved. A project config only overrides specific keys in global config, not the entire file.

## Config Directories

The `.opencode` and `~/.config/opencode` directories use plural names for subdirectories:

- `agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, `themes/`

Singular names (e.g., `agent/`) are supported for backwards compatibility.

## Schema

- **Main config**: `https://opencode.ai/config.json`
- **TUI config**: `https://opencode.ai/tui.json`

Your editor should validate and autocomplete based on the JSON Schema.
