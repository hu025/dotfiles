---
name: fastagency
description: FastAgency — AG2/AutoGen原型到生产部署的适配层。OpenAPI自动工具生成+多UI适配+分布式NATS消息队列。触发词：AutoGen生产部署/多框架适配/分布式Agent。
---

# FastAgency — AG2到生产的桥梁

## 核心定位
**不是新框架，是适配层**。定位：Jupyter notebook原型 → 一行代码切换到生产REST API/分布式部署。

**与AutoGen/CrewAI/LangGraph的关系**：不替代，是它们的生产部署加速器。

## 基本信息
- **Stars**: 543 (ag2ai/fastagency)
- **License**: Apache 2.0
- **维护方**: ag2ai (AG2官方团队)
- **官方**: https://fastagency.ai

## 核心能力

### 1. OpenAPI自动生成Tool
导入OpenAPI spec，自动生成agent可调用的tool函数：
```python
from fastagency.api.openapi import OpenAPI
weather_api = OpenAPI.from_url("https://api.weather.com/openapi.json")
assistant.register_function(function_map=weather_api.get_function_map())
```

### 2. 多UI适配
同一workflow可切换ConsoleUI/MesopUI/FastAPI，无需重写逻辑：
```python
# 开发：控制台
app = FastAgency(workflows=wf, ui=ConsoleUI())

# 生产：Web
from fastagency.ui.mesop import MesopUI
app = FastAgency(workflows=wf, ui=MesopUI())
```

### 3. 分布式部署 (NATS消息代理)
```python
# 从本地3行代码变更到分布式
app = FastAgency(workflows=wf, ui=FastAPIUI())
```
支持多机器多数据中心，水平扩展worker。

### 4. CI友好的Tester Class
自动验证agent行为，集成CI pipeline。

### 5. Cookiecutter脚手架
自动生成项目结构+devcontainer+Docker+Fly.io部署脚本。

## 与现有技能的关系
- **Agent编排**: 已有agent-orchestration(5种模式)，FastAgency专注AG2适配
- **MCP**: 是互补关系，FastAgency管workflow部署，MCP管工具集成

## 适用场景
- 已有AG2/AutoGen notebook原型，需要快速上线REST API
- 需要分布式部署多Agent系统
- 需要统一UI切换（Console→Web）
- 需要OpenAPI自动集成外部API
