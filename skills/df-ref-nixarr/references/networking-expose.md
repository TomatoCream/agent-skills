---
name: nixarr Exposing Services
description: Methods for accessing services remotely (VPN, SSH tunnel, HTTPS)
---

# nixarr Exposing Services

## Overview

"Exposing" means accessing services outside your home network.

---

## Safe Methods (Recommended)

### 1. VPN

Safest method. Route all traffic through your own VPN.

**Options:**
```nix
nixarr.vpn = {
  enable = true;
  wgConf = "/data/.secret/wg.conf";
};

# Then enable per-service
nixarr.jellyfin.vpn.enable = true;
```

### 2. Tailscale

Use [Tailscale](https://tailscale.com/) for easy mesh VPN.

### 3. SSH Tunneling

Access services through an SSH tunnel from a remote machine:

```sh
ssh -N user@your-server-ip \
  -L 6001:localhost:9091 \
  -L 6002:localhost:9696 \
  -L 6003:localhost:8989 \
  -L 6004:localhost:7878 \
  -L 6005:localhost:8686 \
  -L 6006:localhost:8787 \
  -L 6007:localhost:6767
```

Then access services at `localhost:6001` through `localhost:6007`.

**Requirements:**
- SSH service enabled in NixOS config
- Port forwarded on router (or SSH via VPN)
- Password auth disabled, key-based auth only

---

## Direct Internet Exposure (Not Recommended)

Exposes services without VPN or SSH. Relies solely on service authentication.

### Per-Service HTTPS Exposure

```nix
nixarr.jellyfin.expose.https = {
  enable = true;
  domainName = "jellyfin.example.com";
  acmeMail = "admin@example.com";
  upnp.enable = true;  # Optional: auto-open ports
};
```

This creates an nginx reverse proxy with Let's Encrypt SSL.

> **Warning:** Do NOT enable without setting up service authentication first!

---

## Services with HTTPS Exposure

| Service | Option |
|---------|--------|
| Jellyfin | `nixarr.jellyfin.expose.https` |
| Plex | `nixarr.plex.expose.https` |
| Audiobookshelf | `nixarr.audiobookshelf.expose.https` |
| Komga | `nixarr.komga.expose.https` |
| Jellyseerr | `nixarr.jellyseerr.expose.https` |

---

## Quick Comparison

| Method | Security | Complexity | Performance |
|--------|----------|------------|-------------|
| VPN (WireGuard) | Very High | Medium | Best |
| Tailscale | Very High | Low | Good |
| SSH Tunnel | Very High | Medium | Good |
| Direct HTTPS | Medium | Low | Good |

---

## Security Recommendations

1. **Always use strong authentication**
2. **Prefer VPN or SSH over direct exposure**
3. **Disable password authentication for SSH**
4. **Use VPN for transmission/torrenting**
5. **Don't expose *Arrs to VPN** (rate limiting issues)
