---
name: nixarr Jellyfin Options
description: Media server for streaming movies, TV shows, music, and audiobooks
---

# nixarr Jellyfin Options

## Basic Options

```nix
nixarr.jellyfin = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "jellyfin" {};
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/jellyfin";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.jellyfin.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.jellyfin.vpn.enable`

Route Jellyfin traffic through VPN. **Conflicts with** `nixarr.jellyfin.expose.https.enable`.

---

## `nixarr.jellyfin.expose.https`

```nix
nixarr.jellyfin.expose.https = {
  enable = mkOption { type = types.bool; default = false; };
  
  upnp.enable = mkEnableOption "UPNP for ports 80/443";
  
  domainName = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "jellyfin.example.com";
  };
  
  acmeMail = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "mail@example.com";
  };
};
```

Expose Jellyfin to the internet with HTTPS. **Conflicts with** `vpn.enable`.

**Requires:**
- `domainName` - Your domain
- `acmeMail` - Email for Let's Encrypt

**Optional:**
- `upnp.enable` - Auto-open ports 80/443 on router

> **Warning:** Do NOT enable without setting up Jellyfin authentication first!

---

## Media Directories

Jellyfin automatically creates:
- `${nixarr.mediaDir}/library/shows`
- `${nixarr.mediaDir}/library/movies`
- `${nixarr.mediaDir}/library/music`
- `${nixarr.mediaDir}/library/books`
- `${nixarr.mediaDir}/library/audiobooks`

---

## Example

```nix
# Basic with VPN
nixarr.jellyfin = {
  enable = true;
  vpn.enable = true;
};

# Internet-exposed with HTTPS
nixarr.jellyfin = {
  enable = true;
  expose.https = {
    enable = true;
    domainName = "jellyfin.example.com";
    acmeMail = "admin@example.com";
    upnp.enable = true;
  };
};
```

---

## Conflict

Jellyfin and Plex are mutually exclusive (`nixarr.jellyfin.enable` vs `nixarr.plex.enable`).
