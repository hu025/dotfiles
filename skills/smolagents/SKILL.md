---
name: smolagents
description: HuggingFace轻量Agent框架，CodeAgent代码优先，~1000行核心代码，MCP/LangChain工具集成。触发词：轻量agent/CodeAgent/代码执行agent
triggers:
  - 轻量agent框架
  - CodeAgent
  - HuggingFace agent
  - 代码执行agent
  - smolagents
---

# smolagents — HuggingFace 轻量级Agent框架

## 核心定位
- **代码优先Agent**: CodeAgent用Python代码作为action，而非JSON tool calls
- **极简主义**: 核心逻辑~1000行代码（agents.py），抽象最少化
- **Model/Tool/Modality agnostic**: 任何LLM、任何工具、文本/视觉/音频/视频输入
- **GitHub**: 27,700+ stars，2025年1月发布

## 两种Agent类型

### CodeAgent（主力）
```python
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel()  # 默认HF推理API
agent = CodeAgent(tools=[], model=model)
result = agent.run("Calculate sum of 1 to 10")
```
LLM生成Python代码并在sandboxed环境执行，每个推理步骤产出一个可执行代码块。

### ToolCallingAgent
传统JSON/text工具调用，适合需要标准tool-use范式的场景。

## 工具集成（核心差异化）

### MCP服务器工具
```python
from smolagents import ToolCollection, CodeAgent

# 从MCP服务器加载工具
mcp_tools = ToolCollection.from_mcp("npx", "-y", "@modelcontextprotocol/server-filesystem")
agent = CodeAgent(tools=mcp_tools)
```

### LangChain工具
```python
from langchain.tools import WikipediaQueryRun
from smolagents import Tool

wiki_tool = Tool.from_langchain(WikipediaQueryRun())
agent = CodeAgent(tools=[wiki_tool])
```

### Hub Space作为工具
```python
from smolagents import Tool

image_gen = Tool.from_space("black-forest-labs/FLUX.1-dev")
```

## CLI使用
```bash
smolagent                    # 运行多步CodeAgent
webagent                     # 网页Agent
```

## 与现有技能差异化
- **vs Haystack**: smolagents更轻量（1000行 vs Haystack的完整RAG管道）
- **vs LangChain/AutoGen**: smolagents没有复杂的编排图，代码即action
- **适合Hermes场景**: 代码执行能力可用于复杂自动化脚本

## 安装
```bash
pip install smolagents
pip install "smolagents[litellm]"   # 支持OpenAI/Anthropic
pip install "smolagents[transformers]"  # 本地模型
```

## 关键特点
1. **代码优先**: Agent不是"用来写代码"，而是"用代码思考"
2. **Hub集成**: 工具和Agent可直接从HF Hub共享/拉取
3. **多模态**: 内置支持文本、图像、视频、音频输入
4. **MCP原生**: 官方支持Model Context Protocol工具

## 参考
- https://github.com/huggingface/smolagents
- https://huggingface.co/docs/smolagents/en/index
