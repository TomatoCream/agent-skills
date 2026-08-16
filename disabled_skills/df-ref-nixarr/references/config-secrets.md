---
name: nixarr Secrets Management
description: How to securely handle secrets in nixarr configurations
---

# nixarr Secrets Management

## The Problem

Your NixOS configuration is world-readable in the Nix store. Secrets in config files are visible to any user.

## Solutions

---

## Option 1: Simple File-Based (Recommended for Most)

Create a secrets directory outside the Nix store:

```sh
sudo mkdir -p /data/.secret
sudo chmod 700 /data/.secret
```

Store secrets there:
```sh
sudo mkdir -p /data/.secret/vpn
sudo mv /path/to/wg.conf /data/.secret/vpn/wg.conf
```

Reference in Nix:
```nix
nixarr.vpn = {
  enable = true;
  wgConf = "/data/.secret/vpn/wg.conf";
};
```

**Pros:** Simple, works out of the box
**Cons:** "Impure" - rollbacks won't restore secrets; need `--impure` flag

---

## Option 2: Agenix (For Advanced Users)

Encrypt secrets in your configuration using [Agenix](https://github.com/ryantm/agenix).

**Pros:** Pure, rollbacks work, git-tracked secrets
**Cons:** Complex setup

---

## Secrets Used by nixarr

| Secret | Purpose |
|--------|---------|
| WireGuard config (`wg.conf`) | VPN tunnel |
| Njalla DDNS keys | Dynamic DNS |
| `sessionSecret` (Autobrr) | Session encryption |
| API keys | Radarr/Sonarr communication |

---

## API Keys

nixarr automatically generates and manages API keys for services:

```bash
# List all API keys
sudo nixarr list-api-keys

# Keys stored at:
# ${nixarr.stateDir}/api-keys/radarr.key
# ${nixarr.stateDir}/api-keys/sonarr.key
```

---

## Best Practices

1. **Never commit secrets to git**
2. **Keep secrets outside `/home/`**
3. **Use file permissions** (`chmod 700`, `chmod 600`)
4. **Prefer key-based auth** for SSH
5. **Use VPN** for all services when possible

---

## Example: Complete Secrets Setup

```sh
# Create secrets directory
sudo mkdir -p /data/.secret/vpn
sudo mkdir -p /data/.secret/njalla
sudo chmod 700 /data/.secret

# Place WireGuard config
sudo mv wg.conf /data/.secret/vpn/wg.conf
sudo chmod 600 /data/.secret/vpn/wg.conf

# Place Njalla keys
sudo vim /data/.secret/njalla/keys.json
sudo chmod 600 /data/.secret/njalla/keys.json
```

```nix
nixarr = {
  vpn = {
    enable = true;
    wgConf = "/data/.secret/vpn/wg.conf";
  };
  
  ddns.njalla = {
    enable = true;
    keysFile = "/data/.secret/njalla/keys.json";
  };
};
```
