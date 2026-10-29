---
name: memreranker-memory-reranking
description: MemReranker — reasoning-aware, Elo-calibrated reranker for agent memory retrieval (0.6B/4B, Qwen3-Reranker 蒸馏, IAAR-Shanghai). Use when memory/skill recall returns semantically-similar-but-wrong items, when threshold filtering is unreliable, or when choosing a reranker for dialogue/memory recall.
triggers: [memreranker, 记忆重排, memory reranking, 记忆召回重排, Elo 校准, score calibration, 分数校准, threshold filtering, LOCOMO, LongMemEval, reasoning reranker, instruction-aware retrieval, BGE-reranker 对比, mem0 重排, 语义相似≠包含答案]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: arXiv:2605.06132v2 — Zhihao Zhang, Congcong He, Xiaoyang Xu, Jinyu Ye, Shangbin Zhou, Zhuoran Yang, Jian Zhang, Yang Li (IAAR, Shanghai Jiao Tong University)
code: https://github.com/IAAR-Shanghai/MemReranker (Apache-2.0)
model: huggingface.co/IAAR-Shanghai/MemReranker-0.6B / MemReranker-4B
related_work: https://arxiv.org/abs/2609.36805 (UpliftMem, 集合级 uplift) / https://arxiv.org/abs/2608.06880 (SkillAligner) / https://arxiv.org/abs/2607.01071 (MemSyco-Bench) / https://arxiv.org/abs/2508.06781 (BiXSE) / https://arxiv.org/abs/2509.12541 (zELO) / https://arxiv.org/abs/2511.03506 (HaluMem) / https://arxiv.org/abs/2601.03192 (MemRL)
tags: [agent-memory, reranking, retrieval, calibration, elo, bradley-terry, distillation, bce, infonce, locomo, longmemeval, qwen3-reranker, hermes-self-improvement]
---

# MemReranker — 给 agent 记忆召回加一层"会推理、会校准"的重排

## 概述

**一句话**: 通用 reranker 靠语义相似度排序，但**语义相似 ≠ 包含答案**。MemReranker 把 LLM 的推理能力蒸馏进 0.6B/4B 的小模型，并用 Elo/Bradley-Terry 把分数校准到 `[0,1]` 的五档刻度上，**让"阈值过滤"在生产环境第一次真正可用**。

**为什么它和 `upliftmem-evsi-probing` 不重复**:

| | UpliftMem | MemReranker |
|---|---|---|
| 问的问题 | 召回的**记忆集合**该不该被执行（集合级 uplift） | 召回的**单条记忆**排得对不对（排序质量） |
| 优化目标 | 执行效用差 Δ(c,S) = V(c,S) − V(c,∅) | 相关性分数 + 校准 |
| 学出来的东西 | 检索策略 / 主动探测的 EVSI | 一个可直接部署的 reranker 模型 |
| 关系 | **串联**：UpliftMem 决定"要什么"，MemReranker 决定"哪个排前面" | |

两个都是"记忆检索"话题，但一个管**效用**，一个管**排序**。工具链上前者产出的候选集交给后者重排。

---

## 一、核心问题：三个具体的失败模式

论文的立论不是"reranker 不够好"，而是指出**通用 reranker 在记忆场景下的三个具体病**：

### 1. 分数校准失败 → 阈值过滤形同虚设
> "The relevance scores of models such as BGE-Reranker exhibit extreme left-skewed distributions (most scores cluster near 0.00), making it virtually impossible for production systems to set effective cutoff thresholds."

BGE-Reranker 的分数极度左偏（绝大多数挤在 0.00 附近），你没法定一个阈值把噪声切掉。MemReranker 用**五档刻度**解决这个问题：

| 分数区间 | 语义 | 含义 |
|---|---|---|
| 0.8 – 1.0 | **Direct Answer** | 文档**直接包含**回答所需的具体信息 |
| 0.6 – 0.8 | **Highly Relevant** | 提供强证据或相关上下文 |
| 0.4 – 0.6 | **Partially Relevant** | 部分切题，但缺关键细节 |
| 0.2 – 0.4 | **Low Relevance** | 只有主题重合，实际无用 |
| 0.0 – 0.2 | **Irrelevant** | 无实质关联 |

