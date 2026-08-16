# Knowledge Gap Heuristics

How to determine what Claude already knows vs. what the skill must teach.

## Contents
- Library popularity tiers and coverage estimation
- Per-category filtering rules
- Language-specific extraction patterns
- Signal density scoring

---

## Library Popularity Tiers

Claude's training coverage correlates with library popularity. Use GitHub stars as a proxy:

| Tier | Stars | Training Coverage | Skill Strategy |
|------|-------|-------------------|----------------|
| A (Mega) | > 50K | Excellent - Claude knows core API well | Focus almost entirely on gotchas, version-specific changes, and configuration pitfalls. Skip basic usage. |
| B (Popular) | 10K-50K | Good - Claude knows common patterns | Include correct patterns for top 5 operations + all gotchas. Skip conceptual explanations. |
| C (Known) | 1K-10K | Partial - Claude has seen it but may confuse details | Include setup, common patterns, gotchas, and correct API signatures. |
| D (Niche) | < 1K | Minimal - Claude may not know this library | Include everything: setup, all patterns, gotchas, API reference. Most comprehensive skill needed. |

### How to Determine Tier

```bash
# For GitHub repos:
gh repo view <owner/repo> --json stargazerCount -q '.stargazerCount'

# For non-GitHub: estimate from npm downloads, Maven Central downloads, PyPI downloads
```

---

## Per-Category Filtering Rules

### Configuration & Setup

| Item | Tier A | Tier B | Tier C | Tier D |
|------|--------|--------|--------|--------|
| Install command | Skip | Skip | Include | Include |
| Import statements | Skip | Skip | Include | Include |
| Basic initialization | Skip | Include if non-obvious | Include | Include |
| Pool/connection config | Include (gotcha-focus) | Include | Include | Include |
| Recommended production settings | Include | Include | Include | Include |
| Environment requirements | Include if unusual | Include | Include | Include |

### Gotchas & Pitfalls (Always Include)

All gotchas pass the filter regardless of tier. However, prioritize differently:

**Tier A:** Gotchas are the PRIMARY content. Claude knows the API but not the traps.
**Tier B-C:** Gotchas are HIGH priority alongside correct patterns.
**Tier D:** Gotchas are important but secondary to basic API coverage.

### Common Usage Patterns

| Pattern Type | Tier A | Tier B | Tier C | Tier D |
|-------------|--------|--------|--------|--------|
| "Hello world" example | Skip | Skip | Include | Include |
| Top 3 operations | Include only if non-obvious | Include | Include | Include |
| Error handling | Include if library-specific | Include | Include | Include |
| Resource cleanup | Include (often a gotcha) | Include | Include | Include |

### Version-Specific Information

| Item | Include When |
|------|-------------|
| Breaking changes between current and previous major | Always (if multiple versions in use) |
| Deprecated API replacements | Always |
| New features in latest version | Only if Claude's training likely predates them |
| Version compatibility matrix | Only for Tier C-D or when complex |

### Advanced Features

| Feature Type | Include When |
|-------------|-------------|
| Performance tuning | When defaults are inadequate for production |
| Plugin/extension system | When commonly needed |
| Batch operations | When significantly different from single operations |
| Async/reactive variants | When API differs from sync version |

Always put advanced features in **reference files**, not SKILL.md.

### Ecosystem Integration

| Integration | Include When |
|------------|-------------|
| Framework integration (Spring, Express, etc.) | When setup is non-obvious or gotcha-prone |
| Companion libraries | When frequently used together |
| Known conflicts | Always |

---

## Language-Specific Extraction Patterns

### Java (Maven/Gradle)

**Build system detection:**
- `pom.xml` -> Maven: extract groupId, artifactId, version from project coordinates
- `build.gradle` / `build.gradle.kts` -> Gradle: extract dependencies block
- `settings.gradle` -> Multi-module project structure

