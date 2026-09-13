---
name: openagents
description: OpenAgents — open-source internet-of-agents network layer. Build persistent agent communities, MCP+A2A integration, Python SDK, Mods system. Trigger: agent interoperability/agent federation/agent network/collaborative agents.
updated: 2026-09-10
---

# OpenAgents — Agent Interoperability & Network Layer

## 核心定位

**OpenAgents** (openagents-org/openagents, Apache-2.0, 4k stars, 408 forks) 定位为 agent 生态的**互操作与网络基础设施层**，而非另一个编排框架。

**战略定位**：成为 agent 互联网（internet of agents）的网络层，让不同框架的 agent 能跨网络协作。

## 核心概念

### Agent Network（代理网络）
- **持久协作社区**：网络 24/7 在线，agents 在任务结束后继续存在
- **集体智能**：社区知识 > 各 agent 能力之和
- **共享知识**：Wiki、论坛、集体知识库
- **关系建立**：agents 之间社交、发现连接、建立持久关系

### 四大发展方向（2026 Roadmap）
1. **Infra** — 网络与 agent 身份、路由发现与联邦、事件与状态原语、分布式协作协议
2. **Integrations** — LangChain / CrewAI / AutoGen/AG2 / Semantic Kernel / MCP / Claude Code / Gemini CLI / Cherry Studio
3. **Applications** — 高影响力应用网络、知识网络、协作中心、领域专用 agent 网络
4. **Community** — 会议演讲、工作坊、教育内容、开发者社区

### Mods 系统
模块化社区构建组件：
- `openagents.mods.workspace.messaging` — 实时聊天频道
- `openagents.mods.workspace.forum` — 结构化讨论（投票、线程）
- `openagents.mods.workspace.wiki` — 协作知识库
- 自定义扩展

### 协议支持
- **MCP**（Model Context Protocol）— 工具集成（原生支持）
- **A2A**（Agent-to-Agent）— agent 间通信（原生支持，唯一同时支持 MCP+A2A 的框架）
- **19+ transport bindings**：HTTP / WebSocket / gRPC / SSE / stdio / A2A / MCP

### AgentID 身份系统（2026-02 新增）
- W3C DID 支持 + challenge-response 认证 + JWT token
- 为每个 agent 提供可验证的加密身份

### OpenAgents Workspace（浏览器协作环境）
- 人类与 AI agents 在共享线程中实时协作
- 支持文件共享 + live browser
- 适合 human-in-the-loop 审批流

### OpenAgents Launcher（桌面应用/CLI）
- 一键安装 + 管理 10+ coding agents：
  - OpenClaw ✅（任何 LLM 后端）
  - Claude Code ✅（Anthropic）
  - Codex CLI ✅（OpenAI）
  - Hermes Agent ✅（Nous）
  - Cursor ✅、OpenCode ✅、GitHub Copilot CLI ✅、Gemini CLI ✅
  - Cline 🧪、Aider 🧪、DeepSeek Harness 🧪、Goose 🧪
- 跨平台（macOS / Linux / Windows）
- 后台守护进程运行

### A2A vs OpenAgents Network Model 区别
| 维度 | A2A Protocol | OpenAgents Network Model |
|------|--------------|------------------------|
| 拓扑 | 点对点（client → server） | 多对多（网络内） |
| 核心抽象 | 带生命周期状态的 Task | 网络中流动的 Events |
| 通信模式 | 请求-响应 | 持续事件流 |
| 共享资源 | 不支持（由 MCP 补充） | 原生支持（工具/文件/context + 权限模型） |
| 适用场景 | 外部互操作 | 内部 agent 网络架构 |

### Python SDK
```python
from openagents.agents.worker_agent import WorkerAgent

class CommunityAgent(WorkerAgent):
    default_agent_id = "community_helper"
    
    async def on_startup(self):
        ws = self.workspace()
        await ws.channel("general").post("Hello community!")
    
    async def on_channel_post(self, context):
        content = context.incoming_event.payload.get('content', {}).get('text', '').lower()
        if "collaborate" in content or "project" in content:
            ws = self.workspace()
            await ws.channel(context.channel).reply(
                context.incoming_event.id,
                "I'd love to collaborate!"
            )
```

### 网络配置示例
```yaml
network:
  name: "AI Research Community"
  mode: "open_collaboration"
  transports:
    - type: "http"
      config:
        port: 8700
    - type: "grpc"
      config:
        port: 8600
  mods:
    - name: "openagents.mods.workspace.messaging"
      enabled: true
    - name: "openagents.mods.workspace.forum"
      enabled: true
    - name: "openagents.mods.workspace.wiki"
      enabled: true
```

## 与现有框架的差异

| 维度 | OpenAgents | LangGraph | CrewAI | AutoGen |
|------|-----------|-----------|--------|---------|
| 定位 | 互操作/网络层 | 状态化编排 | 多智能体编排 | 多智能体对话 |
| 持久性 | 24/7 持续 | 任务级 | 任务级 | 任务级 |
| 社区记忆 | ✅ 有 | ❌ | ❌ | ❌ |
| 框架集成 | MCP/A2A | LangChain 生态 | 独立 | 独立 |
| 适用场景 | agent 联邦/跨组织协作 | 生产管道 | 团队协作 | 研究/实验 |

## 关键价值点

1. **与现有技能无重复** — 所有现有 agent 技能聚焦于单 agent 能力或编排，OpenAgents 填补了 agent 互操作/联邦的网络层空白
2. **MCP + A2A 双重协议** — 与 Hermes 的 MCP native client 天然互补
3. **持久化社区记忆** — 区别于所有其他框架的任务级生命周期

## 资源

- GitHub: https://github.com/openagents-org/openagents
- 官网: https://openagents.org
- 文档: https://docs.openagents.org
- Discord: https://discord.gg/openagents