> **这条对 Hermes 尤其重要**：`~/.hermes/self-improvement/mem0_manager.py` 的 `search_memory()` 现在用的是 TF-IDF 余弦相似度 + 硬编码阈值 `sims[i] > 0.05`。0.05 这种阈值在左偏分布下几乎不过滤任何东西（余弦相似度对"共享几个常用词"的文档轻易超过 0.05），所以 recall 出来的噪声完全靠下游 LLM 自己扛。换成校准过的分数后，阈值才第一次有意义。

### 2. 推理能力缺失 → 复杂 query 直接退化
Encoder 型 reranker 靠词面 + 浅层语义匹配，遇到**时间约束、数值比较、因果推理**就不行了。

论文给的硬案例（Case 3，多跳推理）：query 是"《百年孤独》的作者是哪国人？"，需要两步推理才能从候选里找出 Colombia。MemReranker 的 top-3 是 `[2, 1, 8]`，正确命中了信息链的两个关键节点；**其他模型 top-3 命中率只有 1/3**。

### 3. 指令感知缺失 → 同一句话在不同上下文含义不同
论文原例：对话在聊手机时，"我想看看 Apple" 指的是苹果公司；在聊水果时指的是苹果。

MemReranker 支持**三类检索指令**：
- **Intent-Focusing（意图聚焦）**：从长历史里抽出真正的检索意图
- **Entity/Keyword Augmentation（实体/关键词增强）**：把口语映射到领域术语
- **Aspect-Constraint（方面约束）**：query 有多个需求但文档只满足其中一个时，做**部分匹配打分**而不是直接判死

---

## 二、训练管线：四级渐进蒸馏

这是论文最可复用的部分——**即使你不训模型，这套"标签怎么造、损失怎么选"的配方可以直接用在任何"要用 LLM 教小模型排序"的场景**。

| Stage | 做法 | 关键设计 |
|---|---|---|
| **Stage 0** 通用能力保持 | 用 Rank-DistiLLM 公开蒸馏数据初始化 | 别一上来就窄化，先保住通用排序能力 |
| **Stage 1** 教师标签生成 | GPT + Qwen 双教师**成对比较**，多数投票 **3×3**；Elo/Bradley-Terry 拟合绝对分 | 见下方"硬负样本过滤" |
| **Stage 2** Pointwise 蒸馏 | 学生用 **BCE** 回归教师软标签；~1M 通用对 + ~50K 多轮合成对话对 | **BCE >> MSE >> InfoNCE**（0.5B 规模） |
| **Stage 3** 对比微调 | **InfoNCE** listwise 微调 | 只针对 **0.4–0.6 相关性带**补判别力 |

### 2.1 关键决策一：BCE 优先于 InfoNCE（在小规模上）

论文明确引用 BiXSE (COLM 2025) 的发现：**500–600M 参数规模上，pointwise 蒸馏损失（BCE/MSE）在分数校准上优于对比学习**。原因是对比学习倾向产生**聚团的分数**，反而让阈值失效。

> **反直觉点**：直觉上"对比学习 = 更好的排序"。但对**要定阈值的生产系统**来说，校准 > 排序精度。MemReranker 的解法是**分两阶段**：Stage 2 用 BCE 保证校准，Stage 3 再用 InfoNCE 补判别力，且**不让它破坏校准**（这是 DeAR 范式）。

### 2.2 关键决策二：成对偏好 → 绝对分数的桥（Elo/BT）

相对偏好不能直接用，需要绝对刻度：

```
P(d_i ≻ d_j) = σ(Elo_i − Elo_j)
```

用 Bradley-Terry 最大似然拟合**绝对** Elo 分，再归一化到 `[0,1]`。这比直接用 zELO 之类直接回归分数的做法更稳，因为它**只需要成对标注**（成对标注比绝对打分便宜且一致性好）。

