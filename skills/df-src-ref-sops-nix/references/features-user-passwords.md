---
description: Decrypt secrets before NixOS user creation for hashedPasswordFile
source: https://github.com/Mic92/sops-nix#setting-a-users-password
---

# User Password Secrets

sops-nix runs after NixOS creates users, so `users.users.<name>.hashedPasswordFile` cannot directly use sops secrets. Use `neededForUsers = true` to decrypt to `/run/secrets-for-users` before user creation.

## Configuration

```nix
{ config, ... }: {
  sops.secrets.my-password.neededForUsers = true;

  users.users.mic92 = {
    isNormalUser = true;
    hashedPasswordFile = config.sops.secrets.my-password.path;
  };
}
```

## Impermanence Compatibility

When using Impermanence, ensure the key is persisted:

```nix
sops.age.keyFile = "/nix/persist/var/lib/sops-nix/key.txt";
```

Or ensure SSH keys are available early:

```nix
fileSystems."/etc/ssh".neededForBoot = true;
```

## Password Hash Generation

```console
$ echo "password" | mkpasswd -s
$y$j9T$WFoiErKnEnMcGq0ruQK4K.$4nJAY3LBeBsZBTYSkdTOejKU6KlDmhnfUV3Ll1K/1b.
```