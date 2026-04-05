---
name: openclaw-agent-first-setup
description: Agent-first setup workflow
source: https://github.com/openclaw/nix-openclaw/templates/agent-first
---

# Agent-First Setup

## Workflow

Copy this to your AI agent:

```
I want to set up nix-openclaw on my machine (macOS or Linux).

Repository: github:openclaw/nix-openclaw

What nix-openclaw is:
- Batteries-included Nix package for OpenClaw (AI assistant gateway)
- Installs gateway + tools everywhere; macOS app only on macOS
- Runs as a launchd service on macOS, systemd user service on Linux

What I need you to do:
1. Check if Determinate Nix is installed (if not, install it)
2. Create a local flake at ~/code/openclaw-local using templates/agent-first/flake.nix
3. Create a documents dir with AGENTS.md, SOUL.md, TOOLS.md
4. Help me create a Telegram bot (@BotFather) and get my chat ID (@userinfobot)
5. Set up secrets (bot token, Anthropic key)
6. Fill in template placeholders and run home-manager switch
7. Verify service running, bot responds

My setup:
- OS: [macOS / Linux]
- CPU: [arm64 / x86_64]
- System: [aarch64-darwin / x86_64-linux]
```

## Template Usage

```bash
mkdir -p ~/code/openclaw-local && cd ~/code/openclaw-local
nix flake init -t github:openclaw/nix-openclaw#agent-first
```

Edit `flake.nix` placeholders:
- `system` = `aarch64-darwin` or `x86_64-linux`
- `home.username`, `home.homeDirectory`
- `programs.openclaw.documents`
- Provider secrets (Telegram/Discord tokens, Anthropic key)

Apply: `home-manager switch --flake .#<user>`

## Bootstrap Ritual

After setup, message your Telegram bot. OpenClaw runs its bootstrap ritual asking about identity - answer the questions to complete setup.
