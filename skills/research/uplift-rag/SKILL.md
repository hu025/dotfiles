---
name: uplift-rag
description: Uplift-RAG — 用"边际增益(uplift)"定义文档效用，把检索器从相关性排序对齐到LLM的知识缺口（EMNLP 2025 Findings）。Use when designing RAG reranking, context budget selection, or diagnosing "retrieved docs hurt the answer" problems.
triggers: [uplift, uplift modeling, uplift-rag, marginal benefit, reranker alignment, document utility, 文档效用, 边际增益, 知识偏好对齐, context budget, dynamic top-k]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: Findings of EMNLP 2025, pp. 9632–9644 (aclanthology.org/2025.findings-emnlp.511)
authors: Changle Qu, Sunhao Dai, Hengyi Cai, Yiyang Cheng, Jun Xu, Shuaiqiang Wang, Dawei Yin (RUC GSAI + Baidu)
code: https://github.com/quchangle1/Uplift-RAG — **404, 代码未公开**（2026-10-24 核验）
related_work: https://arxiv.org/abs/2609.36805 (UpliftMem, set-level uplift for agent memory, 2026-09)
tags: [rag, uplift, reranker, preference-alignment, knowledge-gap, context-budget, emnlp-2025, findings, hermes-self-improvement]
---

# Uplift-RAG — 用边际增益定义"文档到底有没有用"

## 概述

**一句话**: 检索器按**相关性**排序，但 LLM 要的是**填补自己知识缺口**的文档——两者目标错位。Uplift-RAG 把文档效用重新定义为 **uplift（边际增益）= 有该文档时的生成质量 − 无该文档时的生成质量**，用这个信号训练一个轻量 reranker，使选文档从固定 top-k 变成**按需动态选择**，同时省掉 58%–84% 的 token。

**为什么这个定义重要**: 现有的"文档效用"估计都直接把"加了文档之后的生成表现"当监督信号，这**把外部文档的贡献和 LLM 自身的参数化知识混在了一起**（信用分配问题）。uplift 用无文档基线做差，把这两者干净地分开了。这是全篇最可迁移的一点。

---

## 核心洞察：四象限诊断

论文 Figure 1 的实测（e5-base-v2 检索 top-10，Llama-3-8B-Instruct，NQ 数据集）：

| 类别 | 占比 | 现有效用 (Correct_with) | Uplift |
|------|------|------------------------|--------|
| **Helpful-Doc**（纠错型） | **17.81%** | 1 | **+1** |
| Redundant-Doc（无益但无害） | 13.44% | 1 | **0** |
| Redundant-Doc（无益且无害，另一种） | 23.55% | 1 | 0 |
| **Misleading-Doc**（把对的答成错的） | **45.20%** | 0 | **−1** |

**读法**: 检索到的 10 篇里，只有不到 2 成真正帮了忙，**将近一半在把正确答案改错**。而现有的效用定义（Correct_with）会把那 13.44% + 23.55% 的"无害冗余"错判成 1（有益），把 45.20% 的"误导"判成 0（无害）——**恰好把最该罚的（uplift<0）和最该忽略的（uplift=0）混为一谈**。

这解释了 uplift 相对"有无文档"的绝对判据的两个增益：
1. LLM 本来就会答对的题，无关文档 uplift=0 → **不该被算作有益**，但传统方法会算。
2. 把正确答案改错的文档 uplift<0 → **应当被惩罚**，但传统方法与"无用冗余"同等对待。

> **可推广的方法论**: 任何"给上下文 A 之后效果变好了吗"的评估，都要先减去"不给 A 时的基线"，否则测的是被测系统的绝对能力，不是上下文的边际价值。这个模式对 agent 的 skill/tool 注入、memory 召回、context assembly 一律成立。

---

## 方法：两阶段

### 阶段一：Uplift 计算（离线标注）

对每个 query `q` 和每篇候选文档 `d`：

```
S_q     = F(M(q),      y)      # 无文档基线分数
S_q,d   = F(M(q, d),  y)      # 单文档条件下的分数
Uplift(q, d) = S_q,d − S_q     # ← 关键定义（论文 Eq.3）
```

- `F` = 任意下游指标（论文用 EM / F1），`y` = ground truth。
- 每篇文档**独立**喂给 LLM 单独生成一次答案 —— 这是成本所在，也是论文承认的规模化瓶颈。
- uplift > 0 有益，= 0 无益但无害（仍占 token），< 0 有害。

### 阶段二：Uplift 引导的对齐（训练 reranker）

三个损失联合优化（`L = λ₁·L_point + λ₂·L_pair + L_list`）：

