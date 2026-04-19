#!/usr/bin/env bash
# Install skills from ~/.agents/skills/ into ~/.claude/skills/
# Safe to run multiple times (idempotent)

set -euo pipefail

AGENTS_SKILLS="$HOME/.agents/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"

mkdir -p "$CLAUDE_SKILLS"

# Remove broken self-referencing symlinks
for link in "$CLAUDE_SKILLS"/*; do
  [ -L "$link" ] || continue
  target="$(readlink "$link")"
  if [ "$target" = "$link" ]; then
    echo "removing broken self-link: $(basename "$link")"
    rm "$link"
  fi
done

# Symlink each skill from ~/.agents/skills/ into ~/.claude/skills/
for skill_dir in "$AGENTS_SKILLS"/*/; do
  skill_name="$(basename "$skill_dir")"
  link="$CLAUDE_SKILLS/$skill_name"

  if [ -L "$link" ] && [ "$(readlink "$link")" = "$skill_dir" ]; then
    echo "ok: $skill_name"
    continue
  fi

  # Remove stale link or file if present
  if [ -e "$link" ] || [ -L "$link" ]; then
    echo "replacing: $skill_name"
    rm -f "$link"
  else
    echo "installing: $skill_name"
  fi

  ln -s "$skill_dir" "$link"
done

echo "done. $(ls -1d "$CLAUDE_SKILLS"/*/ 2>/dev/null | wc -l) skills linked."
