#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/skills" && pwd)"
TARGET_DIR="${HOME}/.claude/skills"

mkdir -p "$TARGET_DIR"

install_skill() {
    local name="$1"
    local src="${SKILLS_DIR}/${name}"
    local dst="${TARGET_DIR}/${name}"

    if [[ ! -d "$src" ]]; then
        echo "ERROR: skill '${name}' not found in skills/" >&2
        exit 1
    fi

    if [[ -L "$dst" ]]; then
        echo "Updating symlink: ${name}"
        rm "$dst"
    elif [[ -d "$dst" ]]; then
        echo "WARNING: ${dst} exists and is not a symlink — skipping ${name}" >&2
        return
    else
        echo "Installing: ${name}"
    fi

    ln -s "$src" "$dst"
}

if [[ $# -gt 0 ]]; then
    for skill in "$@"; do
        install_skill "$skill"
    done
else
    for skill_dir in "${SKILLS_DIR}"/*/; do
        install_skill "$(basename "$skill_dir")"
    done
fi

echo "Done."
