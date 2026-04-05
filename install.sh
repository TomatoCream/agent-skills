#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="${REPO_DIR}/skills"
AGENTS_SRC="${REPO_DIR}/agents"

CLAUDE_SKILLS="${HOME}/.claude/skills"
CLAUDE_AGENTS="${HOME}/.claude/agents"
OPENCODE_SKILLS="${HOME}/.config/opencode/skills"

mkdir -p "$CLAUDE_SKILLS" "$CLAUDE_AGENTS" "$OPENCODE_SKILLS"

link() {
    local src="$1"
    local dst="$2"
    local label="$3"

    if [[ -L "$dst" ]]; then
        echo "Updating: ${label}"
        rm "$dst"
    elif [[ -e "$dst" ]]; then
        echo "WARNING: ${dst} exists and is not a symlink — skipping ${label}" >&2
        return
    else
        echo "Installing: ${label}"
    fi

    ln -s "$src" "$dst"
}

install_skills() {
    for src in "${SKILLS_SRC}"/*/; do
        [[ -d "$src" ]] || continue
        local name
        name="$(basename "$src")"
        link "$src" "${CLAUDE_SKILLS}/${name}"   "claude/skill/${name}"
        link "$src" "${OPENCODE_SKILLS}/${name}" "opencode/skill/${name}"
    done
}

install_agents() {
    for src in "${AGENTS_SRC}"/*.md; do
        [[ -f "$src" ]] || continue
        local name
        name="$(basename "$src")"
        link "$src" "${CLAUDE_AGENTS}/${name}" "claude/agent/${name}"
    done
}

install_skills
install_agents
echo "Done."
