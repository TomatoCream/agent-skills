---
description: Use environment variables and file contents in config values.
source: https://opencode.ai/docs/config/
---

# Variables & Substitution

Use dynamic values in your config files.

## Environment Variables

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

Syntax: `{env:VARIABLE_NAME}`

If the variable is not set, it replaces with an empty string.

## File Contents

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["./custom-instructions.md"],
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

Syntax: `{file:path/to/file}`

File paths can be:
- Relative to the config file directory
- Absolute paths starting with `/` or `~`

## Use Cases

- Keep API keys in separate secret files
- Include large instruction files without cluttering config
- Share common config snippets across multiple config files
