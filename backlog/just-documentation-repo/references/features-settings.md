---
description: Configuration settings for justfile behavior
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Settings

Settings control interpretation and execution. Each may be specified at most once anywhere in the justfile.

## Table of Settings

| Name | Value | Default | Description |
|------|-------|---------|-------------|
| `allow-duplicate-recipes` | boolean | `false` | Allow later recipes to override earlier |
| `allow-duplicate-variables` | boolean | `false` | Allow later variables to override earlier |
| `dotenv-filename` | string | - | Load custom `.env` filename |
| `dotenv-load` | boolean | `false` | Load `.env` file |
| `dotenv-override` | boolean | `false` | Override existing env vars from `.env` |
| `dotenv-path` | string | - | Custom path to `.env` file |
| `dotenv-required` | boolean | `false` | Error if `.env` not found |
| `export` | boolean | `false` | Export all variables as environment variables |
| `fallback` | boolean | `false` | Search parent for justfile if not found |
| `ignore-comments` | boolean | `false` | Ignore recipe lines beginning with `#` |
| `lazy` | boolean | `false` | Don't evaluate unused variables |
| `positional-arguments` | boolean | `false` | Pass positional arguments to commands |
| `quiet` | boolean | `false` | Disable echoing recipe lines |
| `script-interpreter` | `[COMMAND, ARGS…]` | `['sh', '-eu']` | Interpreter for `[script]` recipes |
| `shell` | `[COMMAND, ARGS…]` | - | Command to invoke recipe lines and backticks |
| `tempdir` | string | - | Directory for temporary files |
| `unstable` | boolean | `false` | Enable unstable features |
| `windows-shell` | `[COMMAND, ARGS…]` | - | Shell on Windows |
| `working-directory` | string | - | Working directory for recipes |

## Boolean Settings

Boolean settings can be written without `:= true`:

```justfile
set NAME
```

## Shell Setting

```just
set shell := ["zsh", "-cu"]

foo:
  ls **/*.txt
```

## Dotenv Settings

```just
set dotenv-load

serve:
  @echo "Starting server with database $DATABASE_ADDRESS"
  ./server --database $DATABASE_ADDRESS
```

With `.env` file:
```console
DATABASE_ADDRESS=localhost:6379
```

```console
$ just serve
Starting server with database localhost:6379
./server --database localhost:6379
```

## Windows PowerShell

```just
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

hello:
  Write-Host "Hello, world!"
```