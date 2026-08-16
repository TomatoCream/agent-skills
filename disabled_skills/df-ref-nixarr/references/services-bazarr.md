---
name: nixarr Bazarr Options
description: Subtitle downloader for movies and TV shows
---

# nixarr Bazarr Options

## Basic Options

```nix
nixarr.bazarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "bazarr" {};
  
  port = mkOption {
    type = types.port;
    default = 6767;
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/bazarr";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.bazarr.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.bazarr.vpn.enable`

Route Bazarr traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Setup Notes

After enabling:
1. Access web UI at port 6767
2. Go to Settings > Languages
   - Select preferred languages
   - Add language profile for Series and Movies
3. Go to Settings > Sonarr and Settings > Radarr
   - Add respective instances
   - Get API key via `sudo nixarr list-api-keys`
   - Test connection and save
4. Go to Settings > Providers
   - Enable desired subtitle providers

---

## Recommendations

- Set `Unmonitor Deleted Subtitles` to true (Settings > General)
- Enable `Automatic Subtitles Audio Synchronization` (Settings > Subtitles)

---

## Example

```nix
nixarr.bazarr = {
  enable = true;
  port = 6767;
};
```
