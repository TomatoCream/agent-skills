---
name: nixarr Jellyseerr Options
description: Request manager for Jellyfin media server
---

# nixarr Jellyseerr Options

## Basic Options

```nix
nixarr.jellyseerr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "jellyseerr" {};
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/jellyseerr";
  };
  
  port = mkOption {
    type = types.port;
    default = 5055;
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.jellyseerr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.jellyseerr.vpn.enable`

Route Jellyseerr traffic through VPN. **Conflicts with** `expose.https.enable`.

---

## `nixarr.jellyseerr.expose.https`

```nix
nixarr.jellyseerr.expose.https = {
  enable = mkOption { type = types.bool; default = false; };
  
  upnp.enable = mkEnableOption "UPNP for ports 80/443";
  
  domainName = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "jellyseerr.example.com";
  };
  
  acmeMail = mkOption {
    type = types.nullOr types.str;
    default = null;
    example = "mail@example.com";
  };
};
```

Expose Jellyseerr to the internet with HTTPS. **Conflicts with** `vpn.enable`.

---

## Setup Notes

1. Access web UI at port 5055
2. Follow installation wizard:
   - Choose Jellyfin (or Plex)
   - Add Jellyfin URL, username & password
   - Sync Libraries toggle Movies and Shows
   - Add Radarr and Sonarr apps
3. Get API key: `sudo nixarr list-api-keys`

---

## Example

```nix
nixarr.jellyseerr = {
  enable = true;
  expose.https = {
    enable = true;
    domainName = "requests.example.com";
    acmeMail = "admin@example.com";
  };
};
```
