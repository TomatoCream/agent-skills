---
description: Writing and running recipe commands in justfiles
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Recipes

Recipes are commands stored in a `justfile` with syntax inspired by `make`.

## Basic Recipe

```just
recipe-name:
  echo 'This is a recipe!'
```

Run with `just RECIPE`:

```console
$ just test-all
cc *.c -o main
./test --all
```

## Recipe Dependencies

Recipes can depend on other recipes. Dependencies run first:

```just
build:
  cc main.c foo.c bar.c -o main

test: build
  ./test
```

```console
$ just test
cc main.c foo.c bar.c -o main
./test
testing… all tests passed!
```

## Default Recipe

When `just` is invoked without arguments, it runs the first recipe or one marked `[default]`:

```just
test:
  cargo test
```

## Documentation Comments

Comments before a recipe appear in `just --list`:

```just
# build stuff
build:
  ./bin/build
```

```console
$ just --list
Available recipes:
    build # build stuff
```

## Quiet Recipes

Prefix recipe name with `@` to suppress echo of recipe lines:

```just
@quiet:
  echo "This won't be echoed"
```

## Error Handling

Use `-` prefix to continue on error:

```just
foo:
  -rmdir bar
  mkdir bar
  echo 'done' > bar/stuff.txt
```

Use `?` prefix for error-handling that doesn't stop other recipes:

```just
set guards

@foo: bar
  echo FOO

@bar:
  ?[[ -f baz ]]
  echo BAR
```

## Private Recipes

Recipes starting with `_` are hidden from `just --list`:

```just
test: _test-helper
  ./bin/test

_test-helper:
  ./bin/super-secret-test-helper-stuff
```