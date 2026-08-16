---
name: nixarr Readarr Audiobook Options
description: Ebook audiobook manager (separate instance from Readarr)
---

# nixarr Readarr Audiobook Options

## Basic Options

```nix
nixarr.readarr-audiobook = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "readarr" {};
  
  port = mkOption {
    type = types.port;
    default = 9494;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/readarr-audiobook";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.readarr-audiobook.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.readarr-audiobook.vpn.enable`

Route Readarr Audiobook traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Why Separate from Readarr?

Readarr and Readarr Audiobook are separate services because the standard approach for querying both ebooks and audiobooks is to run two instances.

---

## Media Directories

Readarr Audiobook automatically creates:
- `${nixarr.mediaDir}/library/audiobooks`

---

## Example

```nix
nixarr.readarr-audiobook = {
  enable = true;
  port = 9494;
};
```
