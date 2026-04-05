---
description: Recipe dependencies and execution order
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Dependencies

Recipes can depend on other recipes. Dependencies run before the dependent recipe.

## Basic Dependencies

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

## Multiple Dependencies

```just
a: b c
  echo A

b:
  echo B

c:
  echo C
```

## Dependency Execution Order

Dependencies always run first, even when passed after:

```console
$ just test build
cc main.c foo.c bar.c -o main
./test
```

## Subsequent Dependencies

Use `&&` for dependencies that run after the recipe:

```just
a:
  echo 'A!'

b: a && c d
  echo 'B!'

c:
  echo 'C!'

d:
  echo 'D!'
```

```console
$ just b
echo 'A!'
A!
echo 'B!'
B!
echo 'C!'
C!
echo 'D!'
D!
```

## Conditional Dependencies

Pass arguments to dependencies:

```just
default: (build "main")

build target:
  @echo 'Building {{target}}…'
  cd {{target}} && make
```

## Dependencies in Submodules

```justfile
mod foo

baz: foo::bar
```

## Deduplication

A recipe with the same arguments runs only once, regardless of how many times it's a dependency:

```just
build:
  cc main.c

test-foo: build
  ./a.out --test foo

test-bar: build
  ./a.out --test bar
```

```console
$ just test-foo test-bar
cc main.c
./a.out --test foo
./a.out --test bar
```