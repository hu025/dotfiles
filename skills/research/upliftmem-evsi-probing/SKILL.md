---
name: upliftmem-evsi-probing
description: UpliftMem — 集合级 execution uplift + EVSI 主动探测，学习 agent memory 检索并解决"反馈覆盖偏差"。Use when designing memory/skill retrieval trained on execution feedback, choosing what to evaluate next, or diagnosing "retrieved memory never helps".
triggers: [upliftmem, set-level uplift, execution uplift, EVSI, expected value of sample information, probe allocation, feedback coverage, active acquisition, 集合级增益, 主动探测, 反馈覆盖偏差, 记忆检索效用, decision-aware probing]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: arXiv:2609.36805 (Under review as a conference paper at ICLR 2027) — Mengkun Liang, Haoran Qiang, Guannan Liu, Junjie Wu (MIIT Key Lab of Data and Decision Intelligence, Beihang University)
code: **未公开**（2026-10-24 核验 github.com/mengkunLiang/UpliftMem 返回 404，论文正文无代码链接）
related_work: https://arxiv.org/abs/2605.06132 (MemReranker) / https://arxiv.org/abs/2608.06880 (SkillAligner) / https://arxiv.org/abs/2607.01071 (MemSyco-Bench) / https://arxiv.org/abs/2601.03192 (MemRL) / https://arxiv.org/abs/2603.28716 (Dynamic Dual-Granularity Skill Bank)
tags: [agent-memory, uplift, evsi, active-acquisition, probe, feedback-coverage, retrieval-learning, iclr-2027-review, hermes-self-improvement]
---

# UpliftMem — 用集合级执行增益学检索，并用 EVSI 决定"下一步该测什么"

## 概述

**一句话**: 检索器按相关性排序，但**相关的记忆不一定让执行变好**。UpliftMem 把记忆检索学成"集合级 execution uplift"（有记忆 vs 无记忆，同一 executor 的效用差），并解决了这个学习问题里最隐蔽的一个陷阱——**只有被执行过的记忆集才有标签，没被选中的集永远得不到反馈，于是低估的集永远选不上（反馈覆盖偏差）**。解法是用 **EVSI（expected value of sample information）**在执行前就决定"这次 rollout 该花在哪个候选记忆集上"。

**为什么这篇值得单独看**: 它是 `uplift-rag` 技能（单文档 uplift、EMNLP 2025 Findings）在**两个维度上的推进**：
1. 从**单文档** → **集合级**（集合内成员有互补/冗余/冲突，单篇 uplift 不可加）
2. 从"离线标注" → **主动采集**（预算有限时，去测哪些未被观测的集合）

而且它引入了前作完全没有的东西：**决策导向的主动学习**。这不是"再训一个 reranker"，而是"我该花下一次 API 调用去测什么"。

---

## 一、核心定义：execution uplift

### 1.1 效用函数（含成本项）

```
U(τ) = R(τ) · ( 1 + γ · I[R(τ) ≥ ρ] · ( 1 − C(τ)/C_max ) )      (Eq.1)
```

- `R(τ) ∈ [0,1]`：任务表现（成功率/reward）
- `C(τ) ∈ [0, C_max]`：执行成本（ALFWorld/WebShop 计**动作步数**；BigCodeBench 计**注入证据 token 数**）
- `γ ≥ 0`：效率加成权重；`ρ`：性能阈值

**为什么必须把成本放进效用**: 同样成功的两次执行，资源消耗可能差很多。纯成功率无法区分。论文特别指出 BigCodeBench 的成本口径是"注入的实现证据 token"，且**排除**记忆标题、作用域元数据、任务 prompt 和生成代码本身——即只算"记忆内容本身的 token 成本"。

### 1.2 Uplift 定义

```
Δ(c, S) = V(c, S) − V(c, ∅)          (Eq.3)   ← 集合 S 相对无记忆执行的期望效用差
y_S     = U(τ(c,S)) − U(τ(c,∅))      (Eq.4)   ← 配对执行观测到的标签
G_θ(c, S) ≈ Δ(c, S)                  (Eq.9)   ← 可学习的集合打分器
G_θ(c, ∅) = 0                                      ← 空集约定锚定
```

**关键点**: 因为 `V(c,∅)` 与 `θ` 无关，所以目标里用 `Δ` 替代 `V` 不改变最优参数 —— **无记忆基线既是参照系，也是一个显式的合法选项**（检索可以返回空集）。

### 1.3 论文 Figure 1(a) 的失败案例（这才是动机）

