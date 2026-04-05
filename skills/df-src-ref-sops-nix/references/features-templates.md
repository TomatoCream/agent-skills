---
description: Inline secrets into configuration files during activation
source: https://github.com/Mic92/sops-nix#templates
---

# Template Feature

Embed secrets into configuration files during activation using sops-nix templates.

## Basic Template

```nix
{
  sops.templates."your-config-with-secrets.toml".content = ''
    password = "${config.sops.placeholder.your-secret}"
  '';
}
```

## Template with Ownership

```nix
{
  sops.templates."your-config-with-secrets.toml".owner = "serviceuser";
}
```

## Use with Systemd Service

```nix
{
  systemd.services.myservice = {
    serviceConfig = {
      ExecStart = "${pkgs.myservice}/bin/myservice --config ${config.sops.templates."your-config-with-secrets.toml".path}";
      User = "serviceuser";
    };
  };
}
```

## Secret Declaration

```nix
{
  sops.secrets.your-secret = {};
}
```

Templates use `config.sops.placeholder.<secret-name>` to reference secrets.