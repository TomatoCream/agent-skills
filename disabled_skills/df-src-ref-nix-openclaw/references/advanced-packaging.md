---
name: openclaw-packaging-updates
description: Update cadence and pinning strategy
source: https://github.com/openclaw/nix-openclaw
---

# Packaging & Updates

## Output Packages

```
.#openclaw         # default: gateway + app + tools
.#openclaw-gateway # CLI only
.#openclaw-tools   # toolchain bundle
.#openclaw-app     # macOS app only
```

Pin source: `nix/sources/openclaw-source.nix`

## Update Pipeline

1. **moltinators updater** proposes new stable pin
2. **Garnix** builds on Linux + macOS, runs `pnpm test`
3. **moltinators smoke test** runs against real Discord
4. If green → promote to stable; if red → keep current

## Manual Pin Bump

```bash
GH_TOKEN=... scripts/update-pins.sh
```

## Verify Freshness

```bash
git pull --ff-only
# Check nix/sources/openclaw-source.nix vs
git ls-remote https://github.com/openclaw/openclaw.git refs/heads/main
```

## Golden Path for Pins

Hourly GitHub Action **Yolo Update Pins** runs `scripts/update-pins.sh`:
- Picks latest upstream SHA with green non-Windows checks
- Rebuilds gateway to refresh `pnpmDepsHash`
- Regenerates `nix/generated/openclaw-config-options.nix`
- Updates app pin/hash, commits, rebases, pushes to `main`

## CI Polling Rule

Never say "I'll keep polling" unless already running a blocking loop. Use tmux or sub-agent.
