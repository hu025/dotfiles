# MiniMax MCP Investigation (Session 2026-05-18)

## Token Plan MCP Package

**Package name**: `minimax-coding-plan-mcp` (NOT `minimax-mcp`)

**Run command**: `uvx minimax-coding-plan-mcp`

**Entry point**: `minimax_mcp.server:main`

**Tools provided**: `web_search`, `understand_image`

**Required env vars**:
- `MINIMAX_API_KEY` — Token Plan Key (different from standard API key)
- `MINIMAX_API_HOST=https://api.minimax.io`

**Hermes CLI add command**:
```bash
hermes mcp add minimax-search \
  --command uvx \
  --args 'minimax-coding-plan-mcp' \
  --env 'MINIMAX_API_KEY=' \
  --env 'MINIMAX_API_HOST=https://api.minimax.io'
```

**Critical note**: Times out if Token Plan Key lacks MCP permissions. Standard MiniMax API keys do NOT work — must be a Token Plan subscription key.

## Free Alternatives for web_search + web_extract

### Tavily (✅ Recommended — 1000/month, no credit card)
- Website: app.tavily.com
- API key: free tier available
- Backend name in Hermes: `tavily`
- Config: `web.extract_backend: tavily`

### MiniMax CLI (mentioned in docs as preferred over MCP)
- Website: platform.minimax.io/docs/token-plan/cli-guide
- Tool: `mmx-cli` — simpler setup than MCP

## web_extract Bug Context

The error `"DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content"` means `web.extract_backend` is set to `ddgs` (search-only).

Fix: set `web.extract_backend: tavily` in config.yaml, or configure an MCP server that provides `web_search`/`understand_image`.

## uvx availability check
```bash
which uvx && uvx --version
# If not found:
curl -LsSf https://astral.sh/uv/install.sh | sh
```
