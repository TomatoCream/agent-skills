---
description: Configure MCP (Model Context Protocol) servers for external integrations.
source: https://opencode.ai/docs/config/
---

# MCP Server Configuration

Configure MCP servers for external integrations like Jira, GitHub, etc.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {}
}
```

## Remote MCP Server

```json
{
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": false
    }
  }
}
```

## Enabling Org-Provided Servers

Remote config from `.well-known/opencode` may provide disabled servers:

```json
// Remote config (org defaults)
{
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": false
    }
  }
}
```

Enable in your local config:

```json
// Your project config
{
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": true
    }
  }
}
```
