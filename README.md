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

### Tavily skills

The [tavily-ai/skills](https://github.com/tavily-ai/skills) submodule is included at `vendor/tavily-skills`. Its skills are automatically symlinked by `install.sh`.

The skills require the Tavily CLI (`tvly`):

```bash
uv tool install tavily-cli   # or: pip install tavily-cli
```

Authenticate once:

```bash
tvly login --api-key tvly-YOUR_KEY
# or: export TAVILY_API_KEY=tvly-...
```

Get an API key at [tavily.com](https://tavily.com).

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with required frontmatter
2. Run `./install.sh`
3. Commit and push

## Adding an Agent

1. Create `agents/<agent-name>.md` with frontmatter + system prompt
2. Run `./install.sh`
3. Commit and push

See `AGENTS.md` for formats and authoring guidelines.
