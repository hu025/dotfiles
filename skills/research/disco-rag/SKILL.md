---
name: disco-rag
description: Disco-RAG — 话语结构感知RAG（ACL 2026），用RST树+修辞图+话语蓝图解决"检索粒度 vs 生成理解"错配。Use when designing long-document RAG, chunking strategy, or evidence-conflict resolution.
triggers: [discourse-aware RAG, RST, rhetorical structure, discourse tree, 话语结构, 长文档检索, chunking strategy, evidence conflict]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: arXiv:2601.04377 / ACL 2026 Long Papers pp.4106-4136
code: https://github.com/dongqi-me/Disco-RAG (MIT, 14 stars)
related_code: https://github.com/DreamH1gh/ACL2026-DISRetrieval (15 stars)
tags: [rag, discourse, rst, long-document, acl-2026, retrieval, chunking, hermes-self-improvement]
---

# Disco-RAG — 话语结构感知检索增强生成

## 概述

**主题**: Disco-RAG: Discourse-Aware Retrieval-Augmented Generation
**会议**: ACL 2026 Main Conference (Long Papers), San Diego, pp. 4106–4136
**作者**: Dongqi Liu (Saarland Univ. / Tencent YouTu Lab), Hang Ding, Qiming Feng, Xurong Xie, Zhucun Xue, Chengjie Wang, Jian Li, Jiangning Zhang, Yabiao Wang
**arXiv**: 2601.04377 (v5, 2026-04-17) | **代码**: github.com/dongqi-me/Disco-RAG (MIT)

**一句话**: 现有RAG把检索结果当作**扁平的、彼此孤立的chunk**喂给LLM，导致模型拿到的是"一袋事实"而非"一条有论证流向的推理链"。Disco-RAG在推理期显式注入三件事——**chunk内的话语树(RST)**、**chunk间的修辞图**、**由二者生成的推理蓝图(blueprint)**——无需微调即在长文档QA/摘要上刷到SOTA。

---

## 问题：两个被忽视的结构性缺陷

### 1. Intra-chunk structural blindness（块内结构盲区）
单个chunk内部也有论证层次，但RAG把它当作一段扁平文本。

### 2. Inter-chunk coherence gaps（块间连贯性断裂）
多个chunk之间存在修辞关系（RST的Elaboration/Contrast/Cause），但RAG不知道它们的存在。

**论文的经典反例**（Figure 1）：
- Chunk A：「维生素D使流感发病率降低 **12%**」
- Chunk B：「未发现显著总体效应」
- 标准RAG → 过度泛化，得出"维生素D能降低流感风险"
- Disco-RAG → 正确推断 Chunk A 是**条件性发现**（在冬季的维生素D缺乏人群中），因此结论必须加限定条件

**这就是为什么"检索到相关片段"≠"能正确综合"**。冲突证据的解决依赖结构关系，不只是语义相似度。

---

## 核心机制：三阶段流水线

```
检索 chunks C
   ↓
(1) 每个 chunk cᵢ → LLM-based RST parser → intra-chunk RST tree tᵢ
      (EDU切分 + nucleus/satellite角色指派 + 关系标注)
   ↓
(2) 所有 chunks 一次性 listwise 输入 → inter-chunk rhetorical graph G
      (有向边，关系类型 或 UNRELATED)
   ↓
(3) (q, C, T, G) → discourse-driven planning → blueprint B (推理步骤序列)
   ↓
最终生成：条件化于 {原始chunk, RST树, 修辞图, 蓝图} 四路输入
```

### 1. Intra-chunk RST Tree

**Rhetorical Structure Theory (RST, Mann & Thompson 1987)** 基础：
- 把文本切成 **EDU (Elementary Discourse Unit)** —— 最小话语单元
- 每个 EDU 指派 **nucleus (核心)** 或 **satellite (附属)** 角色
- EDU 之间用**有向边 + 关系类型**连接：Elaboration / Contrast / Cause / etc.

