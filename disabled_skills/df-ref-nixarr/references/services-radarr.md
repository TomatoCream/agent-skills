---
name: nixarr Radarr Options
description: Movie collection manager with automatic downloading and management
---

# nixarr Radarr Options

## Basic Options

```nix
nixarr.radarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "radarr" {};
  
  port = mkOption {
    type = types.port;
    default = 7878;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/radarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.radarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.radarr.vpn.enable`

Route Radarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Options per *Arr Service

All *Arr services (Radarr, Sonarr, Lidarr, Readarr, Bazarr, Whisparr, Prowlarr) share this structure:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable` | bool | false | Enable the service |
| `package` | package | nixpkgs pkg | Override package |
| `port` | port | service-specific | Web UI port |
| `stateDir` | path | `${nixarr.stateDir}/service` | State directory |
| `openFirewall` | bool | !vpn.enable | Open firewall port |
| `vpn.enable` | bool | false | Route via VPN |

---

## Default Ports

| Service | Port |
|--------|------|
| Radarr | 7878 |
| Sonarr | 8989 |
| Lidarr | 8686 |
| Readarr | 8787 |
| Readarr Audiobook | 9494 |
| Bazarr | 6767 |
| Whisparr | 6969 |
| Prowlarr | 9696 |

---

## Media Directories

Radarr automatically creates:
- `${nixarr.mediaDir}/library/movies`

---

## Example

```nix
nixarr.radarr = {
  enable = true;
  port = 7878;
  vpn.enable = false;  # Not recommended for *Arrs
};
```
