---
name: openclaw-dual-instance-setup
description: Running multiple OpenClaw instances (prod/dev)
source: https://github.com/openclaw/nix-openclaw
---

# Dual-Instance Setup

Run prod + dev instances with shared base config.

## Configuration Pattern

```nix
inputs = {
  nix-openclaw.url = "github:openclaw/nix-openclaw?ref=v0.1.0";
};

let
  prodConfig = {
    channels.telegram = {
      tokenFile = "/run/agenix/telegram-prod";
      allowFrom = [ 12345678 ];
    };
  };
  devConfig = {
    channels.telegram = {
      tokenFile = "/run/agenix/telegram-dev";
      allowFrom = [ 12345678 ];
    };
  };
  prod = {
    enable = true;
    package = inputs.nix-openclaw.packages.${pkgs.system}.openclaw-gateway;
    config = prodConfig;
    plugins = [ { source = "github:owner/your-plugin"; } ];
  };
in {
  programs.openclaw.appPackage =
    inputs.nix-openclaw.packages.${pkgs.system}.openclaw-app;
  programs.openclaw.documents = ./documents;
  programs.openclaw.instances = {
    prod = prod;
    dev = prod // {
      config = devConfig;
      gatewayPort = 18790;
      gatewayPath = "/Users/you/code/openclaw";  # local gateway
      plugins = prod.plugins ++ [
        { source = "path:/Users/you/code/your-plugin"; }
      ];
    };
  };
}
```

## Key Points

- **Last plugin wins** on name collisions (use to override prod with dev)
- Dev uses local `gatewayPath` while app stays pinned
- Different ports avoid conflicts

## Tool Collision Handling

```nix
# Exclude tools already installed elsewhere
programs.openclaw.excludeTools = [ "git" "jq" "ripgrep" ];

# Or provide custom tool list
programs.openclaw.toolNames = [ "nodejs_22" "pnpm_10" "summarize" ];
```
