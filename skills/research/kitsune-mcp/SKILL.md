---
name: kitsune-mcp
description: Runtime MCP proxy hub — shapeshift() into 130K+ MCP servers at runtime
triggers: [MCP dynamic loading, MCP registry search, MCP tool discovery, runtime MCP]
owner: self-evolution
created: 2026-09-27
tags: [MCP, runtime-proxy, tool-discovery, hermes-enhancement]
status: active
sources:
  - https://github.com/kaiser-data/kitsune-mcp
  - https://pypi.org/project/kitsune-mcp
  - https://smithery.ai/server/@kaiser-data/kitsune-mcp
---

# Kitsune MCP — Runtime MCP Proxy Hub

## 核心概念

Kitsune 是**运行时 MCP 代理网关**：一个永远在线的单一入口，让 agent 在会话中动态借取任意 MCP 工具。

```
search → shapeshift → call → shapeshift()   # reach, use, release
connect → shapeshift → edit → reload → call  # MCP REPL 开发模式
```

**关键创新**：会话不断开，工具按需挂载/卸载，不编辑配置文件，不重启客户端。

## 核心 API

| 函数 | 作用 |
|------|------|
| `search(query, registry?)` | 跨 7 个注册中心搜索 MCP 服务器 |
| `shapeshift(server_id, tools?, confirm?, sandbox?)` | 挂载服务器工具到当前会话 |
| `shapeshift()` | 卸载所有工具，回归基线 |
| `call(tool_name, arguments)` | 调用已挂载的工具 |
| `auto(task, server_hint?)` | 一句话模式：自动发现+调用 |
| `auth(api_key_name, token)` | 会话中动态注入凭证 |
| `connect(cmd, name?)` | 启动本地 MCP 服务器进程 |
| `reload(name)` | 热重载：杀进程→重启→重新挂载，一句话完成 |
| `release(name)` | 释放服务器连接 |

## 7 个注册数据源

1. npm
2. PyPI
3. Smithery (HTTP，需要 SMITHERY_API_KEY)
4. Official MCP Registry
5. GitHub
6. Glama
7. 自定义

## Hermes 集成价值

### 当前 Hermes 痛点
- MCP 服务器需配置在 `config.yaml`，修改需重启
- 无法动态加载临时/一次性工具
- 130K+ MCP 生态利用率极低

### Kitsune 解决方案
```json
// config.yaml 添加一次
{
  "mcpServers": {
    "kitsune": { "command": "kitsune-mcp" }
  }
}
```
之后：
```
# 一次性使用 firecrawl（无需预装）
shapeshift("firecrawl", tools=["scrape_url"])
call("scrape_url", arguments={"url": "https://example.com"})
shapeshift()  // 释放

# 开发自己的 MCP 时热重载
connect("uvx --from . my-mcp-server", name="dev")
shapeshift("dev")
# ... 编辑代码 ...
reload("dev")  # 一句话热重载
```

### Token 开销
- 9 个基线工具，~1,774 tokens/turn
- `KITSUNE_TOOLS=all` 才增加更多工具

## 安全模型

| 特性 | 说明 |
|------|------|
| Docker cage | npm/PyPI 服务器默认在沙箱中运行 |
| TOFU pins | 首次连接后固定服务器指纹 |
| confirm 模式 | 挂载前显示工具列表，用户确认 |
| untrusted local | `connect()` 本地目标始终需 confirm |

## 安装要求

- Python 3.12+
- `node`/`npx`（npm 服务器支持）
- `uvx` from uv（PyPI 服务器支持）
- Docker（可选，沙箱模式）

## 落地计划

1. **Hermes MCP 配置**：在 Hermes config.yaml 添加 Kitsune 作为唯一 MCP 入口
2. **动态工具加载**：cron 任务中用 Kitsune 加载临时工具（如 ETF 数据、新闻爬取）
3. **MCP REPL 模式**：开发新 MCP 工具时热重载开发流程
4. **Smithery API Key**：申请免费 Key 访问 HTTP 托管服务器

## 替代方案对比

| 方案 | Token 开销 | 灵活性 | 复杂度 |
|------|-----------|--------|--------|
| Native MCP (always-on) | 0 | 低 | 低 |
| Kitsune (基线) | ~1,774/turn | 极高 | 中 |
| FastMCP Proxy | 0 | 中 | 中 |

**结论**：Hermes 保留核心 always-on MCP 服务器（如 etf_monitor），用 Kitsune 处理一次性/长尾工具需求。

## 引用

- PyPI: https://pypi.org/project/kitsune-mcp
- GitHub: https://github.com/kaiser-data/kitsune-mcp
- Smithery: https://smithery.ai/server/@kaiser-data/kitsune-mcp
