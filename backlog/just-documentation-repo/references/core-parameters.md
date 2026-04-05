---
description: Recipe parameters and command-line arguments
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Recipe Parameters

Recipes may have parameters:

```just
build target:
  @echo 'Building {{target}}…'
  cd {{target}} && make
```

```console
$ just build my-awesome-project
Building my-awesome-project…
cd my-awesome-project && make
```

## Default Values

Parameters may have default values:

```just
default := 'all'

test target tests=default:
  @echo 'Testing {{target}}:{{tests}}…'
  ./test --tests {{tests}} {{target}}
```

```console
$ just test server
Testing server:all…
./test --tests all server

$ just test server unit
Testing server:unit…
./test --tests unit server
```

## Variadic Parameters

The last parameter may be variadic with `+` (one or more) or `*` (zero or more):

```just
backup +FILES:
  scp {{FILES}} me@server.com:
```

```console
$ just backup FAQ.md GRAMMAR.md
scp FAQ.md GRAMMAR.md me@server.com:
FAQ.md                  100% 1831     1.8KB/s   00:00
GRAMMAR.md              100% 1666     1.6KB/s   00:00
```

```just
commit MESSAGE *FLAGS:
  git commit {{FLAGS}} -m "{{MESSAGE}}"
```

## Exporting Parameters

Prefix with `$` to export as environment variables:

```just
foo $bar:
  echo $bar
```

## Parameter Attributes

| Attribute | Description |
|-----------|-------------|
| `[arg(ARG, long="LONG")]` | Use `--LONG` option |
| `[arg(ARG, short="S")]` | Use `-S` option |
| `[arg(ARG, pattern="PATTERN")]` | Validate with regex |
| `[arg(ARG, help="HELP")]` | Add help text |
| `[positional-arguments]` | Turn on positional arguments for recipe |

```just
[arg('n', pattern='\d+')]
double n:
  echo $(({{n}} * 2))
```

## Positional Arguments

Enable with `set positional-arguments` or `[positional-arguments]`:

```just
set positional-arguments

@foo bar:
  echo $0
  echo $1
```

```console
$ just foo hello
foo
hello
```