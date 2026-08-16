---
name: Generating Library Skills
description: >
  Convert any code repository into a Claude Code skill that teaches correct library usage.
  Use when the user wants to create a skill from a GitHub repo, GitLab repo, local directory,
  or library source code. Triggers on "turn this repo into a skill", "create a skill for
  [library]", "generate skill from", "make a skill from this codebase", or when the user has
  a library they want Claude to learn to use correctly. Also use when improving an existing
  library skill.
---

# Generating Library Skills

Convert a repository into a high-quality Claude Code skill through a 5-phase pipeline:
ANALYZE -> EXTRACT -> DISTILL -> GENERATE -> VALIDATE.

## Core Principle: The Knowledge Delta

A library skill is NOT compressed documentation. It is the **delta** between what Claude
already knows from training and what it needs to know to use this library correctly.

Focus on: gotchas, version-specific behaviors, configuration pitfalls, non-obvious patterns.
Skip: general programming concepts, language basics, things Claude can discover by reading source.

## When to Use

- User points you at a repo (local path, GitHub URL, GitLab URL)
- User asks to "make a skill for X" where X is a library/framework
- User wants Claude to use a specific library correctly in future sessions
- User wants to improve an existing library skill

## When NOT to Use

- The library is already well-covered by Context7 MCP (check first)
- The user just needs a quick one-off answer about a library (use web search)
- The repo is an application, not a reusable library

---

## Phase 1: ANALYZE

**Goal:** Understand repo structure and identify knowledge sources.

### Step 1.1: Acquire the Repository

```
Local directory:  Verify path exists, check for .git
GitHub URL:       git clone --depth 1 <url> /tmp/skill-gen-<name>
GitLab URL:       git clone --depth 1 <url> /tmp/skill-gen-<name>
```

If the user provides just a library name (e.g., "Jedis"), search for the canonical repo.

### Step 1.2: Scan Structure

Run the analysis script to produce a repo manifest:

```bash
python3 [skill_dir]/scripts/analyze_repo.py <repo_path>
```

This outputs `repo_manifest.json` with:
- Library name, language, build system, version
- Documentation locations (README, docs/, wiki/, API docs)
- Source code structure (packages, key public classes/interfaces)
- Test locations and patterns
- Changelog/release notes location

### Step 1.3: Manual Inspection

Read these files (in this order, stop when you have enough context):
1. README.md (or equivalent) - understand purpose and quick-start
2. CHANGELOG.md / HISTORY.md / releases - identify breaking changes
3. Main entry-point source files - understand public API surface
4. 2-3 test files - understand intended usage patterns

**Output:** Clear mental model of what this library does, its API surface, and its ecosystem.

---

## Phase 2: EXTRACT

**Goal:** Pull out all knowledge worth including in the skill.

Extract knowledge into 6 categories. For each item, note the source file and line.

### Category 1: Configuration & Setup (CRITICAL)
- Correct dependency coordinates (group:artifact:version)
- Required initialization / connection setup
- Pool/client configuration with **correct defaults and recommended values**
- Environment requirements (Java version, Node version, etc.)

### Category 2: Gotchas & Pitfalls (HIGHEST VALUE)

Search for gotchas in these sources (ordered by signal density):

1. **GitHub Issues** - labels: "bug", "question", "FAQ", "gotcha"
   ```bash
   # If repo is on GitHub:
   gh issue list -R <owner/repo> -l bug -l question --limit 50
   ```
2. **Source code comments** - search for warning keywords:
   ```
   Grep for: WARNING, FIXME, NOTE, IMPORTANT, CAUTION, "do not", "must not",
   "thread-safe", "not thread-safe", "deprecated", "breaking change"
   ```
3. **Changelog breaking changes** - every major/minor version bump
4. **Stack Overflow** (web search): `site:stackoverflow.com "<library-name>" common mistakes`
5. **Test assertions** - what edge cases do tests guard against?

### Category 3: Common Usage Patterns
- The "happy path" for the 3-5 most common operations
- Correct error handling patterns
- Resource management (close/dispose/shutdown patterns)
- Thread safety rules

### Category 4: Version-Specific Information
- API differences between major versions
- Deprecated methods and their replacements
- Migration paths between versions

### Category 5: Advanced Features
- Less common but important capabilities
- Performance tuning options
- Extension points / plugin systems

### Category 6: Ecosystem Integration
- How this library works with common frameworks (Spring, Express, Django, etc.)
- Known conflicts or incompatibilities
- Companion libraries

---

## Phase 3: DISTILL

**Goal:** Filter extracted knowledge through the Knowledge Delta lens.

### Step 3.1: Apply Knowledge Gap Heuristics

For each extracted item, ask:

| Question | If YES | If NO |
|----------|--------|-------|
| Would Claude know this from general training? | Skip | Keep |
| Is this specific to this library version? | Keep | Likely skip |
| Has this caused real bugs (Issues/SO evidence)? | Keep (high priority) | Lower priority |
| Can Claude discover this by reading source at runtime? | Lower priority | Keep |
| Is this a gotcha that violates expectations? | Keep (highest priority) | Standard priority |

See [references/knowledge-gap-heuristics.md](references/knowledge-gap-heuristics.md) for detailed heuristics by library popularity tier.

### Step 3.2: Rank by Signal Value

Priority order:
1. **Gotchas** - non-obvious behaviors that cause bugs
2. **Configuration pitfalls** - wrong defaults, missing required settings
3. **Version-specific traps** - API changes, deprecations
4. **Correct patterns** - the right way to do common tasks
5. **Setup instructions** - dependencies, initialization
6. **Advanced features** - reference-only, loaded on demand
7. **General API reference** - lowest priority, Claude can read source

