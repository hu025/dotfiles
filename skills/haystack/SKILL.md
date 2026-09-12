---
name: haystack
description: Haystack 3.x — 开源 AI 编排框架，Agent Hooks + SkillToolset + 上下文压缩。触发词：Haystack、agent hooks、skill progressive disclosure、RAG pipeline
---

# Haystack 3.x — 生产级 AI Agent 编排框架

## 核心定位

- **定位**：生产级 Agent 编排框架，Pipeline/Component 架构，3.0+ 以 Agent 为中心
- **Stars**：25.5k GitHub（2026-09）
- **License**：Apache-2.0
- **安装**：`pip install haystack-ai`（核心），`pip install agent-pack-haystack`（预置 Agent）

## vs 主要框架

| 维度 | Haystack 3.x | smolagents | Agno |
|------|-------------|------------|------|
| 技能系统 | SkillToolset（渐进披露） | CodeAgent 固定循环 | 内置 memory/trigger |
| Hook 系统 | 6 种生命周期钩子 | ❌ | ❌ |
| 上下文压缩 | CompactionHook 内置 | ❌ | ❌ |
| 多 Agent 嵌套 | AgentTool 包装 | ❌ | ❌ |
| Token 计数 | 内置 3 种计数器 | ❌ | ❌ |
| Pipeline 即 serving | run + run_async + stream 同类 | ❌ | ❌ |
| 安全加载 | YAML allowlist 白名单 | N/A | N/A |
| RAG 深度 | Pipeline 内置，RAG Agent | ❌ | 基础 |

**选型**：需要 Hook guardrails + 渐进式技能发现 + 上下文压缩 → Haystack 3.x

## 核心新能力（3.0 + 3.1）

### 1. Agent Hooks 系统（3.0 核心）

6 种生命周期钩子，**确定性执行**，不依赖 LLM 主动调用：

```python
from haystack.components.agents import Agent
from haystack.hooks import hook

@hook
def audit_tool_calls(state):
    pending = state.data["messages"][-1].tool_calls
    print(f"about to run: {[tc.tool_name for tc in pending]}")

@hook
def confirm_sensitive(state):
    # ConfirmationHook → human-in-the-loop
    if state.data["messages"][-1].tool_calls:
        raise Exception("需要人工确认")

@hook
def offload_large_results(state):
    # ToolResultOffloadHook → 大结果写外部存储
    pass

agent = Agent(
    chat_generator=OpenAIChatGenerator(),
    tools=[...],
    hooks={
        "before_tool": [audit_tool_calls],
        "after_tool": [...],
        "before_llm": [...],
        "on_exit": [...],
    },
)
```

### 2. SkillToolset + 渐进披露（3.0 核心）

模型**仅看到技能名+一句话描述**，按需加载完整指令，上下文保持精简：

```python
from haystack.tools import SkillToolset
from haystack.skill_stores.file_system import FileSystemSkillStore

store = FileSystemSkillStore("skills/")  # 每个技能 = 目录
skills_toolset = SkillToolset(store)

# Skill 目录结构示例：
# skills/
#   caveman/
#     instructions.md    # 完整指令（按需加载）
#     caveman.md         # bundled 参考文件（按需读取）
#   migrate-v2-v3/
#     instructions.md    # 迁移脚本指令
#     migrate.py         # bundled 文件

agent = Agent(chat_generator=OpenAIChatGenerator(), tools=[skills_toolset])
# 模型运行时调用 load_skill("caveman") → 获取完整指令
# 模型运行时调用 read_skill_file("caveman", "caveman.md") → 获取 bundled 文件
```

**对比 smolagents**：smolagents 是固定 CodeAgent 循环，无渐进披露能力。
**对比 Agno**：Agno 有 memory/trigger，无渐进技能加载。

### 3. 上下文压缩 Hook（3.1 独有）

`CompactionHook` 在 `before_llm` 执行，自动压缩长对话：

```python
from haystack.hooks.compaction import CompactionHook, SlidingWindowCompactor, ToolResultPruningCompactor

hook = CompactionHook(
    compactor=SlidingWindowCompactor(),  # 或 ToolResultPruningCompactor(min_keep_steps=2)
    context_window=400_000,
    compact_at=0.7,   # 70% 时触发压缩
    compact_to=0.4,   # 压缩到 40%
)

agent = Agent(
    chat_generator=OpenAIResponsesChatGenerator(model="gpt-5.4-nano"),
    tools=[web_search],
    hooks={"before_llm": [hook]},
)
```

