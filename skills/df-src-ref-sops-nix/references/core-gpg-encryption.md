---
description: Configure GPG encryption with ssh-to-pgp key conversion
source: https://github.com/Mic92/sops-nix#use-with-gpg-instead-of-ssh-keys
---

# GPG Encryption

sops-nix supports GPG encryption using [`ssh-to-pgp`](https://github.com/Mic92/ssh-to-pgp) for SSH RSA key conversion.

## Generate or Convert Keys

From SSH RSA key:

```console
$ ssh root@server01 "cat /etc/ssh/ssh_host_rsa_key" | nix-shell -p ssh-to-pgp --run "ssh-to-pgp -o server01.asc"
```

From unencrypted SSH key:

```console
$ nix-shell -p gnupg -p ssh-to-pgp --run "ssh-to-pgp -private-key -i $HOME/.ssh/id_rsa | gpg --import --quiet"
```

## Configuration

```nix
{
  sops.gnupg.home = "/var/lib/sops";
  sops.gnupg.sshKeyPaths = [];
}
```

## GPG Key Import Hook

For team usage, use the nix-shell hook:

```nix
{
  sopsPGPKeyDirs = [
    "${toString ./.}/keys/hosts"
    "${toString ./.}/keys/users"
  ];
}
```

## Known Issues

GnuPG is not great software and may break in various ways. For stable production use, prefer SSH keys or KMS services.