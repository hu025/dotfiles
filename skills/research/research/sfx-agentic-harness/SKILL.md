---
name: sfx-agentic-harness
description: SFX-TECH agentic-harness — Context-as-Code patterns for durable coding agent workflows
triggers: [agent harness, context as code, Claude Code plugin, durable context, verification gates]
owner: self-evolution
updated: 2026-10-21
license: MIT
stars: 0
repo: SFX-TECH/agentic-harness
---

# SFX-TECH Agentic Harness

**GitHub**: https://github.com/SFX-TECH/agentic-harness
**License**: MIT | **Created**: 2026-06-25

## 核心定位

解决 coding agent 三大通病（遗忘上下文 / 工作超出承载 / 自信代替正确）的 Context-as-Code harness。

> "Anyone can vibe-code a demo in an afternoon. The hard part is shipping something real and then operating it for months without it rotting."

## 三问题→三原则

| 失败模式 | 解决方案 |
|----------|----------|
| 上下文蒸发 | **Context as code**: memory bank 作为项目持久脑（decisions/progress/active-context） |
| 工作超出单窗口 | **One orchestrator**: 一个 lead agent 协调子 agent，顺序执行，从不自由散漫 |
| 自信代替正确 | **Verify against canonical source**: build/test/eval/phase gates 是真相，而非模型自信 |

## 核心组件

### 1. Memory Bank（持久上下文）
```
decisions.md       — 决策记录（可追溯）
active-context.md  — 当前工作状态
progress.md        — 进度追踪
memory-bank-curator sub-agent — 自动维护记忆库
```

### 2. CLAUDE.md（Bootstrap 文件）
每个项目的起点，Claude Code 启动时读取，定义项目规范、上下文、约束。

### 3. 5 个预设 Sub-Agents
- `advisor` — 顾问
- `code-reviewer` — 代码审查
- `block-0-auditor` — 零块审计
- `memory-bank-curator` — 记忆库管理
- `ci-watcher` — CI 监控

### 4. Verification Gates（验证门控）
build / tests / evals / phase gates 作为真相来源，不是模型声称的完成。

### 5. Prospective Outcome Ledger
每个qualifying任务注册前记录预期结果，保留验证序列，结果诚实记录。

## Claude Code 安装
```
/plugin marketplace add SFX-TECH/agentic-harness
/plugin install agentic-harness@sfx-harness
```

获得：key-free MCP loadout（context7, sequential-thinking, filesystem, playwright）+ 5个子agent + `/harness-init`命令。

## 与 Hermes 相关性

**参考价值**: Verification Gates + Context-as-Code模式

- `verification gates` 概念可移植到 Hermes skill authoring 的质量门控
- Memory bank 的 decisions.md/active-context.md 分工模式比单一 SKILL.md 更细粒度
- `/harness-init` 的 scaffolding 机制是 Hermes skill auto-generation 的参考

**局限性**: 0 stars，生产验证不足；专为 Claude Code 设计，Hermes 无法直接使用

## 关键文件模板
```
templates/CLAUDE.md           — 项目引导
templates/AGENTS.md           — Agent定义
CONTEXT-AS-CODE.md           — 方法论
PRINCIPLES.md                 — 原则
PATTERNS.md                  — 模式库
QUALITY-GAUGE.md             — 质量度量
WORKSPACE-HUB.md             — 工作区中心
CODE-GRAPH.md                — 代码图谱
MCP-LOADOUT.md              — MCP配置
```

## 落地动作

- [ ] 将 `decisions.md / active-context.md / progress.md` 三角结构引入 Hermes skill 文档
- [ ] Verification Gates 概念注入 autonomous-improvement-loop 技能
- [ ] CLAUDE.md 作为 Hermes project scaffolding 模板参考
