---
name: a-rag
description: A-RAG — Agentic RAG with hierarchical retrieval interfaces (keyword/semantic/chunk read)
triggers: [agentic RAG, hierarchical retrieval, multi-granularity RAG, adaptive retrieval]
owner: hermes-evolution
updated: 2026-10-20
tags: [agentic-ai, RAG, retrieval, knowledge-base, information-retrieval]
---

# A-RAG — Hierarchical Retrieval Interfaces for Agentic RAG

## Core Identity
- **Type**: Agentic RAG framework (research paper)
- **Paper**: [arXiv:2602.03442](https://arxiv.org/abs/2602.03442) (Feb 2026)
- **Code**: [github.com/Ayanami0730/arag](https://github.com/Ayanami0730/arag)
- **License**: Apache 2.0 (code)

## Problem Statement
Existing RAG systems fail to leverage frontier model capabilities:
1. **Paradigm 1**: Single-shot retrieval → concatenate → generate (no model agency)
2. **Paradigm 2**: Predefined workflow → model follows steps (rigid, no adaptation)
Neither paradigm allows the model to participate in retrieval decisions.

## Core Innovation: Hierarchical Retrieval Interfaces

A-RAG exposes three retrieval tools directly to the model:

### Three Granularities
1. **Keyword Search**: Fast, exact-match (BM25 style)
2. **Semantic Search**: Embedding-based similarity (vector search)
3. **Chunk Read**: Direct passage access (high precision)

### Agentic Loop
```
Agent decides → which tool? → executes → observes result → 
assesses sufficiency → either continues or generates
```

Model can adaptively choose granularity based on query complexity:
- Simple factual query → keyword search
- Semantic concept query → semantic search  
- Specific passage needed → chunk read

## Key Findings

### Scaling with Model Improvements
- Unlike static RAG, A-RAG benefits from stronger models
- Model can learn when to retrieve, what to retrieve, how to retrieve
- Demonstrates comparable/lower token cost with better results

### Test-Time Compute Scaling
- A-RAG scales with increased reasoning effort
- More compute → better retrieval decisions → better answers

## Hermes Integration Potential
- **High priority**: Hermes knowledge retrieval could adopt A-RAG three-tier retrieval
- **Medium priority**: Replace single-vector-search with keyword + semantic + chunk hierarchy
- **Medium priority**: Agentic retrieval loop (decide → retrieve → assess → iterate) for Hermes context building
- **High priority**: Especially valuable for ETF/research cron tasks where retrieval quality matters

## Three-Tier Retrieval Design for Hermes
```python
# Tier 1: Keyword search (fast, exact)
results = keyword_search(query, top_k=50)

# Tier 2: Semantic search (contextual)
results = semantic_search(query, top_k=20)

# Tier 3: Chunk read (precise, for confirmed relevant docs)
results = chunk_read(doc_ids, chunk_size=500)

# Agentic loop: model decides tier progression
if sufficient_context():
    generate()
else:
    refine_query() or escalate_tier()
```

## Related Skills
- `local-rag`: Local RAG pipelines with Ollama
- `agentmemory`: Agent memory frameworks
- `openviking`: Context database with L0/L1/L2 tiering
