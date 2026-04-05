---
description: Model instructions, rules, and guidelines loaded at startup.
source: https://opencode.ai/docs/config/
---

# Instructions Configuration

Provide instruction files and rules for the model.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md"
  ]
}
```

## Usage

- Array of file paths and glob patterns
- Files are loaded and included in context at startup
- Useful for project-specific guidelines, coding standards, and rules

## File Paths

Paths can be:
- Relative to the config file directory
- Absolute paths starting with `/` or `~`
