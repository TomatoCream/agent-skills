---
description: Configure age encryption with SSH keys or file-based keys
source: https://github.com/Mic92/sops-nix#supported-encryption-methods
---

# age Encryption

sops-nix supports `age` encryption using [`age`](https://github.com/FiloSottile/age) tool.

## SSH Key to age Conversion

Convert SSH Ed25519 keys to age format using `ssh-to-age`:

```console
$ nix-shell -p ssh-to-age --run "ssh-to-age -private-key -i ~/.ssh/id_ed25519 > ~/.config/sops/age/keys.txt"
```

Convert SSH host keys for machines:

```console
$ nix-shell -p ssh-to-age --run 'ssh-keyscan example.com | ssh-to-age'
age1rgffpespcyjn0d8jglk7km9kfrfhdyev6camd3rck6pn8y47ze4sug23v3
```

## Configuration

```nix
{
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
  sops.age.keyFile = "/var/lib/sops-nix/key.txt";
  sops.age.generateKey = true;
}
```

## Key Options

- `sshKeyPaths`: List of SSH key files to convert to age keys
- `keyFile`: Path to age private key file (must be passwordless)
- `generateKey`: Automatically generate key if `keyFile` doesn't exist