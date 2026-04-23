#!/usr/bin/env python3
"""Push flashcards to Anki via AnkiConnect API."""

import argparse
import json
import os
import sys

import requests

DEFAULT_URL = "http://localhost:8765"


class AnkiConnectError(Exception):
    """Raised when AnkiConnect is unreachable or returns an error."""
    pass


def build_create_deck_payload(deck_name: str) -> dict:
    return {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": deck_name},
    }


def build_add_notes_payload(cards: list, deck_name: str, tags: list) -> dict:
    notes = []
    for card in cards:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": card["front"], "Back": card["back"]},
            "tags": tags,
        }
        notes.append(note)

    return {
        "action": "addNotes",
        "version": 6,
        "params": {"notes": notes},
    }


def anki_request(url: str, payload: dict) -> dict:
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        raise AnkiConnectError(f"AnkiConnect not reachable at {url}")
    except requests.RequestException as e:
        raise AnkiConnectError(f"AnkiConnect request failed: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Push flashcards to Anki via AnkiConnect")
    parser.add_argument("--deck", required=True, help="Anki deck name")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    args = parser.parse_args()

    url = os.environ.get("ANKI_CONNECT_URL", DEFAULT_URL)
    cards = json.load(sys.stdin)

    if not cards:
        print("Error: no cards to push", file=sys.stderr)
        return 1

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    try:
        # Create deck (idempotent)
        anki_request(url, build_create_deck_payload(args.deck))

        # Add notes
        result = anki_request(url, build_add_notes_payload(cards, args.deck, tags))
    except AnkiConnectError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if result.get("error"):
        print(f"Error from AnkiConnect: {result['error']}", file=sys.stderr)
        return 1

    added = sum(1 for r in result.get("result", []) if r is not None)
    skipped = len(cards) - added
    msg = f"Generated {added} flashcards → pushed to deck '{args.deck}'"
    if skipped:
        msg += f" ({skipped} duplicates skipped)"
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
