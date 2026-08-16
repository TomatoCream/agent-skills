# Language-Specific Build Tools

## Rust: crane (recommended)

GitHub: https://github.com/ipetkov/crane

Incremental builds. Composable checks (clippy, fmt, test as separate derivations).

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    crane.url = "github:ipetkov/crane";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, crane, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        craneLib = crane.mkLib pkgs;
        src = craneLib.cleanCargoSource ./.;
        commonArgs = {
          inherit src;
          strictDeps = true;
          buildInputs = [] ++ pkgs.lib.optionals pkgs.stdenv.isDarwin [ pkgs.libiconv ];
        };
        cargoArtifacts = craneLib.buildDepsOnly commonArgs;
        my-crate = craneLib.buildPackage (commonArgs // { inherit cargoArtifacts; });
      in {
        checks = {
          inherit my-crate;
          clippy = craneLib.cargoClippy (commonArgs // {
            inherit cargoArtifacts;
            cargoClippyExtraArgs = "--all-targets -- --deny warnings";
          });
          fmt = craneLib.cargoFmt { inherit src; };
        };
        packages.default = my-crate;
        devShells.default = craneLib.devShell { checks = self.checks.${system}; };
      }
    );
}
```

## Rust: naersk (minimal)

GitHub: https://github.com/nix-community/naersk

One function call. Parses Cargo.lock automatically.

```nix
{
  inputs.naersk.url = "github:nix-community/naersk";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  outputs = { naersk, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (import nixpkgs) { inherit system; };
        naersk' = pkgs.callPackage naersk {};
      in { packages.default = naersk'.buildPackage { src = ./.; }; }
    );
}
```

## Python: uv2nix (recommended)

GitHub: https://github.com/pyproject-nix/uv2nix
Docs: https://pyproject-nix.github.io/uv2nix/

Parses uv.lock. Pure Nix, no IFD. Based on pyproject-nix.

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
    uv2nix.url = "github:pyproject-nix/uv2nix";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs";
  };
  outputs = { nixpkgs, pyproject-nix, uv2nix, pyproject-build-systems, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
      pythonSets = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in (pkgs.callPackage pyproject-nix.build.packages {
          python = pkgs.python3;
        }).overrideScope (lib.composeManyExtensions [
          pyproject-build-systems.overlays.wheel
          overlay
        ])
      );
    in {
      packages = forAllSystems (system: {
        default = pythonSets.${system}.mkVirtualEnv "myapp-env" workspace.deps.default;
      });
    };
}
```

## Python: poetry2nix (legacy)

GitHub: https://github.com/nix-community/poetry2nix

Seeking maintainers. Use uv2nix for new projects.

```nix
{
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  outputs = { nixpkgs, poetry2nix, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
    in { packages.x86_64-linux.default = mkPoetryApplication { projectDir = ./.; }; };
}
```

## Go: gomod2nix

GitHub: https://github.com/nix-community/gomod2nix

```bash
gomod2nix  # generates gomod2nix.toml from go.mod/go.sum
```

```nix
{
  inputs.gomod2nix.url = "github:nix-community/gomod2nix";
  outputs = { nixpkgs, flake-utils, gomod2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in {
        packages.default = pkgs.callPackage ./. {
          inherit (gomod2nix.legacyPackages.${system}) buildGoApplication;
        };
      }
    );
}
```

## Multi-language: dream2nix

GitHub: https://github.com/nix-community/dream2nix

Unified framework. Each package in `./packages/<name>/default.nix`.

```nix
{
  inputs.dream2nix.url = "github:nix-community/dream2nix";
  outputs = { dream2nix, nixpkgs, ... }:
    let eachSystem = nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-darwin" ]; in {
      packages = eachSystem (system:
        dream2nix.lib.importPackages {
          projectRoot = ./.;
          projectRootFile = "flake.nix";
          packagesDir = ./packages;
          packageSets.nixpkgs = nixpkgs.legacyPackages.${system};
        }
      );
    };
}
```

## Comparison

| Tool | Language | Lock file | Complexity | IFD-free |
|------|----------|-----------|------------|----------|
| crane | Rust | Cargo.lock | Medium | Yes |
| naersk | Rust | Cargo.lock | Minimal | Yes |
| uv2nix | Python | uv.lock | Medium | Yes |
| poetry2nix | Python | poetry.lock | Minimal | No |
| gomod2nix | Go | gomod2nix.toml | Minimal | Yes |
| dream2nix | Multi | Various | Medium | Varies |
