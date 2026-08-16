---
name: df-nix-flakes-tooling
description: >
  Modern Nix flakes ecosystem tooling guide. Use when writing flake.nix files,
  choosing Nix tools, setting up dev environments with Nix, deploying NixOS,
  building language-specific packages with Nix (Rust, Python, Go, Node.js),
  managing secrets in NixOS, containerizing with Nix, setting up Nix CI/CD,
  or configuring NixOS systems declaratively. Covers flake-parts, devenv,
  devshell, treefmt-nix, deploy-rs, Colmena, sops-nix, agenix, crane, naersk,
  uv2nix, dream2nix, nix2container, Omnix, Cachix, disko, nixos-anywhere,
  Stylix, microvm.nix, nix-topology, and 40+ more tools. Also use when user
  mentions nix flake, flake-parts, devenv, nix develop, nix build with flakes,
  or asks "what nix tool should I use for X". Not for basic Nix language syntax,
  NixOS option reference, or nixpkgs internals.
---

# Nix Flakes Tooling Guide

## Decision Tree

When a user asks about Nix flakes tooling, use this to pick the right tool:

```
What are you doing?
|
+-- Structuring a flake.nix?
|   +-- Simple project --> flake-utils (minimal boilerplate)
|   +-- Modular project --> flake-parts (module system, ecosystem)
|   +-- Opinionated structure --> Snowfall Lib (convention-over-config)
|   +-- Large org / SDLC --> std (divnix, cells/block types)
|   +-- Multi-host configs --> flake-parts + Dendritic pattern
|
+-- Dev environment?
|   +-- Full-featured (services, processes) --> devenv
|   +-- Lightweight (TOML config) --> devshell
|   +-- Non-Nix users --> Devbox
|   +-- Auto-activate on cd --> nix-direnv
|
+-- Formatting / linting?
|   +-- Project-wide formatting --> treefmt-nix
|   +-- Git pre-commit hooks --> git-hooks.nix
|
+-- Deploying NixOS?
|   +-- Multi-profile, rollback --> deploy-rs
|   +-- Parallel, stateless --> Colmena
|   +-- GitOps pull model --> comin
|   +-- P2P with secrets --> Clan
|   +-- SSH-only, simple --> Nixinate
|
+-- Secrets?
|   +-- Multi-backend (GPG, age, KMS) --> sops-nix
|   +-- Simple SSH-key based --> agenix
|
+-- Building language packages?
|   +-- Rust (composable) --> crane
|   +-- Rust (minimal) --> naersk
|   +-- Python (uv) --> uv2nix + pyproject-nix
|   +-- Python (Poetry, legacy) --> poetry2nix
|   +-- Go --> gomod2nix
|   +-- Multi-language --> dream2nix
|
+-- Container images?
|   +-- Efficient, no tarball --> nix2container
|   +-- Built-in nixpkgs --> dockerTools
|   +-- On-the-fly registry --> Nixery
|   +-- System images (ISO, VM) --> nixos-generators
|
+-- CI/CD?
|   +-- Build all flake outputs --> Omnix (om ci)
|   +-- Parallel eval+build --> nix-fast-build
|   +-- Better build output --> nix-output-monitor (nom)
|   +-- Flake health checks --> flake-checker
|   +-- Hosted CI+cache --> Garnix
|
+-- Binary caching?
|   +-- Hosted service --> Cachix
|   +-- Self-hosted --> Attic
|   +-- Flake registry --> FlakeHub + fh CLI
|
+-- System config?
|   +-- Disk layout --> disko
|   +-- Remote install --> nixos-anywhere + disko
|   +-- User dotfiles --> Home Manager
|   +-- macOS --> nix-darwin
|   +-- Theming --> Stylix
|   +-- Neovim --> NixVim
|   +-- Network diagrams --> nix-topology
|   +-- Lightweight VMs --> microvm.nix
|
+-- IDE / DX?
|   +-- Language server (full) --> nixd
|   +-- Language server (light) --> nil
|   +-- Generate packages --> nix-init
|   +-- Update packages --> nix-update
```

