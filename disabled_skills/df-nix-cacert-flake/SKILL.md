---
name: df-nix-cacert-flake
description: >
  Use when SSL/TLS certificate errors appear on NixOS (CERTIFICATE_VERIFY_FAILED, unable to get
  local issuer certificate), when setting up Python/pip environments, writing NixOS flakes that
  need network access, or configuring devShells that run curl or requests.
---

# NixOS CA Certificate Fix

## Why NixOS has SSL certificate problems

NixOS stores CA certs in the Nix store, not `/etc/ssl/certs/`. The `security.pki` module
creates `/etc/ssl/certs/ca-bundle.crt` as a symlink into the store — but it does **not**
set the environment variables that Python (`ssl`/`urllib`), the `requests` library, and
`curl` use to find the cert bundle. Any tool that hardcodes `/etc/ssl/certs/ca-bundle.crt`
or assumes a conventional Linux layout will fail.

---

## System-wide fix (configuration.nix / NixOS module)

Add to any NixOS module that applies to all machines (e.g. `common/common.nix`):

```nix
environment.variables = {
  SSL_CERT_FILE      = "/etc/ssl/certs/ca-bundle.crt";  # Python ssl / urllib
  REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-bundle.crt";  # requests library
  CURL_CA_BUNDLE     = "/etc/ssl/certs/ca-bundle.crt";  # curl / libcurl
};
```

`/etc/ssl/certs/ca-bundle.crt` is guaranteed to exist on NixOS — it's the managed symlink.
Rebuild with `sudo nixos-rebuild switch` and all new shells pick it up.

---

## Minimal self-contained flake (NixOS system)

```nix
{
  description = "NixOS system with working SSL";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: {
    nixosConfigurations.myhostname = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ({ pkgs, ... }: {
          environment.systemPackages = [ pkgs.cacert ];

          environment.variables = {
            SSL_CERT_FILE      = "/etc/ssl/certs/ca-bundle.crt";
            REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-bundle.crt";
            CURL_CA_BUNDLE     = "/etc/ssl/certs/ca-bundle.crt";
          };
        })
      ];
    };
  };
}
```

`pkgs.cacert` in `systemPackages` is optional — NixOS always provides the cert bundle via
`security.pki` — but including it makes the dependency explicit.

---

## devShell fix (per-project flake)

For development shells where you need SSL to work (pip installs, API calls, etc.):

```nix
{
  description = "Dev shell with working SSL";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = [ pkgs.cacert pkgs.python3 ];

        shellHook = ''
          export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export NIX_SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export REQUESTS_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
          export CURL_CA_BUNDLE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
        '';
      };
    };
}
```

The devShell variant uses the Nix store path directly (`${pkgs.cacert}/etc/ssl/certs/...`)
rather than `/etc/ssl/certs/ca-bundle.crt`, so it works even outside a full NixOS system
(e.g. nix-darwin, plain Linux with nix installed).

---

## Variable reference

| Variable            | Used by                          |
|---------------------|----------------------------------|
| `SSL_CERT_FILE`     | Python `ssl`, `urllib`, `httpx`  |
| `REQUESTS_CA_BUNDLE`| `requests` (overrides SSL_CERT_FILE) |
| `CURL_CA_BUNDLE`    | `curl`, anything using libcurl   |
| `NIX_SSL_CERT_FILE` | Nix itself, nix-shell propagation |