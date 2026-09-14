---
name: trueforge
description: TrueForge — 开源 Agent Harness（2026-08，MIT，5.5k⭐）。运行时层：模型调用/MCP工具/沙箱/SKILL.md技能包/上下文压缩/人工审批。TypeScript/Node.js，Local(SQLite)或Hosted(Postgres+Redis)模式。
trigger: Use when building TypeScript agents / agent harness evaluation / SKILL.md-based agent skills / sandboxed agent execution
category: agent-engineering
tags: [agent-harness, typescript, mcp, sandbox, skill-md, open-source, 2026]
created: 2026-09-15
source: https://github.com/truefoundry/trueforge
docs: https://trueforge.dev/
---

# TrueForge — 开源 Agent Harness

## 是什么

TrueForge 是将 LLM 转化为可工作 Agent 的**运行时层**（runtime layer），2026-08-19 发布，MIT 许可证，GitHub 5,466 ⭐。

与 Claude Code / Manus 等闭源 harness 的区别：**完全开源 vendor-neutral**，声称同精度下运营成本低 50%。

## 核心架构

```
LLM → TrueForge Runtime → Tools (MCP) / Sandbox / Skills / Human checkpoints
```

三层暴露：
- **Chat UI** — 开箱即用的对话界面
- **HTTP API + TypeScript SDK** — `@truefoundry/trueforge-sdk`
- **Embeddable UI SDK** — `@truefoundry/trueforge-ui`

## 关键特性

### 1. SKILL.md 技能包（与 Hermes 技能格式同构）
```yaml
# skills/my-agent/SKILL.md
---
name: research-agent
trigger: research, investigate
---
# Research Agent Skills
...
```
Git 备份的指令包，按需加载到沙箱中。与 Hermes skill 机制高度相似。

### 2. 沙箱即工具（Sandbox-as-Tool）
- Daytona 提供隔离的代码/文件执行
- 秘密保存在 harness 层，不泄露给 LLM
- 按需provision，不占用常驻资源
- **注**：Hermes 目前无内置沙箱，OpenClaw 的 code-execution-sandbox 覆盖部分场景

### 3. MCP 工具
- 远程 MCP 服务器，支持 Header Auth 或 OAuth
- 聊天内授权（in-chat authorization）
- TrueForge 自己也是 MCP 服务器

### 4. 人工审批 Checkpoints
- Tool approval（工具执行前审批）
- Ask-user-questions（向用户提问）
- Generative UI in chat（聊天内生成式 UI）

### 5. 上下文工程
- Subagents（子 Agent 隔离上下文）
- Deferred tool loading（延迟工具加载）
- Code Mode
- Large-result offloading（大结果卸载）
- Compaction（上下文压缩）

## 部署模式

| 模式 | 适用 | 存储 | 额外基础设施 | 启动方式 |
|------|------|------|------------|---------|
| Local | 个人/试用 | SQLite | 无 | `npx @truefoundry/trueforge` |
| Hosted | 团队/生产 | Postgres | Postgres + Redis | Docker Compose / Helm / Railway |

> ⚠️ Local 模式仅限本地使用，数据在 SQLite 中，无登录机制，勿暴露到互联网。

## 安装

```bash
# Node.js >= 22.14
npx @truefoundry/trueforge@latest

# TypeScript SDK
pip install trueforge-sdk  # Python CLI
npm install @truefoundry/trueforge-sdk  # TypeScript
```

## Benchmark

官方对比（同任务/同工具/同模型）：
- vs Claude Managed Agents：**成本降低 50%，精度相当**
- vs deepagents：**成本更低，精度相当**

详见：[https://trueforge.dev/benchmarking](https://trueforge.dev/benchmarking)

## 与现有技能的区分

| 技能 | TrueForge 补充点 |
|------|----------------|
| `agent-framework-comparison-2026` | 需补充 TrueForge 章节 |
| `coding-agent-cli` | OpenClaw/Claude Code/Codex/DeepSeek vs TrueForge 是不同层（harness vs coding agent） |
| `autonomous-ai-agents` | 子类目需加 TrueForge |
| `browser-use` | Browser-use 是 TrueForge 可集成的工具之一 |

## 对 Hermes 的潜在价值

1. **SKILL.md 技能包机制** → 与 Hermes 技能格式同构，可互相借鉴
2. **沙箱隔离** → OpenClaw 无沙箱，潜在可引入
3. **Human-in-the-loop** → 可用于 Hermes 关键操作审批
4. **Benchmark 方法** → 可迁移到 Hermes agent 评估流程

## 局限

- TypeScript/Node.js 生态，与 Hermes（Python）不同
- Local 模式不适合生产
- 2026-08 新发布，生产验证案例少于 deepagents

## 来源

- GitHub: https://github.com/truefoundry/trueforge
- Docs: https://trueforge.dev/
- PyPI: https://pypi.org/project/trueforge-sdk/
