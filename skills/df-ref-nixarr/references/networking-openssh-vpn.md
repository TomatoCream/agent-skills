---
name: nixarr OpenSSH VPN Exposure
description: Expose SSH service through VPN for secure remote access
---

# nixarr OpenSSH VPN Exposure

## `nixarr.openssh.expose.vpn.enable`

```nix
nixarr.openssh.expose.vpn.enable = mkOption {
  type = types.bool;
  default = false;
};
```

Expose SSH service through VPN, making it accessible from the internet via your VPN's public IP.

**Requires:** `nixarr.vpn.enable`

---

## Security Warning

> **Warning:** This lets anyone on the internet connect through SSH. Make sure SSH is configured securely!

**Required SSH config:**
```nix
services.openssh = {
  enable = true;
  settings.PasswordAuthentication = false;
  ports = [ 12345 ];  # Get from VPN provider
};

users.extraUsers.username.openssh.authorizedKeys.keyFiles = [
  ./path/to/public/key/machine.pub
];
```

**Critical:** Use key-based authentication only, never passwords.

---

## How It Works

1. SSH runs in the VPN namespace
2. Your VPN provider assigns a public IP/port
3. Port is automatically opened via VPN config
4. You can SSH to `vpn-public-ip:port`

---

## Example

```nix
# Enable SSH via VPN
nixarr.openssh.expose.vpn.enable = true;

# SSH service config
services.openssh = {
  enable = true;
  settings.PasswordAuthentication = false;
  ports = [ 12345 ];
};

users.extraUsers.admin.openssh.authorizedKeys.keyFiles = [
  /etc/secrets/admin.pub
];
```

---

## Port Forwarding via VPN

Nixarr automatically maps SSH ports through the VPN:

```nix
vpnNamespaces.wg = {
  portMappings = [
    { from = 22; to = 22; }  # Or your custom SSH port
  ];
  openVPNPorts = [
    { port = 12345; protocol = "both"; }
  ];
};
```
