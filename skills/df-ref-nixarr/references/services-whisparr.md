---
name: nixarr Whisparr Options
description: Adult content collection manager
---

# nixarr Whisparr Options

## Basic Options

```nix
nixarr.whisparr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "whisparr" {};
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/whisparr";
  };
  
  port = mkOption {
    type = types.port;
    default = 6969;
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.whisparr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.whisparr.vpn.enable`

Route Whisparr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Media Directories

Whisparr automatically creates:
- `${nixarr.mediaDir}/library/xxx`

---

## Example

```nix
nixarr.whisparr = {
  enable = true;
  port = 6969;
};
```
