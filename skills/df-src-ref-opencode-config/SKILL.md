---
name: df-src-ref-opencode-config
description: Comprehensive reference for configuring OpenCode AI coding assistant
---

# OpenCode Configuration

Comprehensive reference for configuring OpenCode AI coding assistant.

## Overview

OpenCode uses JSON/JOSNC config files with a layered precedence system. Configs are **merged, not replaced** — later sources override earlier ones only for conflicting keys.

## Reference Index

### Core Configuration

| Category | Description | Reference |
|----------|-------------|-----------|
| **Format & Locations** | Config file formats, paths, precedence order | [core-config-format](references/core-config-format.md) |
| **Server** | Port, hostname, mDNS, CORS settings | [core-server](references/core-server.md) |
| **Models** | Provider, model, small_model, timeout settings | [core-models](references/core-models.md) |
| **Tools** | Enable/disable AI tool access | [core-tools](references/core-tools.md) |
| **Agents** | Specialized agents with custom prompts | [core-agents](references/core-agents.md) |
| **Commands** | Custom command templates | [core-commands](references/core-commands.md) |
| **TUI** | Theme, keybinds, scroll settings | [core-tui](references/core-tui.md) |
| **MCP** | Model Context Protocol servers | [core-mcp](references/core-mcp.md) |
| **Plugins** | Custom tools and integrations | [core-plugins](references/core-plugins.md) |
| **Instructions** | Model instructions and rules | [core-instructions](references/core-instructions.md) |
| **Variables** | Environment variable and file substitution | [core-variables](references/core-variables.md) |

### Advanced Features

| Category | Description | Reference |
|----------|-------------|-----------|
| **Permissions** | Operation approval controls | [advanced-permissions](references/advanced-permissions.md) |
| **Runtime** | Autoupdate, snapshots, compaction, watcher | [advanced-runtime](references/advanced-runtime.md) |
| **Managed** | MDM-based organization config | [advanced-managed](references/advanced-managed.md) |

## Quick Start

### Minimal Config

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5"
}
```

### Common Pattern: Project-Specific Override

```json
// ~/.config/opencode/opencode.json (global)
{
  "autoupdate": true,
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

```json
// project/opencode.json (project)
{
  "model": "anthropic/claude-sonnet-4-5",
  "permission": {
    "bash": "ask"
  }
}
```

## Config Precedence

| Order | Source |
|-------|--------|
| 1 | Remote (`.well-known/opencode`) |
| 2 | Global (`~/.config/opencode/opencode.json`) |
| 3 | Custom (`OPENCODE_CONFIG` env var) |
| 4 | Project (`opencode.json`) |
| 5 | Directories (`.opencode/`) |
| 6 | Inline (`OPENCODE_CONFIG_CONTENT` env var) |
| 7 | Managed (system dirs) |
| 8 | MDM (highest priority) |

## Schema

- **Main config**: `https://opencode.ai/config.json`
- **TUI config**: `https://opencode.ai/tui.json`

Editors with JSON Schema support will provide validation and autocomplete.
