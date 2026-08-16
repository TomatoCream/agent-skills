# Skill Templates by Repository Type

Templates for generating skill files from different types of repositories.

## Contents
- Template: Java library (Maven/Gradle)
- Template: JavaScript/TypeScript library (npm)
- Template: Python library (pip/poetry)
- Template: Go module
- Template: Multi-language / framework-agnostic
- Reference file template
- Eval case template

---

## Template: Java Library (Maven/Gradle)

```markdown
---
name: Using <LibraryName>
description: >
  <LibraryName> Java client for <what-it-connects-to/does>. Use when writing Java code
  that <primary-use-case>, when the user mentions <LibraryName>, <MainClass>,
  <SecondaryClass>, <common-import-path>, or <domain-keywords>.
  Not for <competing-libraries>.
---

# <LibraryName>

## Quick Start

**Maven:**
\```xml
<dependency>
    <groupId><group></groupId>
    <artifactId><artifact></artifactId>
    <version><latest-stable></version>
</dependency>
\```

**Gradle:**
\```groovy
implementation '<group>:<artifact>:<latest-stable>'
\```

**Minimal working example:**
\```java
// <One complete, working example of the most common use case>
// Include imports, initialization, usage, and cleanup
// Use try-with-resources if applicable
\```

## Common Patterns

### <Primary Operation> (e.g., Connection Management)
\```java
// The CORRECT production pattern
// Include pool/client setup with recommended settings
\```

### <Secondary Operation> (e.g., Basic CRUD)
\```java
// 2-3 most common operations
\```

### <Tertiary Operation> (e.g., Error Handling)
\```java
// Correct error handling / retry pattern
\```

## Gotchas

### Thread Safety
- **<Class> instances are [NOT] thread-safe.** <Explanation and correct pattern.>

### Resource Management
- **Always close/return <resource>.** <What happens if you don't.>
  \```java
  // WRONG
  <code that leaks resources>

  // RIGHT
  <code with proper cleanup>
  \```

### Configuration Defaults
- **<Setting> defaults to <value> which <causes problem>.** Set to <recommended>.

### Version Traps
- **<Deprecated API> removed in <version>.** Use <replacement> instead.

## Configuration

| Setting | Default | Recommended | Why |
|---------|---------|-------------|-----|
| <setting1> | <default> | <recommended> | <reason> |
| <setting2> | <default> | <recommended> | <reason> |

## References

- [Advanced Features](references/advanced-features.md) - <topics covered>
- [Migration Guide](references/migration-guide.md) - <version> to <version>
```

---

## Template: JavaScript/TypeScript Library (npm)

```markdown
---
name: Using <library-name>
description: >
  <library-name> - <what-it-does> for JavaScript/TypeScript. Use when writing JS/TS code
  that <primary-use-case>, when the user mentions <library-name>, <main-export>,
  <common-function-names>, or <domain-keywords>.
  Not for <competing-libraries>.
---

# <library-name>

## Quick Start

\```bash
npm install <package-name>
# or
yarn add <package-name>
\```

\```typescript
import { <MainExport> } from '<package-name>';

// Minimal working example
\```

## Common Patterns

### <Primary Pattern>
\```typescript
// Most common usage with proper error handling
\```

### <Secondary Pattern>
\```typescript
// Second most common usage
\```

## Gotchas

### <Category>
- **<Gotcha>:** <What goes wrong and why>
  \```typescript
  // WRONG
  <problematic code>

  // RIGHT
  <correct code>
  \```

## TypeScript Notes

- <Type export locations or quirks>
- <Generic parameter gotchas>
- <Declaration file notes>

## References

- [API Reference](references/api-reference.md) - Full API surface
- [Configuration](references/configuration.md) - All options
```

---

## Template: Python Library (pip/poetry)

```markdown
---
name: Using <library-name>
description: >
  <library-name> Python library for <what-it-does>. Use when writing Python code
  that <primary-use-case>, when the user mentions <library-name>, <main-class>,
  <common-function-names>, or <domain-keywords>.
  Not for <competing-libraries>.
---

# <library-name>

## Quick Start

\```bash
pip install <package-name>
\```

\```python
from <package> import <MainClass>

# Minimal working example
\```

## Common Patterns

### <Primary Pattern>
\```python
# Most common usage with context manager if applicable
\```

## Gotchas

### <Category>
- **<Gotcha>:** <What goes wrong>
  \```python
  # WRONG
  <problematic code>

  # RIGHT
  <correct code>
  \```

## References

- [Advanced Usage](references/advanced-usage.md) - <topics>
```

