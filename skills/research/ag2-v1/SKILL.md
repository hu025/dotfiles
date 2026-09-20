---
name: ag2-v1
description: AG2 v1.0 — Protocol-driven agent framework (AutoGen successor, Aug 2026). Trigger: AutoGen migration, multi-agent network, skill catalog.
triggers:
  - autogen migration
  - ag2 agent network
  - protocol driven agents
  - skills catalog
---

# AG2 v1.0 — Protocol-Driven Agent Framework

## 核心定位

**AG2** (formerly AutoGen) 是开源 agent 框架，2026-08-28 发布 v1.0，从研究原型彻底重写为协议驱动生产框架。

- **v1.0.3** (Latest, Aug 2026)
- Apache 2.0
- `pip install ag2`
- Classic (autogen.*) 迁移至独立仓库 `ag2ai/ag2-classic`

## 核心架构变化

### v1.0 破坏性变更
```
旧: import autogen / ConversableAgent / initiate_chat / GroupChat
新: import ag2 / Agent / ask() / run() / Network
```
Classic API 全部移除，需迁移至 ag2-classic 独立仓库。

### 新 API 核心原语

```python
from ag2 import Agent
from ag2.config import OpenAIConfig

# 创建 agent
agent = Agent("assistant",
    prompt="You are helpful.",
    config=OpenAIConfig("gpt-4o-mini"),
    tools=[my_tool])

# ask() = 阻塞直到完成
reply = await agent.ask("What is AG2?")

# run() = 可观测，可中途注入消息
async with agent.run("Tell me about X") as run:
    run.start()
    # ...观察 live events...
    reply = await run.result()

# 继续同一会话
next_turn = await reply.ask("Make it shorter")
```

### MemoryStream 事件监听

```python
from ag2 import Agent, MemoryStream
from ag2.events import ToolCallEvent

stream = MemoryStream()
@stream.where(ToolCallEvent).subscribe()
async def on_tool(event):
    print(f"Tool called: {event.name}")

reply = await agent.ask("...", stream=stream)
```

## Multi-Agent Network (Beta)

hub-and-spoke 拓扑，替代旧 GroupChat：

| 组件 | 作用 |
|------|------|
| Hub | 注册表、审计日志、通道表、规则引擎 |
| AgentClient | 包装单个 Agent，发送/接收 Envelope |
| HumanClient | HITL 人工参与者 |
| Passport | 稳定身份（name, agent_id, model） |
| Resume | 能力声明 + 观察记录 |
| Rule | 访问控制、速率限制、收件箱配额 |

### 四种通道适配器

| 适配器 | 参与者 | 轮次顺序 | 终止条件 |
|--------|--------|----------|----------|
| conversation | 2 | 自由 | 显式 close 或 TTL |
| consulting | 2 | 严格 1Q1R | 响应后自动关闭 |
| discussion | 2+ | 轮询 | 显式 close 或 TTL |
| workflow | 2+ | 声明式 TransitionGraph | TerminateTarget / max_turns |

## Skills 目录

```bash
npx skills add ag2ai/ag2-skills
```
按需加载，覆盖：quickstart / custom tools / network / middleware / memory / structured output / evaluation。

## 与 Hermes 相关性

- **agent 间通信模式**：Network hub + channel 架构是 Hermes delegate_task 编排演进参考
- **MemoryStream 事件模型**：比 Hermes skill hook 更精细的全链路可观测性
- **HITL 模式**：`HumanClient` 实现比 Hermes 现有 HITL 更结构化

## 落地建议

- **短期**：观察为主，AG2 v1.0 刚发布，生态尚在迁移
- **中期**：Network 的 governance/audit 模式值得 Hermes 借鉴
- **不适**：Hermes 已有成熟编排体系，不需要替换

## 来源

- https://docs.ag2.ai/
- https://github.com/ag2ai/ag2
- https://pypi.org/project/ag2 (v1.0.3, Aug 28 2026)
