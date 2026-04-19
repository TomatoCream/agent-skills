---
name: df-org-anki-basic
description: Use when creating flashcards in Emacs org-mode for Anki sync, especially for technical content like Linux commands or source code.
---

# df-org-anki-basic

## Overview

Write flashcards in org-mode that sync to Anki via org-anki.el. This skill combines the org-anki format with evidence-based flashcard principles (retrieval practice, production over recognition, minimum information).

## When to Use

- Creating new flashcards in an .org file
- Deciding what question type to use
- Tagging cards for organization and scheduling
- Converting technical knowledge into Anki cards

## Core Principle: Production Over Recognition

**Rule**: If you need to produce it (terminal, whiteboard, exam), make it a **production card**.

| Card Type | Front | Back | When to Use |
|-----------|-------|------|-------------|
| Production (Task→Command) | Task description | The command/code | Terminal use, coding from scratch |
| Recognition (Command→Meaning) | Command shown | What it does | Quick lookups only |
| Cloze | Heading with `{{c1::...}}` | Gap-fill | Fast facts, one-liners |

**Bad**: "What does `grep -r` do?" → "Recursively search..."

**Good**: "Write `grep` to find all .log files in /var/log modified in 7 days" → `find /var/log...` or pipeline

## Org-Mode Format

### Basic Card

```org
* <heading> :<tag_1>:<tag_2>:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
<content as back>
```

### Cloze Card

```org
* {{c1::hidden text}} is the answer
:PROPERTIES:
:ANKI_NOTE_TYPE: Cloze
:END:
Optional extra content
```

### Required Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `ANKI_NOTE_TYPE` | Card type | `Basic` or `Cloze` |
| `ANKI_DECK` | Target deck (optional, or use file-level `#+ANKI_DECK:`) | `linux-commands` |
| `ANKI_TAGS` | Additional tags (optional, or use heading tags) | `production` |

## Tag Taxonomy

Use hierarchical tags for organization. Format: `category::value`

### By Domain

```
linux::grep
linux::find
linux::pipelines
code::c++
code::stl
code::templates
```

### By Retrieval Mode (Critical)

```
retrieval::production    # Must generate answer
retrieval::recognition   # Identify from options
retrieval::free-recall   # Open-ended explanation
```

### By Cognitive Level (Bloom's)

```
bloom::remember
bloom::understand
bloom::apply
bloom::analyze
bloom::create
```

### By Difficulty

```
difficulty::easy
difficulty::medium
difficulty::hard
```

### By Transfer Context

```
context::terminal        # For command-line use
context::whiteboard      # For interviews
context::written-exam
context::oral-interview
```

### By Card Type

```
type::basic              # Heading=front, content=back
type::cloze              # Fill-in-blank
type::reversed           # Both directions
```

### Example: Tagged Production Card for grep

```org
* Task: Find all Python files containing "TODO" in current directory :linux::grep:retrieval::production:context::terminal:difficulty::medium:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
grep -rn "TODO" --include="*.py" .
```

## Quick Reference

### Decision Flow

1. **Will you need to produce this without looking it up?**
   - Yes → Production card (front = task/constraint, back = command/code)
   - No → Recognition card (front = command shown, back = meaning)

2. **One card, one retrieval?**
   - Split if asking multiple things (command + flags together? Split them.)

3. **Is this a cloze?**
   - Yes → Use `{{c1::hidden}}` syntax in heading
   - No → Use Basic card

### Tag Checklist Per Card

- [ ] Domain tag (`linux::grep`, `code::stl`)
- [ ] Retrieval mode (`retrieval::production`)
- [ ] Context (`context::terminal`)
- [ ] Difficulty (optional, useful for scheduling)

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| "What does X do?" with command shown | Recognition only, weak transfer | Ask "Write command to..." |
| Bundling multiple things | Multi-part retrieval | Split into separate cards |
| Abstract/generic question | Allows passive recognition | Use concrete scenario |
| Heading too long | Ambiguous front | Front should trigger one answer |

## Real Examples

### Production Card (Terminal Practice)

```org
* Write grep to find all .py files with "TODO" in current dir :linux::grep:retrieval::production:context::terminal:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
grep -rn "TODO" --include="*.py" .
```

### Recognition Card (Quick Lookup)

```org
* grep -rn :linux::grep:retrieval::recognition:difficulty::easy:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
-r: recursive, -n: show line numbers
```

### Cloze Card (Fast Fact)

```org
* {{c1::grep -E}} is the same as {{c2::egrep}} :linux::grep:retrieval::recognition:
:PROPERTIES:
:ANKI_NOTE_TYPE: Cloze
:END:
Both search using extended regex
```

### Source Code Production Card

```org
* Write std::vector::push_back to add string "hello" :code::cpp:retrieval::production:context::whiteboard:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
vec.push_back("hello");
```

### Pipeline Production Card

```org
* Write pipeline to count unique error patterns in syslog :linux::pipeline:retrieval::production:context::terminal:difficulty::hard:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
grep -i error /var/log/syslog | sort | uniq -c | sort -rn | head
```

## See Also

- [[file:///home/df/scratch/org-anki/flashcard-question-formulation/flashcard-research.org][flashcard-research.org]] — Evidence base: retrieval practice, testing effect, desirable difficulties
- [[file:///home/df/scratch/org-anki/flashcard-question-formulation/question-taxonomy.org][question-taxonomy.org]] — Complete question type taxonomy
- [[file:///home/df/scratch/org-anki/flashcard-question-formulation/when-to-use.org][when-to-use.org]] — Decision framework: which card type for which situation