---

## Recommended Starter Stack

For a new project, start with:

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    git-hooks-nix.url = "github:cachix/git-hooks.nix";
    devenv.url = "github:cachix/devenv";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.treefmt-nix.flakeModule
        inputs.git-hooks-nix.flakeModule
        inputs.devenv.flakeModule
      ];
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      perSystem = { pkgs, ... }: {
        treefmt.programs.nixfmt.enable = true;
        pre-commit.hooks.nixfmt.enable = true;
        devenv.shells.default = {
          packages = [ pkgs.hello ];
          enterShell = "echo 'dev environment ready'";
        };
      };
    };
}
```

---

## Tool Reference (condensed)

For full examples with flake.nix snippets, load the reference files:
- **Composition:** Load [references/composition.md](references/composition.md)
- **Dev environments:** Load [references/dev-environments.md](references/dev-environments.md)
- **Deployment & secrets:** Load [references/deployment.md](references/deployment.md)
- **Language build tools:** Load [references/language-tools.md](references/language-tools.md)
- **CI/CD, containers, caching:** Load [references/ci-containers-caching.md](references/ci-containers-caching.md)
- **System config & misc:** Load [references/system-config.md](references/system-config.md)

---

## Quick Examples

### flake-parts (composition)

```nix
{
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-darwin" ];
      perSystem = { pkgs, ... }: {
        packages.default = pkgs.hello;
      };
    };
}
```

### devenv (dev environment)

```nix
# devenv.nix
{ pkgs, ... }: {
  languages.python.enable = true;
  services.postgres.enable = true;
  packages = [ pkgs.jq ];
}
```

### crane (Rust)

```nix
{
  inputs = {
    crane.url = "github:ipetkov/crane";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };
  outputs = { crane, nixpkgs, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      craneLib = crane.mkLib pkgs;
      crate = craneLib.buildPackage {
        src = craneLib.cleanCargoSource ./.;
        cargoArtifacts = craneLib.buildDepsOnly { src = craneLib.cleanCargoSource ./.; };
      };
    in { packages.x86_64-linux.default = crate; };
}
```

### uv2nix (Python)

```nix
{
  inputs = {
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
  };
  # Parses uv.lock, generates Nix derivations, creates virtualenv
  # See references/language-tools.md for full example
}
```

### deploy-rs (deployment)

```nix
{
  inputs.deploy-rs.url = "github:serokell/deploy-rs";
  outputs = { self, nixpkgs, deploy-rs }: {
    deploy.nodes.myserver = {
      hostname = "myserver.example.com";
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos
          self.nixosConfigurations.myserver;
      };
    };
  };
}
```

### sops-nix (secrets)

```nix
# In NixOS configuration module:
{
  sops.defaultSopsFile = ./secrets/secrets.yaml;
  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
  sops.secrets.db-password = {};
  # Available at /run/secrets/db-password
}
```

### treefmt-nix (formatting)

```nix
# treefmt.nix
{ ... }: {
  projectRootFile = "flake.nix";
  programs.nixfmt.enable = true;
  programs.rustfmt.enable = true;
  programs.prettier.enable = true;
}
```
```bash
nix fmt  # formats entire project
```

### nix2container (containers)

```nix
{
  inputs.nix2container.url = "github:nlewo/nix2container";
  outputs = { nixpkgs, nix2container, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      n2c = nix2container.packages.x86_64-linux.nix2container;
    in {
      packages.x86_64-linux.image = n2c.buildImage {
        name = "myapp";
        config.entrypoint = [ "${pkgs.hello}/bin/hello" ];
      };
    };
}
```

### Omnix (CI)

```bash
om ci                    # build all flake outputs
om ci run ~/project      # build a local project
om health                # check flake health
```

### nom (build visualization)

```bash
nom build .#mypackage    # drop-in replacement for nix build
nom develop              # drop-in replacement for nix develop
```

---

## GitHub Links (all tools)

| Tool | GitHub | Category |
|------|--------|----------|
| flake-parts | https://github.com/hercules-ci/flake-parts | Composition |
| flake-utils | https://github.com/numtide/flake-utils | Composition |
| haumea | https://github.com/nix-community/haumea | Composition |
| Snowfall Lib | https://github.com/snowfallorg/lib | Composition |
| std | https://github.com/divnix/std | Composition |
| flakelight | https://github.com/nix-community/flakelight | Composition |
| dendrix | https://github.com/vic/dendrix | Dendritic |
| den | https://github.com/vic/den | Dendritic |
| devenv | https://github.com/cachix/devenv | Dev Env |
| devshell | https://github.com/numtide/devshell | Dev Env |
| Devbox | https://github.com/jetify-com/devbox | Dev Env |
| nix-direnv | https://github.com/nix-community/nix-direnv | Dev Env |
| treefmt-nix | https://github.com/numtide/treefmt-nix | Formatting |
| git-hooks.nix | https://github.com/cachix/git-hooks.nix | Hooks |
| deploy-rs | https://github.com/serokell/deploy-rs | Deployment |
| Colmena | https://github.com/zhaofengli/colmena | Deployment |
| Clan | https://github.com/clan-lol/clan-core | Deployment |
| comin | https://github.com/nlewo/comin | Deployment |
| Nixinate | https://github.com/MatthewCroughan/nixinate | Deployment |
| sops-nix | https://github.com/Mic92/sops-nix | Secrets |
| agenix | https://github.com/ryantm/agenix | Secrets |
| crane | https://github.com/ipetkov/crane | Rust |
| naersk | https://github.com/nix-community/naersk | Rust |
| uv2nix | https://github.com/pyproject-nix/uv2nix | Python |
| pyproject-nix | https://github.com/pyproject-nix/pyproject.nix | Python |
| poetry2nix | https://github.com/nix-community/poetry2nix | Python |
| dream2nix | https://github.com/nix-community/dream2nix | Multi-lang |
| gomod2nix | https://github.com/nix-community/gomod2nix | Go |
| nix2container | https://github.com/nlewo/nix2container | Containers |
| nixos-generators | https://github.com/nix-community/nixos-generators | Images |
| Omnix | https://github.com/juspay/omnix | CI/CD |
| nix-fast-build | https://github.com/Mic92/nix-fast-build | CI/CD |
| nom | https://github.com/maralorn/nix-output-monitor | CI/CD |
| flake-checker | https://github.com/DeterminateSystems/flake-checker | CI/CD |
| Garnix | https://garnix.io/ | CI/CD |
| Cachix | https://github.com/cachix/cachix | Caching |
| Attic | https://github.com/zhaofengli/attic | Caching |
| FlakeHub | https://flakehub.com/ | Registry |
| fh | https://github.com/DeterminateSystems/fh | Registry |
| disko | https://github.com/nix-community/disko | System |
| nixos-anywhere | https://github.com/nix-community/nixos-anywhere | System |
| Home Manager | https://github.com/nix-community/home-manager | System |
| nix-darwin | https://github.com/LnL7/nix-darwin | System |
| Stylix | https://github.com/nix-community/stylix | System |
| NixVim | https://github.com/nix-community/nixvim | System |
| nix-topology | https://github.com/oddlama/nix-topology | System |
| microvm.nix | https://github.com/microvm-nix/microvm.nix | System |
| nixd | https://github.com/nix-community/nixd | IDE |
| nil | https://github.com/oxalica/nil | IDE |
| Lix | https://lix.systems/ | Nix impl |
| Determinate Nix | https://github.com/DeterminateSystems/determinate | Nix impl |
