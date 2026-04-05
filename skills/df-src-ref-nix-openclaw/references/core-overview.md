---
name: nix-openclaw
description: Declarative OpenClaw packaging via Nix and Home Manager
source: https://github.com/openclaw/nix-openclaw
date: 2026-04-06
gitSha: 0f4d0666f1490cbe1ba76062275eb22d2f89cc44
---

# nix-openclaw

nix-openclaw provides **declarative OpenClaw deployments** using Nix flakes and Home Manager. It packages the OpenClaw gateway, tools, and macOS app with reproducible, declarative configuration.

## Key Capabilities

- **Batteries-included**: Gateway + tools on macOS/Linux, macOS app on macOS
- **Plugin system**: Enable community or bundled plugins via Nix config
- **Service management**: launchd (macOS) or systemd user service (Linux)
- **Rollback support**: Nix generations enable instant rollback

## Architecture

```
User (Telegram/Discord) --> Gateway --> Tools --> Machine actions
```

- **Gateway**: Brain service receiving messages, managed by launchd/systemd
- **Plugins**: Bundles CLI tools + AI skills
- **Skills**: Markdown instructions teaching AI how to use tools

## Supported Platforms

- `aarch64-darwin` (Apple Silicon)
- `x86_64-linux`

## Quick Start

```nix
# Minimal setup with Telegram
programs.openclaw = {
  enable = true;
  documents = ./documents;
  config = {
    gateway.mode = "local";
    gateway.auth.token = "<gatewayToken>";
    channels.telegram = {
      tokenFile = "/run/agenix/telegram-bot-token";
      allowFrom = [ 12345678 ];
    };
  };
  instances.default = {
    enable = true;
    plugins = [
      { source = "github:openclaw/nix-steipete-tools?dir=tools/summarize"; }
    ];
  };
};
```

Then: `home-manager switch --flake .#<user>`

## Packages

| Package | Contents |
| --- | --- |
| `openclaw` (default) | macOS: gateway + app + tools · Linux: gateway + tools |
| `openclaw-gateway` | Gateway CLI only |
| `openclaw-tools` | Toolchain bundle |
| `openclaw-app` | macOS app only |
