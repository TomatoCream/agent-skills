---
description: Control which operations require user approval before execution.
source: https://opencode.ai/docs/config/
---

# Permissions Configuration

Control operations that require explicit user approval.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

## Permission Modes

| Mode | Description |
|------|-------------|
| `"ask"` | Prompt user for approval before executing |
| `"allow"` | Execute without asking (default behavior) |
| `"deny"` | Block the operation entirely |

## Per-Operation Wildcards

```json
{
  "permission": {
    "*": "ask",
    "bash": {
      "*": "ask",
      "rm -rf *": "deny"
    }
  }
}
```

This example:
- Requires approval for all operations by default
- Requires approval for all bash commands
- Explicitly denies `rm -rf *`

## Managed Permissions (MDM)

Organizations can enforce permissions via macOS `.mobileconfig`:

```xml
<key>permission</key>
<dict>
  <key>*</key>
  <string>ask</string>
  <key>bash</key>
  <dict>
    <key>*</key>
    <string>ask</string>
    <key>rm -rf *</key>
    <string>deny</string>
  </dict>
</dict>
```
