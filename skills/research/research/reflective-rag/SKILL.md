---
name: reflective-rag
description: ACL 2026 Findings paper on reflection-tagging + ΔP perplexity self-corrected evaluation labels + evaluation-guided strategy constraints for agentic RAG. Use when designing self-verification loops, retrieval-quality gating, or premature-commitment guards.
---

# Reflective RAG — 自评估驱动的策略优化 (ACL 2026 Findings)

## 概述

**主题**: Reflective RAG: Self-Evaluation Driven Strategy Optimization in Agentic RAG
**会议**: Findings of ACL 2026 (San Diego), pp. 13252–13267
**DOI**: 10.18653/v1/2026.findings-acl.648
**作者**: Haiyan Wu, Chenchen Wang 等 (浙江财经大学)
**代码/数据**: Search-R1 训练管线复用 (Qwen2.5 + e5-base-v2 + 2018 Wikipedia dump)

## 问题：现有方法的共同盲点

agentic RAG 普遍只优化"最终答案对不对"（Search-R1/R1-Searcher/ReSearch），或把评估外包给外部专家模型（Self-RAG 用 GPT 打标）。三个具体缺陷：

1. **评估不是可训练组件** — 反思信号是旁路监督，不能直接约束策略
2. **高不确定性下过早承诺** — 模型被误导检索带偏后仍直接输出答案
3. **外部评估模型依赖** — 成本高、语义与被评估模型不一致

## 核心机制

### 1. Reflection Tagging（结构化反思标签）

每步检索后模型必须输出三值评估标签，而非自由文本：

| 标签 | 含义 | 后续策略 |
|---|---|---|
| `Useful` | 检索内容有效 | 充分利用，可继续检索 |
| `Redundant` | 内容冗余 | 降低依赖，可继续检索 |
| `Confusing` | 内容可能误导 | **忽略它，触发新一轮推理或检索** |

统一轨迹格式：`<think>` / `<search>` / `<information>` / `<evaluation>` / `<answer>`。
信息充足时直接输出 `<answer>`。

### 2. ΔPPL 标签自校正（无需外部标注）

**这是本文最可迁移的贡献。** 用模型自身的不确定性信号校正评估标签：

```
ΔPPL_t = log PPL(A | τ_t \ o_t) − log PPL(A | τ_t)
```

即"移除这一步检索内容后，生成正确答案的困惑度上升了多少"。语义：

- `ΔPPL_t > 0` → 检索降低了困惑度 → 有帮助
- `ΔPPL_t < 0` → 检索反而干扰 → 可能误导

**分位数阈值分配（Appendix A）**，论文用 λ_e = 50：
- 正 ΔPPL 分布中前 λ_e% → `Useful`
- 正 ΔPPL 分布后 λ_e/2% 或负 ΔPPL 分布前 λ_e/2% → `Redundant`
- 负 ΔPPL 分布后 λ_e% → `Confusing`

关键性质：完全自监督，只需模型内部生成概率，不需要专家模型或人工标注。

### 3. 评估感知的轨迹重构

标签校正后**约束重采样**后续推理步，使策略与标签对齐（Algorithm 1 第 14–22 行的 while 循环）：
- `Useful` → 完全利用检索信息
- `Redundant` → 削弱依赖
- `Confusing` → 忽略并重新推理/检索

SFT 数据 = 重构后的轨迹，而非原始轨迹。

### 4. Evaluation-Guided Strategy Constraints（推理期硬约束）

训练期和**推理期**都生效的唯一约束：

> 若最后一次检索被标为 `Confusing`，而模型正试图直接生成最终答案 → **强制至少再做一次检索或推理**

对 `Useful` / `Redundant` **不施加任何硬约束**，让模型自由继续检索或作答。

这是"最小干预"设计：只在明确的误导信号上拦截。

### 5. Evaluation-Aware KL 正则（分组权重 + 线性衰减）

```
D_KL = α(t) · D_KL^eval + β · D_KL^other
α(t) = β + (α₀ − β)(1 − t/T_train)
```

`<evaluation>` 段 token 用更大权重 α₀ = 0.005，其余 token 用 β = 0.001。
α(t) 从 0.005 线性衰减到 0.001：早期强约束防语义漂移，后期放松给策略学习留空间。

**消融证据**：KL 值过小（0.001/0.003）会让熵早早塌到低位，评估分布迅速贴合未对齐策略 → 语义漂移 + 适应性下降（Figure 4）。

### 6. 奖励设计：故意不奖励评估标签

```
R_total = λ_acc · R_acc + λ_fmt · R_fmt   (λ_acc = 0.8, λ_fmt = 0.2)
```

稀疏的轨迹级奖励，只看答案正确性和格式合规。**不直接奖励评估标签** —— 否则模型会学会操纵标签刷分（reward hacking），反而诱发语义漂移。这是评估语义稳定性的关键设计。

## 实验结果

Qwen2.5-3B/7B-Instruct，e5-base-v2 检索器，2018 Wikipedia dump，每 query 检索单 passage。

