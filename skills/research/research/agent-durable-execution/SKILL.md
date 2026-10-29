---
name: agent-durable-execution
description: Use when an AI agent must survive crashes, waits hours/days for human approval, or needs idempotent restart-from-step. Covers Temporal/DBOS/Restate/Cloudflare Durable Objects design patterns.
description_zh: AI Agent 持久化执行层：当agent需跨崩溃恢复、需等待数小时人工审批、或需幂等从某步重启用。涵盖 Temporal/DBOS/Restate/Cloudflare Durable Objects 设计模式。
tags: [agent-infrastructure, durable-execution, temporal, dbos, restate, cloudflare-workers, human-in-the-loop, crash-recovery, orchestration]
category: agent-infrastructure
created: 2026-10-23
research_id: agent-durable-execution-2026
---

# Agent Durable Execution — 持久化执行层

## 何时需要这一层

传统 request-response 服务毫秒级结束，崩了重试即可。**Agent 不是这样**：它循环——调模型 → 解析工具 → 调外部API → 回喂 → 再调模型 → 可能等几小时人工审批。
其中每一步都可能独立失败，整体可能跑几天。**从头重跑既贵（token全付第二遍）又危险（可能重复扣款/重复发邮件）**。

判断标准：任务 > 5 分钟、或含人工审批环节、或有不可逆副作用（支付/发信/下单）→ 需要持久化执行。

Gartner 预测 2026年底 40% 企业应用将含任务专用 agent（2025年 <5%）。曲线走到这里，"丢一次运行"就从可容忍变成事故。

## 核心机制（三家一致）

所有引擎的持久化原理相同：**每步执行完成后再执行下一步之前就落盘**，崩溃后重放已记录的结果而非重新执行。

**关键心智模型：把非确定性工作（LLM调用/工具调用/外部API）关进"被记录的step"，编排代码保持确定性可重放。**

三家都强制这条边界。这是整个品类唯一需要记住的事。

| 维度 | Temporal | Restate | DBOS |
|---|---|---|---|
| 持久化模型 | 确定性workflow重放 + event history | journal制，每步先append再继续 | checkpoint写入**你自己的** Postgres |
| 架构 | 多服务集群（Server + Cassandra/Postgres + workers）或 Cloud | 自包含单二进制，笔记本→多区域 | **库**（非server），嵌入应用内 |
| 需独立编排server | 是 | 是（单二进制）| **否** |
| 步延迟 | 几十~几百ms（异步派发）| 中 | **1–2ms**（单次Postgres写）|
| 许可 | MIT / Apache 2.0 | — | MIT |
| 新增故障点 | 2+（server、Cassandra）| 1 | **0**（仅Postgres）|
| 采用成本 | 重构应用 + worker集群 | 中 | 装库 + 加装饰器（~20分钟 vs ~2周）|

## 各自的设计要害

### Temporal — 规模验证的在位者
- workflow代码必须**确定性**；大 LLM payload 会撑爆 workflow history。
- Human-in-the-loop 靠 **Signals** 把人类输入送进 agent。
- 生态最深：OpenAI Agents SDK + Temporal Python SDK 集成 2026-03-23 GA，把每次 agent 调用包成 Temporal activity，崩溃保护近乎免费。
- 已驱动 OpenAI、Cursor、Lovable、Block、Abridge 等。

### DBOS — 最小运维足迹
- `@DBOS.workflow()` + `@DBOS.step()` 装饰已有函数，无需搬进 worker、无需改部署。
- **Durable queues**：全局/每worker/每租户控制并发——Temporal 无对等抽象。
- **SQL 内省**：直接 SQL 查询、暂停、取消、恢复 workflow；可从任意 step fork（Temporal 无此能力）。
- 数据不出你的 Postgres。
- 背后是 Postgres 创建者 Stonebraker + Databricks CTO Zaharia。
- 成本：DBOS 声称比 Temporal 便宜 2–10x。

### Restate — 单二进制 / edge 适配
- journal 每步落盘；Restate Cloud 2025-09-30 全面开放，跑托管版就不用自己运维有状态设施。
- 适合 serverless / edge 部署。

### Cloudflare Durable Objects — actor 模型 + 零空闲成本
最贴近"agent 应该长什么样"的一手资料。核心命题：**agent 是持久身份，不是常驻进程**。

生命周期：`Wake → onStart() → 处理事件 → idle(~2min) → 冬眠`，alarm 或请求唤醒。

**存活 vs 丢失**（设计时必须先划这条线）：
| 存活 | 丢失 |
|---|---|
| `this.state`（setState 持久化到 SQLite）| 内存变量（未走 setState 的类字段）|
| `this.sql` 全部 SQLite 表 | `setTimeout`/`setInterval` 计时器 |
| scheduled tasks | 进行中的 fetch 请求 |
| connection state | 本地闭包 / promise 链 |
| fiber checkpoints 与 stash() | |

唤醒源：HTTP 请求 / WebSocket / RPC(service binding、`@callable`) / scheduled alarm / 收邮件。

**按工作时长选策略**：
| 时长 | 策略 |
|---|---|
| 秒 | 普通请求处理 |
| 分钟 | `keepAlive()` / `keepAliveWhile()`（自动清理心跳，推荐）|
| 分钟 | `startFiber()`（需可重试接收与状态时）|
| 分钟~小时 | Workflows |
| 小时~天 | 异步模式：起job → 冬眠 → 完成时唤醒 |

`runFiber()` = 崩溃可恢复执行，SQLite 存行 + `stash()` 中间态，驱逐后下次激活触发 `onFiberRecovered()`。

**经济账**：1万个各 1% 时间活跃的 agent → 传统方案 1万个常驻实例，DO 方案同时约 100 个活跃。

## 选型决策

> 问题不是"哪个引擎最好"，而是**你最怕哪种失败，以及你愿意为此照看多少基础设施**。

- 最大规模 + 最深框架集成 → Temporal
- 已有 Postgres、想零新基础设施 → DBOS
- 单二进制、serverless/edge → Restate
- agent 大部分时间在等、要零空闲成本 → Cloudflare Durable Objects

LangGraph/框架自带 checkpoint **不等于**完整持久执行：checkpoint 管状态恢复，Temporal/DBOS 管持久调度与人工等待。

## 对 Hermes 的可迁移启示

1. **幂等即纪律**：cron任务涉及外部写（push/通知）时，落地前先问"重放会不会重复副作用"。
2. **区分内存态与持久态**：Hermes 的 session 上下文 vs memory 文件，正好对应 DO 的 `this.state` vs 内存变量边界。
3. **"重放而非重执行"**：已完成步骤的产物应可从记录读回，而不是重算——这对研究队列（已完成 topic 不重复研究）是同一原则。
4. **空闲成本意识**：定时轮询型 agent 应按需唤醒，而非常驻烧算力。
5. **SQL 内省**：用结构化查询检查任务状态，比翻日志快且可组合。

## 来源

- https://alatirok.com/durable-execution-ai-agents-compared/
- https://developers.cloudflare.com/agents/concepts/agentic-patterns/long-running-agents/
- https://www.dbos.dev/compare/dbos-vs-temporal
- https://temporal.io/blog/temporal-langgraph-plugin-durable-execution
- https://docs.temporal.io/ai/cookbook/human-in-the-loop-python