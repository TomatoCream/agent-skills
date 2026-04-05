---
git_sha: $(git -C sources/sops-nix rev-parse HEAD)
source: https://github.com/Mic92/sops-nix
generated: 2026-04-06
modules:
  - modules/sops/default.nix (NixOS)
  - modules/home-manager/sops.nix (Home Manager)
  - modules/nix-darwin/default.nix (nix-darwin)
---

# Generation Metadata

- **Source**: https://github.com/Mic92/sops-nix
- **Git SHA**: See frontmatter (run `git -C sources/sops-nix rev-parse HEAD`)
- **Generated**: 2026-04-06
- **Coverage**: Core modules + Features (9 reference files)