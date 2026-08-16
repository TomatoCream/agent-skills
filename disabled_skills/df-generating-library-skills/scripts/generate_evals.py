#!/usr/bin/env python3
"""
Evaluation Case Generator for Library Skills.

Reads a repo manifest (from analyze_repo.py) and generates:
- evals.json: Test cases with prompts and expected behaviors
- trigger_queries.json: Should-trigger and should-not-trigger queries

Usage:
    python3 generate_evals.py <manifest_path> [--output-dir <path>]

The generated files serve as starting points for skill validation.
Claude should review and customize them based on the actual skill content.
"""

import json
import sys
from pathlib import Path


def generate_evals(manifest: dict) -> list:
    """Generate evaluation cases from repo manifest."""
    name = manifest.get("name", "library")
    lang = manifest.get("build", {}).get("language", "unknown")
    gotchas = manifest.get("gotcha_indicators", {})

    evals = []

    # Eval 1: Basic setup
    evals.append({
        "id": "setup-basic",
        "description": f"Test that Claude sets up {name} correctly",
        "prompt": f"Write a {lang} function that uses {name} to perform a basic operation. Include all necessary setup and cleanup.",
        "expected_behaviors": [
            f"Uses correct {name} dependency/import",
            "Initializes with recommended settings (not bare defaults)",
            "Includes proper resource cleanup (close/dispose/try-with-resources)",
            "Handles basic errors appropriately",
        ],
    })

    # Eval 2: Gotcha avoidance (if gotchas found)
    if gotchas.get("thread_safety"):
        evals.append({
            "id": "thread-safety",
            "description": f"Test that Claude handles {name} thread safety correctly",
            "prompt": f"Write a multi-threaded {lang} application that uses {name}. Multiple threads need to perform operations concurrently.",
            "expected_behaviors": [
                "Does NOT share mutable client instances across threads",
                "Uses connection pool or thread-safe wrapper",
                "Handles concurrent access correctly",
            ],
        })

    if gotchas.get("deprecations"):
        evals.append({
            "id": "avoids-deprecated",
            "description": f"Test that Claude avoids deprecated {name} APIs",
            "prompt": f"Write {lang} code using {name} to perform common operations.",
            "expected_behaviors": [
                "Does NOT use deprecated methods",
                "Uses current recommended API",
                "Follows latest version patterns",
            ],
        })

    # Eval 3: Production readiness
    evals.append({
        "id": "production-ready",
        "description": f"Test that Claude produces production-quality {name} code",
        "prompt": f"Write a production-ready {lang} service that uses {name}. It should handle connection failures, timeouts, and clean shutdown.",
        "expected_behaviors": [
            "Uses connection pooling (not single connections)",
            "Sets appropriate timeouts",
            "Includes retry logic or graceful degradation",
            "Handles connection failures",
            "Cleans up resources on shutdown",
        ],
    })

    # Eval 4: Error handling
    evals.append({
        "id": "error-handling",
        "description": f"Test that Claude handles {name} errors correctly",
        "prompt": f"Write a {lang} function using {name} that handles all common failure scenarios gracefully.",
        "expected_behaviors": [
            "Catches library-specific exceptions",
            "Distinguishes transient from permanent errors",
            "Does not silently swallow errors",
            "Includes appropriate logging or error reporting",
        ],
    })

    # Eval 5: Configuration
    key_files = manifest.get("source", {}).get("key_files", [])
    config_files = [f for f in key_files if "config" in f.lower() or "options" in f.lower()]
    if config_files:
        evals.append({
            "id": "configuration",
            "description": f"Test that Claude configures {name} with appropriate settings",
            "prompt": f"Configure {name} for a high-traffic production environment in {lang}. Explain each setting choice.",
            "expected_behaviors": [
                "Sets connection pool size appropriately",
                "Configures timeouts (connection, read, write)",
                "Explains why each non-default setting is chosen",
                "Does not use dangerous defaults without warning",
            ],
        })

    return evals


def generate_trigger_queries(manifest: dict) -> dict:
    """Generate should-trigger and should-not-trigger queries."""
    name = manifest.get("name", "library")
    lang = manifest.get("build", {}).get("language", "unknown")
    # metadata available for future enrichment: manifest.get("build", {}).get("metadata", {})

    # Extract key class names from key_files
    key_files = manifest.get("source", {}).get("key_files", [])
    class_names = []
    for f in key_files[:5]:
        # Extract class name from file path
        basename = Path(f).stem
        class_names.append(basename)

    should_trigger = [
        f"how do I use {name}",
        f"help me with {name} in {lang}",
        f"{name} setup example",
        f"{name} connection pool",
        f"{name} error handling best practices",
        f"write {lang} code using {name}",
        f"{name} configuration for production",
        f"migrate {name} to latest version",
    ]

    # Add class-specific triggers
    for cls in class_names[:3]:
        should_trigger.append(f"{cls} usage example")
        should_trigger.append(f"how to configure {cls}")

    should_not_trigger = [
        f"general {lang} programming question",
        f"what is {lang} used for",
        "explain design patterns",
        "help me write unit tests",
        f"review my {lang} code",
        "how do I set up CI/CD",
        "database schema design",
        "REST API design best practices",
        f"{lang} performance optimization",
        "code review checklist",
    ]

    return {
        "should_trigger": should_trigger,
        "should_not_trigger": should_not_trigger,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_evals.py <manifest_path> [--output-dir <path>]", file=sys.stderr)
        sys.exit(1)

    manifest_path = sys.argv[1]
    output_dir = "."

    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    with open(manifest_path) as f:
        manifest = json.load(f)

    evals = generate_evals(manifest)
    triggers = generate_trigger_queries(manifest)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    evals_path = output_dir / "evals.json"
    evals_path.write_text(json.dumps(evals, indent=2))
    print(f"Evals written to {evals_path}", file=sys.stderr)

    triggers_path = output_dir / "trigger_queries.json"
    triggers_path.write_text(json.dumps(triggers, indent=2))
    print(f"Trigger queries written to {triggers_path}", file=sys.stderr)

    # Summary
    print(json.dumps({
        "evals_count": len(evals),
        "should_trigger_count": len(triggers["should_trigger"]),
        "should_not_trigger_count": len(triggers["should_not_trigger"]),
    }, indent=2))