> 任务："找一个 $60 以下的防水背包"
> 相似度排序：`m_A > m_C > m_B`。`m_A` 推荐"popular waterproof"，`m_B` 是"apply the price filter"。
> 结果：agent **不用记忆就能成功**（浏览 → 检查防水 → 选 $49 防水包），但听 `m_A` 的话**买了 $89 的**。
> 观测 uplift：`ΔU({m_A, m_C}) = U(τ_记忆) − U(τ_∅) < 0` → **失败**。

这就是 `uplift-rag` 里 45.20% "misleading-doc" 现象在 agent 场景的重演：**高相关性的记忆把本来会成功的执行搞失败了**。

---

## 二、理论：反馈覆盖偏差（本文最硬的部分）

### 2.1 Proposition 1：选择性检索抑制替代观测

定义**累积动作亏损**（cumulative action deficit）：对一条采样路径 `a = (a₁,...,a_L)`，

```
d(a) = Σ_t max_{a'∈A(c,S_{t-1})} g_θ(a|c,S_{t-1}) − g_θ(a_t|c,S_{t-1})        (Eq.7)
```

则普通检索返回集合 B 的概率满足：

```
p_B ≤ Σ_{a∈P(B)} exp( −d(a)/τ_tr )        (Eq.8)
```

**读法**: 路径上每一步"没选最优动作"的亏损会指数级衰减该路径的概率。**一个集合越不受偏好，它被执行的概率就越低，越拿不到标签，越估不准，越不会被选中** —— 这就是自我强化的反馈覆盖偏差。

论文给的**互补性例子**（Appendix A.1）非常关键：

```
G_θ(c,{m₁}) = G_θ(c,{m₂}) = −a  (a>0)      ← 单看两篇都是负的
G_θ(c,{m₁,m₂}) = b > 0                        ← 合起来是正的！
→ p_{m₁,m₂} ≤ min{1, 2e^(−a/τ_tr)}
```

**两种构造顺序都计入上界**。这说明**只按单篇边际增益做贪心检索会系统性地错过互补组合** —— 单篇 uplift 是负的，但集合 uplift 是正的。集合级建模不是"更精细"，是**必要**。

### 2.2 Corollary 3：直接证据到达时间

```
E[N_B(n)] ≤ n·p̄_B ,   Pr(N_B(n)=0) ≥ max{0, 1 − n·p̄_B}
若 p_B > 0，则首次执行 B 的期望时间 E[T_B] ≥ 1/p̄_B
若 p_B = 0，则 T_B 几乎必然为无穷
```

**实践含义**: 一个集合在 n 次普通执行里一次都没被选中是可以量化的下限。被系统性压制的集合，需要**主动**去测。

### 2.3 Proposition 4：未观测替代集不可辨识

存在两个环境使 `Δ(c,B)` 符号相反，但在 B 从未被执行时，n 次普通执行（含无记忆参照）的观测分布**完全相同**。最坏情况符号错误率下界：

```
max_v Pr( ẑ_n ≠ sign(Δ_v(c,B)) ) ≥ ½ · (1 − p_B)^n
```

若 `p_B = 0`，**符号完全不可辨识**。

**这是本文的理论支点**: 光靠"多跑普通 rollout"无法解决被压制的集合，必须**改变观测分布**（= 主动探测）。

### 2.4 A.3：策略变化下的版本

策略在线更新时用历史依赖版本：若 `p_t(B|H_{t-1}) ≤ ε_t`，则

```
E[N_B(n)] ≤ Σ_t ε_t ,   Pr(N_B(n)=0) ≥ max{0, 1 − Σ_t ε_t}
```

并给出一个**探测批次单独贡献的覆盖率**公式（Eq.26）：

```
Pr(至少一次直接观测) = 1 − (1−p_B)^n · (1−r_B)
```

其中 `r_B` 是独立探测批次选中 B 的概率。**这个分解清楚地隔离了"探测批次到底补了多少覆盖"**。

---

## 三、方法：EVSI 决策导向探测

### 3.1 局部高斯代理模型

```
G̃(c,S) = G_θ(c,S) + φ(c,S)ᵀ ξ ,   ξ ~ N(0, Σ)        (Eq.9)
```

- `φ(c,S) ∈ R^d`：任务-集合特征向量；`Σ`：半正定协方差
- 潜变量 `ξ` 描述**期望 uplift 的不确定性**；执行随机性由**独立的噪声模型** `ε_Q` 描述（Appendix A.4 明确区分这两者）

