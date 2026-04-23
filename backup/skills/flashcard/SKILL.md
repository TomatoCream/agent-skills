---
name: flashcard
description: Generate Anki flashcards from files or conversation. Use when the user says "flashcard", "anki", "make cards from", "create flashcards", or wants to turn code/docs/conversation into study material.
---

# Flashcard Skill

Generate Anki flashcards from source material and push them to Anki or export as `.apkg`.

## Invocation

The user invokes this skill as `/flashcard` with arguments:

```
/flashcard [source] --deck "Deck Name" [--tags "tag1,tag2"]
```

- `source`: a file path, or `conversation` (or omitted) for the current conversation
- `--deck`: required — the Anki deck name
- `--tags`: optional — comma-separated tags

If `--deck` is missing, ask: "What deck should these cards go into?"

## Step 1: Ensure Setup

Check if the venv exists. If not, run setup:

```bash
~/.claude/skills/flashcard/setup.sh
```

If this fails, show the error and stop.

## Step 2: Read Source Material

- **File path**: Use the Read tool to read the file. If it doesn't exist or is binary, say: "Cannot read `<path>` — file not found or not a text file" and stop.
- **Conversation** (or no source): Use the current conversation context as source material.
- If the source is empty, say: "No content found to generate flashcards from" and stop.
- If the source exceeds ~5000 lines, warn the user and use only the first ~3000 lines.

## Step 3: Generate Flashcards

From the source material, generate Q&A flashcards as a JSON array. Follow these rules strictly:

- **Maximum 50 cards** per invocation. Prioritize the most important concepts.
- **Atomic**: one concept per card. No compound questions.
- **Context-independent**: each card must make sense months later without remembering the source.
- **Active recall**: questions that force retrieval. Use "What does...", "How does...", "Why does...", "When would you...". Never use "True or false" or yes/no questions.
- **Concise answers**: keep the back of the card focused. Include a brief explanation only if the bare answer would be ambiguous.
- **No junk cards**: if the source material contains nothing worth memorizing (e.g., configuration files, boilerplate, generated code), say: "No meaningful flashcard content found in this source" and stop. Do not generate low-quality cards.

Output format (internal, not shown to user):
```json
[
  {"front": "What does useEffect do in React?", "back": "Runs side effects after render. Accepts a callback and optional dependency array."}
]
```

## Step 4: Push to Anki

First, try AnkiConnect. If it fails, fall back to `.apkg` export.

### Try AnkiConnect

```bash
echo '<JSON_CARDS>' | ~/.claude/skills/flashcard/.venv/bin/python3 ~/.claude/skills/flashcard/anki_connect.py --deck "<DECK_NAME>" --tags "<TAGS>"
```

If the script exits 0, show the success message from stdout and stop.

If the script exits non-zero (AnkiConnect not reachable), proceed to fallback.

### Fallback: Export `.apkg`

```bash
echo '<JSON_CARDS>' | ~/.claude/skills/flashcard/.venv/bin/python3 ~/.claude/skills/flashcard/anki_export.py --deck "<DECK_NAME>" --tags "<TAGS>"
```

Show: "AnkiConnect not reachable — exported to `<filename>.apkg` instead."

Then show the success message from stdout.
