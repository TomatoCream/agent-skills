# Deployment & Secrets

## deploy-rs

GitHub: https://github.com/serokell/deploy-rs

Multi-profile, magic rollback, flake-native.

```nix
{
  inputs.deploy-rs.url = "github:serokell/deploy-rs";
  outputs = { self, nixpkgs, deploy-rs }: {
    nixosConfigurations.myserver = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [ ./configuration.nix ];
    };
    deploy.nodes.myserver = {
      hostname = "myserver.example.com";
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos
          self.nixosConfigurations.myserver;
      };
    };
    checks = builtins.mapAttrs
      (system: deployLib: deployLib.deployChecks self.deploy) deploy-rs.lib;
  };
}
```

```bash
nix run github:serokell/deploy-rs            # deploy all
nix run github:serokell/deploy-rs -- .#myserver  # deploy one
```

## Colmena

GitHub: https://github.com/zhaofengli/colmena

Stateless, parallel, Rust. Tag-based filtering.

```nix
{
  inputs.colmena.url = "github:zhaofengli/colmena";
  outputs = { nixpkgs, colmena, ... }: {
    colmenaHive = colmena.lib.makeHive {
      meta.nixpkgs = import nixpkgs { system = "x86_64-linux"; };
      web-server = {
        deployment.targetHost = "web.example.com";
        deployment.targetUser = "root";
        services.nginx.enable = true;
      };
      db-server = {
        deployment.targetHost = "db.example.com";
        services.postgresql.enable = true;
      };
    };
  };
}
```

```bash
colmena apply                  # deploy all
colmena apply --on web-server  # deploy one
```

## Other Deployment Tools

| Tool | GitHub | Use When |
|------|--------|----------|
| Clan | https://github.com/clan-lol/clan-core | P2P deploy + built-in secrets + VPN |
| comin | https://github.com/nlewo/comin | GitOps pull model (no SSH needed) |
| Nixinate | https://github.com/MatthewCroughan/nixinate | Simple SSH, generates `nix run .#nixinate.host` |
| NixOps | https://github.com/NixOS/nixops | AWS/Hetzner/cloud, official tool |
| krops | https://cgit.krebsco.de/krops | Minimal, rsync-based |

---

## sops-nix

GitHub: https://github.com/Mic92/sops-nix

Multi-backend (GPG, age, AWS/GCP/Azure KMS, Vault). Atomic provisioning.

```nix
# NixOS module
{
  sops.defaultSopsFile = ./secrets/secrets.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
  sops.age.keyFile = "/var/lib/sops-nix/key.txt";
  sops.age.generateKey = true;

  sops.secrets.db-password = {};
  sops.secrets."myapp/api-key" = { owner = "myapp"; };
}
# Secrets available at /run/secrets/db-password, /run/secrets/myapp/api-key
```

```bash
sops secrets/secrets.yaml  # create/edit encrypted file
```

## agenix

GitHub: https://github.com/ryantm/agenix

Simple. age + SSH keys only.

**secrets.nix:**
```nix
let
  user = "ssh-ed25519 AAAAC3...";
  server = "ssh-ed25519 AAAAC3...";
in {
  "db-password.age".publicKeys = [ user server ];
}
```

```bash
agenix -e db-password.age  # encrypt a secret
```

**configuration.nix:**
```nix
{ age.secrets.db-password.file = ../secrets/db-password.age; }
# Available at /run/agenix/db-password
```

## When to use which

- **sops-nix** -- teams, cloud KMS, multiple backends, complex setups
- **agenix** -- personal/small team, SSH keys only, simpler
