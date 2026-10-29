---
name: strands-agents
description: Strands Agents — AWS开源Python/TypeScript Agent SDK，6.3k stars，Apache 2.0，Model-agnostic，内置Hook/Guardrail/OTel。触发词：Strands/AWS agent/多模型支持
triggers: [strands, aws agent, strands-agents, model agnostic, apache 2.0]
version: 2026-09-18
category: research
tags: [agent-framework, python, typescript, aws, model-agnostic, guardrails]
author: self-evolution
sources:
  - https://github.com/strands-agents/sdk-python
  - https://strandsagents.com/
---

# Strands Agents — AWS 开源 Agent SDK

## 核心定位

**Strands Agents** 是 AWS 开源的多语言 Agent SDK（Python + TypeScript），6.3k GitHub stars，Apache 2.0 许可证。来自 Amazon 内部生产系统，为"任何模型、任何云"设计。

## 关键特性

### 1. Model-Agnostic 多模型支持
内置 provider:
- Amazon Bedrock（默认）
- Anthropic
- OpenAI / OpenAI Responses API
- Google Gemini
- Cohere
- LiteLLM
- Ollama（本地）
- Llama API
- SageMaker
- Writer
- **自定义 provider**（Protocol 接口）

对 Hermes 参考价值：Provider 接口设计是 multi-model routing 的最佳参考。

### 2. Hook 系统
```python
from strands import Agent
from strands.hooks import BeforeToolCallEvent, WRITE_OPS

def read_only_guard(event: BeforeToolCallEvent):
    """Block write operations in agent tools."""
    if any(op in event.tool.name for op in WRITE_OPS):
        raise PermissionError(f"Write tool {event.tool.name} blocked")
```

类似 Claude Agent SDK Hook，但 Strands Hook 是完整事件模型（BeforeToolCall/AfterToolCall 等）。

### 3. Guardrails 内置
```python
# 生产级写入保护
read_only_agent = Agent(
    tools=[...],
    hooks=BeforeToolCallHook(read_only_guard)
)
```

### 4. Hot Reloading Tools
```python
agent = Agent(
    tools_directory="./tools"  # 自动热重载
)
```
Agent 自动监听 `./tools/` 目录变化，无需重启。

### 5. MCP 原生集成
```python
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

client = MCPClient(
    lambda: stdio_client(StdioServerParameters(
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"]
    ))
)
with client:
    agent = Agent(tools=client.list_tools_sync())
```

### 6. 多 Agent 模式
- **Swarms**：群体智能模式
- **Graphs**：图结构编排
- **Workflows**：工作流
- **Agents as Tools**：Agent 可被其他 Agent 调用
- **A2A 协议**：Agent-to-Agent 互操作

### 7. Session 管理
- Null manager（无状态）
- Sliding window manager（滑动窗口）
- Summarizing manager（摘要）
- File / S3 / Repository manager（持久化）

### 8. OpenTelemetry 原生
内置 tracing，无需额外配置。

## Quick Start

```bash
pip install strands-agents strands-agents-tools
```

```python
from strands import Agent
from strands_tools import calculator

agent = Agent(tools=[calculator])
response = agent("What is the square root of 1764")
print(response)
```

## 与 Hermes 对比

| 特性 | Strands | Hermes |
|------|---------|--------|
| 语言 | Python/TS | Python |
| Provider 接口 | ✅ 完整 | 有限 |
| Hook 系统 | ✅ Before/After Tool | 部分 |
| Guardrails | ✅ | 弱 |
| MCP | ✅ | ✅ (native) |
| A2A | ✅ | ❌ |
| OTel | ✅ 内置 | 需手动 |
| License | Apache 2.0 | Nous Research |

## Hermes 可借鉴点

1. **Provider Protocol** → Hermes multi-model routing 标准化
2. **Hook 事件模型** → Hermes skill pre/post execution hook
3. **tools_directory 热重载** → Hermes skill 文件监视
4. **Session manager 抽象** → Hermes conversation context 管理