> 标注成本提示：`3×3` 多数投票 = 每个对比要 3 个教师 × 3 票。如果你在自建标注，**先在 0.2/0.4/0.6/0.8 四个刻度上抽样人工校准**，而不是每条都标。

### 2.3 关键决策三：硬负样本的三段式过滤

用**余弦相似度 gap** + **BGE-Reranker-v2-m3 交叉验证**：

| gap 值 | 处理 | 理由 |
|---|---|---|
| `gap < 0` | 交叉验证后**移除** | 标注错误（teacher 都排错了） |
| `0 < gap < 0.2` | **保留**为硬负样本 | 真正的困难负例 |
| `gap > 0.2` | **只保留 20%** | 太容易的负例，浪费训练信号 |

> gap = 候选与正例的余弦相似度之差。gap 为负说明候选比正例还像正例 → 几乎肯定是标注错了。

### 2.4 关键决策四：多轮对话数据的构造法

- 第 n 轮 query 的前 n−1 轮 → 用 LLM **蒸馏成只保留核心实体和结论**，去掉对话冗余
- 当前轮答案 → 直接当正样本文档
- 硬负样本 → 同样的双教师 + gap 分析 + BGE 交叉验证
- **任务指令** → 根据 query-document 对的特征自动生成，用于推理时的上下文引导

---

## 三、实验结果（论文 Table 5–9）

### 3.1 LOCOMO（记忆场景主榜，BGE-M3 Top-100 统一候选）

| 模型 | MAP | MRR | NDCG@3 | NDCG@10 | R@20 |
|---|---|---|---|---|---|
| BGE-v2-m3 | 0.6708 | 0.6994 | 0.7140 | 0.7358 | 0.8631 |
| Qwen3-Reranker-0.6B | 0.6427 | 0.6727 | 0.6382 | 0.6889 | 0.8568 |
| Qwen3-Reranker-4B | 0.6894 | 0.7162 | 0.6906 | 0.7324 | 0.8726 |
| Qwen3-Reranker-8B | 0.7206 | 0.7484 | 0.7593 | 0.7748 | 0.8800 |
| GPT-4o-mini | 0.7151 | 0.7415 | 0.7526 | 0.7698 | 0.8678 |
| Gemini-3-Flash | **0.7772** | **0.7973** | **0.8068** | **0.8161** | **0.8919** |
| **MemReranker-0.6B** | 0.7150 | 0.7377 | 0.7540 | 0.7696 | **0.8848** |
| **MemReranker-4B** | 0.7366 | 0.7596 | 0.7734 | 0.7861 | 0.8886 |

**关键读法**：
- **0.6B 打平 GPT-4o-mini**（MAP 0.7150 vs 0.7151），而参数量不到 1%
- **0.6B 反超 Qwen3-Reranker-4B**（0.7150 vs 0.6894），**以小胜大**
- 4B 打赢了 8B（0.7366 vs 0.7206）→ **参数量不是排序质量的唯一决定因素，领域适配更重要**

### 3.2 LongMemEval（n=500，差距更大）

| 模型 | MAP | MRR | NDCG@10 | R@20 | F1 |
|---|---|---|---|---|---|
| BGE-v2-m3 | 0.7069 | 0.7510 | 0.7412 | 0.8874 | 0.5634 |
| Qwen3-Reranker-8B | 0.6966 | 0.7340 | 0.7210 | 0.8931 | 0.5490 |
| GPT-4o-mini | 0.5684 | 0.6385 | 0.5781 | 0.8349 | 0.4444 |
| Gemini-3-Flash | 0.7259 | 0.7575 | 0.7556 | 0.8977 | 0.6010 |
| **MemReranker-0.6B** | 0.7538 | 0.7876 | 0.7872 | 0.8969 | 0.6375 |
| **MemReranker-4B** | **0.8043** | **0.8315** | **0.8203** | 0.8960 | **0.7039** |

