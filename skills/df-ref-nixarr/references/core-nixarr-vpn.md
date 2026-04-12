---
name: nixarr VPN Options
description: VPN configuration for routing service traffic through WireGuard
---

# nixarr VPN Options

## `nixarr.vpn.enable`

```nix
nixarr.vpn.enable = mkOption {
  type = types.bool;
  default = false;
  example = true;
};
```

Enable VPN support. Requires `nixarr.vpn.wgConf` to be set.

---

## `nixarr.vpn.wgConf`

```nix
nixarr.vpn.wgConf = mkOption {
  type = types.nullOr types.path;
  default = null;
  example = "/data/.secret/wg.conf";
};
```

Path to WireGuard configuration file from VPN provider.

**Requirements:**
- File must NOT be in your Nix configuration git directory
- VPN provider must support wg-quick configurations
- Recommended: provider with static port forwarding (e.g., AirVPN)

---

## `nixarr.vpn.accessibleFrom`

```nix
nixarr.vpn.accessibleFrom = mkOption {
  type = with types; listOf str;
  default = [];
  example = ["192.168.2.0/24"];
};
```

Extra IP ranges allowed to access VPN-confined services.

**Default allowed ranges:**
- `192.168.1.0/24`
- `192.168.0.0/24`
- `127.0.0.1`

---

## `nixarr.vpn.vpnTestService`

```nix
nixarr.vpn.vpnTestService.enable = mkEnableOption "the vpn test service";
nixarr.vpn.vpnTestService.port = mkOption {
  type = with types; nullOr port;
  default = null;
  example = 58403;
};
```

Enable testing service for DNS leak testing and port forwarding verification. If port is set, netcat listens on that port.

---

## `nixarr.vpn.openTcpPorts` / `openUdpPorts`

```nix
nixarr.vpn.openTcpPorts = mkOption {
  type = with types; listOf port;
  default = [];
  example = [46382 38473];
};
```

Extra TCP/UDP ports to allow traffic from when using VPN port forwarding for services not covered by nixarr.

---

## Service VPN Options

Each service has a `vpn.enable` option to route its traffic through VPN:

```nix
nixarr.transmission.vpn.enable = true;
nixarr.jellyfin.vpn.enable = true;
```

> **Note:** The "*Arrs" can be run behind VPN but it's not recommended due to rate limiting issues.

---

## Example

```nix
nixarr.vpn = {
  enable = true;
  wgConf = "/data/.secret/vpn/wg.conf";
  accessibleFrom = ["192.168.2.0/24"];
  
  vpnTestService = {
    enable = true;
    port = 58403;
  };
  
  openTcpPorts = [46382];
};
```
