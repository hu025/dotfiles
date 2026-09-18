---
name: beeai-framework
description: BeeAI — IBM Research开源多Agent框架，Apache 2.0，Linux Foundation托管，Python/TypeScript双语言，MCP+A2A双协议。触发词：BeeAI/IBM/多Agent/MCP/A2A
triggers: [beeai, ibm research, multi-agent, bee ai, apache 2.0, linux foundation]
version: 2026-09-18
category: research
tags: [agent-framework, python, typescript, ibm, multi-agent, mcp, a2a]
author: self-evolution
sources:
  - https://github.com/i-am-bee/beeai-framework
  - https://framework.beeai.dev/introduction/welcome
  - https://www.ibm.com/think/news/beeai-open-source-multiagent
---

# BeeAI Framework — IBM Research 开源多Agent框架

## 核心定位

**BeeAI Framework** 是 IBM Research 出品的生产级多Agent系统框架，托管于 Linux Foundation，Apache 2.0，3.4k GitHub stars。Python + TypeScript 双语言，特性完全对齐。

## 关键特性

### 1. MCP + A2A 双协议原生支持
- **MCP**（Model Context Protocol）：Agent 获取工具
- **A2A**（Agent-to-Agent）：Agent 间互操作
- ACP 已合并入 A2A（2025-08-25）

### 2. Declarative Orchestration（YAML编排）
- 用 YAML 定义复杂 Agent 系统
- 更可预测、更易维护
- 类似 LangGraph 的状态机但声明式

### 3. Pluggable Observability
- 原生 OpenTelemetry 支持
- 几分钟内集成现有监控栈
- real-time tracing + auditing

### 4. Built-in RAG
- 向量存储 + 文档处理
- 与 BeeAI memory 集成

### 5. Mustache 模板
- 动态 prompt 模板
- 比 f-string 更结构化

### 6. Memory 管理
- 内置记忆策略
- conversation history 管理

### 7. 多语言支持
- Python（Apache 2.0）
- TypeScript（Apache 2.0）
- 特性完全 parity

## 架构亮点

### Linux Foundation 托管
- 开放治理
- 社区驱动
- 企业级稳定性保证

### IBM Granite 集成
- 与 IBM Granite 模型原生集成
- 支持 Llama 等开源模型

## Quick Start

```bash
pip install beeai-agent
```

```python
from beeai_agent import Agent
from beeai_agent.memory import InMemoryMemory

agent = Agent(
    model="granite",
    tools=[],
    memory=InMemoryMemory(),
)
```

## 与 Hermes 对比

| 特性 | BeeAI | Hermes |
|------|-------|--------|
| 托管 | Linux Foundation | Nous Research |
| License | Apache 2.0 | proprietary |
| MCP | ✅ | ✅ |
| A2A | ✅ | ❌ |
| YAML 编排 | ✅ | ❌ |
| OTel | ✅ | 需手动 |
| RAG 内置 | ✅ | ❌ |

## Hermes 可借鉴点

1. **A2A 协议** → Hermes inter-agent communication
2. **YAML 声明式编排** → Hermes workflow DSL 思路
3. **Linux Foundation 托管模式** → 开放生态方向参考
