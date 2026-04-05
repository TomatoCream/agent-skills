---
description: Script-based recipe execution with [script] attribute
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Script Recipes

Recipes with `[script(COMMAND)]` or `[script]` are run as scripts.

## Basic Script Recipe

```just
[script]
hello:
  print("Hello from Python!")
```

Default interpreter is `sh -eu` unless `set script-interpreter` is used.

## Custom Interpreter

```just
[script('python3')]
hello:
  print("Hello!")
```

## Setting Default Interpreter

```just
set script-interpreter := ['uv', 'run', '--script']
```

## Python with uv

```just
set script-interpreter := ['uv', 'run', '--script']

[script]
hello:
  print("Hello from Python!")

[script]
goodbye:
  # /// script
  # requires-python = ">=3.11"
  # dependencies=["sh"]
  # ///
  import sh
  print(sh.echo("Goodbye from Python!"), end='')
```

## Shebang vs Script

| Feature | Shebang | Script |
|---------|---------|--------|
| Temp file | Yes | Yes |
| Portable interpreter | No (shebang splitting varies) | Yes (explicit command) |
| Windows Cygpath | Yes (for `/` paths) | No |
| Default quiet | Yes | No |

## Temporary Files

Both script and shebang recipes write to temporary files. Directory precedence:

1. `--tempdir` CLI option or `JUST_TEMPDIR` env var
2. `set tempdir := '...'` in justfile
3. `XDG_RUNTIME_DIR` on Linux
4. System default tempdir

## Python with uv Example

```just
[script]
hello:
  #!/usr/bin/env -S uv run --script
  print("Hello from Python!")
```