形式化：`tᵢ = (Vᵢ, Eᵢ)`，`Eᵢ ⊆ Vᵢ × Vᵢ × R`

**关键工程点**：
- **tree是离线预构建的**（"Intra-chunk RST trees are constructed offline"）——检索时零额外延迟，这是能落地的关键
- LLM parser **zero-shot** 即可用，不需要训练RST parser
- RST-DT benchmark验证（Table 8）：zero-shot Llama-3.3-70B parser 的 Nuclearity F1 63.1 / Relation F1 58.6，逼近监督训练的 Maekawa et al. 2024（70.4 / 60.0）；Span F1 略低（70.4 vs 79.8）
- **zero-shot LLM parser 的独特优势**：微调parser只能输出固定格式，**无法做跨chunk的修辞图预测**；zero-shot parser 格式灵活，能同时承担树解析 + 图预测两个角色

### 2. Inter-Chunk Rhetorical Graph

有向图 `G = (C, F)`，`F ⊆ C × C × (R ∪ {UNRELATED})`

**Listwise 推理**：所有chunk一次性输入parser，联合预测所有chunk对的关系或 `UNRELATED` 标签。
注意 `UNRELATED` 是显式的一等公民——**没有关系也是一种信息**（它告诉模型这两个chunk彼此独立，不构成冲突或支撑）。

### 3. Discourse-Driven Planning（最具迁移价值的一环）

`A(q, C, T, G) → B`，产出 **blueprint**：一个显式的推理步骤序列，负责
- **selecting salient content**（选哪些内容进答案）
- **organizing argumentative flow**（论证流向怎么排）
- **prioritizing supporting evidence**（支撑证据优先级）

这一环把"结构知识"从"知识级先验"提升到"推理级引导"。

---

## 消融数据：哪些部分真正重要（Loong benchmark, Llama-3.3-70B）

| 配置 | Overall LLM Score | EM |
|---|---|---|
| **Disco-RAG (full)** | **62.07** | 0.24 |
| w/o RST tree | 56.22 | 0.20 |
| w/o rhetorical graph | 57.10 | 0.21 |
| w/o planning | 59.75 | 0.22 |
| Standard RAG | 49.33 | 0.17 |
| w/ retrieve-and-plan（通用规划，非话语驱动） | 50.64 | 0.18 |
| w/ plan-and-retrieve | 51.38 | 0.18 |

**三条可直接迁移的结论**：

1. **结构建模 > 规划本身**。RST树和修辞图各自移除带来 ~5–6 分损失，而移除 planner 只损失 ~2.3 分。
2. **通用规划几乎没有用**（50.64 / 51.38 vs standard RAG 49.33，+1~2 分）。**只有"话语驱动的规划"才有价值**——给一个普通 planner 灌结构信号，它学不会用。
3. **三个模块是互补的**，缺一都降，但都不会崩到 standard RAG 以下。

---

## 鲁棒性：为什么这个方法特别值得工程借鉴

### 检索粒度鲁棒（Figure 3a）
- Standard RAG 在 chunk size=256 时最好（49.33），chunk 变大就崩（结构连贯性丢失）
- Disco-RAG 在所有 chunk size 下稳定（58.91–62.07）

### Top-k 鲁棒（Figure 3b）
- Standard RAG 在 Top-10 峰值，Top 更大因噪声累积而下降
- Disco-RAG Top-10 最好，且**到 Top-50 仍稳健**——有能力整合并过滤冗余

### 噪声鲁棒（Figure 3c）
把 Top-10 中一定比例替换成无关chunk：
- Standard RAG：49.33 → 45.23（陡降）
- Disco-RAG：**保持 56.17**

**结构化证据 = 对检索错误的容错层。** 这对"检索器不可靠"的现实场景极有价值。

---

## 扰动实验：证明增益来自"结构质量"而非"多塞了token"

