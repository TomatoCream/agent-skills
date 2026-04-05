# agent-skills

Personal collection of agent skills for Claude Code.

## Install

```bash
git clone git@github.com:TomatoCream/agent-skills.git ~/projects/agent-skills
cd ~/projects/agent-skills
chmod +x install.sh
./install.sh
```

Skills are symlinked into `~/.claude/skills/`. Pulling the repo and re-running `./install.sh` keeps them up to date (symlinks are idempotent).

## Adding a Skill

1. Create `skills/<skill-name>/SKILL.md` with required frontmatter
2. Run `./install.sh <skill-name>`
3. Commit and push

See `AGENTS.md` for the full skill format and authoring guidelines.
