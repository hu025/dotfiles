---
name: mcp-integration
description: MCP (Model Context Protocol) 2026 status, 500+ servers, ecosystem registry, and Hermes integration patterns. Use when wiring external tools into Hermes via MCP stdio/HTTP transports.
---

# MCP Integration for Hermes (2026)

## Protocol Status (Nov 2025 spec, current 2026)
- **Spec**: 2025-11-25, donated to **Linux Foundation** Dec 2025. JSON-RPC 2.0 over two transports.
- **Adoption**: 13,000+ community servers, 97M+ SDK downloads. First-class in Claude, Cursor, VS Code, Kiro, Hermes, OpenClaw, Cline, Gemma 4, DeepSeek V4.
- **Transports**: `stdio` (local subprocess — max security, default) and **Streamable HTTP** (remote, replaces deprecated SSE).
  - ⚠️ **2026-07-28 spec revision**: Streamable HTTP改为纯stateless，移除了protocol-level sessions。
- **Primitives exposed by a server**: `tools` (callable functions), `resources` (read-only context: files/schemas/configs), `prompts` (reusable templates).

## Official Registry & Top Servers
- **MCPfinder** (mcp-finder/best-mcp-servers-2026): 500+ servers tracked, reliability评分
- **OpenModels** (openmodelsrun/mcp): 208 servers, 结构化YAML元数据

## 5 Key MCP Servers (updated 2026-09)
1. **`@modelcontextprotocol/server-filesystem`** — sandboxed FS read/write. Path arg = hard access boundary.
2. **`@modelcontextprotocol/server-github`** — issues, PRs, repo search. Use `tools.include` to block writes.
3. **`@brave/brave-search-mcp-server`** (官方) — ✅ Brave Search已迁移，2,000次/月免费，env `BRAVE_API_KEY`。原`@anthropic/mcp-server-brave-search`已废弃。
4. **`mcp-server-sqlite`** (uvx) — local DB read via `read_query` / `list_tables`.
5. **`chrome-devtools-mcp`** — browser automation via CDP. Pitfall: `--autoConnect` times out with many background tabs — close them first.
6. **`@modelcontextprotocol/server-memory`** — 图结构本地优先记忆层，官方维护。

## 高价值新增服务器 (2026)
| 服务器 | 用途 | 备注 |
|--------|------|------|
| kubernetes (Flux159/mcp-server-kubernetes) | K8s集群管理 | pod/deploy/svc操作 |
| firecrawl | 网页抓取转markdown | 比fetch更强 |
| figma | Figma设计文件读取 | |
| postgres (官方) | 数据库读写 | 默认只读 |
| fetch | 通用HTTP请求 | |
| aws-mcp | AWS Bedrock知识检索 | |

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