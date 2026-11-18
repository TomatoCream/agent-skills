#!/bin/bash
# Self-Improve: SessionStart hook
# Injects project context into Claude's session automatically.
# Stdout becomes Claude's context. Keep it fast (<2s).

set -uo pipefail
# No set -e: individual command failures are expected (glab, docker, etc.)

echo "=== AUTO-CONTEXT ==="

# --- Git State ---
if git rev-parse --is-inside-work-tree &>/dev/null; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    STATUS=$(git status --short 2>/dev/null | head -15)
    RECENT=$(git log --oneline -5 2>/dev/null || true)
    STASH_COUNT=$(git stash list 2>/dev/null | wc -l | tr -d ' ')

    echo ""
    echo "## Git"
    echo "Branch: $BRANCH"
    if [ -n "$STATUS" ]; then
        echo "Uncommitted changes:"
        echo "$STATUS"
    else
        echo "Working tree: clean"
    fi
    if [ "$STASH_COUNT" -gt 0 ]; then
        echo "Stashes: $STASH_COUNT"
    fi
    echo ""
    echo "Recent commits:"
    echo "$RECENT"

    # --- Active MR ---
    if command -v glab &>/dev/null; then
        MR=$(glab mr list --assignee=@me --state=opened 2>/dev/null | head -5)
        if [ -n "$MR" ]; then
            echo ""
            echo "## My Open MRs"
            echo "$MR"
        fi

        # CI status for current branch
        CI=$(glab ci status 2>/dev/null | head -3)
        if [ -n "$CI" ]; then
            echo ""
            echo "## CI Status"
            echo "$CI"
        fi
    fi

    # --- Active PR (GitHub fallback) ---
    if [ -z "${MR:-}" ] && command -v gh &>/dev/null; then
        PR=$(gh pr list --author=@me --state=open 2>/dev/null | head -5)
        if [ -n "$PR" ]; then
            echo ""
            echo "## My Open PRs"
            echo "$PR"
        fi
    fi
fi

# --- Environment ---
echo ""
echo "## Environment"

# Detect project type and show relevant versions
[ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] && {
    JAVA_V=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
    echo "Java: $JAVA_V"
    [ -f "pom.xml" ] && echo "Build: Maven"
    [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] && echo "Build: Gradle"
}

[ -f "package.json" ] && {
    NODE_V=$(node --version 2>/dev/null || echo "not found")
    echo "Node: $NODE_V"
}

[ -f "go.mod" ] && {
    GO_V=$(go version 2>/dev/null | awk '{print $3}')
    echo "Go: $GO_V"
}

[ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ] && {
    PY_V=$(python3 --version 2>/dev/null || echo "not found")
    echo "Python: $PY_V"
}

# Running services (quick check)
if command -v docker &>/dev/null; then
    CONTAINERS=$(docker ps --format '{{.Names}} ({{.Image}})' 2>/dev/null | head -8)
    if [ -n "$CONTAINERS" ]; then
        echo ""
        echo "## Running Containers"
        echo "$CONTAINERS"
    fi
fi

# --- Learnings (if exist) ---
if [ -f "LEARNINGS.md" ]; then
    # Count entries
    ENTRY_COUNT=$(grep -c '^\*\*\[' LEARNINGS.md 2>/dev/null || echo "0")
    echo ""
    echo "## Learnings"
    echo "LEARNINGS.md: $ENTRY_COUNT entries (read it before starting work)"
fi

# --- Active Context from CLAUDE.md ---
if [ -f "CLAUDE.md" ]; then
    ACTIVE=$(sed -n '/^## Active Context/,/^## /p' CLAUDE.md 2>/dev/null | head -25 | sed '1d;$d')
    if [ -n "$ACTIVE" ]; then
        echo ""
        echo "## Active Context (from CLAUDE.md)"
        echo "$ACTIVE"
    fi
fi

echo ""
echo "=== END AUTO-CONTEXT ==="
exit 0
