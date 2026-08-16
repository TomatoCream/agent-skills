---
description: Declare secrets with permissions, symlinks, and service restart triggers
source: https://github.com/Mic92/sops-nix#set-secret-permissionowner-and-allow-services-to-access-it
---

# Secret Configuration

## Basic Secret Declaration

```nix
{
  sops.secrets.example-key = {};
  sops.secrets."myservice/my_subdir/my_secret" = {};
}
```

## Permission Configuration

```nix
{
  sops.secrets.example-secret.mode = "0440";
  sops.secrets.example-secret.owner = config.users.users.nobody.name;
  sops.secrets.example-secret.group = config.users.users.nobody.group;
}
```

## Symlinks to Custom Paths

```nix
{
  sops.secrets."home-assistant-secrets.yaml" = {
    owner = "hass";
    path = "/var/lib/hass/secrets.yaml";
  };
}
```

## Restart Services on Secret Change

```nix
{
  sops.secrets."home-assistant-secrets.yaml" = {
    restartUnits = [ "home-assistant.service" ];
    reloadUnits = [ "nginx.service" ];
  };
}
```

## Binary Secrets

```nix
{
  sops.secrets.krb5-keytab = {
    format = "binary";
    sopsFile = ./krb5.keytab;
  };
}
```

## Per-Secret sops File Override

```nix
{
  sops.secrets.github_token = {
    sopsFile = ./other-secrets.json;
    format = "json";
  };
}
```