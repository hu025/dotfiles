# Strands Agents (AWS Open Source AI Agent SDK)

**分类**: Agent Framework / Multi-Model Routing
**触发词**: strans, strands-agents, AWS agent
**Stars**: 7.1K (2026-09) | **License**: Apache-2.0 | **Gov**: 10 months old, +618% 6-month growth

## 核心定位

AWS 出品的 model-driven agent SDK，核心理念：Agent = Model + Tools + Prompt。与传统 orchestration 框架（LangGraph/CrewAI）不同，Strands 把决策权交给 LLM 本身，而非人工编排 workflow。

## 核心创新

### 1. Model-Driven 哲学
```
旧范式（2023-2024）: 人工编排 workflow → 模型执行
新范式（Strands）:  模型自己规划步骤 → 执行 tools
```
Q Developer 团队从"数月上线一个 agent"压缩到"数天到数周"。核心洞察：SOTA 模型已原生具备 tool-use/reasoning 能力，复杂编排层反而成为障碍。

### 2. Hook 系统（与 Hermes interceptors 互补）
```python
from strands.hooks import BeforeToolCallEvent

def require_sources(event: BeforeToolCallEvent):
    name = event.tool_use["name"]
    inp = str(event.tool_use["input"])
    if name == "save_report" and "[source]" not in inp:
        event.cancel_tool = "Add source citations."

agent = Agent(
    tools=[save_report],
    hooks=[require_sources],
)
```
BeforeToolCall / AfterToolCall / BeforeModel / AfterModel 四类钩子，拦截点比 Hermes 更细。

### 3. 分布式 Tool 架构（高价值）
Agent 与 Tools 可分离部署：
- Agent 运行在 Fargate/本地
- Tools 运行在 Lambda（远程 API 调用）
- 工具返回通过 API 回传
支持 client-side tool execution（return-of-control 模式）。

### 4. Model Provider 生态
```
Bedrock / Anthropic / Llama API / Ollama / LiteLLM（100+ provider）
```
MCP 集成：`uvx strands-agents-mcp-server` → Claude for VSCode / Cursor / Windsurf 即插即用。

### 5. Swarm 自主交接（Multi-Agent）
```python
swarm = Swarm(
    agents=[trend_agent, search_agent, analysis_agent, email_agent],
    entry_point=trend_agent,
    max_handoffs=15,
    repetitive_handoff_detection_window=8,
)
```
自动检测重复交接，避免死循环。与 CrewAI/Hermes subagent 不同：交接策略由模型驱动，非固定编排。

### 6. Structured Output + Zod
```python
const BriefingSchema = z.object({
    headline: z.string(),
    developments: z.array(z.string()),
    sources: z.array(z.string()),
})
const result = await agent.invoke(
    'AI agent frameworks: what happened yesterday?',
    { structuredOutputSchema: BriefingSchema }
)
```

### 7. OpenTelemetry Native
内置 OTEL instrumentation，无需额外配置即可追踪 agent trajectories + distributed tracing。

## 与 Hermes 的互补点

| 方面 | Strands | Hermes |
|------|---------|--------|
| 哲学 | Model-driven（让模型决策） | Human-in-loop（用户授权） |
| Tool 安全 | Hook 拦截（before/after） | Interceptors（异步审批） |
| 多模型路由 | 动态 workflow（Cascade/Critique/Single） | 模型切换（provider 路由） |
| 观测 | OTEL 内置 | 需手动集成 |
| 多 Agent | Swarm（交接驱动） | Subagent（树形编排） |

## 落地建议

**Hook 系统借鉴价值**：Strands 的 `BeforeToolCallEvent.cancel_tool` 机制比 Hermes interceptors 更轻量，适合对特定 tool 强制前置检查（如强制 source citation）。可考虑将此类模式引入 Hermes interceptor 设计。

**不值得全量采用**：Strands 是 AWS-native 生态，深度绑定 Bedrock/LiteLLM。Hermes 用户（自托管/Ollama）无法直接受益。

## 安装

```bash
pip install strands-agents strands-agents-tools
npm install @strands-agents/sdk
```

## 参考

- https://strandsagents.com/
- https://github.com/strands-agents/harness-sdk (7.1K stars)
- AWS Blog: https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/
- Multi-Agent Swarm: https://aws.amazon.com/blogs/machine-learning/multi-agent-social-intelligence-with-strands-agents-and-amazon-bedrock/
- A2A Protocol: https://aws.amazon.com/blogs/opensource/open-protocols-with-the-strands-agents-sdk/
