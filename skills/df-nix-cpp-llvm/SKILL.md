---
name: df-nix-cpp-llvm
description: >
  Generate production-ready Nix flakes for C++ development with LLVM/Clang toolchain.
  Use when user asks to create a C++ dev environment, Nix flake for C++, set up clang/LLVM
  with Nix, add C++ libraries to a flake, fix clangd in Nix, or configure sanitizers/profiling.
  Covers: flake-parts, modular LLVM switching, mold linker, ninja, clangd LSP, valgrind,
  perf, sanitizers, library management, testing/benchmarking.
user-invocable: true
argument-hint: "[init | add-lib <name> | shell <variant>]"
---

# Nix C++ LLVM Development Environment Skill

Generate and manage complete Clang/LLVM C++ development environments using Nix flakes.

## When to Use

- User wants to create a C++ project with Nix flakes
- User needs to set up clang/LLVM toolchain in Nix
- User asks how to add C++ libraries to a Nix devShell
- User has clangd/LSP issues in a Nix environment
- User wants sanitizers, profiling, or benchmarking in Nix
- User asks about mold, ninja, or modern C++ build tooling with Nix

## Core Knowledge

### LLVM Versions in nixpkgs

Available as `llvmPackages_18` through `llvmPackages_22` (22 = git/dev).
Latest stable: `llvmPackages_21` (21.1.1). Always use `nixos-unstable` for latest.

Each set contains: `clang`, `libcxxClang`, `clangUseLLVM`, `llvm`, `lld`, `lldb`,
`libcxx`, `libcxxabi`, `compiler-rt`, `libunwind`, `openmp`, `clang-tools`,
`stdenv`, `libcxxStdenv`.

### Three Levels of Clang Integration

| Level | Attribute | C++ stdlib | Linker | Bintools | Compatibility |
|-------|-----------|-----------|--------|----------|---------------|
| Basic | `clangStdenv` / `llvmPackages_XX.stdenv` | libstdc++ (GCC) | GNU ld | GNU | Highest |
| Recommended | `llvmPackages_XX.libcxxStdenv` | libc++ (LLVM) | GNU ld | GNU | Good |
| Pure LLVM | `clangUseLLVM` / `pkgsLLVM` | libc++ (LLVM) | lld | LLVM | Lowest |

**Recommendation:** Use `libcxxStdenv` for development. Fall back to `stdenv` if you hit libc++ incompatibilities.

### Critical: clangd LSP Fix (nixpkgs #308482)

**Problem:** When `clang` and `clang-tools` are both in PATH, an unwrapped clangd binary shadows the properly-configured one, breaking header resolution.

**Fix:** Always use `llvmPackages_XX.clang-tools` and ensure it appears BEFORE any clang package in `nativeBuildInputs`. When using `libcxxStdenv`, clang is provided by stdenv — do NOT add `llvmPkgs.clang` separately.

```nix
nativeBuildInputs = [
  llvmPkgs.clang-tools  # MUST be first — provides working clangd
  cmake
  ninja
  pkg-config
];
# clang itself comes from libcxxStdenv override — do NOT duplicate
```

### Mold Linker

Use `pkgs.mold-wrapped` (NOT `pkgs.mold`) on NixOS. Unwrapped mold doesn't set RUNPATH correctly due to non-FHS layout.

```nix
packages = [ pkgs.mold-wrapped ];
LDFLAGS = "-fuse-ld=mold";
```

Verify: `readelf -p .comment ./build/binary` shows "Linker: mold".

### mkShell Setup Hook Rule

In `mkShell`, `packages` (alias for `nativeBuildInputs`) **triggers setup hooks** that populate `CMAKE_PREFIX_PATH` and `PKG_CONFIG_PATH`. The `buildInputs` parameter does NOT trigger hooks. Always use `packages` or `nativeBuildInputs` for tools.

### Adding Libraries

1. Find package on https://search.nixos.org/packages
2. Add to `buildInputs` in the flake
3. Use standard `find_package()` in CMakeLists.txt — no path config needed

Nix's cmake setup hook auto-populates `CMAKE_PREFIX_PATH` with store paths of all `buildInputs`.

For libraries NOT in nixpkgs:
```nix
myLib = pkgs.stdenv.mkDerivation {
  pname = "mylib"; version = "1.0";
  src = pkgs.fetchFromGitHub { owner = "x"; repo = "y"; rev = "v1.0"; hash = "sha256-..."; };
  nativeBuildInputs = [ pkgs.cmake ];
};
# Then add myLib to buildInputs
```

Use `lib.fakeHash` first — Nix reports the correct hash on build failure.

### Sanitizer Flags

