# agent-skills

Personal collection of agent skills for Claude Code.

## Install

```bash
git clone --recurse-submodules git@github.com:TomatoCream/agent-skills.git ~/projects/agent-skills
cd ~/projects/agent-skills
chmod +x install.sh
./install.sh
```

`install.sh` symlinks skills into both `~/.claude/skills/` and `~/.config/opencode/skills/`. Re-running after a pull is idempotent.

### Opencode — superpowers plugin

Add to `~/.config/opencode/opencode.jsonc`:

```json
"plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
```

Then restart opencode. The plugin auto-fetches and registers all superpowers skills.

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with required frontmatter
2. Run `./install.sh`
3. Commit and push

## Adding an Agent

1. Create `agents/<agent-name>.md` with frontmatter + system prompt
2. Run `./install.sh`
3. Commit and push

See `AGENTS.md` for formats and authoring guidelines.