### Step 3.3: Determine Architecture

Based on volume of high-value content:

| Content Volume | Architecture |
|---------------|-------------|
| < 200 lines of high-value content | Single SKILL.md, no references |
| 200-500 lines | SKILL.md + 1-2 reference files |
| 500-1500 lines | SKILL.md (hub) + 3-5 reference files by domain |
| > 1500 lines | SKILL.md (hub) + domain references + examples file |

---

## Phase 4: GENERATE

**Goal:** Write the skill files.

### Step 4.1: Choose Output Location

Default: `~/.claude/skills/<library-name>-skill/`

Ask the user if they prefer a different location.

### Step 4.2: Write SKILL.md

Use this structure. **Stay under 500 lines.**

```markdown
---
name: Using <Library Name>
description: >
  <Library> <language> <what-it-does>. Use when writing <language> code that
  <primary-use-case>, when the user mentions <library-name>, <key-class-names>,
  <common-aliases>, or <domain-terms>. Not for <similar-but-different-libraries>.
---

# <Library Name>

## Quick Start

[Minimal working example - the fastest path to "it works"]
[Correct dependency/install command]
[3-10 lines of code that demonstrate the core use case]

## Common Patterns

### <Most Common Operation>
[Correct pattern with code example]

### <Second Most Common Operation>
[Correct pattern with code example]

### <Third Most Common Operation>
[Correct pattern with code example]

## Gotchas

### <Gotcha Category 1>
- **<Specific gotcha>:** <What happens and why>
  [WRONG code example]
  [RIGHT code example]

### <Gotcha Category 2>
- **<Specific gotcha>:** ...

## Configuration

[Only non-obvious configuration. Skip if defaults are fine.]
[Focus on "you MUST set X" and "default Y will bite you"]

## Version Notes

[Only if multiple major versions are in active use]
[Breaking changes between versions]

## References

- [<Domain 1>](references/<domain-1>.md) - <what's in it>
- [<Domain 2>](references/<domain-2>.md) - <what's in it>
```

### Step 4.3: Write Reference Files

One file per domain. Each reference file:
- Starts with a table of contents (for files > 100 lines)
- Contains detailed API patterns, examples, and configuration
- Uses consistent terminology matching SKILL.md
- Includes code examples from real test code (cleaned up)

### Step 4.4: Optimize the Description

The description MUST include:
1. Library canonical name
2. Programming language
3. What it does (brief)
4. Triggering conditions ("Use when...")
5. Key class/function names users would mention
6. Negative triggers ("Not for...")

Write in **third person**. Max 1024 characters.

**Test the description mentally:** If a user says "help me connect to Redis with Java",
would this description cause Claude to load this skill? If not, add the missing keywords.

---

## Phase 5: VALIDATE

**Goal:** Verify the skill actually improves Claude's behavior.

### Step 5.1: Generate Eval Cases

Create `evals.json` in the skill directory:

```json
[
  {
    "id": "basic-usage",
    "prompt": "<realistic task using the library>",
    "expected_behaviors": [
      "<specific correct behavior>",
      "<another correct behavior>"
    ]
  }
]
```

Generate 3-5 eval cases covering:
- Basic setup and usage (does Claude use correct initialization?)
- Error-prone scenario (does Claude avoid the gotcha?)
- Advanced feature (does Claude find the reference file?)
- Version-specific scenario (does Claude use correct API for version?)

### Step 5.2: Generate Trigger Queries

Create `trigger_queries.json`:

```json
{
  "should_trigger": [
    "how do I use <library>",
    "connect to <backend> with <language>",
    "<specific-class> example"
  ],
  "should_not_trigger": [
    "how do I use <competing-library>",
    "<unrelated-topic>",
    "<same-domain-different-tool>"
  ]
}
```

Generate 10 should-trigger and 10 should-not-trigger queries.

### Step 5.3: Manual Review Checklist

Before declaring the skill complete, verify:

- [ ] SKILL.md is under 500 lines
- [ ] Description is in third person and under 1024 characters
- [ ] Description includes library name, language, and trigger keywords
- [ ] Quick Start example actually works (correct imports, API calls)
- [ ] Gotchas section has WRONG/RIGHT code examples
- [ ] Reference files are one level deep (no nested references)
- [ ] No generic knowledge Claude already has
- [ ] No time-sensitive information (no "as of March 2026")
- [ ] Consistent terminology throughout
- [ ] All code examples use the same library version

### Step 5.4: Report to User

Present the generated skill structure and ask for review:
```
Generated skill at: <path>
  SKILL.md          (<N> lines)
  references/
    <file1>.md      (<N> lines) - <topic>
    <file2>.md      (<N> lines) - <topic>
  evals.json        (<N> test cases)
  trigger_queries.json

Key decisions:
- Focused on <N> gotchas from <sources>
- Split references by: <domains>
- Excluded: <what was filtered out and why>

Please review SKILL.md and let me know if you want adjustments.
```

---

## Anti-Patterns

**DO NOT:**
- Dump entire API documentation into SKILL.md
- Include knowledge Claude already has ("Redis is a key-value store")
- Exceed 500 lines in SKILL.md
- Use deeply nested references (keep one level deep)
- Write in first or second person in the description
- Include time-sensitive information
- Skip the gotchas section (it's the highest-value content)
- Generate the skill without reading the actual source code

**DO:**
- Read real source code and tests, not just README
- Prioritize gotchas over API reference
- Include WRONG/RIGHT code examples for every gotcha
- Test the description against realistic user queries
- Generate eval cases for iterative improvement
- Ask the user to review before finalizing
