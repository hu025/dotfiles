# VoltAgent — TypeScript AI Agent Framework

## 基本信息
- **官网**: https://voltagent.dev
- **GitHub**: https://github.com/voltagent/voltagent
- **Stars**: 10,452 ⭐ | **Forks**: 1,108
- **许可证**: MIT
- **语言**: TypeScript (JavaScript 可选)
- **创建**: 2025-04-16
- **最新版本**: 2026 (活跃开发)

## 核心定位

VoltAgent 是一个端到端 AI Agent 工程平台，包含两个部分：
1. **开源 TypeScript 框架** — Memory, RAG, Guardrails, Tools, MCP, Voice, Workflow
2. **VoltOps Console** — 可选商业版：可观测性、部署、Evals、Guardrails（Cloud 或 Self-Hosted）

与 Hermes 的互补点：
- TypeScript 原生，Hermes 用 Python
- 内置 VoltOps 可观测平台（OpenTelemetry）
- Zod 类型化工具，编译时安全
- 多智能体 Supervisor 编排

## 核心架构

### 核心组件

```
Agent (@voltagent/core)
├── Model Providers (OpenAI/Anthropic/Google/自定义)
├── Tools (Zod 类型化，带生命周期钩子)
├── Memory (持久化记忆适配器)
├── Guardrails (输入/输出安全检查)
├── Middleware (预/后处理)
└── Supervisor (多智能体协调)

Workflow Engine
└── 声明式多步骤自动化（无需手写控制流）

MCP Integration
└── 原生 MCP Server 连接（HTTP/stdio）
```

### 核心概念速查

| 概念 | 说明 |
|------|------|
| `Agent.generateText()` | 同步文本生成 |
| `Agent.streamText()` | 流式文本生成 + fullStream 事件 |
| `Workflow` | 声明式多步骤工作流 |
| `Supervisor` | 多智能体任务路由与协调 |
| `MCPConfiguration` | MCP Server 连接管理 |
| `Guardrails` | 输入/输出验证层 |
| `VoltOps` | OpenTelemetry 可观测平台 |

## 与 Mastra 的对比

| 维度 | VoltAgent | Mastra |
|------|-----------|--------|
| Stars | 10.5K ⭐ | ~23K ⭐ |
| 许可证 | MIT | Apache-2.0 |
| 团队背景 | 独立开源 | Gatsby 团队 |
| 可观测性 | 内置 VoltOps (OpenTelemetry) | 内置 Observ Memory |
| 工具类型 | Zod 类型化，带生命周期钩子 | Pydantic 类型化 |
| Multi-Agent | Supervisor 模式 | 多种编排模式 |
| Voice | 内置 (OpenAI TTS) | 不内置 |
| RAG | 原生 RAG + VoltAgent KB | 原生支持 |
| 记忆系统 | Memory Adapters (持久化) | LongMemEval (~95% 命中) |
| 模型路由 | 40+ Provider | 40+ Provider |
| 生产部署 | VoltOps Cloud/Self-Hosted | CF Workers/GitHub Actions |

## 快速开始

```bash
npm install @voltagent/core
```

```typescript
import { Agent } from "@voltagent/core";

// 创建 Agent
const agent = new Agent({
  name: "Assistant",
  instructions: "Answer questions clearly and concisely.",
  model: "openai/gpt-4o",  // 或 "anthropic/claude-3-5-sonnet"
});

// 同步调用
const result = await agent.generateText("What is TypeScript?");
console.log(result.text);

// 流式调用（带详细事件）
const stream = await agent.streamText("Write a story");
for await (const chunk of stream.fullStream) {
  switch (chunk.type) {
    case "reasoning-start": console.log("\nReasoning started"); break;
    case "reasoning-delta": process.stdout.write(chunk.delta ?? ""); break;
    case "tool-call": console.log(`\nUsing tool: ${chunk.toolName}`); break;
    case "tool-result": console.log(`Tool completed: ${chunk.toolName}`); break;
    case "finish": console.log(`\nDone! Tokens: ${chunk.usage?.totalTokens}`); break;
  }
}
```

