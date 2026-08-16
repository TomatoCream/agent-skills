---
name: nixarr Prowlarr Options
description: Indexer aggregator for managing torrent and usenet indexers
---

# nixarr Prowlarr Options

## Basic Options

```nix
nixarr.prowlarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "prowlarr" {};
  
  port = mkOption {
    type = types.port;
    default = 9696;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/prowlarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.prowlarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.prowlarr.vpn.enable`

Route Prowlarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Usage Notes

Prowlarr aggregates indexers for the other *Arrs. After setup:
1. Access web UI at port 9696
2. Set up authentication
3. Add indexers via Settings > Apps
4. Connect to Radarr/Sonarr/etc via API

**Get API key:**
```bash
sudo nixarr list-api-keys
```

---

## Example

```nix
nixarr.prowlarr = {
  enable = true;
  port = 9696;
  vpn.enable = false;
};
```
