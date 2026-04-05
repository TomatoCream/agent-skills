---
description: Predefined functions for use in expressions
source: https://github.com/casey/just/blob/master/README.md
source_sha: 7706216fbbe4b1fbcfa5d0c49962540ea3277a83
---

# Built-in Functions

## System Information

- `arch()` — Instruction set architecture (e.g., `"x86_64"`, `"aarch64"`)
- `os()` — Operating system (e.g., `"linux"`, `"macos"`, `"windows"`)
- `os_family()` — OS family (`"unix"` or `"windows"`)
- `num_cpus()` — Number of logical CPUs

## Environment Variables

- `env(key)` — Get environment variable, abort if not present
- `env(key, default)` — Get with fallback default

```just
home_dir := env('HOME')

test:
  echo "{{home_dir}}"
```

## Executables

- `require(name)` — Find executable in PATH, return full path or error
- `which(name)` — Find executable, return empty string if not found

## Path Functions

- `invocation_directory()` — Absolute path where `just` was invoked
- `justfile()` — Path of current justfile
- `justfile_directory()` — Parent directory of current justfile
- `source_file()` / `source_directory()` — Current source file (for imports/modules)
- `module_file()` / `module_directory()` — Current module file
- `just_executable()` — Absolute path to `just` binary
- `just_pid()` — Process ID of `just` process

## Path Manipulation (Infallible)

- `clean(path)` — Simplify path, remove extra separators and `.` `..`
- `join(a, b…)` — Join paths (uses `\` on Windows)
- `extension(path)` — File extension (can fail)
- `file_name(path)` — File name without directory
- `file_stem(path)` — File name without extension
- `parent_directory(path)` — Parent directory (can fail)
- `absolute_path(path)` — Make path absolute (can fail)
- `canonicalize(path)` — Resolve symlinks (can fail)

## String Functions

- `append(suffix, s)` — Append suffix to whitespace-separated strings
- `prepend(prefix, s)` — Prepend prefix to whitespace-separated strings
- `quote(s)` — Wrap in single quotes, escape internal quotes
- `replace(s, from, to)` — Replace all occurrences
- `replace_regex(s, regex, replacement)` — Replace with regex (capture groups supported)
- `trim(s)` / `trim_start(s)` / `trim_end(s)` — Remove whitespace
- `trim_start_match(s, substring)` / `trim_end_match(s, substring)` — Remove prefix/suffix
- `encode_uri_component(s)` — Percent-encode for URI

## Case Conversion

- `capitalize(s)` — First char uppercase, rest lowercase
- `lowercase(s)` / `uppercase(s)` — Case conversion
- `snakecase(s)` / `kebabcase(s)` — Convert to snake/kebab case
- `uppercamelcase(s)` / `lowercamelcase(s)` — Convert to camel case

## Filesystem

- `path_exists(path)` — Returns `"true"` or `"false"`
- `read(path)` — Read file contents as string

## Hashing and UUID

- `blake3(string)` / `blake3_file(path)` — BLAKE3 hash
- `sha256(string)` / `sha256_file(path)` — SHA-256 hash
- `uuid()` — Random version 4 UUID

## Random and datetime

- `choose(n, alphabet)` — Generate n random chars from alphabet
- `datetime(format)` — Local time with strftime format
- `datetime_utc(format)` — UTC time

## User Directories

- `cache_directory()` — User cache directory
- `config_directory()` — User config directory
- `data_directory()` — User data directory
- `home_directory()` — User home directory

## Constants

- `HEX` / `HEXLOWER` / `HEXUPPER` — Hex character sets
- `PATH_SEP` — `/` on Unix, `\` on Windows
- `CLEAR` / `NORMAL` / `BOLD` / `ITALIC` / etc. — ANSI escape sequences