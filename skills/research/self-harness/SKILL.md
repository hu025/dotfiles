---
name: self-harness
description: Self-Harness — agent improves its own harness via Weakness Mining → Proposal → Validation (上海AI Lab, arxiv:2606.09498)
---

# Self-Harness — Harnesses That Improve Themselves

## 核心概念

**Self-Harness**（上海AI Lab, 2026）是让 LLM Agent 自己改进自己运行脚手架的范式。

三种改进范式对比：
1. **Human Harness Engineering** — 人类工程师手动调整
2. **Meta-Harness** — 更强外部 Agent 指导更弱 Agent（Lee et al. 2026）
3. **Self-Harness** — 同一模型改进自己的 harness（无需外部更强 Agent）

## 三阶段循环

```
Current Harness + Target Model
         ↓
┌─────────────────────────────────┐
│ Stage 1: Weakness Mining        │  从执行轨迹聚类失败模式
│ - 执行当前 harness 收集轨迹       │
│ - LLM 提取失败特征签名           │
│ - 关键词粗粒度聚类               │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Stage 2: Harness Proposal       │  基于失败模式生成 bounded 改进
│ - 使用被改进模型自身作为 proposer │
│ - 9 个 editable surfaces 约束    │
│ - 禁止 broad rewrite            │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Stage 3: Proposal Validation    │  回归测试验证后方接受
│ - held-in 测试（弱点是否解决）   │
│ - held-out 测试（是否引入新问题） │
│ - 通过后合并到新 harness         │
└──────────────┬──────────────────┘
               ↓
         Updated Harness
```

## 9 个 Editable Surfaces

| # | Surface | 说明 |
|---|---------|------|
| 1 | system_prompt | Agent 系统提示词 |
| 2 | subagents | 子 Agent 定义与分工 |
| 3 | skills | Agent 技能/工具定义 |
| 4 | bootstrap_instruction | 任务启动引导指令 |
| 5 | execution_instruction | 任务执行指令 |
| 6 | verification_instruction | 结果验证指令 |
| 7 | failure_recovery_instruction | 失败恢复指令 |
| 8 | runtime_control_policy | 运行时控制策略 |
| 9 | (其他配置) | 日志、超时、重试等 |

## 核心设计原则

### Bounded Proposal（关键约束）
- 每次只改 1-2 个 surface
- 不做全量重写
- 提案必须多样化且有区分度

### Regression-gated Validation
- held-in 验证：弱点是否解决
- held-out 验证：是否引入新问题
- 两项均通过才接受

### 无需更强外部 Agent
- 同一模型既执行任务又提出改进
- 避免对更强模型的需求

## 基准实验结果（Terminal-Bench-2.0）

| Model | Initial | Self-Harness | Gain |
|-------|---------|--------------|------|
| MiniMax M2.5 | 40.5% | 61.9% | +21.4pp |
| Qwen3.5-35B-A3B | 23.8% | 38.1% | +14.3pp |
| GLM-5 | 42.9% | 57.1% | +14.2pp |

**关键发现**：Self-Harness 不只是添加通用指令，而是将模型特定弱点转化为具体可执行的 harness 变更。

## 与 Hermes 相关性

### Hermes 自主进化可借鉴点

1. **Failure Pattern Mining**：Hermes cron 任务失败时，自动聚类分析失败原因（而非简单记录）
2. **Bounded Edit Proposal**：改进提案限制在具体 skill 文件或配置，而非全量修改
3. **Regression-gated Merge**：skill 变更需要通过 held-out 测试（如实际任务验证）
4. **9 Surface 分类**：Hermes skill 结构（system prompt / skills / tools / memory / workflow）可直接映射

### Hermes 现有能力对比

| Self-Harness 机制 | Hermes 当前实现 |
|------------------|----------------|
| Weakness Mining | 手动记录 + agent_core.py |
| Harness Proposal | 人工制定改进方案 |
| Validation | 依赖用户反馈 |
| Editable Surfaces | SKILL.md + config.yaml |
| Bounded Editing | 无（倾向全量重写）|

### 短期可落地改进

```
1. 失败模式自动聚类：
   - cron 任务失败 → 提取错误特征 → 聚类 → 关联到 skill surface
   - 替代方案：先记录到 agent_core.py，每日汇总分析

2. Bounded skill 修订：
   - 改进限制在单个 skill.md 的 single surface
   - 避免大范围重写

3. Regression-like 验证：
   - skill 变更后用小任务验证
   - 验证通过再合并到 dotfiles
```

## 与 Meta-Harness 对比

| 维度 | Self-Harness | Meta-Harness |
|------|-------------|--------------|
| Proposer | 同一模型自身 | 独立 coding agent（Claude Code） |
| 反馈信号 | 文件系统 + 轨迹分析 | 10M tokens/步，82 文件/迭代 |
| 搜索方式 | 迭代式 propose-evaluate-accept | 进化搜索 + Pareto前沿 |
| 外部依赖 | 无 | 需要更强 coding agent |
| 适用场景 | 单模型自优化 | 多模型协同优化 |

## 来源

- 论文：https://arxiv.org/abs/2606.09498
- 官方代码：https://github.com/qzzqzzb/Self-Harness
- 中文复现：https://github.com/zyw-yg/Self-Harness
