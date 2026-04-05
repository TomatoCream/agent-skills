---
description: Configure server settings for opencode serve and opencode web commands.
source: https://opencode.ai/docs/config/
---

# Server Configuration

Configure the OpenCode server for `opencode serve` and `opencode web` commands.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "mdnsDomain": "myproject.local",
    "cors": ["http://localhost:5173"]
  }
}
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `port` | number | 4096 | Port to listen on |
| `hostname` | string | "0.0.0.0" | Hostname to listen on (ignored if mdns enabled without explicit hostname) |
| `mdns` | boolean | true | Enable mDNS service discovery for network device detection |
| `mdnsDomain` | string | "opencode.local" | Custom domain for mDNS (useful for multiple instances) |
| `cors` | string[] | [] | Additional CORS origins (full origins: scheme + host + optional port) |

## Example: CORS for Browser Clients

```json
{
  "server": {
    "cors": [
      "https://app.example.com",
      "http://localhost:5173"
    ]
  }
}
```

## Example: Multiple Instances on Network

```json
{
  "server": {
    "mdns": true,
    "mdnsDomain": "project-a.local"
  }
}
```