| 损失 | 形式 | 作用 | 消融掉掉多少（NQ EM / TriviaQA EM, Llama-3-8B） |
|------|------|------|------------------------------------------|
| **Point-wise** | 二分类交叉熵，`u_ij ∈ {0,1}`（uplift>0 为正例） | 判"有没有用" | 37.12 → **24.43** / 61.31 → **59.88**（NQ 掉 12.7 分，几乎崩） |
| **Pair-wise** | `-Σ log σ(p_ij − p_im)`，文档对按 uplift 序 | 排"谁更有用" | 37.12 → 34.93 / 61.31 → 60.66 |
| **List-wise** | `KL( P_U || P_R )`，`P_U ∝ e^uplift`，`P_R ∝ e^p` | 利用**连续 uplift 值**做列表级分布对齐 | 37.12 → 36.56 / 61.31 → 60.55 |

**工程细节**: 轻量 reranker（roberta-base，10 epoch，lr 1e-5），把最后一层线性层改成输出**两个分数**再做 softmax 得到 `p_ij`（原 reranker 只输出单个相关性分数，没有二分类头）。

### 推理：动态 top-k

不再指定 top-k。对每篇文档算 `p_ij`：
- **保留 `p_ij > 0.5` 的文档**（"比没用更可能有用"）
- 按 `p_ij` 降序排列
- 全部被滤掉 → 退化为 naive generation（正确行为：不该硬塞文档）

---

## 关键实验结果

### 主结果（Table 1，EM/F1）

| 方法 | WQ EM | NQ EM | TriviaQA EM | (1B) NQ EM | (1B) TriviaQA EM |
|------|-------|--------|-------------|-------------|-----------------|
| Naive Generation | 20.62 | 22.43 | 55.29 | 9.05 | 22.27 |
| Standard RAG | 17.32 | 35.95 | 58.68 | 29.05 | 47.64 |
| BGE-reranker | 19.04 | 35.84 | 59.69 | 28.67 | 49.15 |
| Adaptive-RAG | 14.96 | 36.01 | 52.13 | 29.41 | 40.97 |
| DPA-RAG (前 SOTA) | 19.29 | 36.81 | 60.56 | 30.19 | 49.43 |
| **Uplift-RAG** | **23.47** | **37.12** | **61.31** | **30.49** | **50.19** |
| *Uplift-RAG (Upper Bound)* | *35.43* | *51.93* | *73.29* | *42.32* | *59.66* |

**关键读法**:
- 在 **WebQuestions + Llama-3-8B** 上，Standard RAG (17.32) **比 naive generation (20.62) 更差** —— 检索反而伤害了模型。作者点明这正是"有害文档误导 LLM"的直接证据。
- Uplift-RAG 相对最强基线 DPA-RAG 的**增益很小**（NQ +0.31 EM，TriviaQA +0.75 EM），论文自称"最佳"，但真正的故事在 upper bound：**+15% ~ +72%**。
- **upper bound 才是重点**：1B 模型用 uplift 选出的文档集，**全面超过 8B 模型不检索时的表现**（1B/NQ 42.32 vs 8B naive 22.43）。→ **文档选择的质量比模型规模更值钱**。

### Token 消耗（Table 3，核心卖点）

| 配置 | NQ: \|N\| | NQ Token | TriviaQA: \|N\| | TriviaQA Token |
|------|----------|----------|----------------|-----------------|
| Base (固定 top-5) | 5.00 | 712.59 (100%) | 5.00 | 717.13 (100%) |
| **Uplift-RAG (8B)** | **1.63** | **232.77 (32.7%)** | **0.82** | **117.76 (16.4%)** |
| Oracle | 1.85 | 263.17 (36.9%) | 1.21 | 173.96 (24.3%) |
| **Uplift-RAG (1B)** | 1.97 | 281.05 (39.4%) | 2.10 | 301.09 (42.0%) |

- 实际系统省 **58%–84%** token，同时 EM/F1 还略升。
- **文档数随生成器能力自适应**：8B 选 0.82 篇，1B 选 2.10 篇。模型越强，越不需要外部文档。这直接回答了"该给 LLM 塞多少上下文"。
- 固定 top-5 无论模型强弱都塞 5 篇 → 弱模型被噪声淹没。

### 错误分析（Figure 4，Llama-3.2-1B）

| 错误类型 | WQ | NQ | TriviaQA |
|---------|-----|-----|----------|
| Type1 漏掉全部有用文档 | 56.46% | 14.89% | 10.54% |
| Type2 部分漏掉 | 13.88% | 22.77% | 18.57% |
| Type3 有用文档全在 | 29.67% | 66.54% | 66.69% |

**主因是漏检（recall 问题），不是误检**。且即使 Type3（全对），性能也不总是最优 —— 说明**冗余/误导文档即使在有用的旁边也会拉低质量**。

