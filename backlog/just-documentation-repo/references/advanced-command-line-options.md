---
description: Command-line options, flags, and environment variables
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Command-line Options

## Listing Recipes

```console
$ just --list              # List all recipes
$ just --summary           # Concise list
$ just --list --unsorted   # In justfile order
$ just --list-heading 'Custom Header\n'
$ just --list-prefix '···'
$ just --groups            # Show recipe groups
```

## Showing Recipe Details

```console
$ just --show RECIPE       # Show recipe body
$ just --usage RECIPE      # Show usage for recipe arguments
```

## Setting Variables

```console
$ just NAME=VALUE recipe   # Override variable
$ just --set NAME VALUE    # Same as above
$ just --set NAME          # Unset variable
```

## Justfile Selection

```console
$ just --justfile PATH     # Use specific justfile
$ just -f PATH             # Short form
$ just --working-directory PATH
$ just -d PATH             # Set working directory
```

## Environment Variables

| Variable | Effect |
|----------|--------|
| `JUST_UNSTABLE=1` | Enable unstable features |
| `JUSTFILE` | Path to justfile (same as `-f`) |
| `JUST_WORKING_DIRECTORY` | Working directory |
| `JUST_CHOOSER` | Interactive chooser (default: `fzf`) |
| `JUST_TEMPDIR` | Temporary directory |
| `JUST_RR` | Run recipes in parallel (experimental) |

## Unstable Features

```console
$ just --unstable
# or
$ export JUST_UNSTABLE=1
```

## Dry Run

```console
$ just --dry-run RECIPE    # Print without executing
```

## Variables and Evaluation

```console
$ just --evaluate          # Print all variable values
$ just --evaluate foo      # Print single variable
$ just --evaluate-format   # just|shell|json|dump
```

## Chooser

```console
$ just --choose            # Interactive recipe selection
$ just --chooser CMD       # Custom chooser command
```

## Other Options

- `--version` / `-V` — Print version
- `--help` / `-h` — Show help
- `--verbose` — Enable verbose output
- `--quiet` — Suppress all output
- `--clear-cache` — Clear justfile cache