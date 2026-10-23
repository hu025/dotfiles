---
name: megarag-multimodal-graph-rag
description: MegaRAG (ACL 2026) — 多模态知识图谱RAG：页面级两轮构图 + 视觉线索精修 + 文本/视觉双阶段解耦生成。Use when building KG-RAG over PDFs/slides with charts, or diagnosing modality bias in multimodal retrieval.
triggers: [multimodal RAG, 多模态知识图谱, MMKG, 视觉文档问答, 图谱RAG, MinerU, GME embedding, 跨模态推理, PDF图表问答, modality bias]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: arXiv:2512.20626 / ACL 2026 Long Papers pp.48031-48059, DOI 10.18653/v1/2026.acl-long.2218
code: https://github.com/AI-Application-and-Integration-Lab/MegaRAG (73 stars, custom license)
related: LightRAG v1.4.3 (HKUDS), MinerU release-1.3.6, GME-Qwen2-VL-2B
tags: [rag, multimodal, knowledge-graph, mmkg, acl-2026, pdf, slides, retrieval, hermes-self-improvement]
---

# MegaRAG — 多模态知识图谱驱动的 RAG

## 概述

**主题**: MegaRAG: Multimodal Knowledge Graph-Based Retrieval Augmented Generation
**会议**: ACL 2026 Main Conference (Long Papers), San Diego, pp. 48031–48059
**作者**: Chi-Hsiang Hsiao, Yi-Cheng Wang (equal), Tzung-Sheng Lin, Yi-Ren Yeh, Chu-song Chen
**arXiv**: 2512.20626 (v1 2025-11-26 / v2 2026-04-20) | **代码**: github.com/AI-Application-and-Integration-Lab/MegaRAG

**一句话**: 现有 KG-RAG（GraphRAG / LightRAG）只吃文本，遇到图表/示意图/幻灯片就瞎。MegaRAG 把**视觉线索同时注入三个环节——构图、检索、生成**，用「页面级两轮构图 + 全局子图引导精修 + 文本/视觉解耦两阶段生成」在 SlideVQA(2k) 上从 27.66% 打到 64.85%。

---

## 问题：三个被忽视的缺陷

### 1. 单模态盲区
GraphRAG / LightRAG / SubgraphRAG 全部是 text-only KG。文档里 60% 的信息在图表里（GenAI 幻灯片：686 张图 vs 5.5 万文本 token），文本 KG 完全抓不到。

### 2. Chunk 独立抽取 → 图谱碎片化
主流做法按 chunk 切分，**每个 chunk 独立抽实体**，导致：
- 跨 chunk 关系丢失
- 关键实体被割裂（同一本书里"欧盟碳排放政策"在 p.42 和 p.310 各出现一次，被拆成两个节点）

### 3. Modality Bias（模态偏置）⭐ 最有价值的发现
把「子图 + 页面图片」一起塞进 MLLM 的 prompt，模型会**系统性偏向文本**，视觉证据被浪费。论文的消融 A3 证明：单阶段联合条件化 vs 两阶段解耦生成，Overall 差距可达 **30 个百分点**（DLCV: 57.6% vs 27.2% Comprehensiveness）。

---

## 核心机制

### 阶段一：MMKG 构图（页面级 + 两轮）

**页面输入解构**（用 MinerU 抽取 4 类内容）：
| 元素 | 用途 | 是否生成实体节点 |
|------|------|----------------|
| 文本 `T_p` | 实体/关系来源 | ✅ 多个实体 |
| 图表图片 `F_p` | 实体来源 | ✅ **整个图表算一个独立实体** |
| 表格图片 `B_p` | 实体来源 | ✅ 同上 |
| 整页渲染图 | **仅用于空间关系推理** | ❌ 不生成节点 |

关键设计：**图表/表格整体作为一个实体**，而不是拆成图里的每个数字/柱子。例如柱状图 "Monthly Website Visitors" 被当作一个实体，再与周围讨论用户增长的文本建立关系。装饰性视觉（背景纹样、logo）直接忽略。

**实体 schema**：`name` + `type`（人/组织等预定义类型）+ `description`
**关系 schema**：`source` + `target` + `description` + `keywords[]`

**Round 1 — 初始构图（并行）**
```
for page in pages:            # 完全并行，页间独立
    MMKG_page = MLLM(initial_prompt, T_p, F_p, B_p, page_image)
```
每页独立调用 MLLM（论文用 GPT-4o-mini），prompt 强制约束输出格式以保证跨页一致性。

**合并**：同名实体节点合并（描述聚合），(source, target, rel_type) 相同的边合并（描述 + keywords 累加）。

