---
name: set-level-evidence-selection
description: Set-level/submodular evidence selection for RAG — 用边际覆盖(marginal coverage)替代逐篇排序, 贪心选集有 (1-1/e) 保证. Use when designing RAG reranking/selection, multi-hop evidence gathering, context budget, or when "top-K 篇检索结果凑不齐答案" / "该给 LLM 几篇文档" 问题.
triggers: [set selection, set-wise, submodular, marginal coverage, marginal gain, diminishing returns, evidence coverage, greedy selection, 集合选择, 边际覆盖, 边际增益, 递减收益, 贪心选集, 多跳证据, 证据链, 动态K, 变长选择, information coverage, soft anchor, pressure-adaptive, 上下文预算, rerank budget]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: |
  arXiv:2608.25115 (PACE, 2026-08-25) — Weibin Cai, Mojtaba Zafarani
  arXiv:2508.09497 (DPS, 2025-08-13) — Siyuan Meng et al.
  ACL 2025 Long Papers pp.  (arXiv:2507.06838) — SetR, LG AI Research
code: |
  https://github.com/LGAI-Research/SetR — BSD-3-Clause, 28 stars, last push 2025-09-11 (核验 2026-10-24)
  PACE / DPS: 论文未给出公开代码链接
related_work: |
  https://arxiv.org/abs/2609.36805 (UpliftMem — 集合级 uplift, 记忆场景)
  https://arxiv.org/abs/2508.09497 的前置 arXiv:2507.06838 (SetR)
  https://aclanthology.org/2024.acl-long.573/ (ielab/llm-rankers — setwise, heapsort)
  https://k-rt-k.github.io/DISCo/ (DISCo — 稠密子集索引, coverage 可索引化)
  skills/research/uplift-rag/ (单篇 uplift, 本技能是它的集合级对应物)
tags: [rag, set-selection, submodular, marginal-coverage, greedy, multi-hop, evidence-chain, context-budget, reranking, acl-2025, hermes-self-improvement]
---

# Set-Level Evidence Selection — 集合级证据选择

## 核心命题

**逐篇打分排序 ≠ 选集合。** 单篇相关性 Top-K 在多跳/组合式问题上系统性失败：答案所需信息**分散在多篇文档里**，而相关性排序只保证每篇单独相关，不保证集合**覆盖完整**、**彼此互补**。

三条独立证据线指向同一结论：

| 工作 | 机制 | 关键结论 |
|---|---|---|
| **SetR** (ACL 2025) | LLM 先 CoT 拆解"信息需求"，再选满足全部需求的子集 | Hit@k 48.87% → 69.90%；**不用固定 K**；不用排序，输出集合即可 |
| **DPS** (arXiv:2508.09497) | 把选择建模为**变长子集的自回归序列预测** | MuSiQue F1 +30.06% vs Qwen3-reranker；最优 K **依 query 而变**（HotpotQA=5, MuSiQue=3） |
| **PACE** (arXiv:2608.25115) | 训练无关的**边际覆盖**目标 + 贪心 | 目标**单调次模** → 贪心有 (1−1/e)≈63% 保证；"less can be more" |

**联合结论**：证据预算该是**集合级决策**，且集合的选择标准应该是**边际覆盖**而非**单篇相关**。

---

## 一、PACE 边际覆盖目标（可复现公式）

设查询 `q`，稠密检索器返回候选集 `C = {d_i}`，`D_max` 为最大 rerank 预算（通常 top-100）。

### 1.1 覆盖目标

用**非负稀疏表示**（SPLADE-v3 这类 learned sparse；不能用 BM25 归一化 TF 或稠密向量，因为需要 `d_i(v) ≥ 0`）：

```
F(S) = Σ_v  q(v) · max_{d_i ∈ S} [ √(ρ_i) · d_i(v) ]        (1)
```

