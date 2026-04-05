---
description: Deploy organization-wide managed configuration via MDM on macOS.
source: https://opencode.ai/docs/config/
---

# Managed Configuration (MDM)

Organizations can enforce configuration that users cannot override.

## File-Based Managed Config

| Platform | Path |
|----------|------|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode` |

Requires admin/root access to write.

## macOS Managed Preferences (.mobileconfig)

Deploy via MDM (Jamf, Kandji, FleetDM) using `.mobileconfig` files.

### Creating a .mobileconfig

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>PayloadType</key>
      <string>ai.opencode.managed</string>
      <key>PayloadIdentifier</key>
      <string>com.example.opencode.config</string>
      <key>PayloadUUID</key>
      <string>GENERATE-YOUR-OWN-UUID</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
      <key>share</key>
      <string>disabled</string>
      <key>server</key>
      <dict>
        <key>hostname</key>
        <string>127.0.0.1</string>
      </dict>
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
    </dict>
  </array>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadIdentifier</key>
  <string>com.example.opencode</string>
  <key>PayloadUUID</key>
  <string>GENERATE-YOUR-OWN-UUID</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>
```

Generate UUIDs with `uuidgen`.

### OpenCode Checks These Paths

- `/Library/Managed Preferences/<user>/ai.opencode.managed.plist`
- `/Library/Managed Preferences/ai.opencode.managed.plist`

### MDM Deployment

| MDM | Method |
|-----|--------|
| Jamf Pro | Computers > Configuration Profiles > Upload > scope to devices |
| FleetDM | Add to gitops repo under `mdm.macos_settings.custom_settings` |

### Verifying on Device

```bash
opencode debug config
```

All managed preference keys appear in the resolved config and cannot be overridden.
