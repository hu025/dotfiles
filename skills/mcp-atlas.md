---
name: mcp-atlas
description: MCP 2026-07-28 无状态革命 + A2A v1.0 + AAIF 统一栈。触发词：MCP无状态/MCP Atlas/MRTR/Tasks扩展/MCP Apps
triggers:
  - MCP 2026-07-28
  - MCP stateless
  - MCP MRTR
  - MCP Tasks extension
  - MCP Apps
  - MCP authorization hardening
  - A2A v1.0
  - Agentic AI Foundation
---

# MCP Atlas — 2026-07-28 无状态革命 + A2A v1.0 + AAIF

> 2026年7月28日，MCP 发布史上最大版本升级：无状态协议核心 + MRTR + Tasks扩展 + MCP Apps。A2A v1.0 同月迁入 Agentic AI Foundation，与 MCP 正式共处一檐。

---

## 一、MCP 2026-07-28 核心变化：无状态革命

### 1.1 移除握手与会话

**旧协议痛点**：MCP 脱胎于 STDIO 本地传输，远程服务器沿用了双向有状态连接模型——需要 `initialize`/`initialized` 握手 + `Mcp-Session-Id` 头维持会话。这导致：
- 必须 sticky routing 或 Redis session store 才能水平扩展
- serverless (Lambda/Cloudflare Workers) 部署困难
- 容器重启会断会话，透明 failover 几乎不可能

**新协议（SEP-2575/SEP-2567）**：
- `initialize`/`initialized` 握手正式移除
- `Mcp-Session-Id` 头移除
- 每个请求自带 `_meta` 字段，携带协议版本、客户端信息、客户端能力
- `server/discover` RPC 可选调用（客户端想预先了解服务器能力时用）
- **任何请求可落在任何服务器实例上**，普通 round-robin 负载均衡即可

```http
POST /mcp HTTP/1.1
Mcp-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: search
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": { "q": "otters" },
    "_meta": {
      "io.modelcontextprotocol/clientInfo": { "name": "my-app", "version": "1.0" }
    }
  }
}
```

### 1.2 MRTR — Multi Round-Trip Requests（SEP-2322）

**解决的问题**：旧版 elicitation（工具向用户请求确认）、sampling（向 LLM 请求补全）、roots 查询都需要保持双向流连接。

**新方案**：
- 服务器返回 `resultType: "input_required"` + `inputRequests`（含 `requestState` 不透明令牌）
- 客户端向用户收集答案，重新发送原调用（带 `inputResponses` + `requestState`）
- `requestState` 携带完整上下文，**任何服务器实例都能接续处理**——无状态 + 无需保持连接
- 适用场景：工具执行前的确认（如"确认删除此数据？"）、缺失参数请求

### 1.3 HTTP 头路由（SEP-2243）

**Streamable HTTP 请求现在必须携带**：
- `Mcp-Method`：JSON-RPC 方法名（如 `tools/call`）
- `Mcp-Name`：具体工具/提示/资源名
- `Mcp-Protocol-Version`：协议版本

**意义**：网关/WAF/限流器可基于 HTTP 头做路由和计量，无需解析 JSON body。这使 MCP 真正成为普通 HTTP workload。

### 1.4 缓存增强（SEP-2549）

`tools/list`、`prompts/list`、`resources/list`、`resources/read` 的响应现在携带：
- `ttlMs`：毫秒级新鲜度提示
- `cacheScope`：是否可跨用户共享缓存

工具目录现在是确定性顺序，客户端可复用 prompt cache。

### 1.5 W3C Trace Context（SEP-414）

`_meta` 中固定了 `traceparent`、`tracestate`、`baggage` 键名。跨 SDK 和网关的分布式追踪可汇成单一 span 树（OpenTelemetry 兼容）。

---

## 二、Tasks 扩展（SEP-2663）：异步长任务

**背景**：实验性 Tasks API 重新设计后成为官方扩展。

**新模型**：
- 服务器对 `tools/call` 返回 `taskId`，后台开始执行
- 客户端通过 `tasks/get`、`tasks/update`、`tasks/cancel` 驱动生命周期
- 任务创建由服务器驱动，客户端只是 polling/subscribing

**关键改进**：`tasks/list` 被移除（无 session 后无法安全限定作用域）。

---

## 三、MCP Apps 扩展（SEP-1865）

服务器可发送交互式 HTML 界面，由 host 在沙箱 iframe 中渲染。工具提前声明 UI 模板，host 可预取/缓存/安全审查。UI 通过同一 JSON-RPC 协议与 host 通信，所有操作走相同的审计和同意路径。

---

## 四、授权硬化（6个SEP）

| 变化 | 内容 |
|------|------|
| SEP-2468 | 授权服务器必须在响应中返回 `iss` 参数（RFC 9207），客户端必须校验 |
| SEP-837 | 客户端在 DCR 时声明 `application_type`，解决 CLI 桌面客户端 `redirect_uri` 被拒的问题 |
| SEP-2352 | 凭证绑定到签发授权服务器，不可跨服务器重用 |
| SEP-2207 | 文档化如何从 OpenID Connect 风格授权服务器请求 refresh token |
| DCR → CIMD | 动态客户端注册正式废弃，推崇 Client ID Metadata Documents |
| Resource Indicators | RFC 8707，客户端明确指定令牌针对哪个 MCP 服务器，解决"混乱代理"问题 |

