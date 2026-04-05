---
name: openclaw-plugin-system
description: Plugin architecture for extending OpenClaw capabilities
source: https://github.com/openclaw/nix-openclaw
---

# Plugin System

Plugins extend OpenClaw by bundling **CLI tools** + **AI skills** + **config requirements**.

## Plugin Contract

```nix
openclawPlugin = {
  name        = "plugin-name";
  skills      = [ ./skills/my-skill ];
  packages    = [ pkgs.my-cli-tool ];
  needs = {
    stateDirs   = [ ".config/my-plugin" ];
    requiredEnv = [ "MYPLUGIN_API_KEY" ];
  };
};
```

## Host-Side Enable

```nix
programs.openclaw.instances.default.plugins = [
  {
    source = "github:owner/repo";
    config = {
      env = { MYPLUGIN_API_KEY = "/run/agenix/myplugin-key"; };
      settings = { foo = "bar"; retries = 3; };
    };
  }
];
```

## Bundled Plugins

Enable via `programs.openclaw.bundledPlugins`:

| Plugin | Purpose |
| --- | --- |
| `summarize` | Summarize URLs, PDFs, YouTube |
| `peekaboo` | Screenshot |
| `poltergeist` | macOS UI control |
| `sag` | Text-to-speech |
| `camsnap` | Camera snapshots |
| `gogcli` | Google Calendar |
| `goplaces` | Google Places |
| `bird` | Twitter/X |
| `sonoscli` | Sonos control |
| `imsg` | iMessage |

## Config Behavior

- `config.env`: exported as environment variables (files must exist)
- `config.settings`: rendered to `config.json` in first `stateDir`
- **Last plugin wins** on name collisions

## Authoring Rules

- CLI must be env-configurable (no magic defaults)
- Honor XDG paths
- Ship `AGENTS.md` with knobs (no secrets)
- `SKILL.md` calls CLI by PATH name
