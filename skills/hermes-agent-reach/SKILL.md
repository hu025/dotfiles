---
name: hermes-agent-reach
trigger_words: ['agent-reach', 'internet-access', 'web-browsing', 'online-investigation', 'global-search', 'anywhere-access']
category: web-development
description: "Unified cross-platform agent internet access system with provider-agnostic interfaces for web surfing, agent delegation, and endpoint access across social media, video platforms, email, and real-time services"
---

# Hermes Agent Reach — Universal Internet Access Layer

A centralized system for enabling controlled, authenticated, and auditable internet access across social platforms, messaging services, video platforms, search engines, and real-time services. This umbrella consolidates all previous narrow 'agent-reach' implementations into a robust, provider-agnostic interface layer.

## Overview

This skill serves as a gateway for AI agents to safely interact with external web services without requiring per-platform authentication tokens. It provides:
- Standardized access protocols (provider-agnostic wrappers)
- Multi-provider failover ("fail open" with warning logging)
- Real-time credential rotation
- Cross-platform delegation (Twitter/X, YouTube, Facebook Groups, Reddit, Discord, Telegram, Slack, GitHub, Telegram channels, Lemmy, Mastodon, Bluesky, etc.)
- Content verification and prompt injection detection
- Rate limiting and usage logging

## Core Features

### Universal Web Interface Layer
- **Common Access Layer**: Provider-agnostic interface with standardized methods for reading, interacting, and authenticating
- **Fallback Strategy**: Second and third provider automatic switching when primary fails or rate limits
- **Session Management**: Persistent sessions with automatic reconnection and credential rotation
- **Content Caching**: Local first-read caching with SHA-256 validation


### Supported Platforms & Providers

| Platform | Primary Provider | Fallback(s) | Notes |
|----------|----------------|-------------|-------|
| **Twitter/X** | Twitter API v2 | Nitter (read-only), Cloudflare Scraper | OAuth2 + Bearer Token |
| **YouTube** | YouTube Data API v3 | Invidious, Piped instances | Requires API key |
| **Reddit** | Pushshift API (read), PRAW (interact) | Marmit API | OAuth2 auth |
| **Discord** | discord.py REST API | Scrapers, Bot lists | SNAP bot token free |
| **Telegram** | Telethon (MTProto) | TDLib proxy, Bot API fallback | Requires phone number session |
| **Facebook** | Graph API (legacy) | Greyscale FB view, mobile web | VERY RATE LIMITED |
| **Slack** | Slack Web API + RTM | Manual copy/paste, historic web archivers | OAuth2 workspace tokens |
| **GitHub** | REST API v3 | GraphQL fallback, Scrape diffs | PAT or OAuth |
| **Lemmy** | Pushshift-style API | Multiple federated instances | basic auth |
| **Mastodon** | Mastodon API v2 | multiple home instances | user@instance format |
| **Bluesky** | AT Protocol via bsky.app | fallback to old endpoints | Manual APP_PASSWORD |

> ❗ **Important**: Some platforms are explicitly non-authoritative sources (e.g., Nitter for X, Piped for YouTube). All assistant outputs must carry credit attribution: `Source: [platform] ([provider])`

### Authentication & Credential Management

- **Credential Rotation**: Automatic token refresh when approaching limits
- **Token Validity Check**: Probe endpoints with lightweight HEAD/ping before use
- **Rate Kill-Switch**: Global pause when cumulative daily tokens hit 90% or API errors exceed threshold
- **Multi-Account Failover**: Load-balance across multiple authenticated accounts when possible
- **Session TTL**: automatic session expiry and re-prompt after 24h of inactivity


### Content Extraction Layer

- **Structured Data Extraction**: Convert platform HTML/API responses into normalized formats (markdown tables, JSON outlines)
- **Video/ Audio Harvesting**: Detect and extract embedded media, transcripts, captions
- **Real-time Monitoring**: Poll endpoints for updates via webhooks or long polling
- **Search & Discovery**: Cross-platform keyword search with provider hierarchy prioritization
- **Interaction Logging**: All outgoing API calls logged with response time, rate limits, errors

### Security & Compliance Layer

