---
name: lightagent
description: 上海AI实验室轻量Agent框架，整合mem0记忆+Tools+ToT思维树，无LangChain/LlamaIndex，MCP协议，Tool Generator自动生成工具。触发词：轻量agent/mem0记忆/思维树/多Agent协作
triggers:
  - 轻量agent框架
  - LightAgent
  - mem0记忆
  - Tree of Thought
  - MCP协议
  - 思维树
---

# LightAgent — 生产级轻量Agent框架

## 核心定位
- **极简轻量**: 100% Python，无额外依赖，核心代码仅1000行
- **三合一**: Memory(mem0) + Tools + Tree of Thought(ToT)
- **无LangChain/No LlamaIndex**: 独立实现，不依赖重型库
- **GitHub**: 353 stars，上海AI + 上财大联合开源，Apache-2.0

## 核心架构

### 记忆模块（mem0原生支持）
```python
from lightagent import LightAgent

agent = LightAgent(
    model="gpt-4.1",
    api_key="your_key",
    base_url="your_base"
)
# mem0自动管理对话中的用户个性化记忆
```

### 工具集成
```python
def get_weather(city_name: str) -> str:
    """Get current weather for city_name"""
    return f"Query result: {city_name} is sunny."

get_weather.tool_info = {  # 工具元信息
    "name": "get_weather",
    "description": "..."
}

agent = LightAgent(
    model="gpt-4.1",
    api_key="your_key",
    base_url="your_base",
    tools=[get_weather]
)
```

## 差异化特点

### Tree of Thought（思维树）
内置ToT模块，支持reflection和复杂任务分解，适合多步推理场景。

### Adaptive Tool机制（v0.3.2+）
从数千工具中智能筛选候选集，**减少80% token消耗，提升52%响应速度**。

### LightSwarm多Agent协作
内置轻量级多Agent协调机制，intent识别+任务委托，比OpenAI Swarm更简单。

### Tool Generator
上传API文档，自动生成专属工具，1小时可构建数百个性化工具。

### MCP协议集成（v0.3.0+）
官方支持Model Context Protocol，与主流chat框架无缝集成。

## 安装
```bash
pip install lightagent
pip install mem0ai  # 可选记忆模块
```

## Hello World
```python
from LightAgent import LightAgent

agent = LightAgent(model="gpt-4.1", api_key="your_key")
response = agent.run("Hello, who are you?")
print(response)
```

## 支持模型
OpenAI / ChatGLM / DeepSeek / Qwen / 百川 / StepFun 等

## 与现有技能差异化
- **vs OpenViking**: LightAgent偏应用框架，OpenViking偏记忆系统
- **vs mem0**: LightAgent内置mem0但整合了完整ToT+Tools
- **关键优势**: Tool Generator自动化 + Adaptive Tool减少token

## 参考
- https://github.com/wxai-space/LightAgent
- https://arxiv.org/abs/2509.09292