### 跨模型迁移（Figure 5）

- 小模型的 oracle 文档集**部分可迁移**到大模型。
- 大模型的 oracle 文档集**无法迁移**到小模型。
- 原因：大模型更依赖内部知识，oracle 文档集常为空集；小模型更依赖外部文档。

→ **文档偏好是 model-specific 的**，一个模型的"最优证据集"不能直接套给另一个模型。

### 跨模型族泛化（Table 6，Upper Bound）

在 Llama-3-70B / Llama-3.2-3B / GPT-3.5-Turbo / Qwen2.5-14B / 7B / 3B 上，Uplift-RAG upper bound 相对 naive generation 的 EM 增益：

| 模型 | NQ EM (naive→UB) | TriviaQA EM (naive→UB) |
|------|-------------------|------------------------|
| Llama-3-70B | 33.68 → 58.25 | 66.25 → 79.41 |
| Llama-3.2-3B | 17.64 → 52.18 | 44.17 → 71.15 |
| GPT-3.5-Turbo | 35.45 → 53.65 | 69.61 → 74.29 |
| Qwen2.5-14B | 21.71 → 43.18 | 55.08 → 68.14 |
| Qwen2.5-7B | 14.40 → 48.50 | 43.66 → 69.75 |
| Qwen2.5-3B | 12.13 → 51.10 | 32.21 → 67.66 |

→ 方法不依赖特定模型族。**弱模型增益更大**（Qwen2.5-3B 在 NQ 上 +39 EM）。

### 案例（Table 4，Llama-3-8B）

- **Case 1**: 问"德国一战先入侵哪个国家"，naive 答对（Belgium）。DPA-RAG 塞进俄罗斯/法国相关的干扰文档 → 答成 Russia。**Uplift-RAG 选中空集 → 保持 Belgium 正确**。
- **Case 2**: 问"John Cena 和谁结婚"，naive 答错。Uplift-RAG 只选中 1 篇正确文档 → 答对；DPA-RAG 选中 5 篇混入 Nikki Bella 等干扰内容 → 答"未结婚"。

---

## 局限与诚实边界

1. **代码未公开**。论文写 "Our code is available at https://github.com/quchangle1/Uplift-RAG"，但 2026-10-24 核验该 URL 与 GitHub API 均返回 **404**，作者主页也无该仓库链接。→ 复现需自行实现，**不可直接依赖**。
2. **标注成本高**。每篇候选文档都要独立调用一次 LLM 生成 + 打分，是 O(|D_Ret|) 次生成/query。论文只做了 top-10 规模，未涉及规模化方案。
3. **真实增益远小于 upper bound**。实际提升相对最强基线只有 +0.3~+0.8 EM；+15%~+72% 是 oracle 数字。**不要把 upper bound 当作方法实际效果**。
4. **只在单文档粒度建模**。论文自述："Extending our uplift-based preference modeling from single documents to document sets remains a key challenge"——多文档交互（互补/冗余/冲突）未建模。
5. **轻量 reranker 判别力不足**。作者自述 reranker "falls short of effectively identifying truly useful documents"，未来工作是用 LLM 当 reranker。
6. **数据集窄**：仅 WebQuestions / NQ / TriviaQA 三个短答案 QA，无长文档、无 agent 场景。
7. **需要 ground truth**。uplift 定义依赖 `F(M(q), y)`，无标注场景（真实生产）无法直接计算。

---

## 后续工作（该 limitation 已被补上）

**UpliftMem** (arXiv:2609.36805, 2026-09, 北航) 把 uplift 推广到 **agent memory 检索**，并且**直接在集合级(set-level)建模**，正好补上 Uplift-RAG 的第 4 条局限：
（→ 已完成深度研究，全文细节见独立技能 `upliftmem-evsi-probing`）

- 定义 **execution uplift** = 同 executor 下"有 memory 执行"与"无 memory 执行"的效用差。
- 指出**反馈覆盖问题**：只有被执行过的 memory 集合才有直接 uplift 标签，没被选过的集合标签永远缺失 → 低估计的集合永远选不上 → 反馈永远不来。
- 用 **EVSI（expected value of sample information）** 在相关高斯代理模型下闭式求解，按"这次探测能改善多少局部检索决策"分配有限 rollout 预算。
- 在 ALFWorld / WebShop / BigCodeBench 上取得最佳成功率。

**可迁移**: Uplift-RAG 的单文档 uplift 可以直接作为 UpliftMem 式"集合级 uplift"的一个基线项；但如果要做集合级，**必须**处理反馈覆盖问题（否则 uplift 标签本身就有偏）。

