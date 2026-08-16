---
name: df-flashcard-fundamentals
description: Use when given content (text, chat, source code, article) and need to create flashcards from it, particularly for technical content like Linux commands or source code.
---

# df-flashcard-fundamentals

## Overview

Given any content, decide WHAT questions to ask. This skill focuses on question formulation — not tagging, not formatting. Format is fixed: Basic cards with Front/Back subheadings.

**Core principle**: For any piece of information, there are 50-150 distinct useful questions. Choose the RIGHT ones.

## When to Use

- Reading technical content and deciding what to memorize
- Converting chat conversations into flashcards
- Creating cards from source code documentation
- Studying an article and extracting memory-worthy content

## Org-Mode Format (Fixed)

```org
* <title> :tag1:tag2:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Front
question here
** Back
answer here
```

**Source blocks**: Always wrap code/commands in Emacs org-mode source blocks:
```org
#+begin_src bash
perf stat -e page-faults ./program
#+end_src
```

Supported languages include: `bash`, `c++`, `python`, `javascript`, `sql`, `json`, etc.

No cloze. No other types. Just Basic with Front/Back.

## Org-Mode Formatting Conventions

**Inline Code**: Use `~code~` (tilde) for inline code, NOT backticks.
- `~ls -la~` → shows as literal code
- DO NOT use backticks for inline code in org-mode

**Emphasis**:
- `*bold*` — asterisks
- `/italic/` — slashes
- `_underline_` — underscores
- `~code~` — tildes (inline code)
- `=verbatim=` — literal text

**LaTeX in org-mode**: Use `#+begin_export latex` blocks or inline `$...$` syntax.
- Inline: `$E=mc^2$`
- Block: `#+begin_export latex` / `#+end_export`

**Block Syntax**:
- Source blocks: `#+begin_src <lang>` / `#+end_src`
- Export blocks: `#+begin_export <format>` / `#+end_export`
- Example blocks: `#+begin_example` / `#+end_example`
- Quote blocks: `#+begin_quote` / `#+end_quote`

## The Question Dimensions

Every flashcard asks a question along these dimensions:

### 1. Retrieval Mode (Most Important)

| Mode | Question | When to Use |
|------|----------|-------------|
| **Production** | Given task → generate answer | You need to produce without looking up |
| **Recognition** | Shown something → identify meaning | Quick lookups only |
| **Explanation** | Explain concept to newcomer | Deep understanding, interviews |

**Rule**: If you'll need to produce it (terminal, exam, interview), make it a production card.

### 2. Question Direction

| Direction | Question | Example |
|-----------|----------|---------|
| Forward | What is X? | "What does `grep -r` do?" |
| Backward | Given X, produce Y | "Write `grep` to find .py files recursively" |
| Comparison | How does X differ from Y? | "How does `grep` differ from `ack`?" |
| Conditional | When would you use X? | "When choose `grep -E` over basic grep?" |

### 3. Cognitive Level (Bloom's)

- **Remember**: Name, syntax, definition
- **Understand**: What it does, how it works
- **Apply**: Write the command/code
- **Analyze**: Trace execution, find bugs
- **Create**: Combine elements, design pipeline

### 4. Specificity

| Level | Example |
|-------|---------|
| Generic | "How does `grep` work?" |
| Specific | "How does `-mtime -7` work in `find`?" |
| Scenario | "Find all .log files modified in last 7 days" |

**Rule**: More specific = better retrieval. Generic allows passive recognition.

## The 14 Question Types

From research, these are all the question types available:

1. **Factual/Recall** — What is X?
2. **Definition** — Define X
3. **What-If** — What would happen if X?
4. **Procedural** — How do you do X using Y?
5. **Elaborative Why** — Why does X work this way?
6. **Comparative** — How does X differ from Y?
7. **Diagnostic** — True/false: will X compile?
8. **Application** — Write command/code for scenario
9. **Transfer** — Can X be applied to Y?
10. **Metacognitive** — What don't you understand about X?
11. **Synthesis** — Design a pipeline/solution using X, Y, Z
12. **Recognition** — Which flag does X?
13. **Exception** — Which is NOT valid?
14. **Enumeration** — List all flags for X

## Decision Framework

**Step 1: Will you need to produce this without looking it up?**
- Yes → Production card (Task → Command/Code)
- No (always available) → Recognition card

**Step 2: What's the real use case?**
- Terminal → Production: "Write grep to..."
- Whiteboard → Production: "Write the function call"
- Written exam → Enumeration + Trace: "List all flags...", "What does this print?"
- Oral interview → Explanation + Why: "Explain how...works"

**Step 3: How specific should the question be?**
- If you need exact syntax → Specific scenario
- If you need conceptual understanding → Definition/Why

**Step 4: One card = one retrieval?**
- Split if asking multiple things (all flags at once? No. One flag per card.)

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| "What do these flags do?" with all 5 flags | Multi-part retrieval | One flag per card |
| "How does X work?" (generic) | Allows passive recognition | Specific scenario |
| Recognition card for production need | Weak transfer | Task → Command |
| Asking "What is X?" when you need to write X | Wrong direction | Write backward question |
| Duplicate titles (two cards with same heading) | Anki sync issues, ambiguity | Unique titles per card |
| Recognition card for terminal use | Won't transfer to real work | Write "Write command to..." |

## From Baseline Test

**Before skill** (agent wrote):
- ❌ Card with all 5 flags in one card
- ❌ Generic definition card
- Verbose production card

**After skill** (should write):
- One flag per card (5 cards for 5 flags)
- Production card with specific scenario
- Short, unambiguous front

## Real Example: From Content to Cards

### Input Content
`grep` (Global Regular Expression Print) searches files. Flags: `-r` recursive, `-n` line numbers, `-i` case-insensitive, `-v` invert match.

### Bad Cards (Multi-part, generic, duplicate titles)
```org
* grep flags
** Front
What do these flags do? -r, -n, -i, -v
** Back
-r=recursive, -n=line numbers...

* grep flags
** Front
What does -v do?
** Back
Inverts match
```

### Good Cards (One per flag, unique titles, production for terminal)

```org
* Task: Find .py files recursively with grep :linux:grep:retrieval::production:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Front
Write `grep` to find all .py files in current directory recursively
** Back
#+begin_src bash
grep -r --include="*.py" .
#+end_src
```

```org
* grep -r: recursive search :linux:grep:retrieval::recognition:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Front
What does the `-r` flag do in `grep`?
** Back
Searches recursively through directories
```

```org
* Task: Find errors in logs with line numbers :linux:grep:retrieval::production:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Front
Write `grep` to find "error" in /var/log/ recursively with line numbers shown
** Back
#+begin_src bash
grep -rn "error" /var/log/
#+end_src
```

## Quick Reference

**Question formulation checklist:**
1. [ ] Production (write it) or Recognition (identify it)?
2. [ ] Forward (what is) or Backward (given task)?
3. [ ] Which Bloom's level? (remember/understand/apply/analyze/create)
4. [ ] Specific scenario or generic?
5. [ ] One retrieval per card?

**For any content, ask:**
- What will I need to produce?
- What scenario would require this?
- What's the simplest version of this?
- What's commonly confused with this?

## Reference

See [[file:reference/flashcard-research.org][flashcard-research.org]] for evidence base.
See [[file:reference/question-taxonomy.org][question-taxonomy.org]] for complete question type list.
See [[file:reference/when-to-use.org][when-to-use.org]] for when to use each type.
