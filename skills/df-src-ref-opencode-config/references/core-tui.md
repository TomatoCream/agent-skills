---
description: TUI-specific settings for theme, keybinds, scroll behavior, and diff display.
source: https://opencode.ai/docs/config/
---

# TUI Configuration

Use a dedicated `tui.json` (or `tui.jsonc`) for TUI-specific settings.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": true
  },
  "diff_style": "auto",
  "keybinds": {}
}
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `theme` | string | UI theme name (e.g., "tokyonight") |
| `scroll_speed` | number | Scroll speed for output |
| `scroll_acceleration.enabled` | boolean | Enable scroll acceleration |
| `diff_style` | string | Diff display style ("auto" or other) |
| `keybinds` | object | Custom keybindings |

## Locations

| Config | Path |
|--------|------|
| Global | `~/.config/opencode/tui.json` |
| Project | `tui.json` in project root |

Use `OPENCODE_TUI_CONFIG` to specify a custom TUI config file.

## Legacy Support

Legacy theme, keybinds, and tui keys in `opencode.json` are deprecated and automatically migrated when possible.