**测量模型**：

```
y_Q = μ_Q + Φ_Q ξ + ε_Q ,   ε_Q ~ N(0, Ω_Q)             (Eq.27)
```

**共享无记忆参照导致的噪声相关**（重要且容易被忽略）：

```
Ω_Q = diag(ν₁²,...,ν_n²) + ν₀² · 1 1ᵀ                    (Eq.32)
```

即所有辅助执行共享同一条无记忆基线 → 它们的噪声**正相关**。多个独立基线组时用 `Ω_Q = D_assist + Z D₀ Zᵀ`（`Z` 是成员指示矩阵）。

**条件高斯**：

```
E[g_j | D, y_Q] = μ_j + k_jᵀ W_Q⁻¹ (y_Q − μ_Q)          (Eq.29)
Var(g_j | D, y_Q) = σ_j² − k_jᵀ W_Q⁻¹ k_j                (Eq.30)
σ_j² = h_jᵀ Σ h_j ,  k_j = Φ_Q Σ h_j ,  W_Q = Φ_Q Σ Φ_Qᵀ + Ω_Q
```

**可解析的已解决方差**（执行前就能算出）：

```
s_j²(Q) = k_jᵀ W_Q⁻¹ k_j                                (Eq.31)
```

### 3.2 Theorem 2：一次探测对一次决策的价值

对局部比较 j（两个候选集的效用差），设 `μ_j` 是当前期望差、`s_j(Q) > 0` 是探测后能解决的标准差：

```
E_j(Q) = E_{y_Q}[ |μ_j + (μ_j)⁺ − (μ_j)⁺ |_{s_j(Q)} ]
       = s_j(Q) · ψ( |μ_j| / s_j(Q) )
ψ(t) = φ(t) − t·Φ(−t)                                    (Eq.11)
```

**读法**: 这是标准正态的"正部期望"。当 `μ_j = 0`（正负难分）时值最大；当 `|μ_j|` 相对 `s_j` 很大（胜负已定）时值趋于 0。**EVSI 同时奖励"不确定"和"接近决策边界"**。

**Corollary 6 的两个偏导**：

```
∂E/∂s = φ(a/s) > 0        （不确定性越大越值得探测）
∂E/∂a = −Φ(−a/s) < 0      （决策差距越大越不值得探测）
0 ≤ E_j(Q) ≤ s_j(Q)/√(2π) ≤ σ_j/√(2π)
```

**机会损失解释**（A.5）：EVSI 就是**决策机会损失的期望减少量**。观测前的损失 `E[(g_j)⁺|D] − (μ_j)⁺`，观测后是 `E[(g_j)⁺|D] − E[μ_j′⁺]`，两者之差恰为 `E_j(Q)`。

### 3.3 与信息增益（EIG）的关系

对高斯 margin：

```
I(g_j; y_Q | D) = ½ log₂( σ_j² / (σ_j² − s_j²(Q)) )        (Eq.41)
```

**单个固定比较内，MI 和二元 EVSI 对探测的排序完全一致**（因为 `μ_j`、`σ_j` 固定）。但**跨比较时，EVSI 额外考虑了决策差距和效用尺度**，而 MI 不考虑。

→ **这正是论文选择 EVSI 而非 EIG 的理由**，也是它优于 MC-STD / EIG 的原理（实验见 §四）。

另一个有意思的边界条件（A.6 末尾）：若连续 margin 被精确揭示，MI 发散，而二元 EVSI 收敛到**有限的最优信息期望值**。

### 3.4 有限族选择与 EVSI 的关系（Proposition 7）

```
max_k E_k(Q) ≤ E_B(Q) ≤ Σ_k E_k(Q)          (Eq.38)
```

`E_B(Q)` 是"从 J 个候选里选一个"的有限族 EVSI（knowledge-gradient 的标准量，Eq.37）。**二元比较之和是有限族 EVSI 的上界**；反过来，`max_k E_k` 是下界。

论文明确指出一个**陷阱**：如果比较族 `G` 包含重复比较，同一个决策改进会被**重复计数**。例子：`F₁ = F₂ = Z`, `F₀ = 0` 时 `E₁ = E₂ = E[(Z)⁺]` 但 `E_B = E[(Z)⁺]` —— **双倍计数**。所以比较族必须**去重且方向一致**（反转两个选项不改变二元 EVSI）。

### 3.5 批量采集（Batch Acquisition）

聚合局部比较族：

