# Model Provider & Fallback Chain (2026-06-10)

## Current Provider Setup

| Provider | Role | API Key | Endpoint |
|----------|------|---------|----------|
| `minimax` | **Primary** (default model: `MiniMax-M2.7`) | `MINIMAX_API_KEY` | `https://api.minimaxi.com/v1` |
| `minimax-cn` | **Fallback** (only fallback in chain) | `MINIMAX_CN_API_KEY` | `https://api.minimaxi.com/v1` |
| `nvidia` | **Model catalog only** — NOT in fallback chain | `nvapi-...` | `https://integrate.api.nvidia.com/v1` |

**Active fallback chain**: `minimax` → `minimax-cn`

Only `minimax-cn` is in the fallback chain. NVIDIA NIM (~190 models) is configured as a provider with available models but is **not automatically used** when MiniMax fails.

## When Does Fallback Activate?

The fallback chain activates when:
- **HTTP 429** (rate limit / quota exhausted)
- **HTTP 5xx** (server error / timeout)
- **Connection failure** (timeout, DNS, etc.)

Sequence per `api_max_retries: 5`:
```
Primary call fails → retry × 5 → activate fallback → retry × 5 → fail
```

The `_fallback_chain` is built in `agent/agent_init.py:884-907` from `fallback_model` (list or dict). Currently the config only has `minimax-cn` in the fallback chain.

## Adding NVIDIA to Fallback Chain

To enable automatic NVIDIA fallback, add to `~/.hermes/config.yaml`:

```yaml
fallback_providers:
  - provider: minimax-cn
    model: minimax/MiniMax-M2.7
  - provider: nvidia
    model: nvidia/llama-3.3-70b-instruct
```

This would make the chain: `minimax` → `minimax-cn` → `nvidia/llama-3.3-70b-instruct`.

## NVIDIA NIM Auth

NVIDIA NIM at `integrate.api.nvidia.com` is **publicly accessible** — no API key required (uses `api_key: NONE` pattern). The `nvapi-...` key in config is optional but not required for the public endpoint.

## Key Code References

- Fallback chain construction: `agent/agent_init.py:884-907`
- `try_activate_fallback()`: `agent/chat_completion_helpers.py:1020`
- Retry logic: `run_agent.py:240-272` (`_pool_may_recover_from_rate_limit`)
- Stale timeout (90s default, lowered May 2026): `run_agent.py:1084`