---
name: owl-multi-agent
description: OWL multi-agent框架调研技能。触发词：OWL/GAIA/CAMEL多智能体。
trigger: OWL multi-agent CAMEL GAIA benchmark
owner: hermes-evolution
updated: 2026-09-25
---

# OWL — Optimized Workforce Learning

## 核心定位
- **定位**: 多智能体协作框架，GAIA开源第一（69.09%）
- **基础**: 建立在 CAMEL-AI 框架之上
- **许可**: 开源（具体许可证需确认）
- **Stars**: 未明确（从 CAMEL repo 推断为主流框架）

## 核心创新

### 1. 团队工作流（Workforce Architecture）
- Planning Agent：负责任务分解与协调
- Execution Agent：负责具体执行
- 动态角色交互替代静态角色绑定

### 2. GAIA Benchmark 表现
- **69.09% 平均分**，开源框架排名第一
- 测试集：真实世界任务（Web导航、信息检索、多步骤推理）
- 超越所有其他开源方案

### 3. 工具集（Toolkits）
- **MCP Desktop Commander**：跨平台桌面控制
- 文本工具包：Arxiv、GitHub、GoogleMaps、Math、Notion、Reddit、Weather
- Docker 支持开箱即用

### 4. 训练数据集开源（2025.07）
- HuggingFace：训练数据集 + 模型权重开源
- 训练代码即将发布

## 关键数据
- GAIA 69.09%（#1 开源框架）
- Python 3.10/3.11/3.12
- 建立在 CAMEL v1+ 之上
- MCP 协议支持

## 与 Hermes 相关性
- **工具**: OWL 的 MCP Desktop Commander 是精确的桌面自动化方案
- **架构**: Planning/Execution 双Agent模式可参考 Hermes kanban-worker 设计
- **Benchmark**: GAIA 是衡量通用 agent 能力的标准，pass@k > 95% 可靠性

## 不复制内容
CAMEL 基础框架已在 agent-orchestration skill 中覆盖，此处仅记录 OWL 的差异化创新。

## 来源
- https://github.com/camel-ai/OWL
- https://www.camel-ai.org/blogs/whats-inside-the-best-open-source-general-ai-agent
