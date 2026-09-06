---
name: mcp-integration
description: MCP (Model Context Protocol) 2026 status, 5 key servers, and Hermes integration patterns. Use when wiring external tools into Hermes via MCP stdio/HTTP transports.
---

# MCP Integration for Hermes (2026)

## Protocol Status (Nov 2025 spec, current 2026)
- **Spec**: 2025-11-25, donated to **Linux Foundation** Dec 2025. JSON-RPC 2.0 over two transports.
- **Adoption**: 13,000+ community servers, 97M+ SDK downloads. First-class in Claude, Cursor, VS Code, Kiro, Hermes, OpenClaw, Cline, Gemma 4, DeepSeek V4.
- **Transports**: `stdio` (local subprocess — max security, default) and **Streamable HTTP** (remote, replaces deprecated SSE).
- **Primitives exposed by a server**: `tools` (callable functions), `resources` (read-only context: files/schemas/configs), `prompts` (reusable templates).

## 5 Key MCP Servers
1. **`@modelcontextprotocol/server-filesystem`** — sandboxed FS read/write. Path arg = hard access boundary.
2. **`@modelcontextprotocol/server-github`** — issues, PRs, repo search. Use `tools.include` to block writes.
4. **`@anthropic/mcp-server-brave-search`** — web search via Brave API; env `BRAVE_API_KEY`.
5. **`mcp-server-sqlite`** (uvx) — local DB read via `read_query` / `list_tables`.
6. **`chrome-devtools-mcp`** — browser automation via CDP. Pitfall: `--autoConnect` times out with many background tabs — close them first.

## Hermes Integration
- Config: `~/.hermes/config.yaml` → `mcp_servers:` block. Install: `uv pip install -e ".[mcp]"` (already bundled with `[all]`).
- Each server entry: `command`, `args`, `env`, `timeout` (default 120s), `connect_timeout` (60s), optional `tools.include` allowlist.
- Runntime: `hermes chat` discovers tools at startup; `/reload-mcp` after config edits; `tools` filter must be reloaded per gateway session (Telegram/Discord).

## Security Checklist (must-pass before production)
- [ ] `tools.include` allowlist — never expose full server surface to the agent
- [ ] Secrets in `.env` / profile env, **never** in prompts or committed config
- [ ] FS server: path arg is the trust boundary — keep it narrow
- [ ] Audit tool names for `delete` / `execute` / `publish` / `transfer` / `send`
- [ ] Stale gateway processes = missing tools after config change — restart, don't just edit
- [ ] WSL: start Hermes from `/home/...` not `/mnt/c/Users/...` when bridging to Windows stdio

## Use MCP vs Native vs Direct API
- **MCP**: existing server, multi-agent shared bridge, broad ecosystem tool
- **Native Hermes tool**: first-class integration already exists (web_search, terminal, browser, etc.)
- **Direct API**: tight auth/scope control, predictable schema, single-narrow integration