```
H(Q) = Σ_{j∈G} E_j(Q)
V_t(q) = Σ_j [ E_j(Q_t ∪ {q}) − E_j(Q_t) ]                (Eq.12)
```

**逐次更新**（A.7 的 block Gaussian conditioning）：

```
κ_{jq|Q} = Cov(g_j,y_q) − Cov(g_j,y_Q) W_Q⁻¹ Cov(y_Q,y_q)
v_{q|Q}  = Var(y_q) − Cov(y_Q,y_q) W_Q⁻¹ Cov(y_Q,y_q)
s_j²(Q∪{q}) = s_j²(Q) + κ_{jq|Q}² / v_{q|Q}                (Eq.45)
```

**下一个探测的采样分布**：

```
p_t(q) = exp(V_t(q)/τ_evsi) / Σ_{q'∈Q_t} exp(V_t(q')/τ_evsi)   (Eq.49)
```

实际实现用**带熵正则的软最大值**目标：`max_p Σ_q p(q)V_t(q) + τ_evsi·H(p)`。

**重要性质（A.7）**: `H(Q)` 对追加观测**单调不减**，但**边际增益不一定递减**。论文给了反例：`X,Y` 独立标准高斯，`g = X`，探测 `y₁ = X+Y`（无噪）与 `y₂ = Y`。`y₂` 单独看对 `g` 零信息，但**在 `y₁` 之后它能完全揭示 `g`** —— 第二个探测的边际价值**上升**。

→ **这意味着贪心式的 batch 构造并非唯一解，"相关性"反而是好事**：一次探测可以为后续探测"解锁"信息。这与常规 active learning 的直觉相反，值得记住。

**数值细节**: 用 Cholesky 分解解 `W_Q`，不显式求逆；完全冗余的观测（`v_{q|Q}=0`）边际贡献定义为 0。

### 3.6 候选探测集构造（B.2）

对每个任务，可行候选 = **当前选中的集合 S** + **S 的一记忆编辑**：

- 删除：`S \ {m}`
- 增加：`S ∪ {m'}`
- 替换：`(S \ {m}) ∪ {m'}`，其中 `m ∈ S`, `m' ∈ C(c) \ S`

也作用于检索路径的前缀。比较族 `G` 包含：保留/扩展是否改变效用的比较、替换共享基座后哪个延续更好的比较、以零为参照的停止比较。

> **只探"一记忆编辑"这一层邻域，不做全组合搜索** —— 组合爆炸被结构性规避。

### 3.7 集合构造与检索（B.1）

**条件增益**（关键设计）：

```
g_θ(m|c,S) = G_θ(c, S ∪ {m}) − G_θ(c, S)
g_θ(STOP|c,S) = 0
```

**遥推恒等式**（Eq.48）：

```
Σ_t g_θ(m_t|c,S_{t-1}) = G_θ(c, S_L) − G_θ(c, ∅) = G_θ(c, S_L)
```

即**累积条件增益 = 终态集合值**。所以搜索应该按 `G_θ` 排完整集合，而不是按路径似然排（路径概率含状态相关的归一化项，不可比）。

**训练时**: 按条件增益 softmax 采样（Eq.6，温度 `τ_tr`）。
**测试时**: **beam width = 2**，跨深度 archive 保留最高值集合（含 `∅`），每个父节点保留至多 2 个扩展。

> **一个反直觉但重要的设计**：**保留中间即时增益为负的集合**，让后续添加能暴露互补性。这正是 §2.1 那个 `m₁,m₂` 互补例子的工程解法。

**复杂度**: `O(W·N·K)` 次集合打分（N = 候选池大小，K = 记忆数上限）。

---

## 四、学习目标

### 4.1 值损失（三项）

```
L_reg  = E[ w_mag(y_S) · Huber_δ( G_θ(c,S) − y_S ) ]                          (Eq.13)
L_sign = E_{|y_S|>ε_sign}[ BCEWithLogits( G_θ(c,S), I[y_S > 0] ) ]              (Eq.14)
L_pair = E_pair[ softplus( −sign(y_Sa − y_Sb)·(G_θ(c,Sa) − G_θ(c,Sb)) ) ]        (Eq.15)

L_value = λ_reg·L_reg + λ_sign·L_sign + λ_pair·L_pair                        (Eq.16)
```

- `w_mag(y) = max{w_min, min(1, |y|/τ_ref)}` —— 按增益幅度加权
- `L_sign` **排除近零观测**（`|y| ≤ ε_sign`）—— 因为符号判定对近零标签没意义
- `L_pair` 要求同一任务、**同一实现的无记忆参照**、且 `|y_a − y_b| > ε_rank`