- `q(v) ≥ 0`：查询在语义维度 v 上的强度
- `d_i(v) ≥ 0`：文档 d_i 在维度 v 上的强度
- `ρ_i ≥ 0`：文档 i 的**相关性权重**（稠密检索器分数，或经 soft-anchor 精化后的值）

当前覆盖度：
```
m_S(v) = max_{d_i ∈ S} [ √(ρ_i) · d_i(v) ]                    (2)
```

### 1.2 边际增益与贪心

```
Δ(d_i | S) = Σ_v  q(v) · max[ √(ρ_i)·d_i(v) − m_S(v), 0 ]    (3)
d* = argmax_{d_i ∈ C\S} Δ(d_i | S)                            (4)
```

关键结构：`max[…, 0]` 意味着**只有贡献新覆盖维度的文档才有正增益**——已被覆盖的维度不再加分。这正是"边际收益递减"的来源。

### 1.3 次模性定理（可引用）

> **Theorem (Cai & Zafarani 2026, Thm 3.1)**：若 `q(v) ≥ 0`、`ρ̃_i ≥ 0`、`d_i(v) ≥ 0` 对所有 v 和 i 成立，则 `F(S)` **单调且次模**。
>
> **Corollary 3.2**：在基数约束 `|S| ≤ K` 下，贪心 `S_greedy` 满足 `F(S_greedy) ≥ (1 − 1/e) · F(S*)`。

证明思路（自己验证时按此走）：
- 单调：`A ⊆ B` ⇒ `m_A(v) ≤ m_B(v)` ⇒ `F(A) ≤ F(B)`
- 次模：`A ⊆ B` ⇒ `m_A(v) ≤ m_B(v)` ⇒ `Δ(d_j|A) ≥ Δ(d_j|B)`（递减收益）

### 1.4 Soft-anchor 相关性精化（关键机制，易漏）

只用检索器分数 `ρ_i` 会漏掉**桥接文档**——多跳里那些与 query 弱相关、但与已选证据强相关的中间事实/实体桥梁。

精化流程：
```
1. 稳健标准化:  z_i = (ρ_i − median(ρ)) / (MAD(ρ) + ε),  ε = 1e-12
2. 软锚权重:    w_i = exp(z_i) / Σ_{d_j ∈ B} exp(z_j)     (5)   # B = 锚集合
3. 文档间相似:  a_ij = sim(d_i, d_j)
4. 归一化:      b_j = norm(ρ_j),  ā_j = norm(a_j)          # min-max
5. 精化权重:    ρ̃_j = f(b_j, ā_j)   (Eq.9)
```

- **锚（anchor）** = 查询相关性高的候选文档，作为"证据种子"
- 与锚相似的文档获得更高 `ρ̃` → 排名前缀同时包含**直接相关**文档和**桥接**文档
- **可在 rerank 前或后应用**：唯一区别是 Eq.5 中 `ρ_i` 的来源（检索器分数 vs reranker 分数）

### 1.5 压力自适应预算（pressure-adaptive budgeting）

`D` 固定是次优的：大 D 保 recall 但可能把 reranker 变成瓶颈；小 D 降延迟但可能丢证据。

**reranker 压力**（清空积压所需时间）：
```
W_R = P_R / μ̂_R                                                 (17)
```
- `P_R` = reranker 队列中未处理的 query-doc 对数
- `μ̂_R` = 实时估计的 reranker 吞吐

**LLM 压力**（当前 batch + 排队 batch 的剩余服务时间）：
```
T_remain = max[ T̂_L − (t_now − t_start), 0 ]                    (18)
W_L = T_remain + (|Q_L| / B_L) · T̂_L                            (19)
```

**预算决策**：
```
if W_R ≤ W_L:   D(q) = D_max              # reranker 不是瓶颈，用满
else:
    E_R = μ̂_R · (W_R − W_L)                                      (20)
    D(q) = max[ D_min, D_max − ⌈E_R / B_R⌉ ]                     (21)
```

