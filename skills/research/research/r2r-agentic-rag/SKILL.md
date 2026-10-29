---
name: r2r-agentic-rag
description: R2R — SoTA production-ready Agentic RAG (7.9k stars, MIT)
trigger: Use when building knowledge retrieval pipelines, multi-hop QA, Deep Research, or agent memory with knowledge graphs
owner: hermes-evolution
created: 2026-10-21
updated: 2026-10-21
stars: 7984
license: MIT
topics: [rag, agentic-rag, knowledge-graph, multimodal, deep-research, retrieval]
---

# R2R — Agentic RAG System

## 核心概述

R2R (7,984 GitHub stars, MIT) 是生产级 AI 检索系统，将 Agentic RAG 带入企业级 RESTful API 框架。核心差异化：**Deep Research API** — 多步推理系统，从知识库和互联网同步获取数据，输出带引用的结构化答案。

## 关键架构

### 五层检索引擎
- **Multimodal Ingestion**: `.txt/.pdf/.json/.png/.mp3` 等多格式解析
- **Hybrid Search**: 语义搜索 + BM25 关键词搜索 + RRF (Reciprocal Rank Fusion) 融合
- **Knowledge Graph**: 自动实体/关系抽取，构建图谱
- **Agentic RAG**: 推理 agent 集成到检索管道，动态决策检索策略
- **Deep Research API**: 多步推理，跨知识库 + 外部网络，附引用

### Deep Research Agent 能力
```python
response = client.retrieval.agent(
    message={"role": "user", "content": "query with reasoning requirement"},
    rag_generation_config={
        "model": "anthropic/claude-3-7-sonnet-20250219",
        "extended_thinking": True,
        "thinking_budget": 4096,
        "temperature": 1,
        "max_tokens_to_sample": 16000,
    },
)
```

### 部署模式
```bash
# Light mode (SQLite, no Docker)
pip install r2r
export OPENAI_API_KEY=sk-...
python -m r2r.serve  # http://localhost:7272

# Full mode (PostgreSQL + full features)
git clone git@github.com:SciPhi-AI/R2R.git
cd R2R
export R2R_CONFIG_NAME=full OPENAI_API_KEY=sk-...
docker compose -f compose.full.yaml --profile postgres up -d
```

### SDK 支持
- **Python**: `pip install r2r` → `from r2r import R2RClient`
- **JavaScript**: `npm i r2r-js` → `const { r2rClient } = require('r2r-js')`

## 与 Hermes 相关性

### 适用场景
1. **Hermes 研究知识管理**: R2R 替代 `web_search + web_extract` 的粗粒度检索，为 ETF/小说研究提供结构化 Deep Research
2. **Agent Memory 增强**: 知识图谱自动抽取可补充 Hermes fact_store 的实体关系
3. **多跳推理**: R2R 的查询分解 → 检索 → 验证循环可迁移到 Hermes skill 发现流程

### 不适用场景
- R2R 是独立服务，不适合 Hermes 当前单进程架构
- 知识图谱抽取依赖额外 NLP 管道，维护成本高
- Deep Research API 需要强模型（如 Claude Sonnet），成本较高

## 核心创新点

| 能力 | R2R 实现 | Hermes 参考价值 |
|------|----------|----------------|
| Hybrid Search RRF | 语义+关键词融合 | 可用于 skill 检索精度提升 |
| Knowledge Graph | 自动抽取实体关系 | fact_store 结构化方向 |
| Deep Research | 多步推理+外部搜索 | 复杂研究任务的分解模式 |
| Multimodal | 图像/音频/文档 | 未来多媒体 skill 支持 |
| Citation | 答案溯源 | 报告可信度提升 |

## 落地建议

**立即可用（低门槛）**:
- pip 安装 R2R light mode，用作 Hermes 研究管道的 Deep Research 层
- 通过 `python3 -c "from r2r import R2RClient; ..."` 从 Hermes 直接调用
- RRF 混合检索算法可直接参考实现到 Hermes skill 检索

**中期集成（需架构调整）**:
- 将 R2R 作为 sidecar service 与 Hermes 共部署
- 用 Knowledge Graph 自动抽取补充 fact_store 关系

## 来源

- GitHub: https://github.com/SciPhi-AI/R2R
- 文档: https://r2r-docs.sciphi.ai/
- Discord: https://discord.gg/p6KqD2kjtB
