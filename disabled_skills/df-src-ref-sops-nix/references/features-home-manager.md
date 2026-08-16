---
description: Systemd user service for home-manager based secret management
source: https://github.com/Mic92/sops-nix#use-with-home-manager
---

# Home Manager Integration

sops-nix provides a home-manager module that runs as a systemd user service.

## Module Import (Flakes)

```nix
{
  home-manager.sharedModules = [
    inputs.sops-nix.homeManagerModules.sops
  ];
}
```

## Module Import (Non-Flakes)

```nix
{
  imports = [
    <sops-nix/modules/home-manager/sops.nix>
  ];
}
```

## Configuration

```nix
{
  sops = {
    age.keyFile = "/home/user/.age-key.txt";
    defaultSopsFile = ./secrets.yaml;
    secrets.test = {
      path = "%r/test.txt";
    };
  };
}
```

## Service Ordering

Other user services must order after sops-nix:

```nix
{
  systemd.user.services.mbsync.Unit.After = [ "sops-nix.service" ];
}
```

## Secrets Location

- Decrypted to: `$XDG_RUNTIME_DIR/secrets.d`
- Symlinked to: `$HOME/.config/sops-nix/secrets`

## Qubes Split GPG

```nix
{
  sops = {
    gnupg.qubes-split-gpg = {
      enable = true;
      domain = "vault-gpg";
    };
    defaultSopsFile = ./secrets.yaml;
  };
}
```