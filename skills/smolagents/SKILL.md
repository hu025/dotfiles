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
- **GitHub**: 29,400+ stars，v1.26.0（2026-05-29），发布周期12-15天一次

## 版本现状（2026-09）
- **无v2**: 队列标题"smol-agents v2"有误，实际最新为v1.26.0（2026-05-29）
- v1.25.0安全修复：WasmExecutor loopback-only endpoint隔离、Remote Executor token认证、Docker/Modal executor移除`allow_origin`、隔离Deno缓存、修复Remote Executor高危漏洞
- v1.26.0：Exa搜索选项、移除remote WasmExecutor
- Remote Executor安全优先级：E2B/Modal/Blaxel > Docker > LocalPythonExecutor（仅原型用）
- **LocalPythonExecutor明确非安全工具**：文档强调sandboxing是必需的，LocalPythonExecutor不做安全隔离

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

## Multi-Agent Manager模式（核心新能力）

Manager-agent协调多个专门agent，每个子agent独立记忆层，减少token消耗：

```python
from smolagents import CodeAgent, ToolCallingAgent, GoogleSearchTool, VisitWebpageTool, InferenceClientModel

model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", provider="together")

# Web搜索agent
web_search_agent = ToolCallingAgent(
    tools=[GoogleSearchTool("serper"), VisitWebpageTool()],
    model=model,
    name="web_search",
    description="Search the web and visit webpages to gather information"
)

# Manager agent
manager_agent = CodeAgent(
    tools=[calculate_cargo_travel_time],  # 自定义工具
    model=model,
    planning_interval=4  # 每4步触发一次规划，减少token消耗
)

# 注册子agent
manager_agent.add_agent(web_search_agent)
result = manager_agent.run(task)
```

**关键参数**：`planning_interval=N` 控制规划频率——值越大token越少，但任务质量可能下降。

## 执行器安全等级

| Executor | 安全等级 | 适用场景 |
|----------|---------|---------|
| E2B/Modal/Blaxel | ★★★★★ | 生产环境 |
| Docker | ★★★☆☆ | 隔离要求一般 |
| LocalPythonExecutor | ★☆☆☆☆ | 仅原型开发，禁止生产 |

**注意**：LocalPythonExecutor不是安全工具，不做任何沙盒隔离。

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
