---
name: nixarr Lidarr Options
description: Music collection manager for automatic music downloading and management
---

# nixarr Lidarr Options

## Basic Options

```nix
nixarr.lidarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "lidarr" {};
  
  port = mkOption {
    type = types.port;
    default = 8686;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/lidarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.lidarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.lidarr.vpn.enable`

Route Lidarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Media Directories

Lidarr automatically creates:
- `${nixarr.mediaDir}/library/music`

---

## Example

```nix
nixarr.lidarr = {
  enable = true;
  port = 8686;
};
```