---

## Template: Go Module

```markdown
---
name: Using <module-name>
description: >
  <module-name> Go package for <what-it-does>. Use when writing Go code
  that <primary-use-case>, when the user mentions <module-name>, <MainType>,
  <key-function-names>, or <domain-keywords>.
  Not for <competing-packages>.
---

# <module-name>

## Quick Start

\```bash
go get <module-path>
\```

\```go
import "<module-path>"

// Minimal working example
\```

## Common Patterns

### <Primary Pattern>
\```go
// Idiomatic Go usage with proper error handling
\```

## Gotchas

### <Category>
- **<Gotcha>:** <What goes wrong>

## References

- [API Reference](references/api-reference.md) - Exported types and functions
```

---

## Reference File Template

```markdown
# <Domain Name> Reference

Detailed reference for <library-name> <domain>.

## Contents
- <Section 1>
- <Section 2>
- <Section 3>

---

## <Section 1>

### <Sub-topic>

<Detailed explanation with code examples>

\```<language>
// Complete, working example
// Include error handling
// Show edge cases
\```

**When to use:** <guidance>
**When NOT to use:** <guidance>

### <Sub-topic 2>

...
```

---

## Eval Case Template

```json
[
  {
    "id": "setup-basic",
    "description": "Test that Claude sets up the library correctly",
    "prompt": "Write a <language> function that <task requiring library setup>",
    "expected_behaviors": [
      "Uses correct dependency/import",
      "Initializes with recommended settings (not defaults)",
      "Includes proper resource cleanup",
      "Handles errors appropriately"
    ]
  },
  {
    "id": "gotcha-avoidance",
    "description": "Test that Claude avoids known pitfalls",
    "prompt": "Write a <language> function that <task involving known gotcha>",
    "expected_behaviors": [
      "Does NOT use <problematic pattern>",
      "Uses <correct pattern> instead",
      "Includes <required safety measure>"
    ]
  },
  {
    "id": "advanced-feature",
    "description": "Test that Claude can find and use advanced features",
    "prompt": "Write a <language> function that <task requiring advanced feature>",
    "expected_behaviors": [
      "Uses <advanced API> correctly",
      "Configures <required settings>",
      "Handles <edge case>"
    ]
  },
  {
    "id": "version-aware",
    "description": "Test that Claude uses the correct API for the version",
    "prompt": "Using <library> <version>, write <task with version-specific API>",
    "expected_behaviors": [
      "Uses <version-correct API>",
      "Does NOT use <deprecated API>",
      "Follows <version-specific pattern>"
    ]
  },
  {
    "id": "production-ready",
    "description": "Test that Claude produces production-quality code",
    "prompt": "Write a production-ready <component> using <library>",
    "expected_behaviors": [
      "Uses connection pooling (not direct connections)",
      "Sets appropriate timeouts",
      "Includes retry logic or circuit breaker",
      "Logs errors appropriately",
      "Cleans up resources on shutdown"
    ]
  }
]
```

---

## Trigger Query Template

```json
{
  "should_trigger": [
    "how do I use <library>",
    "help me with <library> in <language>",
    "<library> connection pool setup",
    "<library> <common-operation> example",
    "<MainClass> configuration",
    "connect to <backend> from <language>",
    "<domain-operation> with <library>",
    "<library> best practices",
    "<library> error handling",
    "migrate from <library> v<old> to v<new>"
  ],
  "should_not_trigger": [
    "how do I use <competing-library>",
    "<same-backend> with <different-language>",
    "<different-domain> in <language>",
    "what is <backend> (general question)",
    "<library-name-substring-that-matches-other-thing>",
    "install <different-package>",
    "<backend> without <language>",
    "general <language> question unrelated to library",
    "<similar-library-name> setup",
    "<backend> monitoring (not this library's concern)"
  ]
}
```