**按整批削减**（`B_R` = reranker 批大小），不做零碎调整。

### 1.6 "Less can be more" 的准确表述

⚠️ **不要过度引申**。论文的原话是：

> evidence-dense 的 top-ranked candidates 能让**更小的 rerank 预算**达到**更高的最终 recall**。

即：**排序前缀变好之后，裁剪预算不再损失 recall，反而可能因为噪声减少而提升**。这不是"少检索总是更好"。

**实测数据点**：HotpotQA 上 PACE 在 `D=20` 的 evidence recall ≈ 最佳 baseline 在 `D=40` 的水平——**用一半预算打平**。

---

## 二、为什么朴素多样性启发式会失败（PACE 的关键负面发现）

PACE 对比了 4 个 training-free 重排 baseline，结论**反直觉**：

| 方法 | 结果 | 原因 |
|---|---|---|
| **MMR** | ❌ 常常**不如**原始 dense 排序 | 惩罚相似文档，但**多跳的支持文档常常语义相关且共同必需** |
| **Dartboard** | ❌ 同上 | 同上——"多样化"假设在多跳场景不成立 |
| **Rocchio PRF** | ⚠️ 有时受益，但**对初始噪声敏感**，可能 query drift | 扩张查询向量 |
| **Adaptive-K** | ⚠️ 召回被原 dense 排序在所选位置处的召回**上界**卡住（因为它不重排） | 只选 D 不重排 |

**核心教训**：**"相似 = 冗余"是错的**。多跳里两篇都相关的文档可能分别提供"桥接事实"和"终点事实"，去掉任一篇都会断链。多样性启发式把"共同必要"误判为"重复覆盖"。

**这与 UpliftMem 的发现完全一致**：集合级 uplift 不可加（`G(m1)=G(m2)=−a` 但 `G(m1,m2)=b>0`）。单篇打分累加会系统性错过互补组合。

**消融验证相关性权重必要性**：
- `w/o query & anchor relevance`：`F(S) = Σ_v q(v)·max_{d_i∈S}[d_i(v)]`（Eq.22，丢掉 `ρ`）
- `w/o query relevance`：Eq.9 中令 `b_j = 0`（只有锚相关性）
- `w/o anchor relevance`：Eq.9 中令 `ā_j = 0`（只有直接相关性）
→ 去掉任一项都会**削弱** complete evidence recall。两项**共同**必要。

---

## 三、SetR：LLM 侧的集合选择（不训练也能用）

SetR 是**训练**方案（Llama-3.1-8B-Instruct + 40k GPT-4o 标注），但它的**提示词策略**可以直接零样本复用。

### 3.1 信息需求识别（IRI）三步法

```
(1) 枚举回答该问题所需的关键信息需求
(2) 对每个需求，识别包含相应信息的 passage
(3) 选择一个能 collectively 最全面、最互补地覆盖这些需求的 passage 子集
```

### 3.2 与普通 rerank 的区别（关键）

- **不强制**包含所有候选
- **不强制**任何排序 / 顺序（输出是集合）
- **不需要手选 K**——模型自己决定选几个

### 3.3 消融揭示的双组件贡献

| 变体 | 说明 |
|---|---|
| `SetR-CoT & IRI` | 完整：CoT + 显式信息需求识别 |
| `SetR-CoT` | 只有通用 "Let's think step by step" CoT，**无**显式需求识别 |
| `SetR-Selection only` | 无推理，只输出选择结果 |

结论：**set-wise 选择范式**和 **CoT 需求识别**各自独立贡献，两者都增强信息覆盖并**有效拒绝负候选**。

实测（BM25 后 + 5 篇给生成器）：HotpotQA EM 26.90 → 32.20；MuSiQue F1 8.22 → 11.07。
⚠️ 注意 SetR 只输出 **2.48–2.95 篇**（少于 baseline 的固定 5 篇）却效果更好——**变长选择本身就是收益来源**。

