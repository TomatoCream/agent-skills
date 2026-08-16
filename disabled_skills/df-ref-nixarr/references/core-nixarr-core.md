---
name: nixarr Core Options
description: Master options for the nixarr module including enable, mediaDir, stateDir, and mediaUsers
---

# nixarr Core Options

## `nixarr.enable`

```nix
nixarr.enable = mkOption {
  type = types.bool;
  default = false;
  example = true;
};
```

Enable the nixarr module. Required before any service options take effect.

**Supported services when enabled:**
- Audiobookshelf, Autobrr, Bazarr, Jellyfin, Jellyseerr, Lidarr, Plex, Prowlarr, Radarr, Readarr, Readarr Audiobook, Recyclarr, SABnzbd, Sonarr, Transmission, Whisparr

---

## `nixarr.mediaDir`

```nix
nixarr.mediaDir = mkOption {
  type = types.path;
  default = "/data/media";
  example = "/mnt/media";
};
```

Location for media files. Module creates subdirectories automatically.

> **Warning:** Path must not be under a user-owned directory (e.g., `/home/user`)

**Default subdirectories:**
- `library/movies` - Radarr
- `library/shows` - Sonarr
- `library/music` - Lidarr
- `library/books` - Readarr
- `library/audiobooks` - Audiobookshelf
- `library/xxx` - Whisparr
- `torrents/` - Transmission downloads
- `usenet/` - SABnzbd downloads

---

## `nixarr.stateDir`

```nix
nixarr.stateDir = mkOption {
  type = types.path;
  default = "/data/.state/nixarr";
  example = "/data/media/.state/nixarr";
};
```

Location for service state (databases, configs). Only need to backup this + media directory.

> **Warning:** Path must not be under a user-owned directory

---

## `nixarr.mediaUsers`

```nix
nixarr.mediaUsers = mkOption {
  type = with types; listOf str;
  default = [];
  example = ["additionaluser"];
};
```

Extra users to add to the media group for shared access.

---

## Example Configuration

```nix
nixarr = {
  enable = true;
  mediaDir = "/data/media";
  stateDir = "/data/.state/nixarr";
  mediaUsers = ["familyuser"];
};
```