---

## 五、正式弃用（12个月窗口）

| 特性 | 替换方案 |
|------|----------|
| Roots | 工具参数、资源 URI、服务器配置 |
| Sampling | 直接调用 LLM provider API |
| Logging | stdio 用 `stderr`；云端用 OpenTelemetry |
| HTTP+SSE 传输 | Streamable HTTP |
| `ping`、`logging/setLevel` | 移除 |
| 错误码 `-32002` | 改为 `-32602` |

---

## 六、生态落地

### 6.1 SDK 全面支持
- **TypeScript、Python、Go、C#** 四大 Tier-1 SDK 全部支持 2026-07-28
- **FastMCP 4.0**：背景任务、无状态交互、企业认证全面支持
- GitHub MCP Server 已完全移除 Redis session 存储
- Cloudflare Workers / AWS Lambda / Cloudflare R2 等 serverless 成为一等公民

### 6.2 AWS Well-Architected 路径
- 旧协议需要 sticky sessions 或 DynamoDB/ElastiCache 做 session store
- 新协议无需这些补偿基础设施
- AWS Bedrock AgentCore Gateway 已支持并处理向后兼容

### 6.3 Cloudflare Workers 原生支持
- `createMcpHandler` API 支持 2026-07-28
- Workers OAuth Provider 实现所有 MCP 授权要求
- MCP 不再需要 Durable Object 来跑协议

### 6.4 真实数据
- MCP 每月 SDK 下载量接近 **5亿次**
- TypeScript 和 Python SDK 双双突破 **10亿次**累计下载
- OpenAI 已在 2026 年初弃用 Assistants API，全面转向 MCP
- Wiz 扫描：80% 云环境有 MCP，其中约 1/6 暴露至少一台 MCP 服务器

---

## 七、A2A v1.0 + Agentic AI Foundation

### 7.1 A2A 核心定位
- **A2A = agent-to-agent**：发现 → 委托 → 协作，跨厂商边界
- **MCP = agent-to-tool**：工具调用（USB-C）
- **两者组合，不可替代**

### 7.2 A2A v1.0（2026年3月GA）新增特性
- **多租户**：一个 A2A 服务安全服务多个隔离租户
- **版本协商**：协议级版本协商
- **多协议绑定**：HTTP+JSON、JSON-RPC 2.0、gRPC，带正式等价保证
- **签名 Agent Cards**：密码学验证 agent 身份
- **游标分页**：替换 offset-based 分页

### 7.3 Agentic AI Foundation（AAIF）合并
- **2026年8月17日**：A2A 从 Linux Foundation 整体迁入 AAIF
- AAIF 已托管：MCP（Athropic）+ A2A（Google）+ goose（Block）+ AGENTS.md（OpenAI）+ agentgateway
- 一个基金会统一管理"如何让 agent 用工具"和"agent 之间如何对话"

### 7.4 完整协议栈心智模型
```
AGENTS.md  →  告知 agent 如何行为
goose      →  agent 推理和规划的运行时
MCP        →  agent 连接工具和数据
A2A        →  agent 发现另一个 agent、委托任务、获取结果
agentgateway →  边界处理路由、认证授权、限流遥测
```

---

## 八、落地行动建议

1. **立即**：审计现有 MCP 服务器，确认是否仍在用 2025-11-25 及更早版本
2. **短期**：升级 MCP SDK 至 2026-07-28，删除 session store/sticky routing 基础设施
3. **中期**：利用 Tasks 扩展处理长时运行任务（替代一直保持连接）
4. **长期**：探索 MCP Apps（服务器渲染 UI）和 MCP Apps 进入 Extensions framework 的路径
5. **安全**：所有远程 MCP 必须加 OAuth 2.1 + PKCE，绝不能无认证暴露在公网

---

## 九、来源

| 资源 | 链接 |
|------|------|
| MCP 2026-07-28 官方博客 | https://blog.modelcontextprotocol.io/posts/2026-07-28/ |
| MCP RC 博客 | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ |
| Google Cloud: MCP 无状态扩展 | https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/ |
| AWS: MCP Well-Architected | https://aws.amazon.com/blogs/architecture/mcp-went-stateless-is-your-aws-mcp-server-deployment-well-architected/ |
| Cloudflare: MCP v2 | https://blog.cloudflare.com/mcp-v2/ |
| MCP 官方路线图 | https://blog.modelcontextprotocol.io/posts/mcp-roadmap/ |
| AAIF 合并 MCP+A2A | https://rodtrent.substack.com/p/mcp-and-a2a-under-one-roof |
| A2A 加入 AAIF | https://ai2.work/blog/google-s-a2a-protocol-joins-the-agentic-ai-foundation-with-mcp |
| A2A v1.0 深度解析 | https://codex.danielvaughan.com/2026/04/09/a2a-meets-mcp-protocol-stack |
| MCP 架构文档 | https://modelcontextprotocol.io/docs/2026%2D07%2D28/learn/architecture |