**"同一参照"这个约束很关键**：不同参照的标签带着不同的噪声，不同参照的差值有偏。

### 4.2 策略损失：结果加权的检索路径学习

```
L_policy = −E_i[ sg(ω_i) · (1/L_i) · Σ_{t=1}^{L_i} log π_θ(a_{i,t} | c_i, S_{i,t-1}) ]   (Eq.17)
```

带符号的裁剪权重：

```
ω_i = 0                              |y_i| ≤ ε_policy
    = min(y_i, A_max)                y_i > ε_policy
    = η_neg · max(y_i, −A_max)       y_i < −ε_policy
```

**机制**: 正权重强化被采样的动作，负权重抑制它们，零权重不贡献策略梯度。`η_neg ∈ [0,1]` 让负反馈的惩罚强度可调。路径长度 `L_i` **包含采样的终止 STOP**。

**训练顺序**: 先 **value-only warm-up**，再联合更新 `L_value + L_policy`，**executor 全程冻结**。只使用最新一批路径（不重放旧批次）。

### 4.3 打分器参数化（C.1）

- 基座：**Qwen3-Reranker-0.6B**（LoRA 微调，rank 8 / α 16 / dropout 0.1）
- 把任务当 query、**完整记忆集当 document** 打分
- 取 yes/no token 的 logit 差 `z_θ(c,S)`
- 仿射校准到效用单位：`G_θ(c,S) = a·z_θ(c,S) + b`（`a,b` 与 LoRA 联合优化）
- `G_θ(c,∅) = 0`

### 4.4 执行验证的记忆写入（B.3）

从完成的轨迹蒸馏候选记忆 `M₀`，然后**在源任务上单独验证**：

```
u_k = U(τ_{M_k}) − U(τ_∅)                                   (Eq.50)
```

- `u_k > τ_accept(=0)` → **立即接受**
- 否则用 LLM 反思修订 `M_k → M_{k+1}`，**最多 T=3 次修订**，同时单独追踪最高 uplift 版本
- 最终版本 = 首个过阈值的版本，或预算耗尽时的最高 uplift 版本
- **无论是否入库，都进入监督集 `D_v`**（"监督但不采纳"）

> **这一点对 Hermes 特别有启发**: 一条经验即使没被采纳，只要它提供了信息（负向 uplift 也是信息），也该被记录下来。当前 Hermes 的 memory 写入门槛常常是"有没有用"，这里说明**负结果同样值得留档**——它能防止同一个坏经验被反复召回。

---

## 五、实验结果

### 5.1 端到端（Table 1，SR%，Qwen3-4B / 8B）

| 方法 | ALFWorld Seen | ALFWorld Unseen | WebShop SR | BCB SR |
|---|---|---|---|---|
| ReAct | 43.13 / 57.14 | 50.00 / 76.87 | 38.00 / 41.60 | 31.87 / 40.35 |
| BM25-RAG | 59.28 / 75.71 | 52.23 / 70.15 | 37.60 / 41.80 | 33.33 / 40.35 |
| Mem0 | 75.71 / 70.00 | 67.16 / 77.61 | 43.60 / 33.80 | 35.09 / 40.64 |
| MemGPT | 57.14 / 52.86 | 65.67 / 64.18 | 40.20 / 40.40 | 38.01 / 41.52 |
| A-MEM | 57.86 / 58.57 | 58.96 / 61.19 | 39.60 / 33.20 | 33.04 / 38.30 |
| LightMem | 64.29 / 66.43 | 67.91 / 77.61 | 40.40 / 37.80 | 35.96 / 41.81 |
| **UpliftMem** | **76.86 / 81.43** | **70.91 / 79.10** | **45.60 / 44.00** | **39.77 / 42.69** |

同时在 ALFWorld seen 上**步数最少**（14.01 / 13.61）。

**注意基线不是稻草人**：Mem0 的 4B ALFWorld seen 就是 75.71，UpliftMem 4B 是 76.86（+1.15）；8B 上差距拉大（81.43 vs 70.00）。**弱 executor 上增益更明显**。

### 5.2 固定记忆库下的纯检索评估（MemSyco-Bench）

把各记忆系统的原生检索器换成 UpliftMem，**记忆内容与 executor 固定不变**（这是关键的隔离设计）：

