---
name: agent-evaluation-benchmarks
description: AI Agent能力评估基准详解：SWE-bench/SWE-bench-Pro/SWE-bench-Live/WebArena/Tau2-Bench/GAIA/BFCL-v4/AgentBench选型指南。区分saturated/deprecated/active状态，识别数据污染风险，给出实际能力参考值
triggers:
  - agent benchmark comparison
  - SWE-bench vs WebArena vs Tau2-bench
  - AI agent evaluation framework
  - SWE-bench Pro contamination
  - BFCL v4 function calling leaderboard
  - agent capability assessment 2026
  - GAIA benchmark ranking
  - Tau2-bench vs BFCL
category: agent-engineering
---

# AI Agent 评估基准完全指南 (2026 Q2)

## 五大基准概览

| 基准 | 测什么 | 任务数 | 状态 | 最强分数 |
|------|--------|--------|------|----------|
| **SWE-bench Verified** | 修复合真GitHub issue | 500 | ⚠️ SATURATED/污染 | ~80% (虚高) |
| **SWE-bench Pro** | 同上，但无训练数据污染 | 1865 | ACTIVE | ~46% (真实) |
| **SWE-bench Live** | 同上，月更50任务 | 1565+ | ACTIVE | 持续更新 |
| **WebArena** | 浏览器自主操作网站 | 812 | ACTIVE | 71.6% (OpAgent) |
| **VisualWebArena** | 浏览器+多模态视觉理解 | 910 | ACTIVE | ~16-52% |
| **Tau2-Bench** | 多轮客服+工具+策略约束 | 3领域 | ACTIVE | 99.3% (Claude Opus 4.6 电信) |
| **GAIA** | 日常助手任务 | 多级 | ACTIVE | 74.6% (Claude Sonnet 4.5) |
| **BFCL v4** | 函数调用准确性 | 2000+ | ACTIVE | 70.9% (GLM-4.5) |
| **AgentBench** | 8种不同环境 | 混合 | ACTIVE | 广泛覆盖 |

---

## SWE-bench 家族 (代码修复)

### SWE-bench Verified — ⚠️ 高度污染，2026已弃用
```
问题根因（OpenAI 2026-03调查）：
- 60%的"失败案例"测试本身是坏的（误报/要求额外行为）
- 前沿模型在训练时见过这些public repo的solution
- 分数被高估30+个百分点

证据：Claude Opus 4.5
  Verified: 80.9%  ← 污染数据
  Pro:      45.9%  ← 真实能力
  差距:     35个百分点
```

### SWE-bench Pro — 当前最可靠的生产代码基准
```
来源：Scale AI，GPL许可+私有代码库（极不可能在训练集中）
任务：1865个，多语言，覆盖更大变更（平均100+行/4文件）
分数（真实）：
  Claude Opus 4.5/4.6:  ~45-46%
  GPT-5.2:              ~23% (private split)
  Gemini 3.1 Pro:       ~40%
```

### SWE-bench Live — 防止污染的持续更新方案
```
关键创新：每月从活跃仓库新增50个verified issue
结构上不可能被污染（任务在发布前不存在于训练数据）
现状：1565+任务，164个仓库
最佳选择：持续跟踪真实进展
```

---

## WebArena — 浏览器Agent能力

### 核心设计
- **自托管网站**：电商、论坛、CMS、GitLab、地图（受控环境）
- **评判方式**：最终world state（功能结果），不看Agent声称
- **人类基线**：~78%（同类任务）
- **812个任务**，多步骤（导航+填表单+点击+决策）

### 2026排行榜
```
排名 | Agent           | 模型            | 总分   | 购物 | CMS | Reddit | GitLab | 地图 |
-----|-----------------|-----------------|--------|------|------|--------|--------|------|
#1   | OpAgent         | Qwen3-VL-32B+RL | 71.6%  | 59.2 | 71.3| 86.0   | 75.9   | 71.4 |
#2   | ColorBrowserAgent| GPT-5          | 71.2%  | -    | -   | -      | -      | -    |
#3   | GBOX AI         | Claude Code    | 68.0%  | -    | -   | -      | -      | -    |
#4   | DeepSky Agent   | 专有           | 66.9%  | -    | -   | -      | -      | -    |
#5   | Narada AI       | 专有           | 64.2%  | -    | -   | -      | -      | -    |

注意：OpAgent是**开源**Qwen3-VL-32B微调，超越GPT-5
```

