---
name: nixarr Directory Structure
description: Media library and state directory layout
---

# nixarr Directory Structure

## Default Paths

| Path | Description |
|------|-------------|
| `/data/media` | Media files (default, configurable) |
| `/data/.state/nixarr` | Service state (default, configurable) |

---

## Media Directory (`mediaDir`)

```
${nixarr.mediaDir}/
├── library/
│   ├── movies/      # Radarr
│   ├── shows/       # Sonarr
│   ├── music/       # Lidarr
│   ├── books/       # Readarr, Komga
│   ├── audiobooks/  # Audiobookshelf, Readarr Audiobook
│   └── xxx/         # Whisparr (adult content)
├── torrents/        # Transmission downloads
│   ├── .incomplete/
│   ├── .watch/
│   ├── manual/
│   ├── lidarr/
│   ├── radarr/
│   ├── sonarr/
│   └── readarr/
└── usenet/          # SABnzbd downloads
    ├── .incomplete/
    ├── .watch/
    ├── manual/
    ├── lidarr/
    ├── radarr/
    ├── sonarr/
    └── readarr/
```

---

## State Directory (`stateDir`)

```
${nixarr.stateDir}/
├── transmission/
├── radarr/
├── sonarr/
├── lidarr/
├── readarr/
├── readarr-audiobook/
├── prowlarr/
├── bazarr/
├── jellyfin/
├── plex/
├── jellyseerr/
├── audiobookshelf/
├── komga/
├── autobrr/
├── recyclarr/
├── cross-seed/
├── sabnzbd/
├── whisparr/
└── api-keys/        # Generated API keys
    ├── radarr.key
    └── sonarr.key
```

---

## Backup Strategy

Only backup:
1. `${nixarr.mediaDir}` - Your media files
2. `${nixarr.stateDir}` - Service databases and configs

All state is centralized, making backups simple.

---

## Custom Paths

> **Warning:** Custom paths must NOT be under user-owned directories like `/home/user`.

```nix
nixarr = {
  mediaDir = "/mnt/mediaserver/media";
  stateDir = "/mnt/mediaserver/.state/nixarr";
};
```

---

## Permissions

- Media directories: `0775` owned by `media` group
- State directories: `0700` owned by respective service users
- API keys: `0600` owned by respective service users