| 指标 | Native | UpliftMem (4B) | UpliftMem (8B) |
|---|---|---|---|
| Decision ↑ | 41.7 / 44.4 | **66.5** | **68.8** |
| Syco. ↓ | 49.0 / 40.0 | **29.5** | **16.5** |
| Select ↑ | 54.3 / 61.1 | **61.6** | **70.7** |
| Old ↓ | 47.0 / 40.8 | **39.3** | **31.7** |

**Decision 准确率 41.7% → 66.5%（4B）**，**谄媚率 49.0% → 29.5%**。

场景级增益（Figure 3）：
- Scope Control 准确率 +23.7 ~ **+62.7** pp（4B）
- Evidence Conflict 准确率 +29.1 ~ **+54.6** pp（8B）
- Valid Selection：**10 个 store×executor 组合全部提升**，9 个组合的 outdated-memory 使用下降

**这组数字对 Hermes 最有价值**: 记忆库一模一样，只换"选哪几条"，决策准确率就 +25 pp。**检索决策的杠杆远大于记忆内容本身**。

### 5.3 消融（Table 2 + Table 3）

ALFWorld Seen SR（4B / 8B）：

| 变体 | ALFWorld Seen | Decision (4B/8B) |
|---|---|---|
| Base reranker（不训） | 68.57 / 65.00 | 43.1 / 44.5 |
| Warm-up only | 64.76 / 66.19 | 49.6 / 48.8 |
| **Random probing**（同预算） | 66.07 / 72.85 | 55.9 / 54.9 |
| w/o policy loss | 71.42 / 70.71 | 56.7 / 56.1 |
| w/o value loss | 70.00 / 75.00 | 55.8 / 53.1 |
| **Full** | **76.86 / 81.43** | **66.5 / 68.8** |

**关键对比**: EVSI 引导 vs 同预算随机探测 —— Decision 准确率 **+10.6 pp (4B) / +13.9 pp (8B)**，谄媚率降 **9.2 / 14.8 pp**。

**反常识点**: **"Warm-up only" 比 "Base reranker" 在 4B 上更差**（64.76 vs 68.57 ALFWorld seen）。只做 value 适配而没有持续探测和策略学习，会**过拟合到 bootstrap 阶段的记忆分布**。

### 5.4 探测策略效率（RQ4，WebShop）

从同一 warm-up checkpoint 出发，比较 EVSI / Random / MC-STD / EIG，预算 {20,50,80,100,120,150,200}：

- **累积成功率**（截至当前预算至少被一个 checkpoint 解出的任务比例）：EVSI 在**每个非零预算都最高**，50 probes 时 **48.0% vs 随机 42.0%**
- 200 probes 时 EVSI 仍保持最高覆盖，平均 reward **0.694 vs 随机 0.670**

**覆盖差距随反馈增多而收窄，但 EVSI 始终领先**。

### 5.5 检索预算敏感性（RQ5）

MemSyco-Bench 上 `K ∈ {3,5,10}`，跨模型平均增益 **14.2 / 15.8 / 15.1 pp** —— **三个预算都为正**。随 K 增大，Evidence Conflict 增益上升而 Scope Control 增益下降（**纠错重点随上下文容量移动**）。

---

## 六、局限与诚实边界

1. **代码未公开**。2026-10-24 核验 `github.com/mengkunLiang/UpliftMem` 返回 **404**，论文正文也没有代码链接。**复现需自行实现全部内容**（EVSI 闭式解、LoRA 微调、批量采集），工程量不小。
2. **需要执行反馈 + 无记忆基线**。每个标签要**两次执行**（有记忆 / 无记忆）。真实生产环境拿不到 `U(τ_∅)` 就无法算 uplift。这是方法最根本的限制。
3. **依赖"每个候选集可独立执行"**。若记忆之间有强耦合（必须同时注入才有意义），一记忆编辑的候选邻域会漏掉关键组合。
4. **论文没有独立的 Limitations 章节**（ICLR 在审稿格式），也没有代码/复现细节 —— 审稿意见很可能在此攻击。
5. **统计强度有限**：每个配置**只训练一次**（"Each configuration is trained once"），ALFWorld/WebShop/BCB 评估 3 次、MemSyco 主结果 5 次，报的是**推理运行方差**而非训练方差。**单次训练 → 训练随机性的影响完全未知**。
6. **executor 是小模型**（Qwen3-4B / 8B）且**冻结**。结论是否能外推到 MiniMax-M3 或 Gemini 这类强模型、以及非冻结 executor，未验证。
7. **高斯代理模型是建模假设**。EVSI 闭式解依赖相关高斯代理；如果真实 uplift 分布重尾或非单调（Executor/Environment 有异常），EVSI 会误导采集。论文用 Corollary 6 和 Proposition 7 给了理论上的稳健性讨论，但没有实证检验代理模型的拟合质量。
8. **BigCodeBench 的 K=3 而 ALFWorld/WebShop K=5**，且 BCB 的记忆是"成功实现证据投影"（排除诊断性反思、源任务契约、源特定字面量）—— 跨基准的绝对数字**不可直接比较**。
9. **Utility 里的 `γ`（效率加成权重）、`ρ`（阈值）、`C_max` 的具体取值未在正文给出**（只说"within each benchmark protocol"）—— 复现时需自行设定，敏感度未知。

