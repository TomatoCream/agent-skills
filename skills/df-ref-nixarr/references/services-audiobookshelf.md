---
name: nixarr Audiobookshelf Options
description: Self-hosted audiobook and podcast server
---

# nixarr Audiobookshelf Options

## Basic Options

```nix
nixarr.audiobookshelf = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "audiobookshelf" {};
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/audiobookshelf";
  };
  
  port = mkOption {
    type = types.port;
    default = 9292;
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.audiobookshelf.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.audiobookshelf.vpn.enable`

Route Audiobookshelf traffic through VPN. **Conflicts with** `expose.https.enable`.

---

## `nixarr.audiobookshelf.expose.https`

```nix
nixarr.audiobookshelf.expose.https = {
  enable = mkOption { type = types.bool; default = false; };
  
  upnp.enable = mkEnableOption "UPNP for ports 80/443";
  
  domainName = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "audiobooks.example.com";
  };
  
  acmeMail = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "mail@example.com";
  };
};
```

Expose Audiobookshelf to the internet with HTTPS. **Conflicts with** `vpn.enable`.

---

## Media Directories

Audiobookshelf automatically creates:
- `${nixarr.mediaDir}/library/audiobooks`
- `${nixarr.mediaDir}/library/podcasts`

---

## Example

```nix
nixarr.audiobookshelf = {
  enable = true;
  port = 9292;
  vpn.enable = true;
};
```

---

## Conflict

Audiobookshelf and Plex are mutually exclusive.
