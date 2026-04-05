#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="${REPO_DIR}/skills"
AGENTS_SRC="${REPO_DIR}/agents"
SKILLS_DST="${HOME}/.claude/skills"
AGENTS_DST="${HOME}/.claude/agents"

mkdir -p "$SKILLS_DST" "$AGENTS_DST"

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
        link "$src" "${SKILLS_DST}/${name}" "skill/${name}"
    done
}

install_agents() {
    for src in "${AGENTS_SRC}"/*.md; do
        [[ -f "$src" ]] || continue
        local name
        name="$(basename "$src")"
        link "$src" "${AGENTS_DST}/${name}" "agent/${name}"
    done
}

install_skills
install_agents
echo "Done."