| Sanitizer | Flag | Compatible With |
|-----------|------|----------------|
| ASan | `-fsanitize=address` | UBSan, LSan |
| UBSan | `-fsanitize=undefined` | ASan |
| TSan | `-fsanitize=thread` | None (exclusive) |
| MSan | `-fsanitize=memory` | None (exclusive) |
| LSan | `-fsanitize=leak` | ASan |

Always add `-fno-omit-frame-pointer -g` with sanitizers for readable stack traces.

ASan + TSan + MSan are mutually exclusive. Best default: ASan + UBSan.

### Profiling Tools (nixpkgs names)

| Tool | Package | Purpose | Platform |
|------|---------|---------|----------|
| Valgrind | `valgrind` | Memory leaks, Callgrind | Linux |
| perf | `linuxPackages.perf` | CPU sampling | Linux only |
| Hotspot | `hotspot` | perf flame graph GUI | Linux only |
| Heaptrack | `heaptrack` | Heap allocation profiling | Linux only |
| KCachegrind | `kcachegrind` | Callgrind visualization | Linux, macOS |
| rr | `rr` | Record-replay debugging | Linux only |
| GDB | `gdb` | General debugging | All |
| LLDB | `llvmPackages_XX.lldb` | LLVM-native debugging | All |
| cppcheck | `cppcheck` | Static analysis | All |
| iwyu | `include-what-you-use` | Header hygiene | All |

### compile_commands.json

- CMake: `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` or env var `CMAKE_EXPORT_COMPILE_COMMANDS=ON`
- Meson: generated automatically
- Other: use `bear -- make` (add `pkgs.bear` to packages)

---

## Reference Flake Template

When generating a flake, use this as the base and customize:

```nix
{
  description = "Complete Clang/LLVM C++ development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "x86_64-darwin" ];

      perSystem = { config, pkgs, system, lib, ... }:
        let
          # ── Change this ONE line to switch default LLVM version ──
          llvm = pkgs.llvmPackages_21;

          mkClangShell = { llvmPkgs
                         , extraPackages ? []
                         , extraShellHook ? ""
                         , extraBuildInputs ? []
                         , name ? "cpp-dev"
                         }:
            pkgs.mkShell.override { stdenv = llvmPkgs.libcxxStdenv; } {
              inherit name;

              nativeBuildInputs = with pkgs; [
                cmake
                ninja
                pkg-config
                llvmPkgs.clang-tools   # clangd — MUST be first
                bear                   # compile_commands.json for non-cmake
              ];

              buildInputs = [
                llvmPkgs.llvm
                llvmPkgs.lld
                llvmPkgs.compiler-rt
                llvmPkgs.openmp
              ] ++ extraBuildInputs;

              packages = with pkgs; [
                mold-wrapped
                llvmPkgs.lldb
                gdb
                rr
                valgrind
                heaptrack
                kcachegrind
                cppcheck
                include-what-you-use
                catch2_3
                gtest
                gbenchmark
                ccache
                cmake-language-server
                cmake-format
              ] ++ extraPackages
                ++ lib.optionals pkgs.stdenv.hostPlatform.isLinux [
                  linuxPackages.perf
                  hotspot
                ];

              CMAKE_GENERATOR = "Ninja";
              CMAKE_EXPORT_COMPILE_COMMANDS = "ON";
              CMAKE_BUILD_TYPE = "Debug";
              LDFLAGS = "-fuse-ld=mold";

              shellHook = ''
                echo "C++ dev: $(c++ --version | head -1)"
              '' + extraShellHook;
            };

          # ── Add project libraries here ──
          projectLibs = with pkgs; [
            boost fmt spdlog nlohmann_json
            # openssl protobuf grpc eigen tbb opencv
          ];

        in {
          devShells.default = mkClangShell {
            llvmPkgs = llvm;
            extraBuildInputs = projectLibs;
          };

          devShells.llvm20 = mkClangShell {
            llvmPkgs = pkgs.llvmPackages_20;
            name = "cpp-llvm20";
            extraBuildInputs = projectLibs;
          };

          devShells.llvm19 = mkClangShell {
            llvmPkgs = pkgs.llvmPackages_19;
            name = "cpp-llvm19";
            extraBuildInputs = projectLibs;
          };

          devShells.asan = mkClangShell {
            llvmPkgs = llvm;
            name = "cpp-asan";
            extraBuildInputs = projectLibs;
            extraShellHook = ''
              export CFLAGS="''${CFLAGS:-} -fsanitize=address,undefined -fno-omit-frame-pointer -g"
              export CXXFLAGS="''${CXXFLAGS:-} -fsanitize=address,undefined -fno-omit-frame-pointer -g"
              export LDFLAGS="''${LDFLAGS:-} -fsanitize=address,undefined"
              export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:print_stacktrace=1"
              export UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"
            '';
          };

          devShells.tsan = mkClangShell {
            llvmPkgs = llvm;
            name = "cpp-tsan";
            extraBuildInputs = projectLibs;
            extraShellHook = ''
              export CFLAGS="''${CFLAGS:-} -fsanitize=thread -fno-omit-frame-pointer -g"
              export CXXFLAGS="''${CXXFLAGS:-} -fsanitize=thread -fno-omit-frame-pointer -g"
              export LDFLAGS="''${LDFLAGS:-} -fsanitize=thread"
              export TSAN_OPTIONS="second_deadlock_stack=1:history_size=4"
            '';
          };

          devShells.release = mkClangShell {
            llvmPkgs = llvm;
            name = "cpp-release";
            extraBuildInputs = projectLibs;
            extraShellHook = ''
              export CMAKE_BUILD_TYPE="Release"
              export CFLAGS="''${CFLAGS:-} -O3 -DNDEBUG -march=native -flto=thin"
              export CXXFLAGS="''${CXXFLAGS:-} -O3 -DNDEBUG -march=native -flto=thin"
              export LDFLAGS="''${LDFLAGS:-} -flto=thin"
            '';
          };
        };
    };
}
```

