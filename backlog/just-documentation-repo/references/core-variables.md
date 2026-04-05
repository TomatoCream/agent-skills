---
description: Variable assignments, expressions, and string handling
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Variables

Module-level variables are assigned with `:=`:

```just
foo := "hello"
bar := "world"

baz:
  echo {{ foo + " " + bar }}
```

## Concatenation

The `+` operator concatenates strings:

```just
foobar := 'foo' + 'bar'
```

## Path Joining

The `/` operator joins paths with `/`:

```just
tmpdir  := `mktemp -d`
version := "0.2.7"
tardir  := tmpdir / "awesomesauce-" + version
tarball := tardir + ".tar.gz"
```

## Strings

Single-quoted strings (`'...'`) do not process interpolations or escape sequences.
Double-quoted strings (`"..."`) support escape sequences and `{{...}}` interpolation.

Triple-quoted strings for multi-line:

```just
single := '''
  foo
  bar
'''

double := """
  abc
    wuv
  xyz
"""
```

Indented strings are stripped of common leading whitespace.

## Shell-Expanded Strings

Prefix with `x` for shell expansion at compile time:

```just
foobar := x'~/$FOO/${BAR}'
```

| Value | Replacement |
|-------|-------------|
| `$VAR` | Environment variable |
| `${VAR:-DEFAULT}` | With fallback |
| `~` | Home directory |

## Format Strings

Prefix with `f` for interpolated strings:

```just
name := "world"
message := f'Hello, {{name}}!'
```

## Exporting

Prefix assignments with `export` to pass as environment variables:

```just
export RUST_BACKTRACE := "1"

test:
  cargo test
```

Or set globally:

```just
set export
```

## Overriding from Command Line

Pass `NAME=VALUE` before recipes:

```console
$ just os=plan9 build
./build plan9
```

Or use `--set`:

```console
$ just --set os bsd
```