---

## 七、对 Hermes 的可落地启发

### 7.1 最通用的一条：给每条上下文做 uplift 归因

Hermes 每次往 prompt 里塞 skill / memory / tool context，本质就是 RAG 的文档选择。**做法**：对高价值上下文（尤其是自动召回的旧 skill、长期记忆条目），定期做一次配对评估 —— "不加它会答对吗？加了它变好还是变差？"。

**风险提示**（来自 Uplift-RAG 的 45.20%）：**高相关性的旧经验覆盖模型本来就对的答案**，是记忆系统最常见的失效模式。Hermes 的 skill 召回目前是纯相关性驱动的，**没有"这条 skill 到底帮没帮上忙"的反馈回路**。

### 7.2 记忆召回应允许"空集"和"负增益"

- `G_θ(c,∅) = 0` 是硬约束：**召回为空永远合法**。
- 论文的 STOP 动作 + 保留负增益中间态，说明**贪心 top-k 是错的**。Hermes 现在很多地方是"取 top-N 塞进去"，没有"这次一条都不需要"的选项。
- **集合级 > 单篇级**：两条单独都有害但合起来有用的组合存在（§2.1 的例子）。**只做单条打分 + 贪心累加会系统性错过这类组合**。

### 7.3 "监督但不采纳"：负结果也要留档

论文的写入规则：**记忆无论是否入库，都要提供 uplift 标签**。Hermes 的记忆写入门槛如果只看"有没有用"，会丢掉最有价值的一类信号 —— **"我试过这条路，走错了"**。这类负样本正是防止同一个坏经验被反复召回的关键。

### 7.4 反馈覆盖偏差是自进化系统的通病

Hermes 的自我进化有同构问题：**只有被选中的技能/策略才会产生结果数据 → 只有"被选中过的"才有改进依据 → 低估的永远选不上**。

论文给的解法可以抽象成通用流程：
1. 量化"覆盖率下限"：某个候选从未被尝试 → 它的估计必然不可信
2. 主动探测：**不要随机试**，按"这次观测能减少多少决策机会损失"排序
3. EVSI 的直觉版：**优先测那些"胜负未分"且"结果方差大"的候选**（`|μ_j|` 小、`σ_j` 大）

### 7.5 边际增益不递减 —— 与直觉相反

论文 §3.5 的反例：一次探测可能**为后续探测解锁信息**，导致边际价值**上升**。

→ 对 Hermes 的启示：做"要不要多花一次调用去探索"这类决策时，**不要套用常规 active learning 的"边际递减"直觉**。一次高质量的探索可能同时降低多个候选集的不确定性。

### 7.6 效用函数要把成本放进去

Hermes 评估任何 agent 行为时，如果只看"成功/失败"，会忽略**步数/token/时延**。论文的 `U(τ) = R·(1 + γ·I[R≥ρ]·(1 − C/C_max))` 给了一个可直接抄的框架：**达到阈值后再按成本打折**。

---

## 八、复现路线（因代码未公开）

**最小可行版本**（不需要训练神经网络）：

1. 选一批任务，对每个任务跑两次执行：有候选记忆集 / 无记忆 → 得到 `y_S`
2. 用 `y_S` 直接做检索打分（不训模型），验证"集合级 uplift 排序"是否比"相似度排序"好
3. 探测分配用 EVSI 的**简化版**：单比较 + 独立噪声（`Ω_Q` 退化为对角阵）→
   `E_j(Q) = s_j(Q)·ψ(|μ_j|/s_j(Q))`，其中 `s_j(Q) = k_jᵀ W_Q⁻¹ k_j`
4. 候选探测集 = 当前集合 + 一记忆编辑（增/删/换）

