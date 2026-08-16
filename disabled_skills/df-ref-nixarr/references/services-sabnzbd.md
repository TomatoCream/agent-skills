---
name: nixarr SABnzbd Options
description: Usenet downloader with automatic category sorting
---

# nixarr SABnzbd Options

## Basic Options

```nix
nixarr.sabnzbd = {
  enable = mkEnableOption "Enable the SABnzbd service.";
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/sabnzbd";
  };
  
  package = mkPackageOption pkgs "sabnzbd" {};
  
  guiPort = mkOption {
    type = types.port;
    default = 6336;
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.sabnzbd.vpn.enable;
  };
  
  vpn.enable = mkOption { type = types.bool; default = false; };
};
```

---

## `nixarr.sabnzbd.whitelistHostnames`

```nix
nixarr.sabnzbd.whitelistHostnames = mkOption {
  type = types.listOf types.str;
  default = [config.networking.hostName];
  example = ["mediaserv" "media.example.com"];
};
```

URLs allowed to represent your SABnzbd instance (prevents DNS hijacking).

If you see `Refused connection with hostname "your.hostname.com"`, add your hostname to this list.

---

## `nixarr.sabnzbd.whitelistRanges`

```nix
nixarr.sabnzbd.whitelistRanges = mkOption {
  type = types.listOf types.str;
  default = [];
  example = ["192.168.1.0/24" "10.0.0.0/23"];
};
```

IP ranges allowed to connect to SABnzbd's web GUI.

---

## `nixarr.sabnzbd.vpn.enable`

Route SABnzbd traffic through VPN. Requires `nixarr.vpn.enable`.

---

## Directory Structure

```
${nixarr.mediaDir}/usenet/
├── .incomplete/   # Incomplete downloads
├── .watch/        # Watch folder
├── manual/         # Manual downloads
├── lidarr/         # Lidarr category
├── radarr/         # Radarr category
├── sonarr/         # Sonarr category
└── readarr/        # Readarr category
```

---

## Example

```nix
nixarr.sabnzbd = {
  enable = true;
  guiPort = 6336;
  vpn.enable = true;
  whitelistHostnames = ["mediaserv" "media.example.com"];
  whitelistRanges = ["192.168.1.0/24"];
};
```
