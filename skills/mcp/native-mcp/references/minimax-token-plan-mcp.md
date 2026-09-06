# MiniMax Token Plan MCP Server

MiniMax offers an exclusive MCP server (`minimax-coding-plan-mcp`) providing two tools unavailable via any other MiniMax API:

- **`web_search`** — real web search
- **`understand_image`** — image understanding

## ⚠️ Critical: Two Types of MiniMax API Keys

| Key Type | Format | Source | Used For |
|----------|--------|--------|----------|
| **API Key** | `eyJh...` (JWT) | platform.minimax.io → API Keys | Standard MiniMax API calls |
| **Token Plan Key** | `tmp-xxx-xxxxx` | platform.minimax.io → Billing → Token Plan | Token Plan MCP only |

The Token Plan MCP **rejects regular API keys**. Using `MINIMAX_API_KEY` with the wrong key type causes MCP connection timeout after 40s.

Obtain your Token Plan Key at: https://platform.minimax.io/billing/token-plan

## Quick Setup

```bash
# Verify package is available (no install needed with uvx)
uvx --from 'minimax-coding-plan-mcp' --help
```

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  minimax-search:
    command: "uvx"
    args: ["minimax-coding-plan-mcp"]
    env:
      MINIMAX_API_KEY: "tmp-xxx-xxxxx"   # Token Plan Key only
      MINIMAX_API_HOST: "https://api.minimax.io"
    timeout: 60
    connect_timeout: 60
```

Restart:
```bash
systemctl --user restart hermes-gateway.service
```

## Manual Test

```bash
MINIMAX_API_KEY="tmp-xxx-xxxxx" MINIMAX_API_HOST="https://api.minimax.io" \
  uvx minimax-coding-plan-mcp
# Should start without error. Press Ctrl+C to stop.
```

Expected output: `MCP server running on stdio` or similar ready message.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `MCP call timed out after 40.0s` | Wrong key type (regular API key used) | Must use Token Plan Key, not `eyJh...` key |
| Auth / 401 error | `MINIMAX_API_HOST` missing or wrong | Must be `https://api.minimax.io` |
| `Package not found` | Wrong package name | Use exactly `minimax-coding-plan-mcp` |
| Tools not appearing after config | Config in wrong file | Use `~/.hermes/config.yaml` not agent subdirectory |

## Key Packages

- **Python**: `minimax-coding-plan-mcp` (0.0.4) — stdio server
- **Python (older)**: `minimax-mcp` (0.0.18) — desktop/file tools, no web_search
- **npm**: `minimax-mcp-js` (0.0.17) — generation tools only (image/video/audio)
