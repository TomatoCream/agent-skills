#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="${REPO_DIR}/skills"
AGENTS_SRC="${REPO_DIR}/agents"

VENDOR_DIR="${REPO_DIR}/vendor"

CLAUDE_SKILLS="${HOME}/.claude/skills"
CLAUDE_AGENTS="${HOME}/.claude/agents"
OPENCODE_SKILLS="${HOME}/.config/opencode/skills"
OPENCODE_CONFIG="${HOME}/.config/opencode"
OPENCODE_SRC="${REPO_DIR}/opencode"

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

install_skills_from() {
    local src_dir="$1"
    for src in "${src_dir}"/*/; do
        [[ -d "$src" ]] || continue
        local name
        name="$(basename "$src")"
        link "$src" "${CLAUDE_SKILLS}/${name}"   "claude/skill/${name}"
        link "$src" "${OPENCODE_SKILLS}/${name}" "opencode/skill/${name}"
    done
}

install_skills() {
    install_skills_from "${SKILLS_SRC}"
    # vendor submodules
    for vendor_skills in "${VENDOR_DIR}"/*/skills; do
        [[ -d "$vendor_skills" ]] || continue
        install_skills_from "$vendor_skills"
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

install_opencode_config() {
    for src in "${OPENCODE_SRC}"/*; do
        [[ -f "$src" ]] || continue
        local name
        name="$(basename "$src")"
        link "$src" "${OPENCODE_CONFIG}/${name}" "opencode/config/${name}"
    done
}

install_skills
install_agents
install_opencode_config
echo "Done."