**完整版本**：
- 基座 Qwen3-Reranker-0.6B + LoRA（rank 8 / α 16 / dropout 0.1 / lr 1e-5）
- 三项值损失 + 结果加权策略损失
- 每 400 个处理任务触发一次采集，每次至多 300 次探测执行
- 召回 50 条候选，测试时 beam width 2，K=5（ALFWorld/WebShop）或 3（BCB）
- 执行器冻结

**成本提示**: 每个标签要**两次执行**（辅助 + 无记忆参照）。参照可复用（共享基线）以摊薄成本，但要注意噪声相关（`Ω_Q` 里的 `ν₀²·11ᵀ` 项）。

---

## 九、来源

- 论文: https://arxiv.org/abs/2609.36805 (PDF: https://arxiv.org/pdf/2609.36805, HTML: https://arxiv.org/html/2609.36805v1) — Submitted 2026-09-29, "Under review as a conference paper at ICLR 2027"
- 作者单位: MIIT Key Laboratory of Data and Decision Intelligence, Beihang University（北京航空航天大学）
- **无代码**（2026-10-24 核验 404）
- 前作（单文档 uplift）: https://arxiv.org/abs/2609.36805 引用 Qu et al. 2025 → https://aclanthology.org/2025.findings-emnlp.511/ （即 `uplift-rag` 技能）
- MemSyco-Bench: https://arxiv.org/abs/2607.01071 (HF: https://huggingface.co/datasets/MemSyco-Bench/MemSyco-Bench)
- MemReranker（推理感知记忆重排，0.6B/4B）: https://arxiv.org/abs/2605.06132 (HF: IAAR-Shanghai/MemReranker-4B)
- SkillAligner（检索到的技能当"草稿"在执行时适配）: https://arxiv.org/abs/2608.06880
- MemRL: https://arxiv.org/abs/2601.03192
- Dynamic Dual-Granularity Skill Bank: https://arxiv.org/abs/2603.28716
- 理论来源：Frazier et al. 2009 (Knowledge-Gradient for Correlated Normal Beliefs, DOI 10.1287/ijoc.1080.0314)、Howard 1966 (Information Value Theory)、Chaloner & Verdinelli 1995

---

## 十、与现有技能的边界（去重说明）

- **`uplift-rag`** — 本技能是它的**直接后续工作**。`uplift-rag` = 单文档 uplift 定义 + 三损失训 reranker + 动态 top-k（EMNLP 2025 Findings，RAG 场景，固定 top-k 标注）。本技能 = **集合级** uplift + **主动探测**（EVSI 采集反馈）+ 记忆写入验证（agent memory 场景）。**两者互补不重叠**：前者答"这份文档值不值"，后者答"这一组记忆值不值"和"我接下来该测哪一组"。
- `agentmemory` / `hierarchical-memory-2026` / `memorywire` — 记忆**架构/组织**（分层、压缩、写入），不涉及用执行反馈训练检索器，也不涉及反馈覆盖偏差。
- `memm-ai-context-os` — 上下文系统设计，非效用驱动的检索学习。
- `disco-rag` — 话语结构粒度问题。
- `reflective-rag` — 推理期反思层；本技能是**训练期**的采集策略。
- `qmd` / `research/arxiv` — 检索工具，无训练信号设计。

**去重核验**: 本次研究前 `grep -ri uplift ~/dotfiles/skills/` 仅命中 `uplift-rag`（其"后续工作"小节只有二手概述）；`grep -ri "evsi\|probe allocation"` 无命中（除无关的 LaTeX 模板）。本文所引的具体公式、Prop.1/4、EVSI 闭式解、批量采集、MemSyco 数字等**均为本次首次提取**。

---

## 相关技能（跨层互补）

- `research/skillaligner-execution-time-adaptation` — **技能层**的执行时适配。本技能管"要不要调这个工具"，
  SkillAligner 管"检索到的技能在这次执行里该怎么用"。两者是同一套"相关不等于有用"的判据
  在工具层和技能层上的两次应用。SkillAligner 实测：语义相关的技能会让 5.80%–17.91% 的原本成功任务变失败，
  且更强的 backbone 并不免疫（Gemini 2.5 Pro 11.42% vs Qwen3-8B 10.30%）。
- `research/set-level-evidence-selection` — 集合级选择优于逐篇 Top-K。SkillAligner 的 composition 阶段
  把同一洞察用在了跨技能之间（合并重叠、按依赖排序、冲突按「硬约束 > 环境规格 > 技能建议」裁决）。

