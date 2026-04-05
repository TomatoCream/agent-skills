---
description: Recipe and module annotations for customization
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Attributes

## Recipe Attributes

| Name | Description |
|------|-------------|
| `[arg(ARG, ...)]` | Configure recipe argument options |
| `[confirm]` / `[confirm(PROMPT)]` | Require confirmation before executing |
| `[default]` | Use as default recipe |
| `[doc(DOC)]` | Set documentation comment |
| `[dragonfly]` / `[freebsd]` / `[linux]` / `[macos]` / `[netbsd]` / `[openbsd]` / `[unix]` / `[windows]` | Enable on specific OS |
| `[env(ENV_VAR, VALUE)]` | Set environment variable for recipe |
| `[extension(EXT)]` | Set shebang script file extension |
| `[group(NAME)]` | Put recipe in group |
| `[metadata(METADATA)]` | Attach metadata list to recipe |
| `[no-cd]` | Don't change directory before executing |
| `[no-exit-message]` | Don't print error message on failure |
| `[no-quiet]` | Always echo recipe line |
| `[parallel]` | Run dependencies in parallel |
| `[positional-arguments]` | Enable positional arguments |
| `[private]` | Hide from `just --list` |
| `[script(COMMAND)]` / `[script]` | Execute as script |
| `[working-directory(PATH)]` | Set working directory |

## Multiple Attributes

```just
[no-cd]
[private]
foo:
    echo "foo"
```

Or on one line:

```just
[no-cd, private]
foo:
    echo "foo"
```

## OS-Specific Recipes

```just
[unix]
run:
  cc main.c
  ./a.out

[windows]
run:
  cl main.c
  main.exe
```

## Requiring Confirmation

```just
[confirm]
delete-all:
  rm -rf *
```

Custom prompt:

```just
[confirm("Are you sure?")]
delete-everything:
  rm -rf *
```

## Grouping Recipes

```just
[group('lint')]
js-lint:
    echo 'Running JS linter…'

[group('lint')]
rust-lint:
    echo 'Running Rust linter…'
```

List groups with `just --groups`:

```console
$ just --groups
Recipe groups:
  lint
```

## Setting Environment Variables

```just
[env("RUST_BACKTRACE", "1")]
test:
  cargo test
```

## Doc Comments

```just
[doc('Build stuff')]
build:
  ./bin/build

[doc]
test:
  ./bin/test
```