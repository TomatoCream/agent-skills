# Development Environments

## devenv

GitHub: https://github.com/cachix/devenv
Docs: https://devenv.sh/

Most feature-rich. 50+ languages, services, process management.

**Standalone devenv.nix:**
```nix
{ pkgs, ... }: {
  languages.python = { enable = true; version = "3.12"; };
  languages.rust.enable = true;
  services.postgres.enable = true;
  services.redis.enable = true;
  packages = [ pkgs.jq pkgs.curl ];
  enterShell = "echo 'ready'";
  processes.api.exec = "cargo run";
}
```

**With flakes:**
```nix
{
  inputs = {
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    devenv.url = "github:cachix/devenv";
  };
  outputs = { self, nixpkgs, devenv, ... } @ inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = devenv.lib.mkShell {
        inherit inputs pkgs;
        modules = [ ({ pkgs, ... }: {
          packages = [ pkgs.hello ];
          processes.run.exec = "hello";
        }) ];
      };
    };
}
```

**Quick start:** `nix flake init --template github:cachix/devenv#flake-parts`

## devshell

GitHub: https://github.com/numtide/devshell

Lighter. TOML config option. Clean env.

**flake.nix:**
```nix
{
  inputs.devshell.url = "github:numtide/devshell";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = { flake-utils, devshell, nixpkgs, ... }:
    flake-utils.lib.eachDefaultSystem (system: {
      devShell = let
        pkgs = import nixpkgs { inherit system; overlays = [ devshell.overlays.default ]; };
      in pkgs.devshell.mkShell {
        imports = [ (pkgs.devshell.importTOML ./devshell.toml) ];
      };
    });
}
```

**devshell.toml:**
```toml
[[commands]]
package = "go"

[[commands]]
package = "nodejs_20"

[devshell]
packages = [ "postgresql_15" ]
```

## Devbox

GitHub: https://github.com/jetify-com/devbox

For non-Nix users. JSON config, Nix under the hood.

```json
{ "packages": ["python@3.10", "nodejs@20"] }
```

```bash
devbox init && devbox add python@3.10 && devbox shell
```

## nix-direnv

GitHub: https://github.com/nix-community/nix-direnv

Auto-activate dev shells on `cd`. Essential companion.

```bash
# .envrc
use flake
```

```bash
echo "use flake" >> .envrc && direnv allow
```
