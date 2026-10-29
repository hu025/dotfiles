---
name: google-ax
description: Google AX v0.2.3 — open-source distributed agent runtime on Agent Substrate
trigger: Google AX / Agent Executor / distributed agent runtime / agent suspension-resumption / trajectory branching
category: research
tags: [agent-runtime, distributed, google, kubernetes, gvisor, suspend-resume, ax, durable-execution]
sources:
  - https://github.com/google/ax
  - https://github.com/agent-substrate/substrate
  - https://cloud.google.com/blog/products/ai-machine-learning/agent-executor-googles-distributed-agent-runtime
  - https://cloud.google.com/blog/products/containers-kubernetes/agent-substrate-available-on-gke
created: 2026-09-20
updated: 2026-10-01
stars: 1955
license: Apache-2.0
release: v0.2.3 (Aug 13, 2026)
---

# Google AX (Agent Executor) v0.2.3

## 核心定位

AX (Agent Executor) 是 Google 开源的**分布式 Agent 运行时**（~2K stars, Apache 2.0）。
不是 SDK，是用于**大规模运行 agent 的基础设施层**。

## 架构

```
Client
  ↓ (resumable stream)
AX Server (multi-tenant)
  ├── Event Log Storage (durable execution state)
  ├── ControlService ←→ Agent Substrate (suspend/resume)
  └── AX Agent/Harness (session-tenant)
       ├── Snapshots
       ├── Models
       └── MCP Server
```

- **单写架构**：Single controller 保证一致的状态管理
- **事件日志**：Durable execution state，失败后自动恢复
- **高级恢复**：兼容 Agent Substrate 的计算层 actor 恢复

## 关键特性

| 特性 | 说明 |
|------|------|
| Distributed Runtime | Agent/skill/tool 在隔离环境中执行 |
| Resumption | 故障/中断后自动恢复 |
| Built-in Harnesses | 内置 Antigravity，可接入自定义 harness |
| Agent Substrate 集成 | <500ms resume，500+ suspend/resume 每秒 |
| MCP as Actor | MCP server 可部署为 Substrate Actor |
| Event Log | 持久化执行状态 |

## Agent Substrate 集成

Google Agent Substrate = K8s 上的 agent 专用运行时层：
- **子秒级恢复**：sub-500ms resume
- **30x 超额订阅**：大量 actor 复用到少量 Pod
- **快照持久化**：RAM + filesystem 跨休眠周期保留
- **gVisor 隔离**：OCI 容器内核级隔离（非 root）
- **框架无关**：ADK / LangChain / Claude Code / OpenClaw / Hermes / MCP

## Hermes 关联

Google 文章明确列出 Hermes 为早期设计合作伙伴：
> "Nous Research's Hermes ranks first globally by OpenRouter usage"

Agent Substrate 原生支持 Hermes，意味着大规模 Hermes 部署已有基础设施路径。

## 与现有 Skills 关系

- 填补 **agent 运行时基础设施**空白（现有 skills 聚焦编排/治理）
- 补充 `agent-execution-sandbox` 的规模化层
- 与 `openviking`（上下文数据库）互补：AX 负责运行时，Viking 负责上下文

## v0.2.3 新特性 (2026-08-13)

- 5 releases，稳定版发布
- 内置 Antigravity harness
- 支持自定义 harness 实现
- MCP server 可部署为 Substrate Actor

## 核心能力详解

### Durable Execution（持久执行）
通过事件日志和快照实现任意组件（agent/harness/skill/tool/sandbox）的后端弹性恢复。
即使面对 HITL 确认或故障中断也能自动恢复。

### Secure Isolation（安全隔离）
- OCI 兼容的 gVisor 内核级隔离（非 root）
- egress proxies 强制网络策略
- 凭证注入到 agent 不可达的安全区域
- 防止恶意活动危及更广泛的服务

### Session Consistency（会话一致性）
单写架构：Single controller 确保一致的状态管理，
多组件并发更新共享会话状态时减少损坏风险。

### Connection Recovery（连接恢复）
客户端断连后（网络中断等）可重新连接到 agent，
并从最后看到的序列开始回填响应。

### Trajectory Branching（轨迹分支）
在任意时间点创建 agent 执行轨迹的分支，
无需丢失上下文或其他状态即可测试或评估不同路径。

## Agent Substrate（GKE 集成）

Google Agent Substrate = K8s 上的 agent 专用运行时层：
- **子秒级恢复**：sub-500ms resume
- **30x 超额订阅**：大量 actor 复用到少量 Pod
- **快照持久化**：RAM + filesystem 跨休眠周期保留
- **gVisor 隔离**：OCI 容器内核级隔离（非 root）
- **框架无关**：ADK / LangChain / Claude Code / OpenClaw / Hermes / MCP

> **关键发现**：Nous Research (Hermes) 是 Agent Substrate 的**早期设计合作伙伴**，且 Hermes 在 OpenRouter 全球使用量排名第一。

## Hermes 关联

Google 官方博客明确列出 Hermes 为早期设计合作伙伴：
> "Nous Research's Hermes ranks first globally by OpenRouter usage"

Hermes 团队正在 Agent Substrate 之上积极构建，大规模部署已有基础设施路径。

## 与现有 Skills 关系

- 填补 **agent 运行时基础设施**空白（现有 skills 聚焦编排/治理）
- 补充 `code-execution-sandbox` 的规模化层
- 与 `openviking`（上下文数据库）互补：AX 负责运行时，Viking 负责上下文

## 落地评估

- **本地运行**：需要 K8s + Agent Substrate（复杂度高，v0.2.3 仍为早期）
- **监控价值**：立即可记录为重要技术情报
- **规模化参考**：Hermes 未来大规模部署的技术路线
- **MCP as Actor**：MCP server 可作为 Substrate Actor 部署，Hermes MCP 工具链可直接扩展

## 快速参考

```bash
# AX CLI 安装（Go）
go install github.com/google/ax/cmd/ax@latest

# 本地运行（需 K8s + Agent Substrate）
ax --input "Hello agents!"

# 从 Agent Substrate 恢复
ax --conversation <id> --resume

# Trajectory branching
ax --checkpoint <id> --branch <branch-name>
```

## 安装状态

- `pip install ax-agent`（Python CLI，v0.2.3）
- `go install github.com/google/ax/cmd/ax@latest`（Go CLI）
- 当前状态：**早期开发**，API 可能破坏性变更，PR 暂不接受
