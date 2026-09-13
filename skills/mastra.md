---
name: mastra
description: TypeScript agent框架。Harness交互+Observ Memory+40+模型路由。TS首选。
triggers:
  - Mastra TypeScript agent framework
  - Mastra harness session modes
  - Mastra observational memory
  - TypeScript multi-agent framework
category: agent-engineering
---

# Mastra — TypeScript AI Agent Framework

## 核心定位

Mastra 是 TypeScript 原生的 AI 应用 + agent 框架（Apache 2.0 核心），由 Gatsby 团队构建。

**数据**: ~23K GitHub stars，~300K+ 每周 npm 下载（2026 Q2）

## 核心创新

### 1. Mastra v1.0 GA（2026-01 里程碑）
- **生产用户**：Replit、PayPal、Sanity、SoftBank、Brex
- **资金**：$13M seed（Y Combinator W25，Paul Graham 投资）
- **npm**：300K+ 每周下载，21K+ GitHub stars

### 2. Mastra Harness — 交互式 Agent 循环

Harness 是 agent 循环的外层封装：

- **多模式（Modes）**: plan/execute 等多个 agent 模式，同一会话内切换，prompt cache 复用
- **持久化 Session**: `threadId` 持久化存储，不怕崩溃/重启
- **Tool Approval 跨会话**: 单次批准后同类工具不再询问，按类别授权
- **YOLO 模式**: 全工具自动执行，或 `deny` 单工具黑名单
- **Subagent**: `isolated`（无父 context）和 `forked`（warm cache）两种模式
- **Event Stream**: 35 种信号折叠为 `HarnessDisplayState`，可用于 TUI/网页/移动端
- **Ask User**: agent 主动暂停等待用户输入

```typescript
import { Harness } from "@mastra/core/harness";
import { Agent } from "@mastra/core/agent";

const harness = new Harness({
  id: "my-harness",
  modes: [
    { id: "plan", name: "Plan", agent: planAgent, transitionsTo: "execute" },
    { id: "execute", name: "Execute", agent: executeAgent },
  ],
});

harness.subscribe((event) => {
  if (event.type === "display_state_changed") {
    console.log(event.state.isRunning, event.state.tasks);
  }
});
await harness.selectOrCreateThread();
await harness.sendMessage({ content: "Build a REST API" });
```

### 2. Observational Memory — 文本无向量 DB

用结构化 observations 替代向量/图数据库：

- **格式**: 三时间戳日志 + emoji 优先级（🔴重要/🟡待定/🟢信息）
- **工作流**: messages → 30k token → observer agent → observations → reflector agent GC
- **Prompt Cache**: observation 前缀稳定，messages 追加，**全 cache 命中**
- **Benchmark**: ~95% on LongMemEval，无需外部向量库

```text
Date: 2026-01-15
- 🔴 12:10 User building Next.js app with Supabase auth, due Jan 22
  - 🟡 12:12 User asked about middleware for protected routes
```

### 3. 模型路由 — 40+ Provider

```typescript
// provider/model 格式，环境变量自动映射
const agent = new Agent({ model: "openai/gpt-4o" });
```

### 4. 工作流引擎 + MCP

```typescript
pipe.then().branch().parallel()  // 顺序/分支/并行
// Human-in-the-loop: workflow.suspend() 等待批准
// MCP server 创作：暴露 agents/tools 为 MCP 接口
```

## 关键对比

| 特性 | Mastra | LangGraph | CrewAI |
|------|--------|-----------|--------|
| 语言 | TypeScript | Python | Python |
| Memory | Observational (文本) | 需自行接入 | 需自行接入 |
| Harness 封装 | ✅ 原生 | ❌ | ❌ |
| 模型路由 | 40+ provider | via LC | via LC |
| MCP 创作 | ✅ 原生 | adapter | native |
| 学习曲线 | 低 | 高 | 中 |

## 安装

```bash
npm create mastra@latest my-agent -- --llm anthropic
cd my-agent && npx bgproc start -n my-agent -w -- npm run dev
# http://localhost:4111 (Mastra Studio)
```

## 新发现落地

- **Harness 模式**: 适合 Hermes 未来实现"人类监督的长时间自主 agent"
- **Observational Memory**: 三时间戳+emoji 格式可迁移到 Hermes 记忆系统
- **TypeScript 生态**: Hermes 技能库首个 TS 框架

## 来源

- https://mastra.ai/
- https://mastra.ai/blog/announcing-agent-harness
- https://mastra.ai/blog/observational-memory
- https://github.com/Mastra-AI/Mastra