**关键读法**：
- 4B 的 MAP **超 Gemini-3-Flash 7.8 个百分点**（0.8043 vs 0.7259）
- **GPT-4o-mini 在这里崩了**（MAP 0.5684，比 BGE 还低）→ 说明"prompt 打分"这条路线在 query 模式多变时很不稳，**专训小模型反而更鲁棒**
- 0.6B 也超了 Gemini-3-Flash

### 3.3 难例测试（Opus-4.6 生成，n=100/模型）

| 模型 | MAP | NDCG@3 | R@5 | F1@5 |
|---|---|---|---|---|
| BGE-v2-m3 | 0.797 | 0.824 | 0.700 | 0.570 |
| Qwen3-Reranker-8B | 0.840 | 0.872 | 0.746 | 0.605 |
| GPT-4o-mini | 0.910 | 0.933 | 0.828 | 0.677 |
| Gemini-3-Flash | **0.912** | **0.938** | 0.822 | **0.685** |
| MemReranker-0.6B | 0.862 | 0.896 | 0.766 | 0.630 |
| MemReranker-4B | 0.893 | 0.921 | 0.788 | 0.675 |

**关键读法（诚实边界）**：难例上大模型仍有优势，**Gemini-3-Flash / GPT-4o-mini 在难例上更强**。MemReranker 的价值在**成本/延迟**，不是绝对上限。

按类别细分（Appendix A）差距更清楚：
- MemReranker-0.6B **超过** GPT-4o-mini 的类别：低词面重叠/高语义（0.976 vs 0.961）、高词面重叠/低语义（0.975 vs 0.979）
- GPT-4o-mini 明显领先的：**否定/语义反转（0.988 vs 0.964）、多跳推理（0.988 vs 0.923）**、粒度错配
- 结论：MemReranker 在**词面-语义解耦**上很好，在**深推理**上仍落后大模型

### 3.4 延迟（1k token，Table 10）

| 指标 | BGE-Reranker-v2-m3 | MemReranker-0.6B | GPT-4o-mini |
|---|---|---|---|
| Avg (ms) | 241.0 | 247.2 | 1549.2 |
| P95 (ms) | 271.4 | 327.4 | 2034.5 |
| P99 (ms) | 271.4 | 327.4 | 2524.2 |

0.6B ≈ BGE 的延迟，**比 GPT-4o-mini 快 ~6–8 倍**。

### 3.5 垂直领域（金融/医疗）——泛化没有崩

- **FinFact**（金融，n=1000）：MemReranker-0.6B MAP 0.997，**超过 Qwen3-Reranker-8B**（0.997）持平、与 GPT-4o-mini（0.995）相当
- **NFCorpus**（医疗）：4B MAP 0.7456 > Qwen3-Reranker-8B 0.7363
- **SciFact**：0.6B MAP 0.9871 ≈ 8B 0.9864
- **CMedQAv2**（中文医疗 QA）：**BGE 领先**（0.8347 vs 4B 0.7700）——论文承认 BGE 训练集可能含原始数据；**中文场景是 MemReranker 的相对弱项**

> **诚实边界**：CMedQAv2 上 MemReranker 明显输给 BGE，作者自己归因于 BGE 训练集可能泄漏。中文医疗场景不要盲目上。

---

## 四、怎么用（可直接落地）

### 4.1 方式 A：本地 CrossEncoder（需要能下模型权重）

```python
from sentence_transformers import CrossEncoder
import torch

model = CrossEncoder(
    "IAAR-Shanghai/MemReranker-0.6B",          # 或 MemReranker-4B
    model_kwargs={"torch_dtype": torch.bfloat16, "device_map": "cuda"},
)
query = "用户有什么兴趣爱好"
documents = [
    "用户喜欢打羽毛球",
    "用户在杭州做后端开发",
    "用户偏好简洁的回复风格",
]

# 原始 logit 分
scores = model.predict([(query, d) for d in documents])
# tensor([2.969, 1.328, -3.141])

# 0~1 概率（sigmoid）—— 这才是能定阈值的分数
probs = model.predict([(query, d) for d in documents], activation_fn=torch.nn.Sigmoid())

# 或者直接拿排好序的结果
results = model.rank(query, documents)
```

