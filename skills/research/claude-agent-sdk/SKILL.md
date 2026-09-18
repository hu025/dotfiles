---
name: Claude Agent SDK
description: Anthropic官方生产agent框架，将Claude Code作为库使用。触发词：Claude Agent SDK / Anthropic agent / in-process MCP / Python agent
triggers: [claude-agent-sdk, anthropic agent, claude code sdk, in-process mcp]
version: 1.0
updated: 2026-09-25
tags: [agent-framework, anthropic, python, typescript, production]
sources:
  - https://docs.claude.com/en/agent-sdk/overview
  - https://github.com/anthropics/claude-agent-sdk-python
---

# Claude Agent SDK — SKILL.md

## 核心定位

Anthropic官方生产agent框架，将Claude Code能力作为Python/TypeScript库使用。**不是独立agent runtime**，是Claude Code的编程接口。

## 与Hermes的关系

- **不替代**：Hermes是多协议编排层，Claude Agent SDK是单一agent能力库
- **可互补**：Hermes可调用Claude Agent SDK作为Claude Code能力的多会话管理组件
- **架构差异**：Hermes subagent是进程内协作；Claude Agent SDK是独立进程（Claude Code CLI）
- **结论**：监控期6个月，暂不落地

## 核心架构

### 双API模式

| API | 用途 | 特性 |
|-----|------|------|
| `query()` | 单次/快速查询 | async generator，返回消息流 |
| `ClaudeSDKClient` | 交互式多轮对话 | 支持custom tools + hooks |

### In-Process MCP Server（重要创新）

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

server = create_sdk_mcp_server(name="my-tools", version="1.0.0", tools=[greet_user])
```

**优势**：无subprocess开销，同进程类型安全调用，简化部署

### Hooks系统

```python
from claude_agent_sdk import HookMatcher

def check_bash_command(input_data, tool_use_id, context):
    if "forbidden_pattern" in command:
        return {"hookSpecificOutput": {"permissionDecision": "deny", ...}}
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[check_bash_command])]}
)
```

支持：PreToolUse、PostToolUse等生命周期hook点

### Subagents

```python
from claude_agent_sdk import AgentDefinition

options = ClaudeAgentOptions(
    agents={
        "code-reviewer": AgentDefinition(
            description="Expert code reviewer",
            prompt="Analyze code quality and suggest improvements.",
            tools=["Read", "Glob", "Grep"]
        )
    }
)
```

与Hermes subagent驱动开发技能互补：后者是执行模式，前者是agent定义格式

## 关键配置

```python
ClaudeAgentOptions(
    system_prompt="...",
    allowed_tools=["Read", "Edit", "Bash"],  # allowlist
    permission_mode="acceptEdits",              # auto-accept edits
    max_turns=25,                             # agent loop上限
    cwd="/path/to/project",
    api_timeout_ms=600000,                     # per-request超时
    claude_code_max_retries=10,
    task_budget={"total": 100000},            # API-side token budget
    resume="session_id",                      # 恢复会话
    fork_session=True,                         # fork而非继续
    agents={...},                              # 子agent定义
    mcp_servers={"name": server_or_config},
    hooks={...}
)
```

## 错误处理

```python
from claude_agent_sdk import (
    ClaudeSDKError,        # 基类
    CLINotFoundError,      # Claude Code未安装
    CLIConnectionError,    # 连接问题
    ProcessError,          # 进程失败
    CLIJSONDecodeError     # JSON解析错误
)
```

## 安装

```bash
pip install claude-agent-sdk    # Python 3.10+
npm install @anthropic-ai/claude-agent-sdk  # TypeScript
```

**注意**：Claude Code CLI自动打包进包，无需单独安装

## 许可证

**Commercial Terms of Service**（非Apache/MIT/BSD）—— 商业使用需注意条款

## 新发现总结

1. **In-Process MCP Server**：custom tools直接以Python函数定义，无需subprocess，性能最优
2. **Hook系统**：PreToolUse等生命周期hook提供了比Hermes skill更强的运行时拦截能力
3. **task_budget**：API-side token budget（task-budgets-2026-03-13 beta）是成本控制新模式
4. **Session Fork**：fork_session不继续原会话而是创建分支，适合分支实验

## 与现有技能的关系

- `subagent-driven-development`：互补（格式可迁移）
- `mcp-integration`：Claude Agent SDK的in-process MCP是MCP协议的一种高效实现
- `agent-testing-frameworks`：Hooks系统可作为deterministic testing的基础

## 监控建议

- Anthropic是否发布官方生产支持
- Commercial Terms是否允许Hermes类场景使用
- In-process MCP性能数据

---

*Anthropic官方 · docs.claude.com/en/agent-sdk/overview*