> **深度研究已完成** → 独立技能 `research/upliftmem-evsi-probing/SKILL.md`（2026-10-24）。要点：Prop.1 反馈覆盖上界 `p_B ≤ Σ exp(−d(a)/τ_tr)`；Prop.4 未执行集合的符号**完全不可辨识**；EVSI 闭式解 `E_j = s_j·ψ(|μ_j|/s_j)`；集合级反例（两篇单看都负、合起来为正 → 贪心会错过互补组合）；固定记忆库下决策准确率 41.7%→66.5%、谄媚率 49.0%→29.5%。代码未公开（404）。

另有 **arXiv:2608.26379**《Assessing the Downstream Utility of Evidence-Aware Retrieval in RAG》从评估有效性角度做了批判性检查：把"答案支持度"信号用于 retriever 训练**不可靠改善**、用于 system selection 的收益取决于 generator 的 prompt 指令方式、基于它的检索分数**不能稳健预测**未见主题上的答案质量。对 Uplift-RAG 属于间接的负面证据，值得在采纳前留意。

---

## 对 Hermes 的可落地启发

1. **上下文注入前先算边际增益**。Hermes 每次往 prompt 里塞 skill / memory / tool context，本质上就是 RAG 的 doc selection。做法：先问"这个模型自己能不能答对"，再问"加上这段后变好还是变差"。**别让高相关性的旧 skill 覆盖模型本来就对的答案**——这正是 45.20% misleading-doc 的机理。
2. **动态 context 预算**。固定塞 N 条 → 改成按需。可以直接借论文 Table 3 的思路：小模型多给（1B 选 2.1 篇），大模型少给甚至不给（8B 选 0.82 篇）。
3. **信用分配原则（最通用的一条）**：评估任何上下文/工具/记忆注入的效果，都要减掉"不注入"的基线。绝对分数测的是模型，不是你注入的东西。
4. **三个损失对应三个能力**：point-wise = 筛选（有没有用），pair-wise = 排序（谁更有用），list-wise = 利用连续信号做分布对齐。**只做 point-wise 在 NQ 上直接崩 12.7 EM**，说明"判对错"和"排好序"是两个不可互相替代的能力。

---

## 复现路线（因代码未公开）

1. 检索器 `e5-base-v2`，召回 top-10；生成器可换 MiniMax-M3 / Qwen。
2. 标注：对每个 (q, d) 单独调 LLM 生成答案 → 用 EM/F1（或 judge）对 ground truth 打分。
3. 计算 `uplift = S_q,d − S_q`（无文档基线每个 query 只需算一次）。
4. 训练轻量 cross-encoder reranker：最后一层改成 2 头 → softmax 得 `p_ij`；三损失加权。
5. 推理：保留 `p > 0.5` 的文档，按 p 降序，全滤掉则走无上下文路径。

**成本提示**：步骤 2 是瓶颈，top-10 × N query 次生成。实践上可先只对 top-10 标注，或用"批量生成 + 一次评分"降低调用数。

---

## 来源

- 论文: https://aclanthology.org/2025.findings-emnlp.511 (PDF: https://aclanthology.org/2025.findings-emnlp.511.pdf) — Findings of EMNLP 2025, pp. 9632–9644
- 镜像 PDF (人大 IIR Lab): http://ai.ruc.edu.cn/uploads/20251110/62073113f56144552f8f5b2f0e55b465.pdf
- 作者主页: https://quchangle1.github.io/ (Changle Qu, RUC GSAI IIR Lab)
- 声明的代码仓库 (404): https://github.com/quchangle1/Uplift-RAG
- 后续工作 UpliftMem: https://arxiv.org/abs/2609.36805
- 评估有效性批判: https://arxiv.org/abs/2608.26379
- 核心对比基线 DPA-RAG (ACL 2025): https://github.com/oneal2000/DPA-RAG
- FlashRAG 实验框架: https://github.com/RUC-NLPIR/FlashRAG

## 与现有技能的边界（去重说明）

- `disco-rag` — 解决**检索/生成粒度与话语结构**问题（长文档、修辞图）；本技能解决**文档效用定义与选择**问题（短答案 QA、reranker 对齐）。不重叠。
- `hetero-graph-rag-2026` — 异构图 + agent 规划做检索；本技能不涉及图结构与 agent 规划。
- `reflective-rag` — 反思/评估层；本技能是**训练时的监督信号设计**（uplift 定义），非推理时反思。
- `a-rag` — 检索接口分层（keyword/semantic/chunk）；本技能是**重排与预算分配**。
- `r2r-agentic-rag` — 检索增强推理库；未涉及 uplift。
- `local-rag` — 本地部署；未涉及效用建模。

队列中已无其他 uplift / 偏好对齐主题；`grep -ri uplift ~/dotfiles/skills/` 在本次研究前无命中。