**打分机制**（继承 Qwen3-Reranker 的 yes/no logit 头）：
```
score = e^(log p(yes)) / (e^(log p(yes)) + e^(log p(no)))
```
`yes` token id = 9693，`no` token id = 2152。

### 4.2 方式 B：托管 API（无 GPU / 无权重时）

MemOS 开放平台提供托管的 rerank 接口，模型名 `memos-reranker-0.6b` / `memos-reranker-4b`（与 MemReranker 同源）：

```bash
curl --request POST \
  --url https://memos.memtensor.cn/api/openmem/v1/rerank \
  --header 'Authorization: Token YOUR_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "memos-reranker-0.6b",
    "query": "用户有什么兴趣爱好",
    "documents": ["用户喜欢打羽毛球", "用户在杭州做后端开发"]
  }'
```

响应：`results[]` 每项含 `index`（原 documents 下标）、`document.text`、`relevance_score`（**0~1，越高越相关**）。
**约束**：所有 documents 的总 token 数上限 **8k**（与论文训练时的 max_len 8192 一致）。

### 4.3 接到 Hermes 的记忆召回链路上

现有链路（`~/.hermes/self-improvement/mem0_manager.py`）：
```
query → TfidfVectorizer fit_transform → cosine_similarity → argsort → 阈值 0.05 → top_k
```
问题：无重排、分数未校准、阈值形同虚设。

建议改成两段式（**召回用便宜的重排用准的**）：
```
query → TF-IDF/BGE-M3 召回 top 50~100
      → MemReranker 重排（校准分 0~1）
      → 阈值过滤（如 ≥0.6 保留，0.4~0.6 标记为部分相关）
      → top_k 送下游
```

**为什么不直接用 LLM 重排**：
- 论文的 GPT-4o-mini 基线在 LongMemEval 上 MAP 只有 0.5684，**比 BGE 还低**——prompt 式打分不稳
- 延迟 8 倍差距（247ms vs 1549ms）
- 校准过的专用小模型在多轮记忆场景反而更强

**阈值怎么定**：按论文五档刻度，先用 `0.6`（Highly Relevant 起点）起步，再在自己数据上用 **LOCOMO/LongMemEval 风格的标注**校准。别拍脑袋定 0.05。

---

## 五、诚实边界（必读）

- **中文医疗弱项**：CMedQAv2 上 MemReranker 明显落后 BGE（0.7700 vs 0.8347），论文自认 BGE 训练集可能含原始数据。中文 + 专业领域不要盲目替换。
- **难例仍输大模型**：难例测试上 Gemini-3-Flash / GPT-4o-mini 多数指标更强。MemReranker 的卖点是**性价比**，不是天花板。
- **多跳推理是 0.6B 的短板**：Appendix A 显示 GPT-4o-mini 在多跳推理 0.988 vs 0.6B 的 0.923。真需要多跳时应升级到 4B 或保留一个 LLM 重排兜底。
- **候选集强依赖**：论文统一用 BGE-M3 Top-100（LOCOMO）/ Top-50（LongMemEval）做召回。**召回不够好，reranker 救不回来**。
- **未验证在线稳定性**：论文自己在结论里把"真实用户流量下的在线部署稳定性"列为开放问题。**别把 benchmark 数字直接当生产指标**。
- **召回与重排未联合优化**：论文明说这是未来方向。评测数字是"固定召回 + 换 reranker"的对比，不是端到端最优。
- **训练规模是未验证变量**：每个配置只训一次，训练随机性未知；executor 只在 Qwen3-4B/8B 上验证，能否外推到别的 executor 未验证。
- **本文所有数字均为论文报告值**，本机未复现 benchmark（原因见下方环境约束）。

---

## 六、本机环境约束（2026-10-24 实测，影响部署方式）