### 3.4 实操配方（可零样本落地）

```
输入: 问题 + 编号候选段落 [1]p1 [2]p2 ... [n]pn
提示: "I will provide you with {n} passages, each indicated by a numerical identifier.
      1) 列出回答该问题需要的关键信息需求;
      2) 指出每个需求由哪些 passage 覆盖;
      3) 选择一个能最全面互补地覆盖全部需求的子集。"
输出: 选中的编号集合（不要排序，不要理由）
```

---

## 四、DPS：变长子集的自回归建模

若要**训练**一个选择器，DPS 给出最直接的形式化。

### 4.1 建模

```
P_θ(S | q, P) = Π_{j=1}^{k} P_θ( i_j | q, P, i_{<j} )      # k 不固定！
```

- `S` 表示为**有序索引序列** `(i_1, ..., i_k)`
- 自回归分解同时编码了：查询对齐（条件化 `q`）+ **冗余/互补感知**（条件化 `i_{<j}`）
- **生成即终止** → 无需预设子集大小

### 4.2 输入输出格式

```
Input : "Query: {q}\nPassages: [1]p1 [2]p2 ... [n]pn"
Output: "i1, i2, ..., ik"    # 直接预测索引
```

### 4.3 训练配置（可复现）

| 项 | 值 |
|---|---|
| 基座 | Qwen2.5-7B + **LoRA** |
| 硬件 | 4× A100, DeepSpeed ZeRO |
| 超参 | 1 epoch, lr 1e-4, warmup ratio 0.05 |
| 数据 | MS MARCO 100k（~95% 单跳）+ HotpotQA 90k + MuSiQue 20k + GPT-4o 合成 5k（长上下文/高层级） |
| 检索 | BGE-M3 统一取 top-30 候选（对所有方法公平） |
| 生成器 | Qwen2.5-7B |

**难度感知的数据构造**：单跳 QA 当作"容易样本"，多跳/复杂查询当"困难样本"混合训练。

### 4.4 结果

DPS vs 各 baseline（F1）：

| 数据集 | BGE-reranker-v2-m3 | Qwen3-reranker-8B | RankingGPT | **DPS** |
|---|---|---|---|---|
| HotpotQA | 45.46 | 47.37 | 48.10 | **53.28** |
| MuSiQue | 19.14 | 22.08 | 24.98 | **28.85** |
| 2WikiMQA | 23.44 | 32.20 | 36.39 | **46.13** |
| Legal (OOD) | 23.92 | 22.10 | 21.48 | **28.72** |
| CS (OOD) | 19.47 | 19.94 | 18.32 | **29.37** |

**OOD 数据集上优势更明显**（Legal +20%，CS +55% vs Qwen3-reranker）——集合级选择比相关性排序泛化更好。

### 4.5 关键诊断：K 的最优值依 query 而变

论文实测：**HotpotQA 最优 K=5，MuSiQue 最优 K=3**。
- K 从 2→8：HotpotQA recall +13.21%，MuSiQue recall **+53.26%**
- 但 F1 在超过最优 K 后**急剧下降**（无关内容稀释有效证据）

→ **这是"固定 Top-K 是根本缺陷"的最硬证据**。任何按 query 自适应 K 的方法都在用同一条线索。

---

## 五、落地决策树

```
需要给 LLM 几篇文档？
├─ 快速验证 / 无训练资源
│   └─ 零样本 SetR IRI 提示词（§3.4）+ 让模型自己决定选几篇
│       └─ 关键：允许输出 < K 篇，不排序
├─ 有训练资源 / 需要稳定复现
│   └─ DPS 路线：自回归索引预测（§4）
│       └─ 或 SetR 蒸馏（Llama-3.1-8B + 40k 标注）
├─ 有 serving 压力 / 要控 p95 延迟
│   └─ PACE 训练无关双组件（§1）
│       ├─ ① 边际覆盖 greedy 前缀重排（要求稀疏非负表示）
│       └─ ② 压力自适应预算 D(q)（要求能观测队列长度 + 吞吐）
└─ 只是要诊断"检索结果为什么凑不齐答案"
    └─ 算 evidence recall@D（§6），而不是只看 NDCG/EM
```

