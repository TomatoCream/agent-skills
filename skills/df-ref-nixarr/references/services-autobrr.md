---
name: nixarr Autobrr Options
description: IRC and autodl automation for torrent downloading
---

# nixarr Autobrr Options

## Basic Options

```nix
nixarr.autobrr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "autobrr" {};
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.autobrr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/autobrr";
  };
};
```

---

## `nixarr.autobrr.vpn.enable`

Route Autobrr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## `nixarr.autobrr.settings`

```nix
nixarr.autobrr.settings = lib.mkOption {
  type = lib.types.submodule {freeformType = tomlFormat.type;};
  default = {
    host = "0.0.0.0";
    port = 7474;
    checkForUpdates = false;
  };
  example = {
    logLevel = "DEBUG";
  };
};
```

Autobrr configuration in TOML format.

**Default port:** 7474

> **Note:** `sessionSecret` is auto-generated on first installation.

See [Autobrr configuration docs](https://autobrr.com/configuration/autobrr) for full options.

---

## Example

```nix
nixarr.autobrr = {
  enable = true;
  vpn.enable = true;
  settings = {
    host = "0.0.0.0";
    port = 7474;
    checkForUpdates = false;
    logLevel = "DEBUG";
  };
};
```