这是论文方法论上最漂亮的一节（Figure 4）——**控制变量以排除"只是多了上下文"的平凡解释**：

| 扰动 | LLM Score |
|---|---|
| 无扰动 | 62.07 |
| 打乱部分修辞关系标签 | 55.48 |
| 随机改部分 nucleus–satellite 角色 | 55.15 |
| 删除随机子树连接 | 56.77 |
| 随机删除部分chunk间图边 | 57.60 |
| 翻转部分边方向 | 55.82 |
| 替换部分图内关系标签 | 55.50 |
| 省略整个plan | 59.75 |
| 打乱部分plan步骤顺序 | 57.50 |
| 删除部分plan步骤 | 58.14 |

**即使结构被破坏，Disco-RAG 仍然优于 standard RAG 和 full-context。**
→ 增益确实来自模型**利用**结构信号的能力，而不只是多了token。

**可迁移的设计原则**：任何"注入结构/元数据"的方法，都应该做这种扰动对照实验来排除平凡解释。这比"加了X所以涨了Y分"强得多。

---

## 混合模型部署：结构模块可以降级到小模型

**结构模块与生成器是解耦的**，可以分配不同模型：

| 配置 | Structurer / Generator | LLM Score | EM |
|---|---|---|---|
| Standard RAG | 70B / 70B | 49.33 | 0.17 |
| Disco-RAG (all 8B) | 8B / 8B | 58.94 | 0.20 |
| Disco-RAG (8B+70B) | 8B / 70B | 60.52 | 0.22 |
| Disco-RAG (all 70B) | 70B / 70B | 62.07 | 0.24 |

**8B结构器 + 70B生成器 = 60.52**，恢复了全70B配置大部分增益（62.07）。
**即使全8B也有 58.94**，远超 standard RAG 的 49.33。

**成本结论**：结构解析（tree + graph）用小模型即可，昂贵模型只留给最终生成。这是把结构化RAG变成"可负担"的路径。

---

## 与 SFT 的正交性

SciNews 上，结构信号与参数适配**互补**：

| 方法 | RL | SummaC |
|---|---|---|
| End-to-end SFT（无话语输入） | 20.3 | 66.8 |
| Disco-RAG (training-free) | 21.1 | 69.5 |
| SFT + test-time discourse | 22.8 | 72.3 |
| SFT + train & test discourse | 23.3 | 74.0 |

**naive端到端微调反而不如 training-free 的 Disco-RAG**。只有当结构信号在训练和推理两侧都注入时，才能超越。

---

## 主实验结果摘要

### Loong（4档文档长度 10K–250K tokens，Llama-3.3-70B）

| 长度档 | Standard RAG | Disco-RAG | 最佳已发表 |
|---|---|---|---|
| 10K–50K | 62.78 | **71.00** | StructRAG 69.43 |
| 50K–100K | 53.77 | **63.61** | StructRAG 60.95 |
| 100K–200K | 45.77 | **58.86** | StructRAG 57.92 |
| 200K–250K | 35.61 | **54.62** | StructRAG 51.42 |
| **平均** | 49.33 | **62.07** | StructRAG 60.38 |

**增益随文档变长而放大**：短文档 +8.2 分，超长文档（200K+）**+19.0 分**。这正好命中"长文档"这个痛点。

### ASQA（长格式QA）
EM 37.3→42.0，ROUGE-L 36.9→42.3，DR Score 24.1→32.8。超过 MAIN-RAG (RL 42.0)、Tree of Clarifications (RL 39.7)。

### SciNews（长文档科普摘要）
RL 18.17→21.11，BERTScore 61.37→65.67，SARI 37.74→44.37，SummaC 60.39→69.48。**超过此前SOTA RSTformer (RL 20.12, SARI 41.56)**。