### ⚠️ 前提条件（易踩坑）

1. **必须用非负稀疏表示**（SPLADE 类）。稠密向量有负分量 → `d_i(v) ≥ 0` 不成立 → 次模性证明崩塌。BM25 的原始 TF 也不行（需非负且未归一化，论文用的是 learned sparse）。
2. **PACE 的 `ρ` 需要锚集合** `B`。若没有 query-doc 相关性分数就没有锚，需要先有检索器分数。
3. **压力自适应预算需要在线可观测量**：`P_R`（队列长度）、`μ̂_R`（吞吐）、`|Q_L|`、`B_L`、`T̂_L`。批处理系统里这些要能从 metrics 端点拿到；拿不到就只能用固定 D 或离线启发式（Adaptive-K）。
4. **DPS/SetR 需要索引 token 化的段落输入**，长文档需先切段。

---

## 六、评估：必须用 evidence recall，不能只看 EM/NDCG

只看最终答案质量（EM/F1）会**掩盖**选择器的机制差异。必须直接测：

- **complete evidence recall@D**：top-D 文档包含**全部** gold 支持证据的 query 百分比
- **supporting evidence recall@D**：top-D 覆盖的 gold 证据平均比例
- **IC@k**（SetR 用的信息覆盖）：
  ```
  IC@k = |⋃_{i=1..k} ({e ∈ p_i} ∩ E_gold)| / |E_gold|
  ```
  `p_i` = 第 i 篇排名段落，`E_gold` = 标注的全部 gold 证据跨度

**测 D 的扫描范围**：HotpotQA/2Wiki 用 `D = 1..100`；MuSiQue 是 closed-context（最多 20 段候选），用 `D = 1..20`。

**为什么重要**：PACE 的核心主张是"用一半预算达到同等召回"——这个主张**只在 evidence recall 曲线上可见**，用 EM 测会被生成器噪声淹没。

---

## 七、诚实边界

1. **PACE / DPS 代码均未公开**。只有 SetR 公开（BSD-3-Clause，28 stars，2025-09-11 最后 push）。复现 PACE 需自行实现 greedy 边际覆盖 + 软锚精化。
2. **PACE 的实验环境窄**：单张 Quadro RTX 6000（~22GB 可用），splade-v3 检索 + `trecdl22-crossencoder-debertav3` reranker + Provence 压缩 + Qwen2.5-3B-Instruct 生成。压力自适应结论是否在更大模型/多 GPU 成立**未验证**。
3. **"less can be more" 的条件是排序前缀已 evidence-dense**。在没有边际覆盖重排的普通系统上，缩小预算仍会掉 recall——不能直接推广。
4. **PACE 假设 `q(v) ≥ 0`**，这排除了大部分稠密/对比学习表示。若要用于稠密检索，需换目标函数（次模性保证会丢失）。
5. **次模性是数学性质，不是经验结论**。定理保证的是"贪心 ≥ 63% 最优覆盖"，**不保证**"覆盖 = 答案质量"。答案正确性还要经过生成器，论文里的 EM 提升幅度远小于 recall 提升幅度。
6. **SetR/DPS 的收益依赖任务**。主要在 multi-hop QA 上验证；单跳问题上选择器退化为 Top-1（这本身没问题，但别当成普适收益）。
7. **MMR/Dartboard 失败的结论限定在多跳 QA 数据集上**（HotpotQA / MuSiQue / 2WikiMultiHopQA）。单跳或事实型 QA 上多样性启发式仍可能有用。
8. **DPS 论文内部有表述不一致**：正文称 "plug-and-play ... without fine-tuning process"，但方法明确是 SFT 训练 Qwen2.5-7B + LoRA。以方法章节为准。
9. **SetR 的训练数据来自 MS MARCO 排序数据**（top-20 候选 + GPT-4o 零样本标注），与 DPS 的数据构造不同。两者不是同一基线，不能直接比数字。

