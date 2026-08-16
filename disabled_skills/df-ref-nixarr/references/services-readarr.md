---
name: nixarr Readarr Options
description: Ebook collection manager for automatic ebook downloading and management
---

# nixarr Readarr Options

## Basic Options

```nix
nixarr.readarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "readarr" {};
  
  port = mkOption {
    type = types.port;
    default = 8787;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/readarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.readarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.readarr.vpn.enable`

Route Readarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Media Directories

Readarr automatically creates:
- `${nixarr.mediaDir}/library/books`

---

## Example

```nix
nixarr.readarr = {
  enable = true;
  port = 8787;
};
```
