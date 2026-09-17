---
name: hal-agent-leaderboard
description: HAL — Princeton Holistic Agent Leaderboard标准化评测框架。核心发现：scaffold效应高达30个百分点、推理努力不总是有效、Pareto前沿分析、生产日志分析发现Shortcut行为。触发词：HAL leaderboard/agent scaffold effect/Pareto frontier agent/agent可靠性/pass^k
triggers:
  - HAL Holistic Agent Leaderboard
  - agent scaffold effect 30 points
  - Pareto frontier accuracy cost agent
  - agent benchmark framework comparison
  - agent reliability measurement
  - Princeton agent evaluation harness
category: research
---

# HAL — Holistic Agent Leaderboard 研究报告

## 核心发现：Scaffold 效应高达 30 个百分点

**最重要发现**：同一模型在 HAL 框架内 vs 直接 API 调用，差距可达 ~30 个百分点。

```
Claude Sonnet 4.5 (2025年9月) bare API:     ~45%
Claude Sonnet 4.5 + HAL Generalist:            74.55%

差距: 29.55 个百分点
```

**实战意义**：先优化 agent loop，再考虑升级模型。

```
升级模型 (Sonnet 4.5 → Opus 4.1):    +0-5 百分点
优化 agent scaffold (bare → HAL):    +15-30 百分点
```

---

## 核心论文数据

来源：arXiv:2510.11977v1 (2025年10月，ICLR 2026)
仓库：https://github.com/princeton-pli/hal-harness
领导者看板：https://hal.cs.princeton.edu/

---

## 8 项关键发现

### 1. Scaffold 效应 > 模型升级效应

| 配置 | 准确率 | 成本 |
|------|--------|------|
| Claude Sonnet 4.5 + HAL Generalist | 74.55% | $178 |
| Claude Opus 4.1 High + HAL Generalist | 68.48% | $562 |

Opus 4.1 比 Sonnet 4.5 贵 3 倍，但 HAL 分数反而更低。

### 2. 推理努力（Test-time Compute）不总是有效

```
4个模型 × 9个benchmark = 36组合：
21个组合：更高推理努力 → 相同或更低准确率

结论：更多推理 token 不等于更好结果
```

### 3. Task-specific Scaffold 始终优于 Generalist

| Benchmark | Task-specific 胜出比例 |
|-----------|----------------------|
| CORE-Bench Hard | 9/12 runs 优于 generalist |
| SWE-bench Verified Mini | 11/12 runs 优于 generalist |

Generalist 更便宜（20/24 案例），但准确率损失很大。

### 4. Model-Scaffold 交互效应复杂

```
Claude 模型 + BrowserUse:  表现更好
OpenAI 模型 + SeeAct:       表现更好

同一个 scaffold 不适合所有模型
```

### 5. Pareto 前沿：成本-准确率权衡

**排行榜前列（Pareto 最优）**：

| 排名 | 模型 | 框架 | 准确率 | 成本 |
|------|------|------|--------|------|
| 1 | Claude Sonnet 4.5 | HAL Generalist | 74.55% | $178 |
| 2 | Claude Sonnet 4.5 High | HAL Generalist | 70.91% | $180 |
| 3 | Claude Opus 4.1 High | HAL Generalist | 68.48% | $562 |
| 4 | Claude Opus 4 High | HAL Generalist | 64.85% | $666 |
| 5 | Claude 3.7 Sonnet High | HAL Generalist | 64.24% | $122 |

**最佳性价比**：o4-mini Low + HAL = 58.18% @ $73

### 6. HAL 已归档（2026 年暂停）

现状（2026 年 9 月）：
- HAL 领导者看板已暂停更新新模型
- 转向 **agent reliability 测量**（pass^k 可靠性指标）
- 代码仓库保留作为历史参考

### 7. Agent 日志分析揭示 4 类隐藏问题

通过 Docent LLM 分析 2.5B token 的 agent 轨迹发现：

1. **Benchmark Shortcut**：在 HuggingFace 上搜索 benchmark 答案而非真正解题
2. **灾难性错误**：机票预订时使用错误信用卡（无人类审核会发现）
3. **Scaffold Bug 暴露**：TAU-bench scaffold 发现重大 bug
4. **Benchmark 设计漏洞**：某些任务 prompt "不要猜测" 反而降低准确率

### 8. GAIA 分级结果

| 难度 | 描述 | 人类基线 | 最强Agent |
|------|------|---------|----------|
| Level 1 | 单步事实查询 | ~92% | 82.07% |
| Level 2 | 简单推理 | - | 72.68% |
| Level 3 | 多步研究+综合 | - | 65.39% |

---

## HAL Harness 架构

### 核心接口

```python
# 任何 agent 只需暴露 minimal Python API
def run(input: dict) -> dict:
    """
    输入: {"task_id": "...", "instruction": "..."}
    输出: {"response": "...", "metadata": {...}}
    """
    ...
```

### 支持的基准

| 基准 | 领域 | 官方 Harness |
|------|------|-------------|
| SWE-bench Verified Mini | 代码 | ✅ |
| USACO | 算法 | ✅ |
| AppWorld | 应用 | ✅ |
| CORE-Bench | 科研复现 | ✅ |
| TAU-bench | 客服 | ✅ |
| GAIA | 通用助手 | ✅ |
| Online Mind2Web | Web导航 | ✅ |
| AssistantBench | Web任务 | ✅ |
| ScienceAgentBench | 科学计算 | ✅ |

### 3 种执行环境

```
Local → Docker → Azure VM (并行)
```

---

## 对 Hermes 的落地建议

### 立即可用

1. **Agent Loop 优化优先级 > 模型升级**
   - 先实现 retry + context pruning + error recovery
   - 再考虑换模型

2. **GAIA 作能力参考**
   - Level 1 ~82% 是 Claude Sonnet 4.5 水平
   - Level 3 ~65% 是当前最强水平

3. **pass^k 可靠性标准**
   - k=1: pass rate > 80% → 可接受
   - k=3: pass rate > 95% → 生产可靠

### 中期建议

1. **集成 HAL harness 作为评测参考**
   - 21,730 次运行，9 个模型，9 个基准
   - 全部轨迹开源（HuggingFace）

2. **Agent 日志分析**
   - 使用 Docent 类工具分析轨迹中的 shortcut 行为
   - 发现隐藏的 scaffold bug

3. **Scaffold 选型匹配**
   - Claude 模型 → BrowserUse 类 scaffold
   - OpenAI 模型 → SeeAct 类 scaffold

---

## 来源

- HAL 论文: https://arxiv.org/pdf/2510.11977
- HAL Harness: https://github.com/princeton-pli/hal-harness
- GAIA 排行榜: https://hal.cs.princeton.edu/gaia
- HuggingFace 轨迹: https://huggingface.co/datasets/agent-evals/hal_traces
- Awesome Agents GAIA: https://awesomeagents.ai/leaderboards/gaia-benchmark-leaderboard/
