# tests/test_anki_connect.py
import json
import os
import subprocess
import sys

# We test the module's internal functions by importing directly,
# and test the CLI by running the script as a subprocess.

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "anki_connect.py")
PYTHON = os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python3")

# Add parent to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_connect(cards, deck_name, tags=None):
    """Helper to run anki_connect.py as a subprocess."""
    cmd = [PYTHON, SCRIPT, "--deck", deck_name]
    if tags:
        cmd.extend(["--tags", tags])
    result = subprocess.run(
        cmd,
        input=json.dumps(cards),
        capture_output=True,
        text=True,
    )
    return result


def test_builds_correct_add_notes_payload():
    """The AnkiConnect payload has the right structure."""
    import anki_connect

    cards = [{"front": "Q1?", "back": "A1"}, {"front": "Q2?", "back": "A2"}]
    payload = anki_connect.build_add_notes_payload(cards, "TestDeck", ["tag1", "tag2"])

    assert payload["action"] == "addNotes"
    assert payload["version"] == 6
    notes = payload["params"]["notes"]
    assert len(notes) == 2
    assert notes[0]["deckName"] == "TestDeck"
    assert notes[0]["modelName"] == "Basic"
    assert notes[0]["fields"]["Front"] == "Q1?"
    assert notes[0]["fields"]["Back"] == "A1"
    assert notes[0]["tags"] == ["tag1", "tag2"]
    # Must NOT have allowDuplicate
    assert "options" not in notes[0] or notes[0].get("options", {}).get("allowDuplicate") is not True


def test_builds_create_deck_payload():
    """The create-deck payload has the right structure."""
    import anki_connect

    payload = anki_connect.build_create_deck_payload("New Deck")
    assert payload["action"] == "createDeck"
    assert payload["params"]["deck"] == "New Deck"


def test_empty_cards_fails():
    """Empty card list should fail without contacting Anki."""
    result = run_connect([], "Empty")
    assert result.returncode != 0


def test_unreachable_anki_exits_with_error():
    """When AnkiConnect is not reachable, script exits non-zero with message."""
    cards = [{"front": "Q?", "back": "A"}]
    # Use a port that's almost certainly not listening
    env = os.environ.copy()
    env["ANKI_CONNECT_URL"] = "http://localhost:19876"
    cmd = [PYTHON, SCRIPT, "--deck", "Test"]
    result = subprocess.run(
        cmd,
        input=json.dumps(cards),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode != 0
    assert "not reachable" in result.stderr.lower() or "error" in result.stderr.lower()