**Public API extraction:**
```bash
# Find public classes (main API surface)
grep -rn "public class\|public interface\|public enum" src/main/java/ --include="*.java"

# Find deprecated elements
grep -rn "@Deprecated" src/main/java/ --include="*.java"

# Find thread-safety annotations
grep -rn "@ThreadSafe\|@NotThreadSafe\|@GuardedBy\|synchronized" src/main/java/ --include="*.java"
```

**Key files to read:**
- `src/main/java/<package>/` - top-level classes are usually the main API
- `*Config*.java`, `*Options*.java`, `*Builder*.java` - configuration surface
- `*Exception*.java` - error hierarchy
- `src/test/java/` - integration tests show intended usage

### JavaScript/TypeScript (npm)

**Build system detection:**
- `package.json` -> extract name, version, main/module/exports, peerDependencies
- `tsconfig.json` -> TypeScript project, check "declaration" for type exports

**Public API extraction:**
```bash
# Find exports
grep -rn "export\s\+\(default\|class\|function\|const\|interface\|type\)" src/ --include="*.ts" --include="*.js"

# Check package.json "exports" field for public API surface
```

**Key files to read:**
- Entry point (main/module field in package.json)
- `index.ts` / `index.js` - re-exports define public API
- `types/` or `*.d.ts` - type definitions
- `examples/` directory

### Python (pip/poetry)

**Build system detection:**
- `pyproject.toml` -> extract name, version, dependencies
- `setup.py` / `setup.cfg` -> legacy, extract install_requires
- `requirements.txt` -> dependency list

**Public API extraction:**
```bash
# Find __all__ declarations (explicit public API)
grep -rn "__all__" src/ --include="*.py"

# Find public classes and functions
grep -rn "^class \|^def " src/ --include="*.py" | grep -v "^.*:.*_"

# Find deprecation warnings
grep -rn "DeprecationWarning\|warnings.warn" src/ --include="*.py"
```

**Key files to read:**
- `__init__.py` at package root - defines public imports
- `conftest.py` - test fixtures show setup patterns
- `examples/` or `docs/` directory

### Go

**Module detection:**
- `go.mod` -> extract module path, Go version, dependencies

**Public API extraction:**
```bash
# Exported symbols start with uppercase
grep -rn "^func [A-Z]\|^type [A-Z]" --include="*.go" | grep -v "_test.go"

# Find interfaces (the Go API contract)
grep -rn "type [A-Z].*interface" --include="*.go"
```

### Rust

**Crate detection:**
- `Cargo.toml` -> extract name, version, features, dependencies

**Public API extraction:**
```bash
# Find pub items
grep -rn "^pub " src/ --include="*.rs"

# Find feature flags
grep -rn '#\[cfg(feature' src/ --include="*.rs"
```

---

## Signal Density Scoring

When you have more content than fits in the skill, score each item:

| Factor | Points |
|--------|--------|
| Caused real bugs (GitHub Issues evidence) | +3 |
| Violates common expectations | +3 |
| Version-specific (changed recently) | +2 |
| Library-specific pattern (not general) | +2 |
| Frequently asked on Stack Overflow | +2 |
| Has a clear WRONG/RIGHT code example | +1 |
| Documented in source with WARNING/CAUTION | +1 |
| General programming concept | -3 |
| Claude demonstrably knows this already | -3 |
| Can be discovered by reading source at runtime | -1 |

**Include in SKILL.md:** Score >= 4
**Include in reference file:** Score 1-3
**Exclude:** Score <= 0

---

## Quick Decision Flowchart

For each piece of extracted knowledge:

```
Is it a gotcha/pitfall?
  YES -> Include in SKILL.md gotchas section
  NO  -> Continue

Is this library Tier A or B?
  YES -> Would Claude get this wrong without help?
    YES -> Include
    NO  -> Skip
  NO (Tier C-D) -> Is this part of the core API?
    YES -> Include
    NO  -> Put in reference file or skip
```
