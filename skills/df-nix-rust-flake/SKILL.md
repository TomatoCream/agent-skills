---
name: df-nix-rust-flake
description: >
  Create Nix flake development environments for Rust projects using crane + fenix.
  Use when writing flake.nix for Rust, setting up Nix dev shells for Rust, configuring
  crane builds, choosing between crane/naersk/crate2nix/cargo2nix, adding Rust profiling
  or memory tools to Nix, or configuring mold/lld linkers in Nix. Also use when user
  mentions rust nix flake, cargo nix, crane nix, fenix, rust-overlay, rust devShell,
  nix rust toolchain, or rust nix build. Not for non-Nix Rust builds or non-Rust Nix flakes.
---

# Nix Flake for Modern Rust Development

## Stack: Crane + Fenix + Mold

**Always use this combination unless the user explicitly requests otherwise.**

- **Crane** (v0.23.3+): Composable, incrementally-cached Nix build derivations
- **Fenix**: Rust toolchain overlay with rust-analyzer nightly + Cachix binary cache
- **Mold**: 3-10x faster linker for iterative development (Linux only)

## Decision: Which Build Tool?

```
Need composable CI checks (clippy, test, audit as separate derivations)?
  YES → Crane (recommended default)
  NO → Need per-crate caching for huge dependency trees?
    YES → crate2nix (requires codegen step: `crate2nix generate`)
    NO → Need zero-config simplicity?
      YES → naersk
      NO → Crane
Never use cargo2nix (stale, edition 2024 incompatible)
```

| Feature | Crane | Naersk | crate2nix | cargo2nix |
|---------|-------|--------|-----------|-----------|
| Cache granularity | All deps together | All deps together | Per crate | Per crate |
| Codegen required | No | No | Yes | Yes |
| IFD required | No | No | Optional | No |
| Composable checks | Yes | No | No | No |
| Maintenance (2026) | Very active | Moderate | Active | Stale |
| WASM support | Yes | Yes | No | Limited |

## Decision: Which Toolchain Overlay?

```
Need rust-analyzer nightly or Cachix binary cache?
  YES → Fenix (recommended default)
  NO → Need to pin exact historical nightly date?
    YES → oxalica/rust-overlay
    NO → Fenix
Never use nixpkgs-mozilla (deprecated)
```

## Flake Template: Single Crate

```nix
{
  description = "Rust project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    crane.url = "github:ipetkov/crane";
    fenix = {
      url = "github:nix-community/fenix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-utils.url = "github:numtide/flake-utils";
    advisory-db = {
      url = "github:rustsec/advisory-db";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, crane, fenix, flake-utils, advisory-db, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs) lib;

        # Toolchain: stable + components. For nightly: use fenixPkgs.complete
        fenixPkgs = fenix.packages.${system};
        rustToolchain = fenixPkgs.stable.withComponents [
          "cargo" "clippy" "llvm-tools" "rust-analyzer"
          "rust-src" "rustc" "rustfmt"
        ];
        craneLib = (crane.mkLib pkgs).overrideToolchain rustToolchain;

        src = craneLib.cleanCargoSource ./.;

        commonArgs = {
          inherit src;
          strictDeps = true;
          buildInputs = [ ]
            ++ lib.optionals pkgs.stdenv.isDarwin [
              pkgs.libiconv
              pkgs.darwin.apple_sdk.frameworks.Security
              pkgs.darwin.apple_sdk.frameworks.SystemConfiguration
            ];
          nativeBuildInputs = [ pkgs.pkg-config ];
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
          doc = craneLib.cargoDoc (commonArgs // {
            inherit cargoArtifacts;
            env.RUSTDOCFLAGS = "--deny warnings";
          });
          fmt = craneLib.cargoFmt { inherit src; };
          toml-fmt = craneLib.taploFmt {
            src = pkgs.lib.sources.sourceFilesBySuffices src [ ".toml" ];
          };
          audit = craneLib.cargoAudit { inherit src advisory-db; };
          deny = craneLib.cargoDeny { inherit src; };
          nextest = craneLib.cargoNextest (commonArgs // {
            inherit cargoArtifacts;
            partitions = 1;
            partitionType = "count";
            cargoNextestPartitionsExtraArgs = "--no-tests=pass";
          });
        };

        packages.default = my-crate;
        apps.default = flake-utils.lib.mkApp { drv = my-crate; };

        devShells.default = craneLib.devShell {
          checks = self.checks.${system};
          packages = [
            pkgs.clang pkgs.lld
            pkgs.cargo-nextest pkgs.cargo-llvm-cov
            pkgs.cargo-flamegraph pkgs.samply
            pkgs.cargo-bloat pkgs.cargo-udeps pkgs.cargo-expand
            pkgs.cargo-audit pkgs.cargo-deny pkgs.cargo-careful
            pkgs.cargo-criterion pkgs.taplo pkgs.bacon pkgs.pkg-config
          ] ++ lib.optionals pkgs.stdenv.isLinux [
            pkgs.mold pkgs.heaptrack pkgs.valgrind pkgs.linuxPackages.perf
          ] ++ lib.optionals pkgs.stdenv.isDarwin [
            pkgs.libiconv
            pkgs.darwin.apple_sdk.frameworks.Security
            pkgs.darwin.apple_sdk.frameworks.SystemConfiguration
          ];
          shellHook = ''
            export RUST_SRC_PATH="${rustToolchain}/lib/rustlib/src/rust/library"
            ${if pkgs.stdenv.isLinux then ''
              export CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER="clang"
              export CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_RUSTFLAGS="-C link-arg=-fuse-ld=mold"
              export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER="clang"
              export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_RUSTFLAGS="-C link-arg=-fuse-ld=mold"
            '' else ""}
          '';
        };
      }
    );
}
```

