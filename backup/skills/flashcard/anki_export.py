#!/usr/bin/env python3
"""Generate an Anki .apkg file from JSON flashcards on stdin."""

import argparse
import hashlib
import json
import os
import re
import sys

import genanki

# Fixed model ID so all exports share the same note type in Anki.
MODEL_ID = 1607392319

MODEL = genanki.Model(
    MODEL_ID,
    "Claude Flashcard",
    fields=[{"name": "Front"}, {"name": "Back"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
        }
    ],
)


def slugify(name: str) -> str:
    """Lowercase and slugify a deck name for use as a filename."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\-]", "_", slug)
    slug = re.sub(r"_+", "_", slug)
    slug = slug.strip("_")
    return slug


def main() -> int:
    parser = argparse.ArgumentParser(description="Export flashcards to .apkg")
    parser.add_argument("--deck", required=True, help="Anki deck name")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    args = parser.parse_args()

    cards = json.load(sys.stdin)

    if not cards:
        print("Error: no cards to export", file=sys.stderr)
        return 1

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    # Deterministic deck ID derived from deck name so different decks don't collide on import.
    deck_id = int(hashlib.sha256(args.deck.encode()).hexdigest()[:8], 16)
    deck = genanki.Deck(deck_id, args.deck)

    for card in cards:
        note = genanki.Note(model=MODEL, fields=[card["front"], card["back"]], tags=tags)
        deck.add_note(note)

    filename = f"{slugify(args.deck)}.apkg"
    genanki.Package(deck).write_to_file(filename)

    print(f"Generated {len(cards)} flashcards → exported to `{filename}`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