### 人工评测（SciNews，15篇×3名CS研究生，3点Likert）
| 系统 | Relevance | Simplicity | Conciseness | Faithfulness |
|---|---|---|---|---|
| Full Context | 1.65 | 1.98 | 1.52 | 1.45 |
| Standard RAG | 1.87 | 2.12 | 1.60 | 1.67 |
| **Disco-RAG** | **2.40** | **2.43** | **2.27** | **2.53** |
| Human Reference | 2.89 | 2.63 | 2.48 | 2.88 |

**Faithfulness 提升最大（1.67→2.53）**——这正是"证据冲突被正确解决"的直接体现。Fleiss κ = 0.73/0.65/0.66/0.68。

---

## 姊妹工作：DISRetrieval（Beyond Chunking, ACL 2026）

**独立验证了同一方向的另一条实现路径**，值得单独知道：

- **论文**: arXiv:2506.06313, ACL 2026 Long Papers pp. 2026.acl-long.829
- **代码**: github.com/DreamH1gh/ACL2026-DISRetrieval (15 stars)
- **作者**: Huiyao Chen, Yi Yang, Yinghui Li, Meishan Zhang, Baotian Hu, Min Zhang (哈工大深圳 / 深港河套研究院 / 清华)

**核心差异**：Disco-RAG 关注**检索之后**的生成阶段（结构用于引导综合）；DISRetrieval 关注**检索本身**（结构用于构建检索单元）。

三阶段：
1. **Discourse-Aware Tree Construction** — 段落级RST解析 → LLM摘要 → 文档级RST解析 → LLM摘要 → 树合并
2. **Node Representation** — 中间节点用LLM增强（同时含结构+语义）+ dense encoding
3. **Hierarchical Evidence Retrieval** — 结构引导的多粒度证据选择

**关键洞见**：RST树天然提供**多粒度的"自然chunk"**——
- 叶子 = 单句（细粒度，精确检索）
- 中间节点 = 修辞段落（粗粒度，话题完整）
- 根 = 文档摘要（全局）

**与 RAPTOR 的对立**：RAPTOR 按语义相似度递归聚类，会把"上下文相关但话语不连贯"的句子混在一起，丢掉原文的"话题→对比→证据→结论"层级。**"按相似度组织" vs "按话语组织"是这套工作的核心张力。**

**跨语言**：论文支持英文 + 中文（MultiFieldQA-zh），用LLM做数据增广实现"语言通用的话语解析"。这对中文长文档检索特别有价值。

**评测**：QASPER / QuALITY / NarrativeQA / MultiFieldQA-zh，优于 fixed-size chunking 和 RAPTOR 式语义聚类。

**另有LREC 2026 的 DiscoRAG**（同一团队的姊妹扩展）：把整个文档建模为discourse tree并沿结构导航；额外加了**query复杂度分类器**来动态选择最省检索策略。评测集SQuALITY被其扩充了"需要深层话语推理"的问题。

---

## 落地到 Hermes 的可迁移设计

### 1. 「证据冲突解决需要结构，不能只靠语义相似度」
Hermes 的记忆层/知识库检索目前是扁平的chunk召回。当两份材料矛盾时（例如两次会话记录里的冲突配置、论文正文 vs 附录的差异），应当：
- 显式标记每份证据的**核心/附属**角色
- 标注它们之间的关系（支撑/对比/因果/无关）
- 生成时按关系组织，而非按召回顺序拼接

### 2. 「结构是检索器的容错层」
Disco-RAG 在 40% 噪声下仍保持 56.17，而 standard RAG 掉到 45.23。**当检索质量不可控时（agent场景常如此），结构化证据比更多token更有价值。**

### 3. 「规划必须被结构信号驱动，否则等于没做」
通用 planner 只带来 +1~2 分，话语驱动 planner 带来 +12.7 分。**给规划器灌结构信号，它得学会用——不给结构，它就是装饰。**

### 4. 「小模型做结构，大模型做生成」
8B结构器+70B生成器 = 60.52/62.07。对 Hermes（MiniMax M3 主模型 + 可用小模型）意味着：**结构解析层不必用最强模型**。

