---
name: nixarr Transmission Options
description: BitTorrent client with VPN support, flood UI, and cross-seed integration
---

# nixarr Transmission Options

## Basic Options

```nix
nixarr.transmission = {
  enable = mkOption { type = types.bool; default = false; };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/transmission";
  };
  
  openFirewall = mkOption {
    type = types.bool;
    default = !nixarr.transmission.vpn.enable;
  };
  
  peerPort = mkOption {
    type = types.port;
    default = 50000;
  };
  
  uiPort = mkOption {
    type = types.port;
    default = 9091;
  };
  
  extraSettings = mkOption {
    type = types.attrs;
    default = {};
  };
};
```

---

## `nixarr.transmission.vpn.enable`

Route Transmission traffic through VPN. Requires `nixarr.vpn.enable`.

---

## `nixarr.transmission.flood.enable`

Enable [Flood](https://github.com/jesee/flood) web UI for Transmission instead of default UI.

---

## `nixarr.transmission.privateTrackers.disableDhtPex`

```nix
nixarr.transmission.privateTrackers.disableDhtPex = mkOption {
  type = types.bool;
  default = false;
};
```

Disable PEX and DHT. Required for some private trackers.

---

## `nixarr.transmission.privateTrackers.cross-seed`

```nix
nixarr.transmission.privateTrackers.cross-seed = {
  enable = mkOption { type = types.bool; default = false; };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/cross-seed";
  };
  
  indexIds = mkOption {
    type = with types; listOf int;
    default = [];
    example = [1 3 7];
  };
  
  extraSettings = mkOption {
    type = types.attrs;
    default = {};
  };
};
```

Enable [cross-seed](https://www.cross-seed.org/) to automatically find and inject torrents from your existing library.

**Requires:** `nixarr.prowlarr.enable`

**indexIds:** List of indexer IDs from Prowlarr RSS links (the number in `/1/api?apikey=...`)

---

## `nixarr.transmission.credentialsFile`

```nix
nixarr.transmission.credentialsFile = mkOption {
  type = types.path;
  default = "/dev/null";
  example = "/var/lib/secrets/transmission/settings.json";
};
```

Path to JSON file with secret config (e.g., `rpc-password`). Merged with settings.

---

## `nixarr.transmission.extraAllowedIps`

```nix
nixarr.transmission.extraAllowedIps = mkOption {
  type = with types; listOf str;
  default = [];
};
```

Extra IPs allowed to access Transmission RPC (beyond default `192.168.*` and `127.0.0.1`).

---

## `nixarr.transmission.messageLevel`

```nix
nixarr.transmission.messageLevel = mkOption {
  type = types.enum ["none" "critical" "error" "warn" "info" "debug" "trace"];
  default = "warn";
};
```

Logging level for Transmission.

---

## Directory Structure

```
${nixarr.mediaDir}/torrents/
├── .incomplete/     # Incomplete downloads
├── .watch/          # Watch folder for auto-import
├── manual/          # Manual downloads
├── lidarr/          # Lidarr categories
├── radarr/          # Radarr categories
├── sonarr/          # Sonarr categories
└── readarr/         # Readarr categories
```

---

## Example

```nix
nixarr.transmission = {
  enable = true;
  vpn.enable = true;
  peerPort = 50000;
  
  privateTrackers = {
    disableDhtPex = true;
    cross-seed = {
      enable = true;
      indexIds = [1 3];
    };
  };
  
  extraSettings = {
    trash-original-torrent-files = true;
  };
};
```
