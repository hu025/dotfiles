---
name: Google ADK
description: Google Agent Development Kit 2.0 — 五语言生产agent框架（Python/TypeScript/Go/Java/Kotlin），企业级多智能体编排。触发词：Google ADK / Agent Development Kit / Gemini agent / 多语言agent框架
triggers: [google-adk, agent-development-kit, gemini, multi-language-agent]
version: 1.0
updated: 2026-09-25
tags: [agent-framework, google, multi-language, enterprise, production]
sources:
  - https://adk.dev
  - https://github.com/google/adk-python
  - https://dev.to/gde/building-ai-agents-with-the-python-agent-development-kit-adk-2026-edition-v2-32hf
---

# Google ADK — SKILL.md

## 核心定位

Google开源生产agent开发框架，v2.0是企业级版本。**唯一支持5种语言（Python/TypeScript/Go/Java/Kotlin）生产级SDK**。

## 与Hermes的关系

- **不替代**：Hermes是元编排层，ADK是单框架
- **架构差异**：ADK是独立框架，Hermes是多框架编排器
- **结论**：短期不落地，监控Google Cloud集成深度

## 核心架构

### LlmAgent基础

```python
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction="You help users research topics thoroughly.",
    tools=[google_search]
)
```

### ADK 2.0 关键特性

#### Dynamic Workflows（核心创新）

```python
# 确定性代码与自适应AI推理的融合
# 支持原生Python控制流 + asyncio
# 相比静态graph，动态工作流更灵活
```

**架构理念**：将agent探索能力与确定性执行逻辑融合

#### 事件驱动的Agent生命周期

ADK将每个agent交互建模为事件流，session管理比LangGraph更轻量

### Multi-Agent架构

```python
# 支持agent间委托和协作
# 内置工具生态系统
```

### 上下文管理（差异化特性）

> "ADK treats context like source code — sessions, memory, tool outputs, and artifacts are assembled into a structured view where every token earns its place"

- 自动过滤无关事件
- 懒加载artifacts
- 追踪token使用
- summarization for older turns

### Agents CLI

```bash
# AI辅助的agent开发
# 从idea到编码的完整工具链
```

## 与LangGraph对比

| 维度 | ADK 2.0 | LangGraph |
|-----|---------|-----------|
| 语言支持 | Python/TS/Go/Java/Kotlin | Python/JS |
| 状态管理 | 事件驱动session | Checkpoint必选 |
| 多语言 | **5种** | 2种 |
| 企业集成 | Google Cloud原生 | 无 |
| 许可证 | Apache 2.0 | MIT |

## 安装

```bash
pip install google-adk
npm install @google/adk
go get google.golang.org/adk/v2
# Maven/Gradle for Java/Kotlin
```

## 许可证

Apache 2.0

## 新发现总结

1. **5语言支持**：唯一生产级Java/Go agent框架，若Hermes未来需要多语言agent场景有参考价值
2. **Dynamic Workflows**：确定性Python控制流 + AI推理融合，ADK 2.0核心创新
3. **上下文管理理念**：context as source code，每token都值得存在
4. **Event Compaction**：滑动窗口+older交互summarization，是长期会话优化方案

## 监控建议

- ADK 2.0 Dynamic Workflows生产案例
- Google Cloud Agent Runtime集成深度
- Java/Go SDK生产稳定性

---

*Google开源 · adk.dev · 21.6k GitHub stars*