**3B 模型（EM）**：

| 方法 | NQ | WebQ | 2WikiMHQ | HotpotQA | MuSiQue |
|---|---|---|---|---|---|
| Search-o1 | 24.27 | 16.29 | 21.84 | 21.05 | 5.79 |
| Search-R1 | 33.41 | 26.13 | 27.55 | 25.63 | 5.17 |
| **Reflective RAG** | **35.96** | **29.04** | 27.58 | **28.44** | **7.07** |

**7B 模型（EM）**：Reflective RAG 平均比 Search-R1 高 +1.02% EM / +1.47% F1。
- 3B 平均增益 +2.04% EM / +2.65% F1
- **增益无需外部专家模型，也无需额外 RL 采样**

**Self-RAG 在 7B 上全面退化**（2WikiMHQ 12.77 vs Vanilla RAG 16.71）—— 依赖外部专家标签的方案在 Qwen backbone 上不成立。

### 消融（3B）

| 配置 | NQ EM | 说明 |
|---|---|---|
| Original (base) | 17.31 | 基座模型 |
| SFT Only | 22.30 | SFT 有用但远不够 |
| No correction | 31.69 | 去掉标签自校正 → 评估信号变噪 → 约束和 KL 都失效 |
| No Cons. | 30.80 | 去掉推理期约束 → 大多数基准显著下降 |
| No eval. KL | 34.49 | 去掉评估标签 KL → 性能退化 |
| **完整** | **35.96** | |

### 检索频次反直觉发现（Table 3）

| 模型 | 方法 | 平均检索步数 |
|---|---|---|
| Qwen 3B | Search-R1 | 1.47 |
| Qwen 3B | **Reflective RAG** | **1.96**（更多） |
| Qwen 7B | Search-R1 | 2.78 |
| Qwen 7B | **Reflective RAG** | **1.74**（更少） |

**弱模型检索更多（因为自评估不可靠，需要更多证据补偿）；强模型检索更少（能更早 confident 停止）。**

结论：稳健性不来自"一律增加检索"，而是来自**自评估引导的选择性调节**。All Compulsory（无条件多检索一次）增益更小，NQ 上甚至轻微下降。

## 对 Hermes 的可迁移价值

### 1. ΔPPL 自校正 → 任何"评估是否有帮助"的地方

不需要 LLM judge 打分，直接用模型自己的 logprob 计算这一步信息的边际贡献。可用于：
- 检索结果质量门控
- 工具调用返回值的有用性判断
- skill 加载后是否真正改善了输出

### 2. `Confusing` → 强制重试 = 反过早提交护栏

Hermes 的执行纪律问题之一是"高不确定性下过早承诺最终答案"。可直接实现为一条运行时规则：

```
若 <evaluation>Confusing</evaluation> 且模型正输出最终答案 → 拦截，强制再走一轮
```

这是**唯一需要硬约束的场景**，其余情况保持自由 —— 最小干预原则。

### 3. 反思标签不直接进奖励

若未来做 skill 演化 RL / 偏好优化：**不要把"评估标签准确"写进奖励函数**。否则模型会学会操纵标签。评估信号应当作为**约束**（constraint）而非**目标**（objective）。

这条与 AgentForge 的 Safety 三层、Uber ADR 的双层检测是同一类设计直觉：检测层与优化层解耦。

### 4. 分组 KL 权重 = 保护关键语义段

若对 Hermes 做权重级自我进化（见 weight-level-self-evolve），可类比：给元数据/路由 token 更高 KL 约束权重并随训练线性衰减，给生成 token 低权重。

### 5. 弱模型该多检索，强模型该早停

对模型路由的直接启示：给弱模型配更多检索预算 / 更高 tool-call 上限；强模型收紧上限防止 token 浪费。这与 Agent FinOps 的"协调者占 40-60% 预算"是同一层的资源分配问题。

## 与已有技能的关系

- `hetero-graph-rag-2026` — 图结构检索 + 充分性重排；本文是**评估信号内生化**，两者正交可组合
- `r2r-agentic-rag` — 生产级 RAG 系统 + RRF 混合检索；本文提供 RL 训练方法论
- `a-rag` — 检索粒度由 agent 决定；本文解决"决定之后如何评估选择是否正确"
- `agent-finops` — 成本归因与预算；本文的检索频次发现补充资源分配视角
- `self-harness` / `primeagent-continual-2026` — harness 自改进；本文的"约束而非目标"原则可直接用于 skill 修订的接受准则

## 局限（作者自述，引用时不可夸大）

1. 只在 3B/7B 小模型上验证，大模型上的泛化性未证实
2. 评估信号不是直接优化目标（这是设计选择也是局限）
3. 检索环境受限：每 query 单 passage、2018 Wikipedia dump
4. s3 这类需要更大候选池的收益型方法在受限环境下被低估

## 来源

- https://aclanthology.org/2026.findings-acl.648/
- https://aclanthology.org/2026.findings-acl.648.pdf
- https://doi.org/10.18653/v1/2026.findings-acl.648