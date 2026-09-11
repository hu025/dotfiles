---
name: autoresearch-evomap
description: EvoMap AutoResearch — AI科研agent从想法到实验验证的完整管线。触发词：AI科研/假设验证/实验自动化/研究迭代
triggers: [AutoResearch, EvoMap, AI科研框架, 假设验证, 实验自动化, 研究迭代]
version: 1.0.0
category: agent-engineering
tags: [research-agent, hypothesis-testing, experiment-automation, multi-model-review, evomap]
sources:
  - https://github.com/EvoMap/AutoResearch (2.9K stars, Apache-2.0)
  - https://evomap.ai/blog
  - https://arxiv.org/abs/2608.17906
created: 2026-09-22
updated: 2026-09-22
---

# EvoMap AutoResearch — AI科研假设验证框架

## 核心定位

EvoMap开源的AI科研agent工作流（2.9K⭐ Apache-2.0），解决"AI模型自信≠真实成功"的科研验证问题。把研究想法通过可衡量实验测试，而非依赖模型自我置信度。

**与现有框架的差异**：
- 不同于Karpathy autoresearch（聚焦LLM训练单一步骤自动化）：AutoResearch是通用科研框架，覆盖多学科
- 不同于现有autonomous-improvement-loop（聚焦工程任务改进）：AutoResearch聚焦科研假设验证与迭代
- 不同于普通RAG/文献综述工具：AutoResearch产出可复现的实验证据包

## 核心创新

### 1. 多模型交叉评审（Idea Forge）
- 多个AI模型独立生成并交叉评审研究想法
- 减少单一模型的幻觉和过度自信
- Blind review挑战结论后才视为完成

### 2. 可执行研究计划
每个接受的想法转换为：
- **指标**（metrics）：如何衡量成功
- **成功标准**（success criteria）：明确的阈值
- **资源预算**（resource budgets）：算力/时间/成本上限
- **评估程序**（evaluation procedures）：如何执行测试

### 3. 专项Agent执行管线
5类专业化agent处理不同阶段：
- 规划agent：制定详细研究计划
- 实现agent：编写实验代码
- 实验agent：运行实验
- 分析agent：解读结果
- 评审agent：独立验证结论

### 4. 持久化工作空间
```
data/projects/        # 实验项目+状态+结果
data/ideas/           # 待执行的研究想法
knowledge_base/       # 本地领域知识库
```
- 中断可恢复：失败实验不丢弃，保留部分结果
- 研究状态/代码/日志/指标/失败原因全程记录
- 可供人工审查或接管

### 5. 证据驱动决策
- 部分结果 → 修订假设
- 外部测试暴露问题 → 新一轮实验
- 重复失败 → 终止方向但保留学到的东西

## 性能数据

| 基准 | 原始 | AutoResearch后 |
|------|------|---------------|
| RSICD（图像描述） | 32.84 | 34.69 |
| 官方新功能测试 | 2/7 | 4/7 |

## 快速启动

```bash
git clone https://github.com/EvoMap/AutoResearch.git
cd AutoResearch
bash scripts/bringup.sh

# 配置API
test -f .env || cp .env.example .env
test -f config/providers.local.json || \
  cp config/providers.example.json config/providers.local.json

# 验证API可用性
set -a && source .env && set +a
.venv/bin/python scripts/preflight.py --live

# 运行想法生成管线
python idea_generation.py
```

## 与Hermes的互补价值

**当前局限**：Hermes的autonomous-improvement-loop主要处理工程任务（代码/配置/部署）的自动化改进，缺乏科研假设验证能力。

**潜在整合方向**：
1. 当Hermes发现新的LLM/框架时，用AutoResearch验证其在特定基准上的真实改进
2. 研究想法生成可以补充研究队列——用实验数据而非主观判断决定研究优先级
3. 持久化工作空间可作为Hermes长期研究的知识沉淀层

**不适合的场景**：
- 日常工程任务改进（autonomous-improvement-loop已覆盖）
- 需要快速原型验证（太重）
- 非可实验领域（如纯数学证明）

## 架构图

```
研究想法输入
    ↓
┌─────────────────────┐
│   Idea Forge        │ ← 多模型独立生成+交叉评审
│  (想法生成+过滤)     │
└─────────────────────┘
    ↓ 通过评审的想法
┌─────────────────────┐
│  研究计划制定        │ ← 指标/标准/预算/程序
│  (Planning Agent)   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  执行管线            │ ← 专项agent协作
│  Planning→Impl→Exp  │
│  →Analysis→Review   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  持久化工作空间      │
│  projects/+logs/    │
│  (可恢复+人工审查)   │
└─────────────────────┘
    ↓
证据包 → 论文写作 / 继续迭代
```

## 参考链接

- Repo: https://github.com/EvoMap/AutoResearch
- 论文: https://arxiv.org/abs/2608.17906
- 官网: https://evomap.ai/
- Blog: https://evomap.ai/blog