- **Prompt Injection Detection**: Full page analysis, both HTML and text
- **Anti-Automation Gate**: Naive CAPTCHA and bot-detection bypass at the cost of undetectable fingerprints
- **Content Verification**: Compare scraped content against keywords, hashtags, channel consistency checks
- **Historical Integrity**: Archive fetched content with URL and timestamp signatures
- **Delta Feeds**: Only fetch updates since last successful pull (when history exists)

## Usage Patterns

### Real-time Social Monitoring (Batched)
```bash
# Monitor @company across platforms
hermes agent-reach monitor \
  --platforms twitter,x,youtube,discord \
  --query "@company" \
  --rate-limit 100/hour \
  --output-format json-table
```

### Multi-Platform Search Campaign
```python
from hermes_tools import reach_query

results = reach_query(
  query="AI safety regulation 2026",
  platforms=["reddit", "mastodon", "bluesky", "lemmy"],
  max_results=50,
  include_media=False
)

# Returns compacted JSON with source attribution
for platform, content in results.items():
  print(f"Source: {platform} ({content['provider']}): {len(content['posts'])} results")
```

### Cross-Platform Webhook Integration
```yaml
# config/agent-reach-webhooks.yaml
webhooks:
  twitter:
    endpoint: https://x.com/status/{id}
    extractor: tweet-simple-extractor
    rate_limit: 1000/day
    oauth:
      type: bearer
      token_env: X_BEARER_TOKEN
      token_path: ~/.config/hermes/agent-reach/tokens/x.json
  bluesky:
    endpoint: https://bsky.app/profile/{username}/post/{id}
    extractor: bluesky-text-extractor
    auth: app_password
    app_password_env: BSKY_APP_PASSWORD
```

### Failure Handlers & Auto Retry
```python
from hermes_tools import aio_reach_loop

async def consume_platform_updates():
  while True:
    try:
      updates = await platform.fetch_all_updates()
      await process(updates)
    except ReachException as e:
      log_warning(f"Platform {platform.name} failed: {e}")
      await platform.failover()
      continue
    except RateLimitExceeded:
      await asyncio.sleep(platform.calculate_cooldown())
```

## Multi-Provider Failover Implementation

```python
PROVIDERS = {
 'twitter': [
   {'type': 'api-x', 'auth_token': TWITTER_BEARER_TOKEN},
   {'type': 'nitter', 'url': 'https://nitter.net', 'priority': 2},
   {'type': 'cloudflare-scraper', 'priority': 3}
 ],
 'youtube': [
   {'type': 'api-v3', 'key': YT_API_KEY, 'priority': 1},
   {'type': 'invidious', 'url': 'https://vid.puffyan.us'},
   {'type': 'piped', 'url': 'https://piped.kavin.rocks'},
 ]
}

def get_provider(platform: str, rank=1):
  """Return configured provider with rank priority"""
  idx = 0 if rank == 1 else rank-1
  return PROVIDERS.get(platform, [{}])[idx]

def fallback(platform: str):
  """Advance provider index for this platform"""
  # Atomic counter doesn't exist in user land -> use env var simplistic
  idx = fetch_env(f"HERMES_{platform.upper()}_PROVIDER_IDX", default=0)
  store_env(f"HERMES_{platform.upper()}_PROVIDER_IDX", (idx + 1) % len(PROVIDERS.get(platform, [{}]))
  return get_provider(platform, idx+1)
```

### Automatic Switching Strategy
| Failure Type | Response |
|--------------|----------|
| Token Expiry | Re-ping auth, automatic renew if possible |
| Rate Limit (429) | Immediate switch to rank 2, backoff 2^(retries) seconds |
| Platform Ban | Blacklist provider, use manual reservation |
| Network Timeout | Switch to CLI-based fallbacks (curl/wget) |

## Provider-Specific Guides

### Twitter/X Provider Switching
1. **Rank 1 (API)**: OAuth2 Bearer Token + Twitter API v2
   - Daily limit: 50k tweets, 5k retweets
   - Rate limit reset: 15 minute windows
2. **Rank 2 (Read)**: Nitter instances (node/`nitter` instances)
   - No auth, HTML scraping
   - Ratelimit: IP-based 5k/hr
