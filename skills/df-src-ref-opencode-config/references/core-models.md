---
description: Configure AI providers, models, timeout settings, and local model support.
source: https://opencode.ai/docs/config/
---

# Provider & Model Configuration

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {},
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `provider` | object | Provider-specific configuration |
| `model` | string | Primary model (format: `provider/model-name`) |
| `small_model` | string | Lightweight model for cheap tasks (title generation, etc.) |

## Provider Options

```json
{
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "chunkTimeout": 30000,
        "setCacheKey": true
      }
    }
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | number | 300000 | Request timeout in ms (false to disable) |
| `chunkTimeout` | number | 30000 | Timeout between streamed response chunks |
| `setCacheKey` | boolean | false | Ensure cache key is always set |

## Amazon Bedrock

```json
{
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile",
        "endpoint": "https://bedrock-runtime.us-east-1.vpce-xxxxx.amazonaws.com"
      }
    }
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `region` | string | AWS_REGION or us-east-1 | AWS region for Bedrock |
| `profile` | string | AWS_PROFILE env var | AWS named profile from ~/.aws/credentials |
| `endpoint` | string | - | Custom VPC endpoint URL |

## Provider Filtering

```json
{
  "disabled_providers": ["openai", "gemini"]
}
```

```json
{
  "enabled_providers": ["anthropic", "openai"]
}
```

**Note**: `disabled_providers` takes priority over `enabled_providers`.