## Flake Template: Workspace

Key differences from single crate:

```nix
# Build individual crates from workspace
individualCrateArgs = commonArgs // {
  inherit cargoArtifacts;
  inherit (craneLib.crateNameFromCargoToml { inherit src; }) version;
  doCheck = false;  # tests run via nextest on whole workspace
};

fileSetForCrate = crate: lib.fileset.toSource {
  root = ./.;
  fileset = lib.fileset.unions [
    ./Cargo.toml ./Cargo.lock
    (craneLib.fileset.commonCargoSources ./crates/my-common)
    (craneLib.fileset.commonCargoSources crate)
  ];
};

my-cli = craneLib.buildPackage (individualCrateArgs // {
  pname = "my-cli";
  cargoExtraArgs = "-p my-cli";
  src = fileSetForCrate ./crates/my-cli;
});
```

Add `cargo-hakari` for workspace-hack crate optimization in large workspaces.

## Crane API Quick Reference

| Function | What It Does |
|----------|-------------|
| `buildDepsOnly` | Compile deps into cached derivation |
| `buildPackage` | Build final binary |
| `cargoClippy` | Lint with clippy |
| `cargoFmt` | Check rustfmt formatting |
| `cargoDoc` | Build docs (supports `RUSTDOCFLAGS`) |
| `cargoAudit` | RustSec advisory check |
| `cargoDeny` | License/ban/source check |
| `cargoNextest` | Run tests via nextest (supports partitioning) |
| `cargoLlvmCov` | LLVM source-based coverage |
| `cargoTarpaulin` | Alternative coverage |
| `taploFmt` | TOML formatting |
| `buildTrunkPackage` | WASM frontend with Trunk |
| `devShell` | Dev shell inheriting check tools |
| `cleanCargoSource` | Filter source to Cargo-relevant files |
| `overrideToolchain` | Use custom Rust toolchain |

## Crane Templates

Initialize directly: `nix flake init -t github:ipetkov/crane#<template>`

Templates: `quick-start`, `quick-start-simple`, `quick-start-workspace`, `trunk`, `cross-rust-overlay`, `cross-musl`, `cross-windows`, `build-std`, `custom-toolchain`, `alt-registry`, `trunk-workspace`, `sqlx`, `end-to-end-testing`

## Linker Configuration

### Mold (Linux, 3-10x faster links)

In `.cargo/config.toml`:
```toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

[target.aarch64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
```

**Caveat**: Mold can fail with native C library deps (libpq, openssl) due to rpath issues. Use lld as fallback for mixed Rust/C projects.

### LLD (cross-platform fallback)

Use `pkgs.llvmPackages.bintools` NOT `pkgs.lld` (the bintools wrapper sets rpath correctly).

### macOS

Use the default Apple linker. `zld` is archived. Apple's linker has improved in recent Xcode.

## Rust Performance Tooling for Nix

### Allocators (Cargo crate dependencies, not Nix packages)

| Allocator | When to Use |
|-----------|-------------|
| **tikv-jemallocator** | Long-running services, multi-threaded, fragmentation-sensitive |
| **mimalloc** | Many small allocations, cross-platform (incl. Windows) |
| **bumpalo** | Batch/phase-based allocation (parsers, compilers, request handlers) |
| **typed-arena** | Single-type arena, simpler than bumpalo, runs Drop |
| **snmalloc-rs** | High-throughput concurrent allocation |
| **dlmalloc** | wasm32 targets (Rust default for wasm) |

Do NOT use `wee_alloc` (archived August 2025).

### Profilers (add to devShell packages)

| Tool | nixpkgs | Platform | Best For |
|------|---------|----------|----------|
| `heaptrack` | Yes | Linux | Heap profiling with GUI |
| `samply` | Yes | All | CPU profiling, Firefox Profiler UI |
| `cargo-flamegraph` | Yes | All | Quick flamegraph generation |
| `valgrind` | Yes | Linux | Memcheck, DHAT, Cachegrind |
| `linuxPackages.perf` | Yes | Linux | Hardware counter profiling |

Also: `dhat` Rust crate (cross-platform heap profiling, by valgrind author).

### Sanitizers (nightly Rust, no Nix packages needed)

