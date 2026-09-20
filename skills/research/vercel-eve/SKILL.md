---
name: vercel-eve
description: Vercel Eve — filesystem-first durable agent framework (Apache 2.0, 4957 stars)
trigger: eve / vercel agent framework / durable session / filesystem-first agent
tags: [agent-framework, durable-execution, typescript, vercel, apache-2]
updated: 2026-10-20
---

# Vercel Eve — Filesystem-First Durable Agent Framework

## Overview

**eve** (4,957 GitHub stars, Apache 2.0) is Vercel's open-source agent framework built on a filesystem-first philosophy — the agent directory IS the contract. Markdown for human-readable specs, TypeScript for typed runtime behavior.

**核心差异**：其他框架让你写配置，Eve让你写文件。目录结构即架构，文件位置即语义。

## Architecture

### Core Principles

1. **Filesystem-First**: Agent = directory (`agent/`), not a config object
2. **Durable Sessions**: Immutable `sessionId`, resume after cold-starts/deploys
3. **Separation of Concerns**: Channel (transport) ↔ Harness (AI work) ↔ Runtime (persistence)
4. **Inspectable Artifacts**: Compiled output under `.eve/` directory

### Runtime Model

```
Channel (normalize inbound transport + auth)
  → Harness (one AI unit of work, returns {session, next})
    → Runtime (persists state, follows next, streams events)
```

### Authored Directory Structure

```
my-agent/
├── agent/
│   ├── agent.ts          # additive runtime config (model, name, build, compaction)
│   ├── instructions.md   # always-on instructions prompt
│   ├── tools/            # typed executable integrations
│   ├── skills/           # named procedures loaded on demand
│   ├── hooks/            # lifecycle + stream-event subscribers
│   ├── channels/          # message ingress (HTTP, Slack, …)
│   ├── connections/       # external MCP server connections
│   ├── sandbox/          # single per-agent sandbox
│   ├── workspace/        # files seeded into sandbox per session
│   ├── subagents/        # specialist child agents
│   ├── schedules/        # recurring jobs
│   └── lib/              # shared authored code
├── package.json
└── tsconfig.json
```

## Key Capabilities

### Durable Sessions
- Immutable `sessionId` as stable HTTP protocol identifier
- Sessions stream incremental output and resume after cold-starts/deploys/long-pauses
- Follow-up turns, controls, streaming, inspection all via sessionId

### Tools
- `defineTool()` with Zod input schema
- `defineDynamic()` for runtime-discovered tools
- `disableTool()` to gate tools on conditions
- Built-in tools: `bash`, `readFile`, `writeFile`, etc.

### Skills
- `defineSkill()` creates named procedures
- `getSkill()` loads at runtime on demand
- Markdown or TypeScript format

### Hooks
- `defineHook()` for lifecycle subscribers
- Stream events, pre/post-tool, session events

### Channels
- HTTP, Slack, custom via `defineChannel()`
- Vercel Connect for OAuth token management
- Per-channel auth and delivery policy

### Sandboxes
- Per-agent isolated execution environment
- Optional authored override
- Network egress control

### Subagents
- `defineAgent()` recursively in `subagents/<id>/agent.ts`
- Specialist child agents with full harness

### Evals
- `defineEval()` + `defineEvalConfig()` for built-in evaluation
- Per-case run JSONs, judge-FPR probes

## Production Templates (9)

1. **Chat**: Next.js + per-user long-term memory + Better Auth + Drizzle + Neon + Upstash Redis
2. **LLM Council**: Parallel 4-model query → judge model → agreement scores
3. **Design**: Slack design collaborator from versioned corpus
4. **Slack Agent**: Webhook + Vercel Connect + starter agent + example tool
5. **GitHub Maintainer** ("Kody"): Weekly issue digest, email reply, PR summarize, @mention respond
6. **Software Factory** ("Foreman"): GitHub/Linear → classifier → analyst → implementer → reviewer → PR
7. **Incident Response** ("sre"): Datadog + GitHub + Vercel evidence, read-only default
8. **Marketing Team**: Lead → specialists (positioning, content, social, SEO, email)
9. **Sanity Copilot**: GROQ queries, schema management, Notion drafting
10. **Social Media**: Typefully integration, multi-platform publishing
11. **Mux Video**: Durable video agent with human approval gates
12. **Weather**: Minimal fixture agent

## Deployment

- **Vercel**: Native via `vercel-plugin` (npx plugins add vercel/vercel-plugin)
- **Self-hosted**: Node.js service with own workflow storage + sandbox backend
- **Runtime**: Nitro + Workflows on Vercel; raw Node.js elsewhere

## Hermes Integration Relevance

**文件系统目录结构哲学** 与 Hermes SKILL.md + structured directories 高度共鸣。Eve 的 `agent/` 目录即 agent 合同的思想可用于 Hermes skill authoring 规范化。

**生产模板参考**：
- LLM Council 模板的多模型路由仲裁模式 → Hermes 多模型路由
- Incident Response 的可观测性设计 → Hermes skill 自检系统
- Foreman Software Factory 的多 station 流水线 → Hermes delegate_task 编排

**不值得直接集成**：Eve 强绑定 Vercel 基础设施，不适合 self-hosted Hermes 环境。

## Quick Start

```bash
npx eve@latest init my-agent
cd my-agent && pnpm dev

# Add a tool
cat > agent/tools/get_weather.ts << 'EOF'
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Get current weather for a city.",
  inputSchema: z.object({ city: z.string() }),
  async execute(input) {
    return { city: input.city, condition: "Sunny", temperatureF: 72 };
  },
});
EOF

# Build and deploy
eve build && eve start
```

## Key Files

- `agent/agent.ts`: `defineAgent({ model: 'openai/gpt-5.4-mini' })`
- `agent/instructions.md`: Always-on system prompt
- `agent/tools/<name>.ts`: One file = one tool
- `agent/skills/<name>.md`: Markdown skill procedure

## Links

- GitHub: https://github.com/vercel/eve
- Docs: https://eve.dev/docs
- Templates: https://eve.dev/templates
- Changelog: https://eve.dev/changelog.md