**Round 2 — 全局子图引导的精修** ⭐ 核心创新
初始图漏掉了大量跨模态关系。做法：
1. 对每一页 `p`，从初始 KG 中检索**轻量子图** `G_sub(p)`
2. 子图检索不用整图注入（会撑爆 context window），而是复用该页第一轮已抽出的**实体名 + 关系关键词**，编码成 dense embedding，与初始 KG 的实体/关系向量匹配，再**扩展一跳邻居**
3. 把 `(页面原始多模态输入, 子图)` 喂给 MLLM 的 refinement prompt
4. MLLM 找出：输入里提到但子图里没有的实体 + 隐含但缺失的关系

**论文原例**：文本说 "Electric vehicle sales increased significantly in 2023"，旁边的柱状图 "Annual Sales by Vehicle Type" 有个显著的 "EV" 柱。第一轮把文本和图当成两个独立实体；精修阶段 MLLM 推断出图**视觉上支撑**该文本论断，自动补出 `illustrates` / `supports` 关系。

> **可迁移的通用模式**：这是「用已有产出做检索锚点，再让模型带着全局上下文回头补漏」的自举精修（self-bootstrapped refinement）。不限于 RAG——任何「第一遍局部抽取 + 第二遍全局补全」的场景都能套。

### 阶段二：统一索引与双层检索

**索引**：三类内容用同一个多模态编码器 **GME (GME-Qwen2-VL-2B)** 编码到同一向量空间，分三个独立向量库存储：
- 页面图片：直接编码
- 实体：`name + description` 拼成描述句后编码
- 关系：`keywords + src_name + tgt_name + description` 拼成描述句后编码

**Graph Retrieval（双层关键词策略）**：
```
keywords = MLLM(query) → 拆成 low-level(具体实体) + high-level(宽泛概念)
→ 低层+高层合并 → 在实体库检索 top-N 实体
→ 并行在关系库检索 top-N 关系（连带其 src/tgt 实体）
→ 每个实体再扩展一跳邻居
```
这个 low-level/high-level 双层关键词是 LightRAG 的设计，**不是 MegaRAG 原创**，但配合 MMKG 效果最好。

**Page Retrieval（互补）**：
同一 query 在共享向量空间里做 text→page-image 检索，取 top-N 页。负责抓符号图谱表达不了的**细粒度视觉与版面线索**。

> 两个检索通道是**并联互补**，不是二选一。页面检索负责"看"，图检索负责"串"。

### 阶段三：解耦式两阶段生成 ⭐

**动机**：联合输入会产生 modality bias。

```
Stage 1（并行两个中间响应）：
    answer_graph   = MLLM(subgraph + query)        # 只看符号图谱
    answer_visual  = MLLM(page_images + query)      # 只看视觉内容
Stage 2：
    final_answer   = MLLM(answer_graph, answer_visual, query)   # 融合
```
解耦后再融合，模型无法偏袒某一模态。

---

## 实验结果

**文本 Global QA（UltraDomain，pairwise LLM-judge 胜率）**

| 维度 | MegaRAG 胜率 |
|------|-------------|
| Comprehensiveness | 59.0% |
| Diversity | 71.4% |
| Empowerment | 74.8% |
| **Overall** | **71.8%** |

**多模态 Global QA（vs NaiveRAG / GraphRAG / LightRAG）**
Overall 胜率均值 **89.5%**；Comprehensiveness 83.3% / Diversity 92.7% / Empowerment 84.7%。
幻灯片类数据集（DLCV、GenAI）优势最大——核心内容是视觉而非文本。

**多模态 Local QA（accuracy，有 ground truth）**

| 数据集 | NaiveRAG | GraphRAG(L) | GraphRAG(G) | LightRAG | **MegaRAG** |
|--------|----------|-------------|-------------|----------|------------|
| SlideVQA (2k) | 11.34 | 6.80 | 5.22 | 27.66 | **64.85** |
| FinReport | 29.66 | 24.50 | 10.08 | 31.30 | **39.51** |
| FinSlides | 14.64 | 11.98 | 3.04 | 13.02 | **58.37** |
| TechReport | 36.63 | 29.60 | 15.07 | 42.74 | **51.51** |
| TechSlides | 32.94 | 26.81 | 16.03 | 31.39 | **60.86** |

FinSlides / TechSlides 上比最佳基线高 **45 / 29 个百分点**。

**消融（最关键）**

| 变体 | 含义 | 结论 |
|------|------|------|
| A1 | 构图时去掉所有视觉输入 | 一致下降，视觉密集文档受害最重 |
| A2 | 禁用 MMKG 检索，只用页面检索 | 崩塌，说明图谱不可替代（不是"多模态检索就够了"） |
| A3 | 单阶段联合生成，替代两阶段解耦 | 大幅下降，验证 modality bias 存在 |

