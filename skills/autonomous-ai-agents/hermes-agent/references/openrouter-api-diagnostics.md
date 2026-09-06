# OpenRouter API Diagnostics

## Quick Diagnostic Sequence

```bash
# 1. Verify key is valid — returns account info
curl -s -X GET "https://openrouter.ai/api/v1/auth/key" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print('Valid:', d.get('is_free_tier'))
print('Usage:', d.get('usage'), '| Daily:', d.get('usage_daily'))
print('Credits remaining:', d.get('limit_remaining'))
"

# 2. List available models
curl -s -X GET "https://openrouter.ai/api/v1/models" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('Total models:', len(d.get('data',[])))
"

# 3. Test a simple chat completion
curl -s -w "\nHTTP:%{http_code}" -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "HTTP-Referer: https://hermes.local" \
  -H "X-Title: HermesAgent" \
  -d '{"model":"meta-llama/llama-3.1-8b-instruct","messages":[{"role":"user","content":"Say hi"}],"max_tokens":10}'
```

## HTTP Error Code Meanings

| Code | Meaning | Next Step |
|------|---------|-----------|
| **200** | Success | — |
| **401** | Invalid API key | Check key is correct |
| **402** | **Insufficient credits** | Account balance too low — free tier still needs balance |
| **400** | Request rejected | Geo-blocked (e.g., Google AI Studio blocks CN), wrong model ID, bad format |
| **429** | Rate limited | Wait and retry, or add credits |
| **500** | Upstream provider error | Model provider is down — try different model |
| **502/503** | Gateway error | OpenRouter upstream issue — wait |

## Critical: Free Tier ≠ $0 Total Cost

OpenRouter "free" models have `pricing.prompt: "0"` meaning the **model provider costs nothing**, but OpenRouter still charges a small platform fee per request. A $0 balance fails with **HTTP 402** even for free models.

## Geo Restrictions

Some free models are **geo-blocked by their upstream provider**, returning HTTP 400:
- `google/gemma-4-31b-it:free` → 400 "User location is not supported"
- Models from Google AI Studio, Anthropic, OpenAI often block non-supported regions

Workaround: Use models from unrestricted providers (NousResearch, Meta, Mistral, Poolside, etc.).

## Hermes Configuration (already done)

```yaml
# ~/.hermes/config.yaml
providers:
  openrouter:
    api_key: sk-or-v1-...     # full key (not env var)
    base_url: https://openrouter.ai/api/v1

# Delegation subagent uses OpenRouter
delegation:
  model: qwen/qwen3-coder:free
  provider: openrouter
  base_url: https://openrouter.ai/api/v1
  api_key: sk-or-v1-...
```

## OpenClaw Configuration (already done)

```json
// ~/.openclaw/openclaw.json → models.providers.openrouter
{
  "apiKey": "sk-or-v1-...",
  "baseUrl": "https://openrouter.ai/api/v1",
  "api": "openai",
  "authHeader": true,
  "models": [
    {"id": "openrouter/owl-alpha", "name": "Owl Alpha (Free)", "contextWindow": 1048576},
    {"id": "google/gemma-4-31b-it:free", "name": "Gemma 4 31B (Free)", "contextWindow": 262144},
    {"id": "qwen/qwen3-next-80b-a3b-instruct:free", "name": "Qwen3 Next 80B (Free)", "contextWindow": 262144},
    {"id": "qwen/qwen3-coder:free", "name": "Qwen3 Coder (Free)", "contextWindow": 262000},
    {"id": "openrouter/free", "name": "Free Router", "contextWindow": 200000},
    {"id": "openai/gpt-oss-120b:free", "name": "GPT-OSS 120B (Free)", "contextWindow": 131072},
    {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Llama 3.1 8B (Free)", "contextWindow": 131072},
    {"id": "mistralai/mistral-small-24b-instruct-2501", "name": "Mistral Small 3 (Free)", "contextWindow": 131072},
    {"id": "google/gemma-3-4b-it", "name": "Gemma 3 4B (Free)", "contextWindow": 32768}
  ]
}

// agents — bound to OpenRouter models
"coder":      {"model": "qwen/qwen3-coder:free", "provider": "openrouter"},
"reasoner":   {"model": "google/gemma-4-31b-it:free", "provider": "openrouter"},
"fast":       {"model": "google/gemma-3-4b-it", "provider": "openrouter"},
"synthesizer":{"model": "openrouter/owl-alpha", "provider": "openrouter"}
```

## What Failed in Testing (2026-05-13)

All tested free models returned HTTP 500 (upstream provider down). Root cause: **HTTP 402** confirmed when testing `openrouter/auto` — account has $0 balance. Free tier designation means model price is $0, but **OpenRouter platform fee requires credits**.

Fix: Add credits at https://openrouter.ai/settings/credits
