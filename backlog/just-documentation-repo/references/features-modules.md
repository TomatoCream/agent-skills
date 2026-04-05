---
description: Modular justfile organization with mod statements
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Modules

Modules organize justfiles into separate files.

## Basic Module

```justfile
# justfile
mod foo

baz: foo::bar
```

```justfile
# foo.just
mod bar

export BAR := "bar"

bar:
  echo "Bar!"
```

## Module Syntax

```just
mod NAME                 # Load NAME.just
mod NAME "path.just"     # Load specific path
mod NAME ?               # Optional module (don't error if missing)
```

## Using Recipes in Modules

```just
mod foo

test: foo::test
```

## Module Variables

Variables in modules are private unless exported:

```just
# in submodule
export VERSION := "1.0"
```

## Listing Module Recipes

```console
$ just --list foo bar
Available recipes:
    baz

$ just --list foo::bar
Available recipes:
    baz
```

## Importing

Modules can import other modules:

```just
# foo.just
mod bar

# bar.just
mod baz
```

## Cross-module Dependencies

```justfile
mod foo

baz: foo::bar
```

## Environment Variables in Modules

Dotenv files are inherited and can be overridden in submodules:

```just
# parent .env
FOO=bar

# child .env (in submodule)
FOO=baz
```