### 关键发现
```
- OpAgent得分86%在Reddit任务，但仅59.2%在购物（精确表单填写）
- 动态UI、anti-bot、页面加载慢是主要障碍，非推理能力
- WebArena-Verified（ServiceNow）：2026-02发布Docker镜像，本地运行更简单
- BrowserGym：WebArena等Web基准的统一底层框架
```

---

## Tau2-Bench — 多轮客服对话

### 3个领域
```
电信：Claude Opus 4.6 → 99.3%（接近完美）
零售：Claude Opus 4.6 → 91.9%
航空：Claude Opus 4.6 → 89.3%
GPT-5.2 Thinking：电信 98.7%（接近）
```

### 特点
- **多轮对话**：模拟真实客服场景，客户会纠正、追问
- **策略约束**：退票窗口、折扣叠加、库存检查等政策
- **最终状态验证**：账号状态是否正确
- Claude Opus 4.6在政策推理上显著优于GPT-5.2

---

## GAIA — 日常助手通用任务

### 分级
```
Level 1: 简单事实查询
Level 2: 需要简单推理
Level 3: 多步骤研究+综合
```

### 排行榜（2026）
```
#1 HAL Generalist Agent    | Claude Sonnet 4.5 (High) | 82.1% L1 | 72.7% L2 | 65.4% L3
#2 (多个Claude系Agent占据前6)
```

---

## BFCL v4 — 函数调用准确性

### 6个维度
```
1. 简单函数调用
2. 并行调用
3. 多函数选择
4. 相关性检测（何时不调用函数）
5. 多轮交互
6. 多步推理
```

### 排行榜
```
#1 GLM-4.5 (FC)    | 智谱AI      | 70.9%  ← 开源第一
#2 Claude Opus 4.1 | Anthropic  | 70.4%
#3 Claude Sonnet 4 | Anthropic  | 70.3%
#4 Llama 3.1 405B  | Meta       | ~68%
#5 GPT-5           | OpenAI     | 59.2%   ← 意外落后

GPT-5函数调用显著弱于Claude，开源GLM-4.5意外领先
```

### 函数数量对准确率的影响
```
单工具:   96% (Claude Opus 4.7)
5工具:    91%
20+工具:  76%
→ 工具编排是生产落地的主要瓶颈
```

---

## AgentBench — 广度优先

### 8种环境
```
OS Shell (bash命令) | SQL数据库 | 知识图谱 | 卡牌游戏
逻辑谜题 | 家务任务 | 网页购物 | 网页浏览
```

### 用途
- **不适合深度评估**，但适合快速筛查Agent的综合能力
- 与专项基准配合使用

---

## 实用选型指南

### 场景 → 基准
```
代码修复能力          → SWE-bench Live（避免SWE-bench Verified）
Web浏览器操作        → WebArena 或 VisualWebArena（多模态）
客服对话/多轮工具调用 → Tau2-Bench
通用助手能力         → GAIA
函数调用准确性       → BFCL v4
综合初筛             → AgentBench
```

### 模型 → 推荐基准
```
Claude Opus 4.6/4.7  → SWE-bench Live + Tau2-Bench（电信）
GPT-5                → GAIA + WebArena（注意BFCL弱）
开源本地模型         → BFCL v4（GLM-4.5领先）
```

---

## 重要警示

### 1. Harness影响巨大
```
2026-02实测：同一Claude Opus 4.5模型
在不同Agent框架下：731题得分相差17题
→ 框架选型与模型选型同样重要
```

### 2. 基准污染问题
```
SWE-bench Verified：已被OpenAI证实污染，前沿模型虚高30%+
所有公开排行榜需核对：swebench.com官方数据
```

### 3. 不能跨基准排名
```
不同基准测不同能力：代码≠浏览器≠客服≠日常助手
"综合最强Agent"是无意义的说法
```

---

## 来源
- SWE-bench: https://www.swebench.com
- Awesome Agents Leaderboard: https://awesomeagents.ai/leaderboards/agentic-ai-benchmarks-leaderboard/
- Presenc AI: https://presenc.ai/research/ai-agent-capability-benchmarks-2026
- PaperClipped: https://www.paperclipped.de/en/blog/ai-agent-benchmarks-swe-bench-webarena/
- BenchmarkingAgents: https://benchmarkingagents.com/
