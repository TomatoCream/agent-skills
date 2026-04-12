---
name: nixarr DDNS Options
description: Dynamic DNS configuration using Njalla
---

# nixarr DDNS Options

## `nixarr.ddns.njalla`

```nix
nixarr.ddns.njalla = {
  enable = mkOption { type = types.bool; default = false; };
  
  keysFile = mkOption {
    type = with types; nullOr path;
    default = null;
    example = "/data/.secret/njalla/keys-file.json";
  };
};
```

Enable Njalla DDNS to automatically update DNS records when your public IP changes.

---

## `nixarr.ddns.njalla.vpn`

```nix
nixarr.ddns.njalla.vpn = {
  enable = mkOption { type = types.bool; default = false; };
  
  keysFile = mkOption {
    type = with types; nullOr path;
    default = null;
  };
};
```

Enable Njalla DDNS over VPN. Updates DNS to point to your VPN public IP.

**Requires:** `nixarr.vpn.enable`

---

## Keys File Format

Create a JSON file with domain-to-key mappings:

```json
{
  "jellyfin.example.com": "zeubesojOLgC2eJC"
}
```

To get keys, create a dynamic Njalla record. You'll see a suggested command like:
```sh
curl "https://njal.la/update/?h=jellyfin.example.com&k=zeubesojOLgC2eJC&auto"
```

---

## Example

```nix
nixarr.ddns.njalla = {
  enable = true;
  keysFile = "/data/.secret/njalla/keys.json";
};

# Or for VPN IP
nixarr.ddns.njalla.vpn = {
  enable = true;
  keysFile = "/data/.secret/njalla/vpn-keys.json";
};
```

---

## Recommendation

Njalla is privacy-oriented, accepts Monero, and doesn't require personal data. You "lease" domains rather than "own" them for privacy reasons.

See [Njalla](https://njal.la/) for more info.
