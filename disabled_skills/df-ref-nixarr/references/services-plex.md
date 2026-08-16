---
name: nixarr Plex Options
description: Media server for streaming movies, TV shows, music, and photos
---

# nixarr Plex Options

## Basic Options

```nix
nixarr.plex = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "plex" {};
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/plex";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.plex.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.plex.vpn.enable`

Route Plex traffic through VPN. **Conflicts with** `nixarr.plex.expose.https.enable`.

---

## `nixarr.plex.expose.https`

```nix
nixarr.plex.expose.https = {
  enable = mkOption { type = types.bool; default = false; };
  
  upnp.enable = mkEnableOption "UPNP for ports 80/443";
  
  domainName = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "plex.example.com";
  };
  
  acmeMail = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "mail@example.com";
  };
};
```

Expose Plex to the internet with HTTPS. **Conflicts with** `vpn.enable`.

**Requires:**
- `domainName` - Your domain
- `acmeMail` - Email for Let's Encrypt

---

## Media Directories

Plex automatically creates:
- `${nixarr.mediaDir}/library/shows`
- `${nixarr.mediaDir}/library/movies`
- `${nixarr.mediaDir}/library/music`
- `${nixarr.mediaDir}/library/books`
- `${nixarr.mediaDir}/library/audiobooks`

---

## Example

```nix
# Internet-exposed with HTTPS
nixarr.plex = {
  enable = true;
  expose.https = {
    enable = true;
    domainName = "plex.example.com";
    acmeMail = "admin@example.com";
  };
};
```

---

## Conflict

Plex and Jellyfin are mutually exclusive.
