---
description: YAML, JSON, INI, dotenv, and binary secret file formats
source: https://github.com/Mic92/sops-nix#different-file-formats
---

# Secret File Formats

sops-nix supports multiple encrypted file formats.

## YAML

```yaml
github_token: 4a6c73f74928a9c4c4bc47379256b72e598e2bd3
ssh_key: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...
  -----END OPENSSH PRIVATE KEY-----
```

```nix
{
  sops.defaultSopsFile = ./secrets.yaml;
  sops.secrets.github_token.format = "yaml";
}
```

## JSON

```json
{
  "github_token": "4a6c73f74928a9c4c4bc47379256b72e598e2bd3"
}
```

```nix
{
  sops.defaultSopsFormat = "json";
  sops.secrets.github_token = {
    format = "json";
    sopsFile = ./secrets.json;
  };
}
```

## INI/Dotenv

Secrets stored as `key=value` pairs in `.env` files.

## Binary

For arbitrary binary files (e.g., kerberos keytabs):

```console
$ sops -e /etc/krb5/krb5.keytab > krb5.keytab
```

```nix
{
  sops.secrets.krb5-keytab = {
    format = "binary";
    sopsFile = ./krb5.keytab;
  };
}
```

## Plain File Extraction

To extract entire YAML/JSON files without key extraction:

```nix
{
  sops.secrets.my-config = {
    format = "yaml";
    sopsFile = ./my-config.yaml;
    key = "";
  };
}
```