```bash
# Address Sanitizer (buffer overflow, use-after-free) — 2x slowdown
RUSTFLAGS="-Z sanitizer=address" cargo +nightly test -Z build-std --target x86_64-unknown-linux-gnu

# Leak Sanitizer
RUSTFLAGS="-Z sanitizer=leak" cargo +nightly test

# Memory Sanitizer (uninitialized reads) — requires -Z build-std
RUSTFLAGS="-Z sanitizer=memory -Z sanitizer-memory-track-origins" cargo +nightly test -Z build-std

# Thread Sanitizer (data races)
RUSTFLAGS="-Z sanitizer=thread" cargo +nightly test -Z build-std
```

ASan/TSan: Linux x86_64 + macOS x86_64. MSan: Linux x86_64 only.

### Benchmarking (Cargo dev-dependencies)

| Framework | Style | Best For |
|-----------|-------|----------|
| **criterion** | Macro-based | Statistical analysis, HTML reports, regression detection |
| **divan** | Attribute-macro | Simple API, auto-parameterization, allocator profiling |
| **iai-callgrind** | Valgrind-based | CI (instruction counts, deterministic, no system load noise) |

### Security (both nixpkgs AND crane built-in)

| Tool | nixpkgs | Crane | What It Checks |
|------|---------|-------|----------------|
| `cargo-audit` | Yes | `cargoAudit` | RustSec vulnerabilities |
| `cargo-deny` | Yes | `cargoDeny` | Licenses, bans, sources, advisories |

### Unsafe Code (add to devShell or use via nightly)

| Tool | nixpkgs | What It Does |
|------|---------|-------------|
| `cargo-careful` | Yes | Std library debug assertions + extra UB checks |
| `cargo-fuzz` | Yes | Fuzz testing with ASan enabled |
| miri | Via fenix/rustup | MIR interpreter, aliasing model validation |

### Dev Workflow (add to devShell packages)

| Tool | nixpkgs | What It Does |
|------|---------|-------------|
| `bacon` | Yes | Background code checker (modern cargo-watch) |
| `cargo-nextest` | Yes | Fast parallel test runner |
| `cargo-llvm-cov` | Yes | LLVM source-based coverage |
| `cargo-expand` | Yes | Macro expansion viewer |
| `cargo-bloat` | Yes | Binary size analysis |
| `cargo-udeps` | Yes | Unused dependency detection |
| `taplo` | Yes | TOML formatter/linter |

## Common Patterns

### Adding C/system library dependencies

```nix
commonArgs = {
  inherit src;
  strictDeps = true;
  buildInputs = [
    pkgs.openssl   # example: reqwest with native-tls
    pkgs.sqlite    # example: rusqlite
  ] ++ lib.optionals pkgs.stdenv.isDarwin [
    pkgs.libiconv
    pkgs.darwin.apple_sdk.frameworks.Security
    pkgs.darwin.apple_sdk.frameworks.SystemConfiguration
  ];
  nativeBuildInputs = [ pkgs.pkg-config ];
  # If openssl-sys needs env vars:
  env.OPENSSL_DIR = "${pkgs.openssl.dev}";
};
```

### Cross-compilation to musl (static binary)

```nix
commonArgs = {
  inherit src;
  CARGO_BUILD_TARGET = "x86_64-unknown-linux-musl";
  CARGO_BUILD_RUSTFLAGS = "-C target-feature=+crt-static";
};
```

### WASM target

Use fenix to add the wasm target:
```nix
rustToolchain = fenixPkgs.stable.withComponents [
  "cargo" "clippy" "rustc" "rustfmt" "rust-src"
] // fenixPkgs.targets."wasm32-unknown-unknown".stable.withComponents [
  "rust-std"
];
```

### Nightly toolchain

```nix
rustToolchain = fenixPkgs.complete.withComponents [
  "cargo" "clippy" "llvm-tools" "miri" "rust-analyzer"
  "rust-src" "rustc" "rustfmt"
];
```

### Using rust-toolchain.toml with oxalica

If project has a `rust-toolchain.toml`, use oxalica/rust-overlay instead:
```nix
fenix = { }; # remove fenix input
rust-overlay = {
  url = "github:oxalica/rust-overlay";
  inputs.nixpkgs.follows = "nixpkgs";
};
# ...
rustToolchain = pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml;
craneLib = (crane.mkLib pkgs).overrideToolchain rustToolchain;
```

## Anti-Patterns

- **Using `rustPlatform.buildRustPackage` with `cargoHash`**: Use crane instead. `buildRustPackage` rebuilds all deps on every source change and requires manual hash updates.
- **Using `pkgs.lld` directly**: Use `pkgs.llvmPackages.bintools` which includes the rpath wrapper.
- **Mold with C deps**: Mold can break rpath resolution for native libraries. Use lld for mixed Rust/C.
- **`wee_alloc` for WASM**: Archived. Use `dlmalloc` (Rust default for wasm) or no custom allocator.
- **`nixpkgs-mozilla` for toolchain**: Deprecated. Use fenix or oxalica/rust-overlay.
- **Putting profiling tools in `buildInputs`**: Dev tools go in `devShells.default.packages`, not in `buildInputs` (which affects the build derivation).
