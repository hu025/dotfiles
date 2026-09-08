---
name: mcp-integration
description: MCP (Model Context Protocol) 2026 status, 2,500+ servers, ecosystem registry, and Hermes integration patterns. Use when wiring external tools into Hermes via MCP stdio/HTTP transports.
---

# MCP Integration for Hermes (2026)

## Protocol Status (Nov 2025 spec, current 2026)
- **Spec**: 2025-11-25, donated to **Linux Foundation** Dec 2025. JSON-RPC 2.0 over two transports.
- **Adoption**: 2,500+ community servers, 100M+ SDK downloads. First-class in Claude, Cursor, VS Code, Kiro, Hermes, OpenClaw, Cline, Gemma 4, DeepSeek V4.
- **Transports**: `stdio` (local subprocess — max security, default) and **Streamable HTTP** (remote, replaces deprecated SSE).
  - ⚠️ **2026-07-28 spec revision**: Streamable HTTP改为纯stateless，移除了protocol-level sessions。
- **Primitives exposed by a server**: `tools` (callable functions), `resources` (read-only context: files/schemas/configs), `prompts` (reusable templates).

## MCP Registry Landscape (2026-09)
| Registry | Servers | Type | Best For |
|----------|--------|------|----------|
| [Smithery](https://smithery.ai/) | 7,000+ | Marketplace (SaaS + local CLI) | Fast prototyping |
| [MCP Market](https://mcpmarket.com/) | 10,000+ | Community directory | Browsing |
| [MCP.so](https://mcp.so/) | 19,000+ | Resource hub | Research |
| [Official Registry](https://registry.modelcontextprotocol.io) | Metadata only | Metaregistry | Upstream source |
| [TrueFoundry](https://www.truefoundry.com/) | Enterprise | VPC-native gateway | Production governance |
| [Glama](https://glama.ai/) | Metadata only | Metaregistry | Managed hosting |

⚠️ **Smithery 安全漏洞 (GitGuardian Aug 2026)**: Path traversal in Docker build config → Docker credentials exfil → 3,000+ hosted服务器被入侵，fly.io tokens泄露。**避免使用Smithery SaaS托管生产服务**。改用官方 `@modelcontextprotocol/*` npm包直接npx运行。

## 5 Key MCP Servers (updated 2026-09)
1. **`@modelcontextprotocol/server-filesystem`** — sandboxed FS read/write. Path arg = hard access boundary.
2. **`@modelcontextprotocol/server-github`** — issues, PRs, repo search. Use `tools.include` to block writes.
3. **`@brave/brave-search-mcp-server`** (官方) — ✅ Brave Search已迁移，2,000次/月免费，env `BRAVE_API_KEY`。原`@anthropic/mcp-server-brave-search`已废弃。
4. **`mcp-server-sqlite`** (uvx) — local DB read via `read_query` / `list_tables`.
5. **`chrome-devtools-mcp`** — browser automation via CDP. Pitfall: `--autoConnect` times out with many background tabs — close them first.
6. **`@modelcontextprotocol/server-memory`** — 图结构本地优先记忆层，官方维护（v2026.7.4）。
   - 工具：`create_entities/create_relations/add_observations`（写）；`search_nodes/open_nodes/read_graph`（读）；`delete_*`（删）
   - 存储：`memory.jsonl`（默认），可自定义 `MEMORY_FILE_PATH`
   - MCP Resource：`memory://knowledge-graph`（JSON格式，订阅后实时推送变更）
   - ⚠️ 数据明文本地存储，跨机器不同步，敏感数据禁用

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