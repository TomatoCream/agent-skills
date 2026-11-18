#!/bin/bash
# Self-Improve: Stop hook
# Runs at end of each turn. Emits a brief reminder to Claude
# to capture learnings if significant work was done.
# Keeps it lightweight — just a context nudge, not a full skill invocation.

set -euo pipefail

# Read stdin for hook payload
INPUT=$(cat)

# Only emit reminder if we're in a git repo with a LEARNINGS.md
if [ -f "LEARNINGS.md" ]; then
    echo "REMINDER: If this session involved significant work, corrections, or discoveries, run /self-improve before ending."
fi