---

## 与现有技能的差异化（避免重复）

| 技能 | 覆盖范围 | 与 MegaRAG 的区别 |
|------|---------|-------------------|
| `disco-rag` | 话语结构（RST + 修辞图） | Disco-RAG 管文本内部的论证流向；MegaRAG 管**模态**与**跨页实体图谱** |
| `hetero-graph-rag-2026` | 异构图 + agent 检索规划 | 那是 text KG 的 agent 化；MegaRAG 是**视觉信号进入 KG 构图** |
| `reflective-rag` | 反思标签 + ΔPPL 自监督 | 那是**评估/策略约束**层；MegaRAG 是**检索/构图架构**层 |
| `local-rag` | 本地 RAG 部署管线 | 工程栈，无多模态构图方法论 |
| `a-rag` | 三粒度检索接口 | 检索粒度维度正交于模态维度 |

MegaRAG 的独立贡献 = **视觉线索进 KG + 两轮全局引导精修 + 解耦式两阶段生成**。

---

## Hermes 落地路径

### 立即可用（无需新依赖）
1. **modality bias 检查项** → 加进任何"图 + 图"混合上下文的提示词设计：不要把符号结论和原始截图直接丢给模型一起总结，先分别问再融合。
2. **自举精修模式** → Hermes 已有 `~/.hermes/skills/` 分层加载机制。第一遍局部产出（实体/关系/摘要）→ 用它做检索锚点 → 带全局上下文回头补漏。这个模式可直接套到 skill 体系本身的"元数据补全"上。
3. **图表作为单一实体** → Hermes 处理 PDF/报告类任务时，一张图表 = 一个实体节点，而不是拆成数字碎片。实体粒度规则值得抄。

### 中期（需要 GPU + 依赖）
4. **MinerU**（opendatalab, release-1.3.6）做 PDF 结构化抽取 → 产出 text/figure/table/page-image 四件套。
5. **GME-Qwen2-VL-2B** 做统一多模态编码 → 三库（page/entity/relation）。
6. **LightRAG v1.4.3** 作为图检索底座（MegaRAG 本身就是 inspired by LightRAG 且直接依赖它）。

### 不建议
- 直接照搬其评测协议：GPT-4o-mini 做生成 + GPT-4.1-mini 做 judge，Hermes 用 MiniMax M3 跑需要重标定。
- 全量复现：Ultradomain 428 本教材 1000 万 token 级 token 成本太高。

---

## 工程要点与坑

| 要点 | 说明 |
|------|------|
| **环境隔离** | README 强制两套 conda 环境：`mineru`（跑 MinerU 抽取）+ `megarag`（跑图谱），还要把 LightRAG clone 到 `lib/` 目录 |
| **推理依赖** | 需要 GPU 做 embedding 推理（2B 视觉编码器），OpenAI API key 做 MLLM 抽取 |
| **自定义数据** | `cp -r egs/.template egs/<dataset>` → 改 `conf/addon_params.yaml` 的实体类型 → 跑 `run_build_mmkg.sh` / `run_querying.sh` |
| **prompt 格式** | Appendix B 给全了初始抽取 prompt 和 refinement prompt，跨页一致性靠"约束输出格式"保证，不是靠后处理 |
| **许可** | GitHub 显示 "License: Other"（自定义），README 里写 "This work has been accepted to ACL 2026" 的表述可能未随最终版更新，商用前要读 LICENSE 原文 |
| **维护活跃度** | 7 commits / 1 主要贡献者（Amiannn）——**学术原型，非生产级**，不要指望上游修 bug |

---

## 关键洞察（可迁移到 Hermes）

1. **模态解耦优于模态融合**。把不同类型的证据分开问、再合并，比一次性混合输入更可靠。同样的道理适用于"结构化数据 + 非结构化文本"、"检索结果 + 用户偏好"等异质上下文。
2. **局部抽取 + 全局精修的两轮法**能让图谱从碎片变成网络，成本只是一次额外的 MLLM 调用（每页仍并行）。
3. **符号抽象（KG）和原始感知（页面图）必须并存**。消融 A2 证明只留页面检索会崩塌——图谱不是检索的替代品，是检索的补充维度。
4. **"图表 = 单实体"是好的抽象粒度**。过度切分图内元素会制造噪声实体，丢失"这张图讲的是什么"。

---

## 来源

- ACL Anthology: https://aclanthology.org/2026.acl-long.2218/
- arXiv HTML v2: https://arxiv.org/html/2512.20626v2
- 代码: https://github.com/AI-Application-and-Integration-Lab/MegaRAG
- HuggingFace Papers: https://huggingface.co/papers/2512.20626
