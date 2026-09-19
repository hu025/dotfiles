---
name: google-ax
description: Google AX — open-source distributed agent runtime on Agent Substrate
trigger: Google AX / Agent Executor / distributed agent runtime / agent suspension-resumption
category: research
tags: [agent-runtime, distributed, google, kubernetes, gvisor, suspend-resume, ax]
sources:
  - https://github.com/google/ax
  - https://github.com/agent-substrate/substrate
  - https://cloud.google.com/blog/products/containers-kubernetes/bringing-you-agent-sandbox-on-gke-and-agent-substrate
created: 2026-09-20
updated: 2026-09-20
stars: 1955
license: Apache-2.0
---

# Google AX (Agent Executor)

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

## 落地评估

- **本地运行**：需要 K8s + Agent Substrate（复杂度高）
- **监控价值**：立即可记录为技术情报
- **规模化参考**：Hermes 未来大规模部署的技术路线

## 快速参考

```bash
# AX CLI 安装
pip install ax-agent

# 本地运行（需 K8s + Agent Substrate）
ax --input "Hello agents!"

# 从 Agent Substrate 恢复
ax --conversation <id> --resume
```
