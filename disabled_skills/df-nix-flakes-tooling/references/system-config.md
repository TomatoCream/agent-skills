# System Configuration & Misc Tools

## disko (disk partitioning)

GitHub: https://github.com/nix-community/disko

Declarative disk layout. GPT/MBR, LVM, LUKS, ZFS, btrfs.

```nix
{
  disko.devices.disk.main = {
    device = "/dev/sda";
    type = "disk";
    content = {
      type = "gpt";
      partitions = {
        ESP = {
          type = "EF00";
          size = "500M";
          content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; };
        };
        root = {
          size = "100%";
          content = { type = "filesystem"; format = "ext4"; mountpoint = "/"; };
        };
      };
    };
  };
}
```

## nixos-anywhere (remote install)

GitHub: https://github.com/nix-community/nixos-anywhere

Pairs with disko. Install NixOS on any SSH-reachable machine.

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake .#my-machine --target-host root@<ip>
```

## Home Manager (user config)

GitHub: https://github.com/nix-community/home-manager

Manages dotfiles, user services, shell config. NixOS module system for $HOME.

```nix
# As a NixOS module:
home-manager.users.myuser = { pkgs, ... }: {
  home.packages = [ pkgs.ripgrep pkgs.fd ];
  programs.git = { enable = true; userName = "Me"; };
  programs.zsh.enable = true;
};
```

## nix-darwin (macOS)

GitHub: https://github.com/LnL7/nix-darwin

NixOS module system for macOS. Combine with Home Manager for full declarative macOS.

## Stylix (theming)

GitHub: https://github.com/nix-community/stylix

System-wide color scheme from a single base16 definition. NixOS + Home Manager + nix-darwin.

## NixVim (Neovim)

GitHub: https://github.com/nix-community/nixvim

Configure Neovim entirely in Nix. Plugins, LSP, keybinds, themes as modules.

## nix-topology (network diagrams)

GitHub: https://github.com/oddlama/nix-topology

Auto-generate SVG infrastructure diagrams from NixOS configs.

```nix
{
  inputs.nix-topology.url = "github:oddlama/nix-topology";
  outputs = { nixpkgs, nix-topology, ... }: {
    nixosConfigurations.host1 = nixpkgs.lib.nixosSystem {
      modules = [ ./host1/configuration.nix nix-topology.nixosModules.default ];
    };
  };
}
```

```bash
nix build .#topology.x86_64-linux.config.output  # renders SVGs
```

## microvm.nix (lightweight VMs)

GitHub: https://github.com/microvm-nix/microvm.nix

NixOS MicroVMs. 8 hypervisors (qemu, firecracker, cloud-hypervisor, etc.).

```nix
{
  inputs.microvm.url = "github:microvm-nix/microvm.nix";
  outputs = { nixpkgs, microvm, ... }:
    let system = "x86_64-linux"; in {
      packages.${system}.default =
        self.nixosConfigurations.my-vm.config.microvm.declaredRunner;
      nixosConfigurations.my-vm = nixpkgs.lib.nixosSystem {
        inherit system;
        modules = [ microvm.nixosModules.microvm {
          networking.hostName = "my-vm";
          microvm = {
            hypervisor = "qemu";
            volumes = [{ mountPoint = "/var"; image = "var.img"; size = 256; }];
            shares = [{ proto = "9p"; tag = "ro-store";
              source = "/nix/store"; mountPoint = "/nix/.ro-store"; }];
          };
        }];
      };
    };
}
```

```bash
nix flake init -t microvm && nix run .#my-vm
```

---

## IDE Tools

| Tool | GitHub | What it does |
|------|--------|-------------|
| nixd | https://github.com/nix-community/nixd | Full Nix LSP (options completion, whole-codebase) |
| nil | https://github.com/oxalica/nil | Lighter Nix LSP (fast, error-tolerant) |
| nix-init | https://github.com/nix-community/nix-init | Generate nix packages from URLs |
| nix-update | https://github.com/Mic92/nix-update | Auto-update package versions/hashes |
| nixpkgs-review | https://github.com/Mic92/nixpkgs-review | Review PRs by building affected packages |

## Nix Implementations

| Impl | Link | Notes |
|------|------|-------|
| Determinate Nix | https://github.com/DeterminateSystems/determinate | Flakes default, GC daemon, 7M+ installs |
| Lix | https://lix.systems/ | Community fork, correctness focus, compatible |
| Tvix | https://tvl.fyi/ | Rust rewrite, in development |

## Dependency Management

| Tool | GitHub | Use when |
|------|--------|----------|
| npins | https://github.com/andir/npins | Need to follow Git tags (flakes can't) |
| unflake | https://codeberg.org/goldstein/unflake | Non-flake projects needing flake inputs |
