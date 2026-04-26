---
name: df-nix-python-flake
description: >
  Create production-ready Nix flakes for modern Python development with uv, ruff,
  pyright, treefmt-nix, and direnv. Use when writing flake.nix for Python projects,
  setting up Nix dev shells for Python with type checking and linting, configuring
  uv for fast package management, or building Python developer environments with
  modern tooling (ruff, pyright, mypy, pytest). Triggers on: python nix flake,
  uv nix, python devenv, ruff pyright nix, python devshell, nix python development,
  treefmt python, or modern python nix.
---

# Nix Flake for Modern Python Development

## Stack: uv + ruff + pyright + treefmt-nix

**Always use this combination unless the user explicitly requests otherwise.**

- **uv**: 10-100x faster than pip, modern Python package manager
- **ruff**: Rust-based linter/formatter, 10-100x faster than flake8/pylint
- **pyright**: Microsoft's static type checker (faster than mypy)
- **treefmt-nix**: Unified multi-language formatting via Nix

## Decision: Which Python Package Approach?

```
Need reproducible builds with locked deps?
  YES → Use uv + requirements.txt/requirements.in
  NO → Need flexibility for dev?
    YES → uv venv + requirements.txt (can be loose)
    NO → uv + pyproject.toml only
```

For AI/ML projects requiring CUDA: use `pkgs.python313` with `cudatoolkit`.

## Complete Flake Template

```nix
{
  description = "Modern Python development environment with uv, ruff, and pyright";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, treefmt-nix, devenv, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        isLinux = pkgs.stdenv.isLinux;
        isDarwin = pkgs.stdenv.isDarwin;

        # Python packages for tooling (NOT project deps)
        pythonTooling = with pkgs; [
          pkgs.python313
          pkgs.uv
          pkgs.ruff
          pkgs.pyright
          pkgs.mypy
          pkgs.psi
        ];

        # CACERT: Required for SSL/TLS in Python (pip, requests, etc.)
        cacertEnv = pkgs.writeShellScriptBin "cacert-env" ''
          export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export REQUESTS_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export CURL_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
        '';

        # Optional: CUDA support for AI/ML
        cudaPackages = pkgs.lib.optionals isLinux pkgs.cudaPackages;
      in {
        # treefmt configuration for `nix fmt`
        formatter = treefmt-nix.lib.mkTreefmtEval {
          projectRootFile = ./flake.nix;
          programs.ruff.enable = true;
          programs.nixfmt.enable = true;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Core Python
            pkgs.python313Full
            # Package manager
            pkgs.uv
            # Linting & formatting
            pkgs.ruff
            # Type checking
            pkgs.pyright
            pkgs.mypy
            pkgs.psi
            # Testing
            pkgs.pytest
            pkgs.pytest-cov
            pkgs.pytest-xdist
            # Dev tools
            pkgs.direnv
            pkgs.fzf
            pkgs.jq
            # CA certificates for SSL
            pkgs.cacert
          ] ++ pkgs.lib.optionals isLinux cudaPackages;

          shellHook = ''
            # CACERT: SSL/TLS for Python
            export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
            export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
            export REQUESTS_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
            export CURL_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"

            # uv: Create venv if not exists, install deps
            if [ ! -d .venv ]; then
              echo "Creating virtual environment with uv..."
              uv venv .venv
            fi
            export VIRTUAL_ENV="$(pwd)/.venv"
            export PATH="$VIRTUAL_ENV/bin:$PATH"

            # Show status
            echo "Python: $(python --version)"
            echo "uv: $(uv --version)"
            echo "ruff: $(ruff --version)"
            echo "pyright: $(pyright --version 2>/dev/null || echo 'see pyproject.toml')"
          '';
        };
      }
    );
}
```

## pyproject.toml Configuration

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.uv]
dev-dependencies = [
    "ruff>=0.8.0",
    "pyright>=1.1.0",
    "mypy>=1.0",
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "pytest-xdist>=3.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "YTT", # flake8-2020
    "ASYNC", # flake8-async
    "RUF", # Ruff-specific rules
]
ignore = ["E501"]  # line too long (use formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pyright]
include = ["src"]
exclude = ["**/node_modules", "**/__pycache__"]
reportMissingImports = true
reportMissingTypeStubs = false
pythonVersion = "3.11"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

## .envrc for direnv

```
use flake
```

Or with devenv:
```
use flake --override-input devenv github:cachix/devenv
```

## Common Patterns

### Using uv with requirements.txt

