---
name: nixarr Recyclarr Options
description: Automatic sync of custom formats to Radarr and Sonarr
---

# nixarr Recyclarr Options

## Basic Options

```nix
nixarr.recyclarr = {
  enable = mkOption { type = types.bool; default = false; };
  
  package = mkPackageOption pkgs "recyclarr" {};
  
  schedule = lib.mkOption {
    type = lib.types.str;
    default = "daily";
  };
  
  stateDir = mkOption {
    type = types.path;
    default = "${nixarr.stateDir}/recyclarr";
  };
};
```

---

## Configuration Methods

You can configure Recyclarr using EITHER `configFile` OR `configuration`, but not both.

---

### `nixarr.recyclarr.configFile`

```nix
nixarr.recyclarr.configFile = mkOption {
  type = types.nullOr types.path;
  default = null;
  example = "./recyclarr.yaml";
};
```

Path to a YAML configuration file.

**API keys** can be referenced using `!env_var RADARR_API_KEY` and `!env_var SONARR_API_KEY` macros.

See [Recyclarr docs](https://recyclarr.dev/wiki/yaml/config-reference) for config format.

---

### `nixarr.recyclarr.configuration`

```nix
nixarr.recyclarr.configuration = mkOption {
  type = types.nullOr format.type;
  default = null;
};
```

Inline Nix configuration that gets converted to YAML.

**Example:**
```nix
nixarr.recyclarr.configuration = {
  sonarr = {
    series = {
      base_url = "http://localhost:8989";
      api_key = "!env_var SONARR_API_KEY";
      quality_definition = { type = "series"; };
      delete_old_custom_formats = true;
      custom_formats = [
        {
          trash_ids = ["85c61753df5da1fb2aab6f2a47426b09"];
          assign_scores_to = [{ name = "WEB-DL (1080p)"; score = -10000; }];
        }
      ];
    };
  };
  radarr = {
    movies = {
      base_url = "http://localhost:7878";
      api_key = "!env_var RADARR_API_KEY";
      quality_definition = { type = "movie"; };
      delete_old_custom_formats = true;
    };
  };
};
```

---

## Requirements

**Requires at least one of:**
- `nixarr.radarr.enable = true`
- `nixarr.sonarr.enable = true`

---

## Schedule

Default is "daily" (systemd calendar format). Examples:
- `"hourly"` - Every hour
- `"daily"` - Every day at midnight
- `"*-*-1,15 02:00:00"` - 1st and 15th of each month at 2 AM

---

## Example

```nix
nixarr.recyclarr = {
  enable = true;
  schedule = "daily";
  configuration = {
    sonarr = {
      series = {
        base_url = "http://localhost:8989";
        api_key = "!env_var SONARR_API_KEY";
        quality_definition = { type = "series"; };
        delete_old_custom_formats = true;
      };
    };
    radarr = {
      movies = {
        base_url = "http://localhost:7878";
        api_key = "!env_var RADARR_API_KEY";
        quality_definition = { type = "movie"; };
      };
    };
  };
};
```
