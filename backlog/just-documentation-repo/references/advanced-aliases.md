---
description: Alternative names for recipes
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Aliases

Aliases allow recipes to be invoked with alternative names.

## Basic Alias

```just
alias b := build

build:
  echo 'Building!'
```

```console
$ just b
echo 'Building!'
Building!
```

## Aliases in Submodules

```justfile
mod foo

alias baz := foo::bar
```

## Private Aliases

```just
[private]
alias s := some-really-long-recipe-name

some-really-long-recipe-name:
  echo "Hello"
```

```console
$ just --list
Available recipes:
    some-really-long-recipe-name
```