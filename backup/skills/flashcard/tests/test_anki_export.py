# tests/test_anki_export.py
import json
import os
import subprocess
import sys
import tempfile
import zipfile

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "anki_export.py")
PYTHON = os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python3")


def run_export(cards, deck_name, tags=None, cwd=None):
    """Helper to run anki_export.py and return the result."""
    cmd = [PYTHON, SCRIPT, "--deck", deck_name]
    if tags:
        cmd.extend(["--tags", tags])
    result = subprocess.run(
        cmd,
        input=json.dumps(cards),
        capture_output=True,
        text=True,
        cwd=cwd or tempfile.mkdtemp(),
    )
    return result


def test_generates_valid_apkg():
    """Output file is a valid zip (apkg is a zip)."""
    cards = [
        {"front": "What is 2+2?", "back": "4"},
        {"front": "Capital of France?", "back": "Paris"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_export(cards, "Test Deck", cwd=tmpdir)
        assert result.returncode == 0, result.stderr
        apkg_path = os.path.join(tmpdir, "test_deck.apkg")
        assert os.path.exists(apkg_path)
        assert zipfile.is_zipfile(apkg_path)


def test_filename_sanitization():
    """Special characters in deck name produce a valid filename."""
    cards = [{"front": "Q?", "back": "A"}]
    cases = {
        "Python / Auth": "python_auth.apkg",
        "C++ Gotchas": "c_gotchas.apkg",
        "My  Deck": "my_deck.apkg",
        "simple": "simple.apkg",
    }
    for deck_name, expected_filename in cases.items():
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_export(cards, deck_name, cwd=tmpdir)
            assert result.returncode == 0, f"{deck_name}: {result.stderr}"
            assert os.path.exists(os.path.join(tmpdir, expected_filename)), (
                f"Expected {expected_filename} for deck '{deck_name}', "
                f"got files: {os.listdir(tmpdir)}"
            )


def test_empty_cards_fails():
    """Empty card list should fail with non-zero exit."""
    result = run_export([], "Empty Deck")
    assert result.returncode != 0


def test_output_message():
    """Script prints card count and filename on success."""
    cards = [{"front": "Q?", "back": "A"}]
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_export(cards, "My Deck", cwd=tmpdir)
        assert "1" in result.stdout
        assert "my_deck.apkg" in result.stdout


def test_tags_included():
    """Tags are accepted without error (genanki stores them in the apkg)."""
    cards = [{"front": "Q?", "back": "A"}]
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_export(cards, "Tagged", tags="python,auth", cwd=tmpdir)
        assert result.returncode == 0, result.stderr
