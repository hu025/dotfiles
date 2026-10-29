---
name: voltagent
description: VoltAgent — TypeScript AI Agent Framework with built-in observability (10k+ stars). 触发词：VoltAgent/TypeScript agent框架/内置观测台
triggers: [voltagent, typescript agent framework, built-in observability, voltops]
version: 2026-09-18
category: research
tags: [agent-framework, typescript, mcp, observability, production]
author: self-evolution
sources:
  - https://github.com/VoltAgent/voltagent
  - https://runany.dev/blog/voltagent-typescript-ai-agent-framework/
---

# VoltAgent — TypeScript AI Agent Framework

## 核心定位

**VoltAgent** 是开源 TypeScript Agent 工程平台，由开源框架 + VoltOps Console 两部分组成。10.6k GitHub stars，活跃开发（最新 2026-08-27，708 releases）。

> "Next.js + Datadog + LangChain — for AI agents"

## 关键特性

### 1. 内置观测台 VoltOps Console
- 内嵌 tracing/eval/guardrail/prompt 管理，无需 LangSmith/Datadog
- 支持 cloud 和 self-hosted 部署模式
- 对 Hermes 参考价值：**内嵌观测台设计**可作为 Hermes skill 自检系统参考

### 2. Zod typed tools
- 工具定义用 Zod schema 类型校验，编译时即捕获错误
- 工具注册到 Tool Registry，支持 lifecycle hooks + cancellation
- 对 Hermes 参考价值：Hermes skill 参数校验可借鉴 Zod schema 模式

### 3. Supervisors & Sub-Agents 模式
- Supervisor runtime 协调多个专业 sub-agent
- 任务路由 + 状态同步，类似 CrewAI 的 Crew 但 TypeScript 实现
- 支持 A2A 协议（Agent-to-Agent）

### 4. Workflow Engine（可暂停/恢复）
- Human-in-the-loop：suspend/resume 能力
- expense approval 等真实场景：外部审批后从断点恢复
- 对 Hermes 参考价值：Hermes cron 任务中断恢复机制可参考此模式

### 5. Guardrails 运行时拦截
- 输入/输出拦截，在数据到达 LLM 前执行内容策略
- 对 Hermes 参考价值：skill 安全检查机制

### 6. Memory + RAG
- LibSQL adapter（SQLite 后端），可插拔到 PostgreSQL/MySQL
- VoltAgent Knowledge Base：文档摄取 + chunk + embeddings + search
- 对 Hermes 参考价值：**fact_store + memory 双层架构**与 VoltAgent memory 设计一致

### 7. Voice 支持
- TTS/STT via OpenAI, ElevenLabs 或自定义 provider
- 对 Hermes 参考价值：已有 edge-tts，可借鉴集成模式

### 8. MCP 集成
- `@voltagent/mcp-docs-server`：让 AI coding assistant 直接学会用 VoltAgent
- 对 Hermes 参考价值：**MCP server 暴露 skill 文档**的思路值得借鉴

### 9. 多语言 SDK
- `@voltagent/core` — 核心 runtime
- `@voltagent/libsql` — LibSQL memory adapter
- `@voltagent/logger` — Pino logger 集成
- `@voltagent/mcp-docs-server` — 文档 MCP server

## Quick Start

```bash
npm create voltagent-app@latest
cd my-agent
npm run dev
# 访问 VoltOps Console
```

```typescript
import { VoltAgent, Agent, Memory } from "@voltagent/core";
import { LibSQLMemoryAdapter } from "@voltagent/libsql";
import { openai } from "@ai-sdk/openai";

const memory = new Memory({
  storage: new LibSQLMemoryAdapter({ url: "file:./.voltagent/memory.db" }),
});

const agent = new Agent({
  name: "my-agent",
  instructions: "A helpful assistant for various tasks",
  model: openai("gpt-4o-mini"),
  tools: [weatherTool],
  memory,
});

new VoltAgent({
  agents: { agent },
  workflows: { expenseApprovalWorkflow },
}).start();
```

## 架构亮点

### Agent Loop Tracing
每个决策默认 trace，通过 Hook 拦截任意步骤做日志/验证/重定向。

### Guardrail 示例
```typescript
// 拦截写入操作
const readOnlyGuard = (event: BeforeToolCallEvent) => {
  const writeOps = ["INSERT", "UPDATE", "DELETE", "DROP"];
  if (writeOps.some(op => event.tool.name.includes(op))) {
    throw new Error("Write operations blocked by guard");
  }
};
```

## Hermes 可借鉴点

1. **VoltOps 内嵌观测台理念** → 自建 Hermes skill 自检 dashboard
2. **Zod typed tools** → Hermes skill 参数 schema 校验
3. **suspend/resume workflow** → Hermes cron 断点恢复
4. **MCP docs server** → Hermes skill 文档暴露给 coding agent

## License
MIT

## 与现有框架对比

| 特性 | VoltAgent | Mastra | CrewAI |
|------|-----------|--------|--------|
| 语言 | TypeScript | TypeScript | Python |
| 内置观测台 | ✅ VoltOps | ❌ | ❌ |
| Zod typed tools | ✅ | ❌ | ❌ |
| Supervisor 模式 | ✅ | ❌ | ✅ |
| RAG 内置 | ✅ | ✅ | ❌ |
| License | MIT | proprietary | Apache 2.0 |