```nix
shellHook = ''
  # ... cacert exports ...

  if [ -f requirements.txt ]; then
    uv pip install -r requirements.txt
  fi
  if [ -f requirements-dev.txt ]; then
    uv pip install -r requirements-dev.txt
  fi
'';
```

### Adding Project-Specific Dependencies via uv

```nix
# Install project in editable mode
editablePackage = pkgs.python313.withPackages (ps: [
  ps.uv
]);

devShells.default = pkgs.mkShell {
  buildInputs = [
    pkgs.python313Full
    pkgs.uv
    editablePackage
    # ... other tooling
  ];
};
```

### Multi-Shell Setup (default + quiet for AI)

```nix
devShells = {
  default = pkgs.mkShell { /* ... */ };
  quiet = pkgs.mkShell {
    buildInputs = [ pkgs.python313Full pkgs.uv pkgs.ruff ];
    shellHook = ''
      export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
      uv venv .venv 2>/dev/null || true
      export VIRTUAL_ENV="$(pwd)/.venv"
      export PATH="$VIRTUAL_ENV/bin:$PATH"
    '';
  };
};
```

## Python Tooling Reference

### Linters/Formatters (add to devShell)

| Tool | nixpkgs | What It Does |
|------|---------|--------------|
| `ruff` | Yes | Lint + format (use instead of flake8, isort, black) |
| `ruff-lsp` | No | LSP server for ruff |
| `pyflakes` | Yes | Simple linting |
| `flake8` | Yes | Legacy linting (use ruff instead) |

### Type Checkers (add to devShell)

| Tool | nixpkgs | What It Does |
|------|---------|--------------|
| `pyright` | Yes | Microsoft's type checker (fast, strict) |
| `pyre` | Yes | Facebook's type checker |
| `mypy` | Yes | Popular gradual type checker |
| `psi` | Yes | NASA's type checker |

### Test Runners (add to devShell)

| Tool | nixpkgs | What It Does |
|------|---------|--------------|
| `pytest` | Yes | Standard test runner |
| `pytest-cov` | Yes | Coverage plugin |
| `pytest-xdist` | Yes | Parallel test execution |
| `pytest-mock` | Yes | Mocking plugin |
| `pytest-asyncio` | Yes | Async test support |
| `nox` | Yes | Configurable test automation |

### Package Managers

| Tool | nixpkgs | What It Does |
|------|---------|--------------|
| `uv` | Yes | Modern 10-100x faster pip/venv replacement |
| `pdm` | Yes | PEP-582 package manager |
| `poetry` | Yes | Dependency management |
| `pip` | Yes | Legacy (use uv instead) |

### Editors/LSP

| Tool | nixpkgs | What It Does |
|------|---------|--------------|
| `python-lsp-server` | Yes | Generic LSP server |
| `ruff-lsp` | AUR/custom | Ruff as LSP server |

## CACERT: SSL/TLS in Dev Shells

**Always include cacert in dev shells.** Python's `ssl`, `urllib`, `requests`, and `httpx`
need CA certificates to verify HTTPS connections. Without proper environment variables,
pip installs, API calls, and package downloads will fail with certificate errors.

```nix
# Required in every Python devShell
buildInputs = [ pkgs.cacert ];

shellHook = ''
  export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
  export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
  export REQUESTS_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
  export CURL_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
'';
```

See `df-nix-cacert-flake` skill for full documentation.

## treefmt-nix Configuration

```nix
programs.ruff = {
  enable = true;
  settings = {
    fix = true;
    eager = true;
  };
};
```

Run `nix fmt` to format all files. Run `nix flake check` to validate formatting in CI.

## Quick Start

```bash
# 1. Initialize flake
nix flake init -t flake-templates#python

# 2. Create pyproject.toml with ruff/pyright config
# 3. Add .envrc with `use flake`
# 4. Allow direnv
direnv allow

# 5. Enter shell
nix develop

# 6. Format code
nix fmt

# 7. Type check
pyright

# 8. Lint
ruff check .
```

## Anti-Patterns

- **Using pip instead of uv**: uv is 10-100x faster and handles venv automatically.
- **Using black instead of ruff-format**: ruff-format is built into ruff, no separate tool needed.
- **Using flake8/pylint instead of ruff**: ruff is 10-100x faster and combines multiple tools.
- **Skipping CACERT**: Python SSL will fail without proper certificate environment variables.
- **Using mypy only when pyright is available**: pyright is faster and more strict by default.
- **Putting dev deps in buildInputs instead of uv**: Nix packages are for tooling, uv handles project deps.