3. **Rank 3 (Fallback)**: Cloudflare Workers scraper (non-official, fingerprints)
   - IP rotation via cloud side auto-
   - Emulate Chrome headers

> ⚠️ **Ethics Note**: Direct scraping bypasses API TOS. Use only on public, non-paywalled content. Add attribution and performance descr in outputs.

### YouTube Provider Chain
1. **Rank 1**: YouTube Data API v3 (requires key + OAuth)
   - Quota: 10k units/day
   - 1 search = 100 units
2. **Rank 2-4**: Invidious Piped proxy instances
   - Pick based on load (check /api/v1/stats)
   - Return JSON transcripts when possible
3. **Manual**: Direct HTML scrape of /watch?v={id} for captions (requires manual CAPTCHA solve)

> 🔐 **Security**: All video platform scrapers must filter:
> - NSFW videos (when worker instructed to avoid adult content)
> - Copyrighted material (you are client-side only responsible for retrieval, not redistribution)

## Cross-Agent Communication

Enable Multi-Agent collaboration via standard JSON RPC over HTTP:

```python
# Agent-A calls Agent-B via webhook
POST /agent/reach/bridge HTTP/1.1
Content-Type: application/json
X-Agent-Auth: Bearer secure_token_123

{
  "routing_key": "agent-b/subtask/compute-value",
  "payload": {"arg1": "value"},
  "ttl": 300
}

>>> Agent-B receives, processes, responds JSON
```

All inter-agent traffic logged under `.hermes/agent-reach/logs/rpc/[timestamp].json` for audit.

## Asynchronous Update Loop

```python
from aiohttp import ClientSession
import async_timeout

class AsyncReachClient:
  async def fetch_updates(self, platform, last_seen_id=None):
    # Implement for each platform
    return []

async def poll_loop(self):
  while True:
    for platform in SUPPORTED_PLATFORMS:
      try:
        async with async_timeout.timeout(30):
          updates = await self.fetch_updates(platform)
          await self.process(updates)
      except Exception as e:
        log_error(f"Platform {platform} errored: {e}")
        await self.failover(platform)
    await asyncio.sleep(PULL_INTERVAL)
```

## Filesystem Integrity Features

### Cache Digest
Each fetch builds a filename-safe digest:
```
path = f".cache/agent-reach/{platform}/{year}/{month}/{dt_str}-{url_path_sha256(link)[:8]}.json"
```

### SHA-256 Manifest
```bash
sha256sum $CACHE_DIR/agent-reach/**/*.json > $CACHE_DIR/agent-reach.sha256
```

### Local First Search
```bash
rg "query text" ~/.cache/agent-reach --type json
```

## RPC Bridge Configuration

```yaml
# config/agent-reach-bridge.yaml
rpc:
  enabled: true
  listen: 0.0.0.0:8080
  auth_tokens:
    - hermes-secret-1234
  cors_origins:
    - https://chat.nous.sh
    - https://hermes.nous.sh
  rate_limit_tokens:
    - max_per_minute: 60
```

## Troubleshooting Guide

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| **Auth Token Expired** | GET /api/v2/user returns 401 | Re-prompt user for new token (interactive) |
| **Platform Unavailable** | GET 503/504/timeout repeatedly > 10x | Switch provider rank, log warning in agent memory |
| **Scraper Fork Bomb** | Too many concurrent requests 429 | Increase cool-down exponential backoff, use async per platform |
| **Content Mismatch** | Scraped text != expected keywords | Check anti-bot JS execution, use rank 3 provider |

## Legacy Migrations

This umbrella absorbs the original narrow `agent-reach` skill focused only on enabling Twitter/X delegation between agents.

---

references:
  01-credential-store.md: "Encrypted credential storage format"
  02-rate-limiting.md: "Provider-specific rate limits and backoff strategies"
  03-content-extraction.md: "Schema for normalized response formats"
templates:
  agent-reach-config.yaml: "Main configuration file template"
scripts:
  reach-sync.py: "Continuous polling daemon for cross-platform updates"
  token-rotator.sh: "Automated token refresh with alerts"