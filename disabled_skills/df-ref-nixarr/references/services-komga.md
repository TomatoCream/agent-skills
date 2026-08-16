---
name: nixarr Komga Options
description: Media server for comics and manga libraries
---

# nixarr Komga Options

## Basic Options

```nix
nixarr.komga = {
  enable = mkOption { type = types.bool; default = false; };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/komga";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.komga.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

**Note:** Komga uses a fixed port `25600`.

---

## `nixarr.komga.vpn.enable`

Route Komga traffic through VPN. **Conflicts with** `expose.https.enable`.

---

## `nixarr.komga.expose.https`

```nix
nixarr.komga.expose.https = {
  enable = mkOption { type = types.bool; default = false; };
  
  upnp.enable = mkEnableOption "UPNP for ports 80/443";
  
  domainName = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "komga.example.com";
  };
  
  acmeMail = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "mail@example.com";
  };
};
```

Expose Komga to the internet with HTTPS. **Conflicts with** `vpn.enable`.

---

## Media Directories

Komga automatically creates:
- `${nixarr.mediaDir}/library/books`

---

## Example

```nix
nixarr.komga = {
  enable = true;
  expose.https = {
    enable = true;
    domainName = "komga.example.com";
    acmeMail = "admin@example.com";
  };
};
```

---

## Conflict

Komga and Plex are mutually exclusive.
