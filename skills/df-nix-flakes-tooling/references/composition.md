# Flake Composition & Module Systems

## flake-parts

GitHub: https://github.com/hercules-ci/flake-parts
Docs: https://flake.parts/

The de facto standard for structuring flake.nix. Uses the NixOS module system.

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };
  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      perSystem = { pkgs, self', ... }: {
        packages.default = pkgs.hello;
        devShells.default = pkgs.mkShell { packages = [ pkgs.hello ]; };
      };
      flake = {
        # Non-per-system outputs (nixosConfigurations, etc.)
      };
    };
}
```

Import ecosystem modules: `imports = [ inputs.treefmt-nix.flakeModule ];`

## flake-utils

GitHub: https://github.com/numtide/flake-utils

Simpler, no module system. Good for small projects.

```nix
{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in {
        packages.default = pkgs.hello;
        apps.default = flake-utils.lib.mkApp { drv = pkgs.hello; };
      }
    );
}
```

## haumea

GitHub: https://github.com/nix-community/haumea

Filesystem-based module system. Directory layout = attribute set.

```nix
{
  inputs.haumea.url = "github:nix-community/haumea/v0.2.2";
  outputs = { haumea, nixpkgs, ... }:
    let
      lib = haumea.lib.load {
        src = ./src;         # src/foo.nix becomes lib.foo
        inputs = { inherit (nixpkgs) lib; };
      };
    in { inherit lib; };
}
```

## Snowfall Lib

GitHub: https://github.com/snowfallorg/lib

Convention-over-config: `systems/`, `packages/`, `modules/`, `shells/`, `overlays/` auto-discovered.

```nix
{
  inputs.snowfall-lib.url = "github:snowfallorg/lib";
  outputs = inputs: inputs.snowfall-lib.mkFlake {
    inherit inputs;
    src = ./.;  # discovers everything from directory structure
  };
}
```

## std (divnix)

GitHub: https://github.com/divnix/std
Docs: https://std.divnix.com/

Full SDLC framework with Cells + Block Types. TUI included. Best for large orgs.

## Dendritic Pattern

Every non-entry file is a NixOS module. File path = feature.

- dendrix: https://github.com/vic/dendrix
- den: https://github.com/vic/den
- flake-file: https://github.com/vic/flake-file

Works with flake-parts or without flakes entirely.
