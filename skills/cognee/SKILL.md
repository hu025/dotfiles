---
name: cognee
description: Cognee — open-source AI memory platform with knowledge graph layer for agents. Ingests any data format, builds a queryable knowledge graph, 92.5% retrieval accuracy. Use when agents need structured long-term memory with graph relationships.
triggers:
  - cognee memory graph
  - knowledge graph for AI agents
  - structured agent memory
  - graph-based retrieval
  - memory for autonomous agents
  - cognee integration
category: agent-engineering
---

# Cognee — Knowledge Graph Memory for AI Agents

## What It Does

Cognee is an open-source AI memory platform that ingests data in any format and continuously builds a self-hosted knowledge graph. It combines vector embeddings, graph reasoning, and cognitive-science-grounded ontology generation to make information both searchable by meaning and connected by relationships.

## Core Capabilities

- **v1.0 Memory-Native API**: Four verbs — `remember`, `recall`, `improve`, `forget` — same interface in Python SDK, HTTP API, and MCP
- **Hybrid Retrieval**: Combines vector similarity + graph traversal + BM25 lexical retrieval → fused with reciprocal rank fusion (RRF); up to 92.5% retrieval accuracy
- **Self-Improving Memory**: Feedback weights on graph nodes/edges influence retrieval scoring; importance-weighted ingestion; frequency weights via session API
- **Multiple Storage Backends**:
  - Local: SQLite + LanceDB + Ladybug (default, zero infra)
  - Production: PostgreSQL (full graph backend), Neo4j, Amazon Neptune, Redis
  - Vector: pgvector, ChromaDB, Qdrant, Weaviate, Milvus
- **Data Ingestion**: Any format — JSON, CSV, Markdown, PDFs, DOCX, websites (scraping), code graphs
- **Ontology Support**: Define custom data models to ground memory in your schema
- **TypeScript SDK**: Same core memory verbs in TypeScript for JS/TS agent platforms
- **MCP Integration**: Connect via Model Context Protocol to Claude Code and other MCP-compatible agents
- **Import/Export**: Import from Mem0, Zep, Letta; export portable COGX archives
- **Modal Deployment**: One-click deploy to Modal, Railway, Fly, Render

## Installation

```bash
# Base install (local dev — no external services)
pip install cognee
# or
uv pip install cognee

# With PostgreSQL (production)
pip install "cognee[postgres]"

# With Neo4j graph + AWS S3
pip install "cognee[neo4j,aws]"

# With Claude Code integration
pip install "cognee[anthropic]"

# With web scraping
pip install "cognee[scraping,docs]"

# With code graph analysis
pip install "cognee[codegraph]"

# CLI (global)
pipx install cognee  # or: uv tool install cognee
cognee-cli remember ./my_data/ --dataset my_project
cognee-cli recall "What does the project know about X?"
cognee-cli improve  # enrich existing dataset
cognee-cli forget --dataset my_project  # delete dataset
```

## Quickstart

```python
import asyncio
import cognee

await cognee.forget(everything=True)

# Ingest data → builds knowledge graph
await cognee.remember(
    text_data,
    node_set=["my_knowledge"],
    self_improvement=False
)

# Query the graph with natural language
result = await cognee.recall(
    "What do you know about topic X?",
    dataset_name="my_project"
)

# Improve — run enrichment pipeline
await cognee.improve(dataset_name="my_project")
```

## Hermes Integration

Cognee's knowledge graph approach is the most structured memory option for Hermes:

```python
# Hermes can use cognee as its persistent memory layer:
# 1. On task completion → remember key facts, patterns, outcomes
# 2. On new task → recall relevant past experiences
# 3. Periodic improve → enrich memory with new relationships

# Cognee vs Mem0 for Hermes:
# - Mem0: simpler, user-preference focused, self-editing
# - Cognee: richer graph relationships, ontology support,
#           better for complex structured knowledge
```

## Memory-Native API (v1.0)

```
remember(data, node_set)  → ingest and build graph
recall(query)             → retrieve from graph + vectors
improve(dataset)          → run enrichment pipeline
forget(dataset)           → delete stored data
```

## Self-Improvement Mechanism

```python
# Feedback loop — agents rate memory quality
await cognee.recall(
    query,
    dataset_name="my_project",
    feedback={"relevance": 0.9, "accuracy": 0.8}
)
# Feedback weights update retrieval scores automatically
```

## Comparison: Cognee vs Mem0 vs Letta

| Feature | Cognee | Mem0 | Letta |
|---------|--------|------|-------|
| Memory Type | Vector + Graph | Vector + Key-Value | Tiered + Archived |
| Schema/Ontology | Yes | No | Partial |
| Self-Improving | Yes (feedback weights) | Yes (self-editing) | Yes (sleep-time) |
| Deployment | Local to cloud | Library to cloud | Server-based |
| Data Model | Customizable | Fixed tiers | Agent File (.af) |
| Retrieval | Hybrid (graph+vector+BM25) | Hybrid | Similarity |

## Pitfalls

- Default local storage (SQLite/LanceDB) not suitable for production multi-user
- Graph-native backend (Neo4j) recommended for production knowledge graphs
- Requires careful ontology design for maximum benefit
- Some advanced features (distributed execution, code graphs) need extra setup
