---
name: Pydantic AI v2
description: Pydantic AI v2 — Capability为核心的生产Python agent框架，强类型+MCP原生+Durable Execution。触发词：Pydantic AI / capability pattern / durable execution / agent框架
triggers: [pydantic-ai, capability, durable-execution, mcp, python-agent]
version: 1.0
updated: 2026-09-25
tags: [agent-framework, python, pydantic, type-safe, production, mcp]
sources:
  - https://pydantic.dev/articles/pydantic-ai-v2
  - https://pydantic.dev/docs/ai/mcp/overview/
  - https://pydantic.dev/pydantic-ai
---

# Pydantic AI v2 — SKILL.md

## 核心定位

强类型Python agent框架，v2以**Capability**为核心组织agent行为模块。内置MCP客户端+Durable Execution+Logfire可观测性。

## 核心架构

### Capability系统（v2核心创新）

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability, Thinking, ToolSearch, WebSearch

agent = Agent(
    'anthropic:claude-opus-4-7',
    instructions='Research thoroughly and cite your sources.',
    capabilities=[
        Thinking(effort='high'),          # extended thinking
        WebSearch(),                        # native + local fallback
        ToolSearch(),                       # on-demand tool discovery
        Capability(
            id='github',
            description='Look up GitHub issues and PRs',
            instructions='Use GitHub tools when asked about a repository',
            toolset=MCPToolset('https://mcp.example.com/github'),
            defer_loading=True              # 按需加载
        ),
    ]
)
```

**设计理念**：一个Capability捆绑指令+工具+lifecycle hooks+模型设置为一个可组合单元

### MCP深度集成

#### `MCP` Capability（推荐方式）

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import MCP

agent = Agent(
    'openai:gpt-5.2',
    capabilities=[
        MCP(url='https://mcp.example.com/api'),           # 本地优先
        MCP(url='https://mcp.example.com/other', native=True)  # provider原生支持
    ]
)
```

**双重支持**：本地fallback + provider原生MCP，单flag切换

#### `MCPToolset`（低级API）

```python
from pydantic_ai.mcp import MCPToolset

# 支持多种transport
toolset = MCPToolset('https://mcp.example.com/api')           # Streamable HTTP
toolset = MCPToolset('/path/to/script.py')                     # stdio
toolset = MCPToolset(fastmcp_client)                          # FastMCP client
toolset = MCPToolset(in_process_server)                        # in-process

# 生命周期管理
async with agent:
    result = await agent.run('...')
```

**高级特性**：
- `process_tool_call` callback：自定义tool调用和响应
- `error_policy`：retry/fail/exception三种错误策略
- `include_instructions=True`：自动注入MCP server初始化指令
- `task` flag：SEP-1686 task-augmented execution
- `http_client` parameter：自定义httpx配置（mTLS/CA/proxy）
- `auth` argument：bearer token/OAuth/httpx.Auth

#### 认证与会话

- Streamable HTTP是推荐remote传输方式
- 每个MCPToolset实例维护一个MCP session
- **陷阱**：共享实例中concurrent runs会共享认证session
- **解法**：用`@agent.toolset` decorator动态创建per-run实例

### Durable Execution（生产关键）

```python
# 支持4种durable执行方案
from pydantic_ai import Agent

# Temporal / DBOS / Prefect / Restate
# 仅使用Pydantic AI公开接口，可扩展到其他durable系统
```

### WebSearch默认行为变化

v2中`WebSearch`和`WebFetch`默认使用native实现，不再强制本地

### Pydantic AI Harness

v2核心保持稳定，Harness是快速迭代层：
- memory, guardrails, context management
- file system access, code mode
- headless coding agent（dogfooding中）

## 与Hermes的关系

- **不替代**：Hermes是多框架编排，Pydantic AI是单一Python框架
- **可参考**：
  - Capability模式 → Hermes skill/component系统设计
  - Durable Execution → Hermes长期任务可靠性
  - MCP深度集成 → Hermes MCP工具链优化
- **结论**：架构参考，短期不落地（已有LangGraph）

## 新发现总结

1. **Capability模式**：bundle instructions+tools+lifecycle hooks+model settings为可组合单元，Hermes skill系统可借鉴
2. **MCP双重fallback**：`native=True`让同一个MCP server在provider支持和本地实现间自动切换
3. **Durable Execution**：4种方案（Temporal/DBOS/Prefect/Restate）提供生产fault tolerance，Hermes无对应能力
4. **按需Capability加载**：`defer_loading=True`使capability仅在需要时加载，减少prompt token
5. **per-run认证**：`@agent.toolset` decorator解决concurrent runs共享认证session问题

## 关键陷阱

- v2 breaking change：`openai:`模型名改用Responses API，用`openai-chat:`保持Chat Completions
- `WebSearch`/`WebFetch`默认native，需确认provider支持
- 共享MCPToolset实例在concurrent runs中认证session会冲突

## 监控建议

- Pydantic AI Harness新capabilities发布
- Durable Execution生产案例
- MCP SEP-1686 task-augmented执行标准化

---

*Pydantic · pydantic.dev · Apache 2.0*