| 约束 | 实测结果 | 影响 |
|---|---|---|
| **GPU** | `nvidia-smi` 不存在，**无 GPU** | 只能 CPU 跑 0.6B，或走托管 API |
| **huggingface.co** | `curl` 返回**空响应**；`snapshot_download` 报 `ConnectError: [Errno 101] Network is unreachable` | **权重下不下来** |
| **hf-mirror.com** | API 401 / `resolve/main/config.json` 404 | 镜像不可用 |
| **cdn-lfs.hf.co** | 403 | 不可用 |
| **modelscope.cn** | 404（无该模型镜像） | 不可用 |
| **memos.memtensor.cn** | HTTP **401**（即网络可达，仅需 API Key） | 托管 API 路径可用 |
| **PyPI** | HTTP 200 ✅ | `sentence-transformers` 可装 |
| **torch CPU 轮子** | `download.pytorch.org/whl/cpu` 可达，torch CPU 187MB | 必须走 CPU index，否则 uv 会拉 **~1.5GB CUDA 轮子**（nvidia-cublas 403MB + cudnn 527MB） |

**结论：本机目前拿不到 MemReranker 权重**。可行路径是**托管 API（方式 B）**，需要 `MEMOS_API_KEY`。

**部署建议**：本机优先走 **托管 API（方式 B）**；若必须本地跑，先用 CPU-only torch 索引装依赖：
```bash
# 第一步: 单独装 CPU torch(绝不能直接 pip install sentence-transformers, 否则拉 ~1.5GB CUDA 轮子)
uv pip install --index-url https://download.pytorch.org/whl/cpu torch
# 第二步: 装上层包
uv pip install sentence-transformers transformers huggingface-hub safetensors scipy scikit-learn
```
> **踩坑 1**：`uv pip install sentence-transformers` 会默认解析到 PyPI 的 CUDA torch 轮子，在无 GPU 机器上白占 ~1.5GB 磁盘和大量下载时间。**必须先单独装 CPU torch。**
> **踩坑 2**：用 `--no-deps` 装 sentence-transformers 会漏掉 `packaging` / `scipy` / `scikit-learn` 等传递依赖，报 `ModuleNotFoundError: No module named 'packaging'`。上层包**不要**用 `--no-deps`。
> **实测可用版本组合**（2026-10-24，Python 3.13）：torch 2.14.1+cpu / sentence-transformers 6.2.0 / transformers 5.20.2 / scipy 1.18.1 / scikit-learn 1.9.1。

---

## 六·补、Hermes 侧的落地实现（2026-10-24 已建并实测）

### 6.1 顺手修掉的真 bug：记忆检索层一直是坏的

研究过程中实测发现 `~/.hermes/self-improvement/mem0_manager.py` 有**两个叠加故障**：

**故障 A：sklearn 从未安装 → 模块级 import 就炸**
```python
from sklearn.feature_extraction.text import TfidfVectorizer   # 硬 import
```
本机任何 venv 都没装 sklearn，`import mem0_manager` 直接 `ModuleNotFoundError`。
**整个记忆检索层不可用。** 因为 `scripts/learning_search.py` 也依赖它但**没挂任何 cron**，这个故障一直静默存在。

**故障 B：中文 TF-IDF 分词失效 → 检索结果全零**
即使装上 sklearn，默认 `TfidfVectorizer(max_features=512, stop_words='english', ngram_range=(1,2))` **按空白分词**，中文整段被当成一个 token → 实测 63 条中文记忆的 query 相似度**全部为 0.0**，阈值 `0.05` 会把结果**全过滤掉**。

**已修复**（`mem0_manager.py`）：
```python
# A: sklearn/numpy 改为可选导入, 缺失时模块仍能 import
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    ...
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False

# B: 中文感知分词 —— char_wb 字符 n-gram, 中英文通用且不引入 jieba
TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 3), max_features=4096)
```
**修复后实测**：
- `"如何压缩 Hermes 上下文"` → 正确命中 rank1（score 0.213，id=137 `Hermes上下文压缩：max_turns 200→50...`）
- `"用户的ETF投资偏好是什么"` → 返回相关记忆（score 0.154），之前是全零
- `scikit-learn 1.9.1` 已装入 `~/.hermes/venv`

