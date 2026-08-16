# CI/CD, Containers & Caching

## treefmt-nix (formatting)

GitHub: https://github.com/numtide/treefmt-nix

One command formats all files. 100+ formatters.

```nix
# treefmt.nix
{ ... }: {
  projectRootFile = "flake.nix";
  programs.nixfmt.enable = true;
  programs.rustfmt.enable = true;
  programs.prettier.enable = true;
  programs.black.enable = true;
}
```

```nix
# flake.nix (standalone, without flake-parts)
{
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  outputs = { self, nixpkgs, treefmt-nix, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      treefmtEval = treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
    in {
      formatter.${system} = treefmtEval.config.build.wrapper;
      checks.${system}.formatting = treefmtEval.config.build.check self;
    };
}
```

```bash
nix fmt          # format everything
nix flake check  # verify in CI
```

## git-hooks.nix (pre-commit)

GitHub: https://github.com/cachix/git-hooks.nix

```nix
{
  inputs.git-hooks.url = "github:cachix/git-hooks.nix";
  outputs = { self, git-hooks, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      checks.${system}.hooks = git-hooks.lib.${system}.run {
        src = ./.;
        hooks = {
          nixfmt.enable = true;
          shellcheck.enable = true;
          black.enable = true;
        };
      };
      devShells.${system}.default = pkgs.mkShell {
        inherit (self.checks.${system}.hooks) shellHook;
      };
    };
}
```

---

## Omnix (CI)

GitHub: https://github.com/juspay/omnix
Docs: https://omnix.page/

Successor to nixci. Builds all flake outputs.

```bash
om ci                                    # build current flake
om ci run ~/code/myproject               # build local project
om ci run https://github.com/user/repo/pull/42  # build a PR
om ci run --on ssh://user@server .       # remote build
om ci gh-matrix --systems=x86_64-linux   # GitHub Actions matrix
om health                                # flake health check
```

## nix-fast-build

GitHub: https://github.com/Mic92/nix-fast-build

Parallel eval + build. Uses nix-eval-jobs + nom.

```bash
nix-fast-build                          # build all
nix-fast-build --remote user@host       # remote build
nix-fast-build --cachix-cache mycache   # build + push to cache
nix-fast-build --no-nom --skip-cached   # CI-friendly mode
```

## nix-output-monitor (nom)

GitHub: https://github.com/maralorn/nix-output-monitor

Drop-in replacement with TUI build visualization.

```bash
nom build .#mypackage   # instead of nix build
nom develop              # instead of nix develop
nom shell .#mypackage   # instead of nix shell
```

## flake-checker

GitHub: https://github.com/DeterminateSystems/flake-checker

```bash
nix run github:DeterminateSystems/flake-checker
```

---

## nix2container

GitHub: https://github.com/nlewo/nix2container

Efficient OCI images. No tarballs in store. Skips pushed layers.

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
        tag = "latest";
        config = {
          entrypoint = [ "${pkgs.hello}/bin/hello" ];
          env = [ "PATH=${pkgs.coreutils}/bin" ];
        };
      };
    };
}
```

## dockerTools (nixpkgs built-in)

```nix
pkgs.dockerTools.buildLayeredImage {
  name = "myapp";
  tag = "latest";
  contents = [ pkgs.hello pkgs.bash ];
  config.Cmd = [ "${pkgs.hello}/bin/hello" ];
}
```

```bash
nix build .#image && docker load < result
```

## Nixery

Pull `nixery.dev/shell/git/curl` -- builds image on the fly from package names.

## nixos-generators

GitHub: https://github.com/nix-community/nixos-generators

```bash
nixos-generate -f iso -c ./configuration.nix
nixos-generate -f virtualbox -c ./configuration.nix
nixos-generate -f amazon -c ./configuration.nix
```

---

## Cachix

GitHub: https://github.com/cachix/cachix

Hosted binary cache. Free for open source.

```bash
cachix create mycache && cachix use mycache
nix build .#pkg | cachix push mycache
```

## Attic

GitHub: https://github.com/zhaofengli/attic

Self-hosted binary cache. S3 backend.

```bash
attic login myserver https://attic.example.com <token>
attic push mycache result
attic use mycache
```

## FlakeHub + fh CLI

GitHub: https://github.com/DeterminateSystems/fh

```bash
fh init              # create new flake with project detection
fh add nixos/nixpkgs # add input
fh search rust       # find flakes
fh apply nixos "org/config/0.1"  # apply config
```
