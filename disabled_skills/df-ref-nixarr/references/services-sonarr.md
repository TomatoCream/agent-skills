---
name: nixarr Sonarr Options
description: TV show collection manager with automatic episode management
---

# nixarr Sonarr Options

## Basic Options

```nix
nixarr.sonarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "sonarr" {};
  
  port = mkOption {
    type = types.port;
    default = 8989;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/sonarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.sonarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.sonarr.vpn.enable`

Route Sonarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Media Directories

Sonarr automatically creates:
- `${nixarr.mediaDir}/library/shows`

---

## Setup Notes

After enabling, access the web UI and:
1. Set up authentication (Forms method recommended)
2. Go to Settings > Media Management > Show Advanced
3. Enable "Use Hardlinks instead of Copy"
4. Set `chmod Folder` to `775`
5. Add Root Folder: `/data/media/library/shows/`
6. Add Transmission as download client with category `sonarr`

---

## Example

```nix
nixarr.sonarr = {
  enable = true;
  port = 8989;
};
```
