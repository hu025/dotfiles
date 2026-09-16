---
name: a2a-protocol
description: A2A (Agent-to-Agent) 协议 — 多主体协作互操作标准。触发词：agent间通信/跨框架协作/A2A/多主体委派/Hermes subagent扩展。
updated: 2026-09-17
---

# A2A Protocol — Agent 互操作标准

## 核心定位

**A2A (Agent2Agent Protocol)** — 填补 MCP（agent→工具）的空白——让异构 agent 之间相互发现、委派任务、交换结果。

```
协议层级对比:
  MCP  → agent→工具  (工具调用，stateless/单主体)
  A2A  → agent→agent (任务委派，stateful，多主体协作)
  MPAC → 跨信任边界多主体协调 (补充场景)
```

**关键区分**: A2A 不替代 MCP，两者互补：
- agent 对外使用 A2A 协调多个 agent
- agent 对内使用 MCP 调用具体工具（数据库/API/文件系统）
- 协调者只需知道 sub-agent 的 A2A Agent Card，不需要知道其内部工具实现

---

## 协议规格 (A2A v1.0, 2026)

### 架构原则
- JSON-RPC 2.0 over HTTP(S)（主绑定）+ gRPC + SSE streaming
- 每个长期交互 = **Task**，有显式状态机
- 签名 Agent Card 防篡改（JWS + RFC 8785 JCS）
- Linux Foundation Agentic AI Foundation 主持（2026年加入）

### 核心数据模型
| 概念 | 作用 |
|---|---|
| **AgentCard** | 发现信息：name/version/capabilities/endpoints/skills[] |
| **Task** | 长期交互单元，有完整状态机 |
| **Message** | Part 的容器，支持多模态 |
| **Part** | 原子内容单元（text/file/structured JSON） |
| **Artifact** | Task 的最终产出 |

### Task 状态机
```
SUBMITTED → WORKING → COMPLETED / FAILED / CANCELED / REJECTED / INPUT_REQUIRED / AUTH_REQUIRED
```

### 核心方法
- `tasks/send` — 同步发送消息
- `tasks/sendSubscribe` — SSE 流式订阅任务进度
- `tasks/get` — 轮询任务状态（异步恢复）
- `tasks/list` — 列出任务
- `tasks/cancel` — 取消任务
- `tasks/pushNotification` — Webhook 推送通知配置

### AgentCard 示例
```json
{
  "name": "code-review-agent",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "extendedAgentCard": false
  },
  "skills": [
    {
      "id": "code-review",
      "name": "Code Review",
      "description": "Performs security and quality code review",
      "tags": ["security", "quality"],
      "inputModes": ["text"],
      "outputModes": ["text", "json"]
    }
  ],
  "security": {
    "schemes": ["oauth2", "apiKey"]
  }
}
```

---

## ACP 合并 (重要历史)

2025年8月，IBM Research 的 **ACP (Agent Communication Protocol)** 并入 A2A：
- ACP 的核心特性（Task 持久化、异步恢复、webhook 进度推送）成为 A2A v1.0 标准
- BeeAI 用户通过官方迁移指南迁移到 A2AServer/A2AAgent 适配器

---

## 与 MCP 的深度对比

| 维度 | MCP | A2A |
|---|---|---|
| **核心目的** | model→工具/数据源 | agent↔agent 协作 |
| **状态模型** | session-stateful (initialize handshake) | task-stateful (SUBMITTED→WORKING→...) |
| **发现机制** | 动态 in-session (tools/list) | 静态 well-known URI + AgentCard |
| **典型场景** | agent 调用 GitHub API / SQL DB | orchestrator 委派给 specialist agent |
| **实现复杂度** | 较低（4个协调抽象，2个阶段/交互） | 较高（10个协调抽象，6个阶段/交互） |
| **多轮对话** | 不原生支持（需应用层实现） | 原生支持（Task 状态机） |
| **治理** | 部分（MCP Auth spec） | AgentCard.securitySchemes |

**经验数据** (arXiv 2607.23884):
- MCP: 2协调阶段/交互，4个协调原语
- A2A: 6协调阶段/交互，10个协调原语
- A2A 更适合长期、复杂、多轮协作；MCP 更适合轻量、标准化工具调用

---

## 治理缺口 (重要研究)

arXiv 2606.31498 识别了 A2A/MCP/ACP/ANP/ERC-8004 的治理缺口：

| 维度 | A2A 状态 |
|---|---|
| 成员管理 | Partial（AgentCard 能力声明） |
| 协商/辩论 | **Absent** |
| 投票 | **Absent**（所有协议均无） |
| 异议保留 | **Absent**（所有协议均无） |
| 人类升级 | **Absent** |
| 审计/回放 | Partial（依赖底层传输） |

> **设计哲学**: 当前协议将 agent 视为"任务执行者"而非"社区参与者"。治理是缺失的架构层，而非缺失的功能。

---

## Hermes 集成

### 当前状态
- Hermes subagent (`delegate_task`) 是内存级协作，不走 A2A
- `native-mcp` 技能覆盖 agent→工具场景
- 尚无 A2A 原生支持

### 落地建议
```
短期（1-3月）:
  - 了解 A2A 协议规范，作为Hermes未来扩展的理论基础
  - 若需多Hermes实例协作，评估 A2A server 实现

中期（3-6月）:
  - 监控 hermes-agent A2A 插件生态
  - 参考 A2A Task 状态机改进 Hermes 任务生命周期设计

不推荐现在落地:
  - Hermes subagent 是进程内协作，A2A 是网络协议
  - 引入 A2A 需要每个 agent 有独立进程+持久化存储
  - 当前 Hermes 架构不匹配 A2A 的 client-server 模型
```

---

## 来源

- https://a2a-protocol.org/latest/ — 官方文档
- https://github.com/google/A2A — 23k stars，5个语言SDK
- https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/ — MCP vs A2A vs ACP 完整对比
- https://arxiv.org/html/2607.23884 — A2A vs MCP 实证工程对比
- https://arxiv.org/pdf/2606.31498 — 协议治理缺口分析
- https://architecture.learning.sap.com/docs/ref-arch/76ec36 — SAP A2A+MCP 企业落地
