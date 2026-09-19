---
name: agent-lightning
description: Microsoft Agent Lightning v1.0 — lightweight Agentic RL training framework (18.3k stars, MIT)
trigger: Agent RL / agent training optimization / RLHF for coding agents
trigger_condition: 当研究agent自我优化/RL训练/编码agent能力提升时调用
updated: 2026-09-28
---

# Agent Lightning v1.0

## 概述

**Microsoft Research 开源框架**（MIT License），专注用强化学习训练任意agent框架。
核心价值：**零代码改动**即可对任何agent（LangChain/OpenAI Agent SDK/AutoGen/CrewAI）进行RL优化。

## 核心架构（三组件）

```
Agent → API Gateway → Trainer → 策略更新 → Agent
              ↑                          ↓
         Rollout Controller ← ← ← ← ← ← ←
```

| 组件 | 职责 |
|------|------|
| **API Gateway** | rollout存储、OpenAI兼容代理（/proxy/rollout/{id}/attempt/{id}/mode/train/openai/v1/chat/completions）、事件记录 |
| **Rollout Controller** | 本地进程或Kubernetes Jobs执行agent，状态同步 |
| **Customized Trainer** | 基于verl，运行GPU推理和优化，将rollout数据转为策略更新 |

## 核心概念

### Rollout
agent单次执行。状态机：`QUEUING → RUNNING → SUCCEEDED/FAILED`
每个rollout含append-only事件：`model_request`、`reward`
**Rollout ≠ 训练样本**：GRPO等算法可从同一example生成多个独立rollout以比较reward。

### LightningStore
中心hub：存储tasks/resources/traces。算法读写spans并发布更新后的资源（prompt模板/策略权重）。

### agl.emit_xxx()
agent侧插入的轻量helper，仅需一行代码：
```python
from agentlightning import agl
# 在任意agent框架的代码中插入
response = agl.emit_complete(model, messages, tools)
```

## Agent Lightning Skill（v1.0.1新增）

**agent优化自动化**：提供待优化agent + benchmark，skill引导系统性迭代改进prompt/tools/workflow/model/reasoning settings。

```bash
# Claude Code/Codex/Copilot 安装
gh skill install microsoft/agent-lightning agent-lightning --agent <agent>
```

## 关键数据

- **3,500行代码**：极简主义
- **18.3k GitHub stars**，MIT许可
- **SWE-bench验证**：Qwen3.5-9B，6K训练样本，41.8% → 56.4%（+14.6pp）
- **v1.0**: 2026-08-19，arXiv:2608.17528
- **v1.0.1**: 2026-08-24，Skill正式发布

## 与现有技能的关系

- **不重复**：当前已研究的agent框架（CrewAI/LangGraph/smolagents等）均为**推理/编排**框架，Agent Lightning是**训练/优化**框架，是正交能力
- **互补**：Hermes可作为Agent Lightning的目标agent进行RL优化训练

## 落地建议

### 短期（不落地）
Agent Lightning需要GPU+verl+完整RL pipeline，当前Hermes环境无GPU训练条件。

### 中期参考价值
1. **Rollout概念**：可用于Hermes内部的任务执行追踪和评价机制
2. **LightningStore理念**：中心化事件/spans/traces存储是Hermes遥测设计的参考
3. **Skill for coding agents**：v1.0.1的agent优化skill证明了"skill引导系统性改进"模式，Hermes自我改进可借鉴

### 长期
若用户有GPU训练资源，可用Agent Lightning对定制编码agent进行专项强化学习优化。

## 来源

- https://github.com/microsoft/agent-lightning
- https://microsoft.github.io/agent-lightning/stable/05-basics/
- https://arxiv.org/abs/2608.17528
- https://github.com/microsoft/agent-lightning/releases/tag/v1.0.1
