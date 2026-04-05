---
name: openclaw-golden-paths
description: Supported deployment topologies
source: https://github.com/openclaw/nix-openclaw/docs/golden-paths.md
---

# Golden Paths

Opinionated deployment topologies with secure defaults and reproducibility.

## GP1: Single Mac

- **Platform**: macOS laptop or Mac mini
- Gateway: macOS (launchd)
- OpenClaw.app: same machine
- Networking: localhost

## GP2: VPS + Mac Node (Recommended)

- Gateway: Linux VPS (systemd user service)
- Node: OpenClaw.app on macOS (WebSocket)
- Networking: **Tailscale tailnet** (private, no public exposure)

Key: Gateway routes tool calls to node when `host=node` selected.

### Why Tailscale?

- Private-by-default connectivity
- MagicDNS stable hostnames
- Easy ACL locking

## GP3: Laptop-Only Dev

- Gateway: macOS/Linux laptop
- Node: optional
- Expect downtime/sleep/network changes

## macOS Permissions (TCC)

Privacy permissions (Screen Recording, Accessibility) are not fully declarative. Check with `openclaw nodes status` then approve once.

## Runtime vs Pinned Config

**Pinned (Nix-managed):**
- `openclaw.json` (gateway config)
- documents (AGENTS.md, SOUL.md, TOOLS.md)
- workspace path

**Runtime:**
- sessions, caches
- pairing state
- exec approvals