### 6.2 新增 `memory_reranker.py`（可运行的适配器）

`~/.hermes/self-improvement/memory_reranker.py` —— 双后端（托管 API / 本地 CrossEncoder）+ 自动降级 + 分数分布诊断。

```bash
# 用 TF-IDF 兜底跑通链路 + 看分数分布诊断
~/.hermes/venv/bin/python ~/.hermes/self-improvement/memory_reranker.py \
    --query "Hermes 上下文压缩参数是多少" --top-k 4 --backend tfidf --explain

# 托管 API(需 MEMOS_API_KEY)
~/.hermes/venv/bin/python ~/.hermes/self-improvement/memory_reranker.py \
    --query "..." --backend api --min-score 0.6

# 本地模型(需能下权重)
~/.hermes/venv/bin/python ~/.hermes/self-improvement/memory_reranker.py \
    --query "..." --backend local
```

**`--explain` 的诊断输出直接印证论文的核心论点**。实测 `"Hermes 上下文压缩参数是多少"`：

```
diagnostics: {
  "n": 50, "max": 0.2172, "min": 0.0415, "median": 0.0813,
  "left_skew_frac_below_0.05": 0.1,
  "frac_above_threshold": 0.0,
  "bands": {"direct_answer": 0, "highly_relevant": 0,
            "partially_relevant": 0, "low_relevance": 1, "irrelevant": 49},
  "threshold_is_effective": false,
  "note": "全部被阈值过滤 -> 阈值过严"
}
```

**正确答案是 rank1**（id=137，Hermes 上下文压缩那条，score 0.2172），但**所有分数都挤在 0.04–0.22**，用 0.6 这种"校准分语义"的阈值会把正确答案一起干掉。
> **这就是论文 §1 "Score calibration failure" 的现场复现**：原始余弦相似度和校准后的相关度分**不是同一个量纲**，不能共用阈值。MemReranker 的五档刻度（0.8-1.0=直接答案）只有在校准模型上才成立。

### 6.3 两个后端的通路都已用 mock 端到端验证

```
local: raw logits [2.969, 1.328, -3.141] → sigmoid → [0.9512, 0.7905, 0.0414]
       → bands: [direct_answer, highly_relevant, irrelevant]
       → threshold 过滤 → 排序, 全部正确
api:   results[].index → relevance_score → [0.93, 0.41, 0.07]
       → bands: [direct_answer, partially_relevant, irrelevant]
```
> **踩坑 3**：后端返回的分数数量可能少于候选数，`zip` 会**静默截断**导致部分候选没有 `score` 字段 → `KeyError: 'score'`。适配器里加了长度校验与补零。

### 6.4 落地建议的链路改造

```
query → TF-IDF(char_wb) / BGE-M3 召回 top 50~100
      → MemReranker 重排 → 校准分 0~1
      → 阈值过滤(≥0.6 保留 / 0.4~0.6 标记部分相关)
      → top_k 送下游
```
**阈值别拍脑袋定 0.05**——那是原始余弦相似度的量纲。校准模型上从 **0.6**（Highly Relevant 起点）起步，再在自己数据上用 LOCOMO/LongMemEval 风格的标注校准。

---

## 七、相关技能

- `upliftmem-evsi-probing` — 集合级 execution uplift + EVSI 主动探测（管"要什么"，与本技能管"怎么排"串联）
- `local-rag` — 本地 RAG 全栈（其中推荐的 `bge-reranker-v2-m3` **在记忆/多轮对话场景应升级为 MemReranker**）
- `mem0-integration` — Hermes 当前的 TF-IDF 记忆层（本技能的落地靶点）
- `memm-ai-context-os` / `memorywire` — 其他记忆层方案
- `agentmemory` — agent memory 机制综述
