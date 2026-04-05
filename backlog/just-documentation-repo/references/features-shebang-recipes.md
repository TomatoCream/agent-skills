---
description: Writing recipes in other programming languages
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Shebang Recipes

Recipes starting with `#!` are executed by saving the body to a file and running it.

## Multi-Language Example

```just
polyglot: python js perl sh ruby nu

python:
  #!/usr/bin/env python3
  print('Hello from python!')

js:
  #!/usr/bin/env node
  console.log('Greetings from JavaScript!')

perl:
  #!/usr/bin/env perl
  print "Larry Wall says Hi!\n";

sh:
  #!/usr/bin/env sh
  hello='Yo'
  echo "$hello from a shell script!"

nu:
  #!/usr/bin/env nu
  let hello = 'Hola'
  echo $"($hello) from a nushell script!"

ruby:
  #!/usr/bin/env ruby
  puts "Hello from ruby!"
```

```console
$ just polyglot
Hello from python!
Greetings from JavaScript!
Larry Wall says Hi!
Yo from a shell script!
Hola from a nushell script!
Hello from ruby!
```

## How Shebang Works

On Unix: saves to temp file, marks executable, runs via OS shebang parsing.
On Windows: splits shebang line, saves to temp file, invokes command with file path as final arg.

## Passing Arguments with env

```just
run:
  #!/usr/bin/env -S bash -x
  ls
```

## Shebang Recipe Notes

- Shebang recipes are quiet by default (no echoing)
- Use `@` before recipe name to show recipe line before execution
- Temporary files created in system tempdir (configurable with `--tempdir`, `XDG_RUNTIME_DIR`, etc.)

## Safer Bash Shebang

Add `set -euxo pipefail` for safer bash recipes:

```just
foo:
  #!/usr/bin/env bash
  set -euxo pipefail
  hello='Yo'
  echo "$hello from Bash!"
```

## Windows Cygpath Translation

On Windows, Unix-style paths in shebang are translated via `cygpath`:

```just
echo:
  #!/bin/sh
  echo "Hello!"
```

`/bin/sh` becomes a Windows path via cygpath.

## Shebang vs Script Recipes

Use `[script]` attribute for more portable script execution, avoiding temp file and shebang splitting issues.