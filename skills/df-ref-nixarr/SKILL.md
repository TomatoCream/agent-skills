---
name: nixarr
description: NixOS module for self-hosted home media server with VPN support, automatic directory/user management, and state management
---

# Nixarr Skill

A NixOS module that makes installing and managing a home media server easy and pain-free.

## Features

- **VPN Support**: Run services through a VPN using WireGuard
- **Automatic Management**: Creates directories, users, and sets sane permissions automatically
- **State Management**: All services store state in `/data/.state/nixarr/*`
- **Dynamic DNS**: Optional Njalla DDNS support
- **Auto Port Forwarding**: UPNP support for automatic router port mapping

## References

### Core Options

| Category | Reference | Description |
|----------|-----------|-------------|
| Core | [nixarr-core](core-nixarr-core.md) | Master enable, mediaDir, stateDir, mediaUsers |
| Core | [nixarr-vpn](core-nixarr-vpn.md) | VPN enable, wgConf, accessibleFrom, test service |
| Core | [nixarr-structure](core-nixarr-structure.md) | Directory structure, media layout |

### Services

| Category | Reference | Description |
|----------|-----------|-------------|
| Media | [service-jellyfin](services-jellyfin.md) | Jellyfin media server |
| Media | [service-plex](services-plex.md) | Plex media server |
| Download | [service-transmission](services-transmission.md) | BitTorrent client with VPN, cross-seed |
| Download | [service-sabnzbd](services-sabnzbd.md) | Usenet downloader |
| *Arrs | [service-radarr](services-radarr.md) | Movie collection manager |
| *Arrs | [service-sonarr](services-sonarr.md) | TV show collection manager |
| *Arrs | [service-lidarr](services-lidarr.md) | Music collection manager |
| *Arrs | [service-readarr](services-readarr.md) | Ebook collection manager |
| *Arrs | [service-bazarr](services-bazarr.md) | Subtitle downloader |
| *Arrs | [service-whisparr](services-whisparr.md) | Adult content manager |
| *Arrs | [service-prowlarr](services-prowlarr.md) | Indexer aggregator |
| *Arrs | [service-recyclarr](services-recyclarr.md) | Custom format syncer |
| Library | [service-audiobookshelf](services-audiobookshelf.md) | Audiobook server |
| Library | [service-komga](services-komga.md) | Comics/manga server |
| Request | [service-jellyseerr](services-jellyseerr.md) | Jellyfin request manager |
| Automation | [service-autobrr](services-autobrr.md) | IRC/autodl automation |

### Networking

| Category | Reference | Description |
|----------|-----------|-------------|
| Net | [networking-ddns](networking-ddns.md) | Njalla dynamic DNS |
| Net | [networking-expose](networking-expose.md) | Exposing services (HTTPS, SSH tunnel) |
| Net | [networking-openssh-vpn](networking-openssh-vpn.md) | SSH via VPN |

### Configuration

| Category | Reference | Description |
|----------|-----------|-------------|
| Config | [config-example](config-example.md) | Full example configuration |
| Config | [config-secrets](config-secrets.md) | Secrets management |

## Quick Start

```nix
{
  inputs.nixarr.url = "github:nix-media-server/nixarr";
  
  outputs = { nixarr, ... }: {
    nixosConfigurations.servarr = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
        nixarr.nixosModules.default
      ];
      specialArgs = { inherit inputs; };
    };
  };
}
```

## Default Ports

| Service | Port |
|---------|------|
| Jellyfin | 8096 |
| Plex | 32400 |
| Transmission | 9091 (UI), 50000 (peer) |
| SABnzbd | 6336 |
| Radarr | 7878 |
| Sonarr | 8989 |
| Lidarr | 8686 |
| Readarr | 8787 |
| Readarr Audiobook | 9494 |
| Bazarr | 6767 |
| Whisparr | 6969 |
| Prowlarr | 9696 |
| Jellyseerr | 5055 |
| Audiobookshelf | 9292 |
| Komga | 25600 |
| Autobrr | 7474 |