### 5. 「扰动对照实验」是验证结构注入有效性的标准做法
任何往prompt里加元数据/结构的设计，都应做shuffle/flip/drop扰动对照，排除"只是多了token"的平凡解释。这是可以直接复用到 Hermes skill 设计的验证范式。

### 6. 「离线预构建」
Disco-RAG 的 RST 树是离线构建的，检索时零延迟。Hermes 若要做类似，应把结构解析作为**摄入时（ingestion-time）**的一次性成本，而非查询时成本。

---

## 实现要点（若要复现）

**Disco-RAG 仓库技术栈**：
- LangChain + LCEL chains + FAISS
- 自定义 `Embeddings` wrapper 封装 Qwen3-Embedding-8B（last-token pooling, instructed queries）
- token-exact `TextSplitter`（256-token chunks, **no sliding window**）
- 自定义 `BaseChatModel` wrapper 封装 vLLM beam search（width 3）
- 需要CUDA机器；70B/72B backbone用 `tensor_parallel_size: 4` 分片

**实验入口**：
```bash
python -m experiments.main_results.run_loong
python -m experiments.main_results.run_asqa
python -m experiments.main_results.run_scinews
python -m experiments.ablation.run_ablation
python -m experiments.perturbation.retrieval_robustness
python -m experiments.perturbation.structure_perturbation
python -m experiments.mixed_model.run_mixed_model
bash scripts/run_all.sh
```
预测输出存 `outputs/` JSONL（每条含 reference）。

**DISRetrieval 仓库**：三套独立虚拟环境（RSTparser / vllm / rag）；RST设置沿用 Yu's work (E-NNERSTParser)；embedding用 `multi-qa-mpnet-base-cos-v1`；QA模型 `unifiedqa-t5-3b`。

**可复用的离线RST解析器**（不依赖LLM的现成方案）：
- `github.com/tchewik/isanlp_rst` (65 stars, MIT) — 支持 gumrrg / rstdt / rstreebank 三种treebank，输出带 `relation`、`nuclearity`(NS/NN)、字符offset的树结构
- `github.com/tchewik/UniRST` (6 stars) — CODI 2025统一多语种RST parser，based on IsaNLP

---

## 局限与注意

- **额外token与延迟开销**：需要额外的LLM调用做话语解析和规划。作者建议caching / 批处理结构查询 / 蒸馏更轻的parser来缓解。
- **评测集偏窄**：仅 Loong / ASQA / SciNews 三个公开集，跨语种、跨体裁泛化未系统验证。
- **模型依赖**：假定backbone具备基本的话语理解与长上下文处理能力。
- **LLM-as-judge偏差**：Loong的LLM Score用GPT-4-turbo-2024-04-09，可能继承训练数据偏见，数字应视为"指示性"而非穷尽。
- **无配套的Hermes侧现成组件**：仓库是研究代码，需要CUDA+70B级别vLLM，本机（无GPU）跑不动。**落地应借鉴其设计而非直接部署。**

---

## 来源链接

- 论文 arXiv: https://arxiv.org/abs/2601.04377 (v5: https://arxiv.org/html/2601.04377v5)
- ACL Anthology: https://aclanthology.org/2026.acl-long.189/ (pp. 4106–4136)
- 项目页: https://dongqi.me/projects/Disco-RAG
- 官方代码 (MIT): https://github.com/dongqi-me/Disco-RAG
- 姊妹工作 arXiv: https://arxiv.org/abs/2506.06313
- 姊妹工作 ACL: https://aclanthology.org/2026.acl-long.829/
- 姊妹工作代码: https://github.com/DreamH1gh/ACL2026-DISRetrieval
- LREC 2026 DiscoRAG: https://lrec.elra.info/lrec2026-main-162
- 现成RST parser: https://github.com/tchewik/isanlp_rst
