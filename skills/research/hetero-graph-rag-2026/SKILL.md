# Agent-Enhanced Heterogeneous Graph RAG (WWW 2026)

## 概述

**主题**: Agent-Enhanced Heterogeneous Graph RAG for Academic Question Answering
**会议**: ACM Web Conference 2026 (WWW '26)
**论文**: arXiv:2609.00761, DOI: 10.1145/3774904.3792960
**作者**: Runsong Jia, Mengjia Wu, Ying Ding, Jie Lu, Yi Zhang (University of Technology Sydney, UT Austin)
**许可**: CC BY 4.0

## 核心创新

### 三阶段 Agentic Pipeline

将 RAG 三个核心阶段显式 agentic 化：

```
Query-Aware Retrieval Agent
    ↓ query_type / start_node / hop_budget / traversal_plan
Graph Retrieval + Sufficiency-Aware Reranking Agent
    ↓ coverage + relevance 评分 / 自适应扩展
Graph-Grounded Verification Agent
    ↓ entity alignment / relation alignment / attribute match
```

### 1. Query-Aware Retrieval Agent

**四类查询分类**（核心贡献）：
- `Attr` (0-hop): 属性查询，如"作者A来自哪个机构"
- `Rel` (1-hop): 直接关系查询，如"某作者发表了哪些论文"
- `Agg` (1-2 hops): 聚合查询，需要数值推理
- `Multi` (2+ hops): 多跳推理查询

**输出结构化检索计划**：
```
Ω(q) = (t, s, h, E(q), π_t)
  t ∈ {Attr, Rel, Agg, Multi}     # query type
  s ∈ {Author, Paper, Venue}     # start node type
  h                                   # hop budget
  E(q)                               # entity mentions
  π_t                                 # traversal plan
```

**实现**: GPT-4-turbo classifier + in-context examples，零微调。

### 2. Sufficiency-Aware Reranking Agent

**充分性评分**：
```
S_suf = α·Cov(q, G_q) + (1-α)·Rel(q, G_q)
  Cov = 实体/属性覆盖率（E(q)中mention在图中的匹配比例）
  Rel = 语义相关性（query embedding与子图节点文本的相似度）
```

**自适应扩展**：当 S_suf < τ 时，触发受控图扩展（最多2次），控制延迟同时保证召回。

**检索指标**: Sentence-Transformers (all-MiniLM-L6-v2) 384维嵌入，语义相似度匹配。

### 3. Graph-Grounded Verification Agent

**事实一致性评分**：
```
S_cons = β₁·EntAlign(a, G_q) + β₂·RelAlign(a, G_q) + β₃·AttrMatch(a, G_q)
  EntAlign: 答案中实体是否在图中有对应节点
  RelAlign: 答案中关系三元组是否在图中有对应边
  AttrMatch: 数值/类别属性是否与图节点属性一致
```

**验证-再生成循环**: 若 S_cons < γ，最多尝试2次重新生成，或输出不确定性信号。

## 实验结果

### 数据集
- **OpenAlex**: 76,569 节点, 105,290 边
- **DBLP**: 62,443 节点, 79,697 边
- 每数据集 400 queries (100/类型)

### 性能对比

| Model | OpenAlex Acc | DBLP Acc |
|-------|-------------|----------|
| Qwen 2.5 7B | 48.63 | 45.93 |
| GPT o3 | 53.58 | 51.65 |
| Vanilla RAG | 54.36 | 52.14 |
| GraphRAG | 61.87 | 60.27 |
| GraphCoT | 64.28 | 68.52 |
| AdaptiveRAG | 72.58 | 70.23 |
| Agent-G | 73.14 | 69.74 |
| **Ours** | **76.68** | **73.43** |

### Ablation 贡献度
- Retrieval Agent 移除 → 最大性能下降（query-type 规划最重要）
- Reranking Agent 移除 → 次大下降（自适应扩展是关键）
- Verification Agent 移除 → F1/Hit@1 下降（实体/关系/属性检查有效）

## 对 Hermes 的价值

### 可迁移设计

1. **Query-type 分类 → skill 分层加载**
   - Attr → 简单直接 skill
   - Multi → 复杂多步 skill
   - 对应 skill 按复杂度选择加载策略

2. **Sufficiency Score → skill 充分性检查**
   - 在 skill 执行前检查上下文覆盖率
   - 不足时触发 skill 补充或扩展

3. **Verification Agent → 输出事实性检查**
   - 对 cron 报告内容进行实体/关系验证
   - 防止幻觉式报告

4. **图结构验证 → 知识图谱增强**
   - fact_store 可借鉴三元组验证逻辑
   - EntAlign/RelAlign/AttrMatch 模式

### 核心启发

> **Query complexity modeling 是 agentic RAG 的核心差距**
> 固定检索深度 vs 自适应扩展 = 固定 skill 执行 vs 动态 skill 组合

## 来源

- 论文: https://arxiv.org/abs/2609.00761
- HTML: https://arxiv.org/html/2609.00761v1
- ACM: https://dl.acm.org/doi/10.1145/3774904.3792960
