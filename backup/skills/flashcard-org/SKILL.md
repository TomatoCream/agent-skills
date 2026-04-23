---
name: flashcard-org
description: >-
  Generate Anki flashcards in Emacs org-mode format for the org-anki plugin.
  Use when the user says "flashcard-org", "org-anki", "anki org-mode",
  "make org flashcards", or wants to create study cards in .org format.
---

# Flashcard Org Skill

Generate Anki flashcards in Emacs org-mode format for the `org-anki` plugin.

## Invocation

The user invokes this skill as `/flashcard-org` with arguments:

```
/flashcard-org <output-path> [source]
```

- `output-path` (required): The `.org` file to append cards to (e.g., `~/org/cs-notes.org`)
- `source` (optional): One of the following:
  - A file path — reads the file content
  - `conversation` or omitted — uses current conversation context
  - A URL (starts with `http://` or `https://`) — fetches the page via WebFetch
  - A bare topic string in quotes (e.g., `"Python decorators"`) — generate cards from your own knowledge

If `output-path` is missing, ask: "Where should I write the cards? (org file path)"

## Step 1: Determine Source Type

Determine the source type by process of elimination:

1. If source starts with `http://` or `https://` → URL
2. If source is `conversation` or omitted → conversation context
3. If source resolves to an existing file path → file
4. Otherwise → bare topic string

## Step 2: Read Source Material

- **File path:** Use the Read tool to read the file. If it doesn't exist or is binary, say: "Cannot read `<path>` — file not found or not a text file" and stop.
- **Conversation:** Use the current conversation context as source material. If the conversation is empty or trivial, say: "No meaningful content to generate flashcards from" and stop.
- **URL:** Use the WebFetch tool to fetch the page. If WebFetch is not available, ask the user to paste the content instead. If unreachable, say: "Cannot fetch `<url>`" and stop.
- **Bare topic:** No reading needed. Generate cards from your own knowledge on the topic.
- **Size guard:** If source exceeds 5000 lines, warn the user and process only the first 3000 lines. Tell the user how many lines were skipped.

## Step 3: Generate Flashcards

From the source material, generate flashcards. Follow these rules strictly:

- **Atomic:** One concept per card. No compound questions.
- **Context-independent:** Each card must make sense months later without remembering the source.
- **Active recall:** Questions that force retrieval — "What does...", "How does...", "Why does...", "When would you...". No true/false or yes/no questions.
- **Concise answers:** Keep the back focused. Include a brief explanation only if the bare answer would be ambiguous.
- **No junk cards:** If the source contains nothing worth memorizing (config files, boilerplate, generated code), say: "No meaningful flashcard content found in this source" and stop. Do not generate low-quality cards.
- **Rich formatting:** Use org-mode features when they help:
  - LaTeX for math: `$...$` (inline) or `\[...\]` (display)
  - Source blocks for code: `#+begin_src <lang> ... #+end_src`
  - Tables, lists, emphasis (`*bold*`, `/italic/`, `=verbatim=`, `~code~`) as appropriate
- **No card limit:** Generate as many cards as the content warrants.

### Tags

- `study_card` is always the first tag (compulsory).
- Auto-infer 1-3 additional domain tags from the content (e.g., `python`, `algorithms`, `linear_algebra`).
- Tags use `snake_case`, lowercase.
- No user-specified tags — fully automatic.

### Note Type

Always `Basic`. No cloze or reversed cards.

## Step 4: Write Cards to File

### Output Format

Each card MUST follow this exact org-mode structure. Do not deviate from this format:

```org
* <title> :study_card:<tag_0>:<tag_1>:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:

** Front
<front content>


** Back
<back answer content>

```

**Formatting rules:**
- **Title:** A short descriptive label for the card (not the question itself).
- **Blank lines:** One blank line after `:END:`, two blank lines after front content (before `** Back`), one blank line after back content (separates cards from each other).
- **Tag syntax:** Colon-delimited, no spaces, in the headline: `:study_card:python:decorators:`

### File Writing

- If the file **exists**, read it first with the Read tool, then append the new cards after the last top-level headline. Add a blank line separator before the first new card if the file doesn't already end with one. Do not generate cards that duplicate titles already present in the file.
- If the file **does not exist**, create it with the Write tool.
- After writing, report: "Added N cards to `<path>`" and show a summary list of the card titles.

No retries, no fallbacks. If an error occurs, fail clearly and stop.

## Example

Given `/flashcard-org ~/org/python.org "Python decorators"`, generate cards like:

```org
* Decorator Purpose :study_card:python:decorators:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:

** Front
What is the purpose of a decorator in Python?


** Back
A decorator is a function that takes another function as input and returns a modified version of it. It allows you to add behavior to functions without changing their source code.

* Decorator Syntax :study_card:python:decorators:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:

** Front
What does the =@= syntax do when placed above a function definition in Python?


** Back
It applies a decorator to the function. Writing:

#+begin_src python
@my_decorator
def my_func():
    pass
#+end_src

is equivalent to:

#+begin_src python
def my_func():
    pass
my_func = my_decorator(my_func)
#+end_src

```
