---
name: smolagents
description: Hugging Face 轻量级 AI Agent 库 — ~1000行核心代码、CodeAgent 原生代码执行、多模型支持、沙箱隔离执行。触发词：smolagents、轻量 agent、Hugging Face agent
---

# smolagents — Hugging Face 轻量级 Agent 库

## 核心定位

- **定位**：极简 Agent 框架，核心逻辑 ~1000 行代码（agents.py）
- **Stars**：29.3k（2026-09，Apache-2.0）
- **关键差异**：CodeAgent 原生用代码作为 action，而非生成 JSON/文本 tool call

## 核心能力

### Agent 类型

```python
# CodeAgent — 原生代码执行（推荐）
from smolagents import CodeAgent, InferenceClientModel
agent = CodeAgent(tools=[], model=InferenceClientModel(model_id="mistralai/Mistral-3-70B"))
result = agent.run("Calculate sum 1 to 100")
```

### ToolCallingAgent — JSON tool call（传统）

```python
from smolagents import ToolCallingAgent
# 适合不需要代码执行的场景
```

### 多 Agent 协作

```python
# managed_agents — 主 agent 调用子 agent
from smolagents import CodeAgent
sub_agent = CodeAgent(tools=[...], model=model, name="researcher")
main_agent = CodeAgent(tools=[], model=model, managed_agents=[sub_agent])
```

### 沙箱执行

```python
# 安全执行不可信代码
from smolagents import CodeAgent, E2BExecutor
agent = CodeAgent(tools=[], model=model, executor=E2BExecutor())
# 支持: E2B / Modal / Docker / Blaxel
```

## 模型支持

```python
# HuggingFace Inference API（默认）
from smolagents import InferenceClientModel
model = InferenceClientModel(model_id="mistralai/Mistral-3-70B")

# LiteLLM（100+ 模型：OpenAI/Anthropic等）
from smolagents import LiteLLMModel
model = LiteLLMModel(model_id="anthropic/claude-sonnet-4")

# 本地模型（Transformers/Ollama）
from smolagents import TransformersModel
model = TransformersModel(model_id="meta-llama/Llama-3-8B")
```

## 工具集成

```python
# MCP 服务器
from smolagents import ToolCollection
tools = ToolCollection.from_mcp("path/to/mcp_server.py")

# Hub Space 作为工具
from smolagents import Tool
tool = Tool.from_space("m-ric/text-to-image")

# LangChain 工具
tool = Tool.from_langchain(langchain_tool)
```

## 核心特性

| 特性 | 说明 |
|------|------|
| **极简** | 核心 agents.py ~1000 行，无过度抽象 |
| **CodeAgent** | action 直接生成 Python 代码执行，而非 JSON tool call |
| **多模态** | 支持 text/vision/video/audio 输入 |
| **Hub 集成** | `agent.from_hub()` 加载预训练 agent |
| **沙箱** | E2B/Modal/Docker/Blaxel 隔离执行 |
| **planning_interval** | 定期 planning step（无工具调用，反思+规划）|
| **CLI** | `smolagent` / `webagent` 命令行工具 |

## 实用配置

```python
# 定期 planning（每 N 步反思一次）
agent = CodeAgent(tools=[], model=model, planning_interval=3)

# 自定义指令
agent = CodeAgent(tools=[], model=model, instructions="Always think step by step")

# 多媒体输入
agent.run("分析这张图", additional_args={"image": "path/to/image.jpg"})
```

## 安装

```bash
pip install 'smolagents[toolkit]'  # 含默认工具
pip install 'smolagents[litellm]'  # OpenAI/Anthropic
pip install 'smolagents[transformers]'  # 本地模型
```

## vs 其他框架

| 维度 | smolagents | Mastra | AutoGen |
|------|-----------|--------|---------|
| 代码量 | ~1000 行 | 中等 | 较大 |
| Agent 类型 | CodeAgent 优先 | 混合 | 混合 |
| 多 agent | ✅ managed_agents | ✅ Harness | ✅ 强 |
| 沙箱 | E2B/Modal/Docker | 无 | 无 |
| 重点 | 极简+安全执行 | TS/观测性 | 成熟度 |

## 来源

- GitHub: https://github.com/huggingface/smolagents
- Docs: https://huggingface.co/docs/smolagents/index
- v1.26.0（2026-05，dev: v1.27.0）