## MCP 集成

```typescript
import { MCPConfiguration } from "@voltagent/core";

const mcpConfig = new MCPConfiguration({
  servers: {
    myServer: {
      type: "http",
      url: "https://mcp-server.example.com",
    },
  },
});

const mcpTools = await mcpConfig.getTools();

const agent = new Agent({
  name: "Agent",
  model: "openai/gpt-4o",
  tools: mcpTools,
});
```

## 多智能体 Supervisor

```typescript
import { Agent, Supervisor } from "@voltagent/core";

const researcher = new Agent({
  name: "Researcher",
  instructions: "You research topics thoroughly.",
  model: "anthropic/claude-3-5-sonnet",
});

const writer = new Agent({
  name: "Writer",
  instructions: "You write clear summaries.",
  model: "openai/gpt-4o",
});

const supervisor = new Supervisor({
  agents: [researcher, writer],
  routingStrategy: "automatic",  // 自动路由到最适合的 Agent
});
```

## Zod 类型化工具

```typescript
import { z } from "zod";
import { tool } from "@voltagent/core";

const calculate = tool({
  name: "calculate",
  description: "Perform a calculation",
  parameters: z.object({
    expression: z.string().describe("Mathematical expression"),
  }),
  execute: async ({ expression }) => {
    // 安全计算
    const result = eval(expression);
    return { result };
  },
});

const agent = new Agent({
  name: "Math Assistant",
  model: "openai/gpt-4o",
  tools: [calculate],
});
```

## Guardrails（安全护栏）

```typescript
import { Agent, InputGuardrail, OutputGuardrail } from "@voltagent/core";
import { z } from "zod";

const profanityGuard = new InputGuardrail({
  name: "profanity",
  execute: async (input) => {
    const blocked = ["badword1", "badword2"];
    const found = blocked.filter(w => input.text.includes(w));
    return {
      pass: found.length === 0,
      blockedWords: found,
    };
  },
});

const agent = new Agent({
  name: "Assistant",
  model: "openai/gpt-4o",
  guardrails: {
    input: [profanityGuard],
  },
});
```

## VoltOps 可观测性

VoltAgent 内置 OpenTelemetry 追踪：
- 每个 Agent 决策的完整 trace
- Tool 调用次数与延迟
- Token 消耗统计
- 流式事件完整记录

```typescript
const agent = new Agent({
  name: "Assistant",
  model: "openai/gpt-4o",
  // VoltOps API keys 自动注入（环境变量）
});
```

## 适用场景

✅ **适合的场景**：
- TypeScript/JavaScript 项目需要 AI Agent 能力
- 需要编译时类型安全的 Agent 工具
- 需要内置可观测性（不想自己搭建）
- 多智能体 Supervisor 协调
- Voice Agent（OpenAI TTS 原生）
- MCP Server 连接

❌ **不适合的场景**：
- Python 项目（用 Pydantic AI / LangGraph）
- 需要深度 AWS 集成（用 Strands Agents）
- 极简需求（用 OpenAI Agents SDK）

## 与 Hermes 的互补价值

VoltAgent 的以下特性可补充 Hermes：
1. **TypeScript 类型化工具** → Hermes 可借鉴 Zod 类型化工具设计
2. **Supervisor 多智能体模式** → 补充 Hermes 的 Agent 编排能力
3. **VoltOps 可观测性** → Hermes 可参考内置 tracing 设计
4. **Guardrails 机制** → Hermes 安全检查可参考

## 相关链接

- 文档: https://voltagent.dev/docs
- GitHub: https://github.com/voltagent/voltagent
- Discord: https://s.voltagent.dev/discord
- NPM: https://www.npmjs.com/package/@voltagent/core
