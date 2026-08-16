# sops-nix Skill

Atomic, declarative, and reproducible secret provisioning for NixOS based on sops encryption.

## References

### Core
| File | Description |
|------|-------------|
| [core-overview](references/core-overview.md) | Overview, features, and quick start |
| [core-age-encryption](references/core-age-encryption.md) | age encryption with SSH key conversion |
| [core-gpg-encryption](references/core-gpg-encryption.md) | GPG encryption setup |

### Features
| File | Description |
|------|-------------|
| [features-secret-configuration](references/features-secret-configuration.md) | Declare secrets with permissions and symlinks |
| [features-user-passwords](references/features-user-passwords.md) | User password secrets with neededForUsers |
| [features-home-manager](references/features-home-manager.md) | Home-manager integration |
| [features-file-formats](references/features-file-formats.md) | YAML, JSON, INI, dotenv, binary formats |
| [features-templates](references/features-templates.md) | Template injection into config files |

## Quick Start (Flakes)

```nix
{
  inputs.sops-nix.url = "github:Mic92/sops-nix";
  outputs = { self, nixpkgs, sops-nix }: {
    nixosConfigurations.yourhostname = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
        sops-nix.nixosModules.sops
      ];
    };
  };
}
```

## Basic Secret Usage

```nix
{
  sops.defaultSopsFile = ./secrets/example.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
  sops.age.generateKey = true;

  sops.secrets.example-key = {};
  # Access at /run/secrets/example-key
}
```