---
name: openclaw-configuration
description: OpenClaw configuration schema and options
source: https://github.com/openclaw/nix-openclaw
---

# Configuration Reference

## Top-Level Options

```nix
programs.openclaw = {
  enable = true;
  package = pkgs.openclaw;           # default: batteries-included
  toolNames = [ "nodejs_22" ];       # override toolchain
  excludeTools = [ "git" ];          # remove built-ins
  stateDir = "~/.openclaw";          # state directory
  workspaceDir = "~/.openclaw/workspace";
  documents = ./documents;           # AGENTS.md, SOUL.md, TOOLS.md
  skills = [ ... ];                  # declarative skills
  reloadScript.enable = true;        # no-sudo restart helper
};
```

## Instance Configuration

```nix
programs.openclaw.instances = {
  prod = {
    enable = true;
    package = pkgs.openclaw;
    stateDir = "~/.openclaw";
    launchd.enable = true;           # macOS service
    systemd.enable = true;           # Linux service
    plugins = [ ... ];
    config = { ... };                 # gateway config
  };
};
```

## Gateway Config (Schema-Typed)

```nix
config = {
  gateway = {
    mode = "local";                  # or "node"
    auth.token = "<token>";
  };
  channels.telegram = {
    tokenFile = "/path/to/token";
    allowFrom = [ 12345678 ];
    groups."*" = { requireMention = true; };
  };
};
```

## Service Commands

```bash
# macOS
launchctl print gui/$UID/com.steipete.openclaw.gateway | grep state
launchctl kickstart -k gui/$UID/com.steipete.openclaw.gateway

# Linux
systemctl --user status openclaw-gateway
systemctl --user restart openclaw-gateway

# Rollback
home-manager generations
home-manager switch --rollback
```

## What Nix Manages vs User Manages

| Component | Nix | User |
| --- | --- | --- |
| Gateway binary | ✓ | |
| macOS app | ✓ | |
| Service (launchd/systemd) | ✓ | |
| Tools | ✓ | |
| Telegram bot token | | ✓ |
| Anthropic API key | | ✓ |