两种内置压缩策略：
- `SlidingWindowCompactor`：先删整轮对话，再删单步，仍不够则删除最旧步骤并替换为省略注释
- `ToolResultPruningCompactor`：不删整轮，而是将旧的/large tool results 替换为占位符，保留最近的关键步骤

### 4. Token 计数器（3.1）

```python
from haystack.token_counters import ApproximateTokenCounter, TiktokenCounter, OpenAITokenCounter

# 无依赖，按字符估算
counter_app = ApproximateTokenCounter(chars_per_token=4.0)
count = counter_app.count(messages)

# 需 tiktoken，接近真实值
counter_tik = TiktokenCounter(encoding="o200k_base")
count = counter_tik.count(messages)

# 调用 OpenAI 计数 API，精确
counter_exact = OpenAITokenCounter("gpt-5-mini")
count = counter_exact.count(messages)
```

用途：在 CompactionHook 中决定何时压缩，监控 token 消耗，控制成本。

### 5. AgentTool — 多 Agent 嵌套（3.1）

将一个 Agent 包装为另一个 Agent 的 Tool，中间步骤对主 Agent 不可见：

```python
from haystack.tools import AgentTool

researcher = Agent(
    chat_generator=OpenAIResponsesChatGenerator(model="gpt-5.4-mini"),
    system_prompt="You are a research specialist.",
    tools=[web_search],
)
research_specialist = AgentTool(
    agent=researcher,
    name="research",
    description="Research a question on the web and report findings",
)

coordinator = Agent(
    chat_generator=OpenAIResponsesChatGenerator(model="gpt-5.4-mini"),
    tools=[research_specialist, ...],  # Agent 作为 Tool 使用
)
```

### 6. 预置 Deep Research Agent

```python
# pip install agent-pack-haystack
from haystack_integrations.agent_pack import create_deep_research_agent

agent = create_deep_research_agent()
result = agent.run(messages=[ChatMessage.from_user("研究主题")])
print(result["report"])  # 带引用的 markdown 报告
```

### 7. Pipeline 即 Serving（同一人类两种接口）

```python
from haystack import Pipeline

p = Pipeline()
# 同步开发 / 同步 serving
result = p.run(data)

# 异步 serving（生产）
result = await p.run_async(data)

# 流式
for chunk in p.stream(data):
    print(chunk)
```

### 8. 安全：YAML Pipeline 白名单加载

```python
Pipeline.load(fp, allowed_modules=["mypkg.*"])   # 白名单
Pipeline.load(fp, unsafe=True)                   # 仅在完全信任来源时使用
```

## 安装

```bash
pip install haystack-ai
pip install agent-pack-haystack  # 预置 Agent
# 各集成组件独立安装（不再捆绑）：
pip install sentence-transformers-haystack
pip install haystack-agents  # 若需 Legacy 支持
```

## 关键迁移（2.x → 3.x）

```python
# 旧导入已移除
# from haystack.components.generators import OpenAIGenerator  ❌
from haystack.components.generators.chat import OpenAIChatGenerator
reply = OpenAIChatGenerator().run("What is NLP?")["replies"][0]  # 返回 ChatMessage
text = reply.text  # str
```

## Skill 创作最佳实践

```markdown
skills/
  {skill-name}/
    instructions.md    # 必需：技能完整指令
    {any-file}.md      # 可选：bundled 参考文件
```

- `instructions.md` 第一行 = 技能一句话描述（渐进披露用）
- 使用 `{% include "file.md" %}` 在指令中引用 bundled 文件
- Agent 系统提示应要求：匹配技能时**必须调用** `load_skill` 而非直接输出

## 观测性

```python
# 内置 state 暴露
result = agent.run(...)
print(result["step_count"])
print(result["token_usage"])
print(result["tool_call_counts"])
print(result["exit_reason"])  # "text" | "tool_name" | "max_agent_steps"
```

Tracing：`haystack.agent.step` span 包含嵌套 `.llm` / `.tool` 子 span，标记实际使用的工具名。

## 链接

- 文档：https://docs.haystack.deepset.ai/docs
- GitHub：https://github.com/deepset-ai/haystack
- Haystack 3.0 发布：https://haystack.deepset.ai/blog/haystack-3-release
- Haystack 3.1：https://haystack.deepset.ai/release-notes/3.1.0