## DevShell Usage Reference

| Shell | Command | Purpose |
|-------|---------|---------|
| default | `nix develop` | LLVM 21 + all tools + mold + ninja |
| llvm20 | `nix develop .#llvm20` | LLVM 20 variant |
| llvm19 | `nix develop .#llvm19` | LLVM 19 variant |
| asan | `nix develop .#asan` | ASan + UBSan pre-configured |
| tsan | `nix develop .#tsan` | ThreadSanitizer |
| release | `nix develop .#release` | O3 + LTO + march=native |

## Workflow Commands

```bash
# Build
cmake -B build && cmake --build build -j$(nproc)

# Test
ctest --test-dir build --output-on-failure

# Profile (CPU)
perf record -g --call-graph dwarf ./build/app && hotspot perf.data

# Profile (memory)
valgrind --tool=callgrind ./build/app && kcachegrind callgrind.out.*
heaptrack ./build/app && heaptrack_gui heaptrack.*.gz

# Record-replay debug
rr record ./build/app && rr replay

# Multi-version CI test
for s in llvm19 llvm20 default; do
  nix develop .#$s -c bash -c "cmake -B build-$s && cmake --build build-$s"
done
```

## .envrc (direnv integration)

```bash
use flake
```

## .clangd (editor config)

```yaml
CompileFlags:
  CompilationDatabase: build/
  Add: ["-std=c++23", "-Wall", "-Wextra"]
Diagnostics:
  UnusedIncludes: Strict
  ClangTidy:
    Add: [modernize-*, performance-*, bugprone-*]
```

## Common Gotchas

1. **clangd broken** -- `clang-tools` must be BEFORE any clang in PATH. Don't add `llvmPkgs.clang` when using `libcxxStdenv` (it provides clang already).
2. **mold on NixOS** -- Use `mold-wrapped`, never `mold`. Unwrapped breaks RUNPATH.
3. **CC=gcc despite clangStdenv** -- Known bug (nixpkgs #304311). Use `libcxxStdenv` instead.
4. **Missing headers** -- Ensure library is in `buildInputs` (not just `packages`). Check `.dev` output if needed: `pkg.dev`.
5. **MSan useless with nixpkgs deps** -- All linked libs must be MSan-instrumented. Only practical for your own code.
6. **perf on macOS** -- Doesn't exist. Use Instruments or `dtrace`.
7. **buildInputs vs packages in mkShell** -- `packages`/`nativeBuildInputs` triggers setup hooks (CMAKE_PREFIX_PATH). `buildInputs` does NOT.
8. **Split outputs** -- Some packages split headers into `.dev`. If `find_package` fails, try `pkg.dev` in buildInputs.

## Package Derivation Pattern (for `nix build`)

When the user also wants a buildable package, add a `package.nix`:

```nix
# package.nix
{ lib, stdenv, cmake, ninja, boost, fmt, catch2_3 }:
stdenv.mkDerivation {
  pname = "my-project";
  version = "0.1.0";
  src = lib.sourceByRegex ./. [ "^src.*" "^include.*" "^test.*" "CMakeLists.txt" ];
  nativeBuildInputs = [ cmake ninja ];
  buildInputs = [ boost fmt ];
  nativeCheckInputs = [ catch2_3 ];
  doCheck = true;
}
```

In the flake, add:
```nix
packages.default = pkgs.callPackage ./package.nix {};
```

Use `inputsFrom = [ config.packages.default ]` in devShell to inherit deps without duplication.

## Cross-Compilation

```nix
packages.crossAarch64 = pkgs.pkgsCross.aarch64-multiplatform.callPackage ./package.nix {};
packages.static = pkgs.pkgsStatic.callPackage ./package.nix {};
```

Requires correct `nativeBuildInputs` (build host) vs `buildInputs` (target) separation.