---

## 八、与其他技能的关系

| 技能 | 层级 | 区别 |
|---|---|---|
| `uplift-rag` | **单篇** uplift | 定义"这篇文档对 LLM 有多少边际价值"（反事实）；本技能是**集合级**——但集合级 uplift 不可加，见 `upliftmem-evsi-probing` |
| `upliftmem-evsi-probing` | 集合级 uplift（记忆场景） | 结论互补：单篇打分累加会错过互补组合 → 必须集合级 |
| `rag-eval-validity-composition` | 评估效度 | 本技能是"选什么"，它是"你怎么知道选对了"——用 evidence recall 而非 EM 测，正是它的效度纪律 |
| `a-rag` | 检索粒度 | 那是"检索什么粒度"，本技能是"检索到之后选哪几篇" |
| `disco-rag` | 话语结构 | 用 RST 解决 chunk 粒度错配；本技能用边际覆盖解决**集合互补性**错配 |
| `r2r-agentic-rag` / `reflective-rag` | 迭代式 RAG | 迭代获取 vs 一次性选集；可叠加（先 PACE 选前缀，再迭代扩链） |

**统一心智模型**：
```
单篇 uplift      →  "这篇有用吗？"          (per-doc counterfactual)
集合 marginal    →  "这篇在当前集合里补什么？"  (set-dependent gain)
集合 uplift      →  "这个集合整体值多少？"     (non-additive, 需集合级监督)
evidence recall  →  "集合覆盖全了吗？"          (选择器的直接度量)
```

---

## 九、来源

- PACE: https://arxiv.org/abs/2608.25115 — "Less can be More: Relieving RAG Bottlenecks via Evidence Frontloading and Pressure-Adaptive Budgeting", Cai & Zafarani, 2026-08-25
- DPS: https://arxiv.org/abs/2508.09497 — "From Ranking to Selection: A Simple but Efficient Dynamic Passage Selector for RAG", Meng et al., 2025-08-13
- SetR: https://aclanthology.org/2025.acl-long.861/ + https://arxiv.org/abs/2507.06838 — "Shifting from Ranking to Set Selection for RAG", Lee, Jo, Park, Lee (LG AI Research), ACL 2025
- SetR code: https://github.com/LGAI-Research/SetR (BSD-3-Clause, 28★)
- DISCo: https://k-rt-k.github.io/DISCo/ — 稠密子集索引，把 coverage 变可索引
- ielab/llm-rankers: https://github.com/ielab/llm-rankers — setwise ranking (heapsort) 实现参考
- UpliftMem: https://arxiv.org/abs/2609.36805 — 集合级 uplift 不可加的反例

---

## 相关技能（跨层互补）

- `research/skillaligner-execution-time-adaptation` — **技能层**的执行时适配。本技能管"要不要调这个工具"，
  SkillAligner 管"检索到的技能在这次执行里该怎么用"。两者是同一套"相关不等于有用"的判据
  在工具层和技能层上的两次应用。SkillAligner 实测：语义相关的技能会让 5.80%–17.91% 的原本成功任务变失败，
  且更强的 backbone 并不免疫（Gemini 2.5 Pro 11.42% vs Qwen3-8B 10.30%）。
- `research/set-level-evidence-selection` — 集合级选择优于逐篇 Top-K。SkillAligner 的 composition 阶段
  把同一洞察用在了跨技能之间（合并重叠、按依赖排序、冲突按「硬约束 > 环境规格 > 技能建议」裁决）。

