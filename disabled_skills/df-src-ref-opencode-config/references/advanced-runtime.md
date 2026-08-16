---
description: Control automatic updates, snapshots, context compaction, and watcher ignore patterns.
source: https://opencode.ai/docs/config/
---

# Advanced Settings

## Autoupdate

```json
{
  "autoupdate": false
}
```

| Value | Description |
|-------|-------------|
| `true` | Auto-download updates on startup (default) |
| `false` | Disable auto-update |
| `"notify"` | Notify but don't install (not for package managers) |

## Snapshot (Undo/Redo)

```json
{
  "snapshot": false
}
```

Disabling snapshots means agent changes cannot be rolled back through the UI. Useful for large repos with many submodules to avoid slow indexing and disk usage.

## Context Compaction

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto` | boolean | true | Automatically compact when context is full |
| `prune` | boolean | true | Remove old tool outputs to save tokens |
| `reserved` | number | 10000 | Token buffer left during compaction |

## Watcher (File Watching)

```json
{
  "watcher": {
    "ignore": ["node_modules/**", "dist/**", ".git/**"]
  }
}
```

Patterns follow glob syntax. Exclude noisy directories from file watching.

## Experimental Features

```json
{
  "experimental": {}
}
```

**Caution**: Experimental options may change or be removed without notice.

## Sharing

```json
{
  "share": "manual"
}
```

| Value | Description |
|-------|-------------|
| `"manual"` | Share via `/share` command (default) |
| `"auto"` | Automatically share new conversations |
| `"disabled"` | Disable sharing entirely |

## Formatters

```json
{
  "formatter": {
    "prettier": {
      "disabled": true
    },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```
