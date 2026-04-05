---
description: Declarative secret management for NixOS using sops encryption
source: https://github.com/Mic92/sops-nix
---

# sops-nix Overview

sops-nix provides atomic, declarative, and reproducible secret provisioning for NixOS based on [sops](https://github.com/mozilla/sops). Secrets are decrypted during activation time and stored as one secret per file with fully declarative permission control.

## Core Features

- **Encryption methods**: GPG and age (SSH Ed25519/RSA key conversion supported)
- **Deployment compatibility**: NixOps, nixos-rebuild, krops, morph, nixus, flakes
- **Version-control friendly**: Encrypted files can be committed directly
- **CI-friendly**: Secrets can be added to Nix store without leaking
- **Atomic upgrades**: New secrets written to new directory, replaced atomically
- **Home-manager support**: User-level secret management module
- **Formats**: YAML, JSON, INI, dotenv, binary

## Quick Start (Flakes)

```nix
{
  inputs.sops-nix.url = "github:Mic92/sops-nix";
  inputs.sops-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, sops-nix }: {
    nixosConfigurations.yourhostname = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        sops-nix.nixosModules.sops
      ];
    };
  };
}
```

## Basic Configuration

```nix
{
  sops.defaultSopsFile = ./secrets/example.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
  sops.age.keyFile = "/var/lib/sops-nix/key.txt";
  sops.age.generateKey = true;

  sops.secrets.example-key = {};
  sops.secrets."myservice/my_subdir/my_secret" = {};
}
```

Secrets are available at `/run/secrets/example-key` after activation.