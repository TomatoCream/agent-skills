---
name: nixarr Complete Example
description: Full nixarr configuration example with all common options
---

# nixarr Complete Example

## Basic Setup with VPN

```nix
{
  inputs.nixarr.url = "github:nix-media-server/nixarr";
  
  outputs = { nixarr, ... }: {
    nixosConfigurations.servarr = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        nixarr.nixosModules.default
      ];
      specialArgs = { inherit inputs; };
    };
  };
}
```

---

## Full Configuration Example

```nix
nixarr = {
  enable = true;
  mediaDir = "/data/media";
  stateDir = "/data/.state/nixarr";
  mediaUsers = ["familyuser"];

  # VPN Configuration
  vpn = {
    enable = true;
    wgConf = "/data/.secret/wg.conf";
    accessibleFrom = ["192.168.2.0/24"];
    
    vpnTestService = {
      enable = true;
      port = 58403;
    };
  };

  # Media Server (choose ONE)
  jellyfin = {
    enable = true;
    expose.https = {
      enable = true;
      domainName = "jellyfin.example.com";
      acmeMail = "admin@example.com";
      upnp.enable = true;
    };
  };

  # OR Plex instead of Jellyfin
  # plex = {
  #   enable = true;
  #   expose.https = {
  #     enable = true;
  #     domainName = "plex.example.com";
  #     acmeMail = "admin@example.com";
  #   };
  # };

  # Download Clients
  transmission = {
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
  };

  sabnzbd = {
    enable = true;
    vpn.enable = true;
    guiPort = 6336;
    whitelistHostnames = ["mediaserv"];
    whitelistRanges = ["192.168.1.0/24"];
  };

  # *Arrs (Media Management)
  prowlarr = {
    enable = true;
    port = 9696;
  };

  radarr = {
    enable = true;
    port = 7878;
  };

  sonarr = {
    enable = true;
    port = 8989;
  };

  lidarr = {
    enable = true;
    port = 8686;
  };

  readarr = {
    enable = true;
    port = 8787;
  };

  readarr-audiobook = {
    enable = true;
    port = 9494;
  };

  bazarr = {
    enable = true;
    port = 6767;
  };

  whisparr = {
    enable = true;
    port = 6969;
  };

  # Custom Format Sync
  recyclarr = {
    enable = true;
    schedule = "daily";
    configuration = {
      sonarr = {
        series = {
          base_url = "http://localhost:8989";
          api_key = "!env_var SONARR_API_KEY";
          quality_definition = { type = "series"; };
          delete_old_custom_formats = true;
        };
      };
      radarr = {
        movies = {
          base_url = "http://localhost:7878";
          api_key = "!env_var RADARR_API_KEY";
          quality_definition = { type = "movie"; };
        };
      };
    };
  };

  # Request Management
  jellyseerr = {
    enable = true;
    expose.https = {
      enable = true;
      domainName = "requests.example.com";
      acmeMail = "admin@example.com";
    };
  };

  # Additional Services
  autobrr = {
    enable = true;
    vpn.enable = true;
    settings = {
      port = 7474;
      logLevel = "INFO";
    };
  };

  # Library Servers
  audiobookshelf = {
    enable = true;
    port = 9292;
  };

  komga = {
    enable = true;
    expose.https = {
      enable = true;
      domainName = "komga.example.com";
      acmeMail = "admin@example.com";
    };
  };

  # Dynamic DNS
  ddns.njalla = {
    enable = true;
    keysFile = "/data/.secret/njalla/keys.json";
  };
};
```

---

## Ports Summary

| Service | Port | VPN | HTTPS Expose |
|---------|------|-----|--------------|
| Jellyfin | 8096 | Yes | Yes |
| Plex | 32400 | Yes | Yes |
| Transmission UI | 9091 | Yes | No |
| Transmission Peer | 50000 | Yes | No |
| SABnzbd | 6336 | Yes | No |
| Radarr | 7878 | Yes | No |
| Sonarr | 8989 | Yes | No |
| Lidarr | 8686 | Yes | No |
| Readarr | 8787 | Yes | No |
| Readarr Audiobook | 9494 | Yes | No |
| Bazarr | 6767 | Yes | No |
| Whisparr | 6969 | Yes | No |
| Prowlarr | 9696 | Yes | No |
| Jellyseerr | 5055 | Yes | Yes |
| Autobrr | 7474 | Yes | No |
| Audiobookshelf | 9292 | Yes | Yes |
| Komga | 25600 | Yes | Yes |
