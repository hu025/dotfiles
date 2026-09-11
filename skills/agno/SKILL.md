---
name: agno
description: Agno — open-source Python framework for building multi-agent systems with built-in reasoning, memory, knowledge retrieval, and high performance. Use when building complex agent teams or production agent pipelines.
triggers:
  - Agno agent framework
  - multi-agent orchestration
  - agent reasoning
  - production agent framework
  - agent team coordination
  - Agno SDK
category: agent-engineering
---

# Agno — High-Performance Multi-Agent Framework

## What It Does

Agno is an open-source Python framework for building production-grade multi-agent systems (Apache-2.0, **42.1K stars**). It provides the full stack: agents with tools, reasoning, memory, knowledge retrieval, agent teams, and a runtime to serve them. Known for extreme performance (~3μs agent instantiation, ~6.5KB memory footprint). 400 contributors, v2.5+.

## Core Capabilities

- **Model Agnostic**: Unified interface to 23+ providers — OpenAI, Anthropic, Gemini, Groq, Mistral, Cohere, Ollama, and more
- **Built-in Reasoning**: Three approaches — Reasoning Models, ReasoningTools, or custom chain-of-thought; reasoning is a first-class citizen
- **Agent Teams**: Coordinate multiple agents (coordinate, collaborate, supervisor patterns); narrow-scoped agents with shared context; Team Modes, HITL for Teams, Approval System
- **Knowledge & Retrieval**: Agentic RAG as default (模型决定何时search); Hybrid Search (vector + keyword); Cohere Rerank v3.5重排序; 19种VectorDB (LanceDB/ChromaDB/Pinecone/Milvus等); 知识可写入=Agent可保存学习成果; Traditional RAG (retrieval before first call) also supported
- **Memory & Storage**: Built-in `Storage` and `Memory` drivers for long-term memory and session storage
- **Structured Outputs**: Return fully-typed Pydantic responses via model structured outputs or `json_mode`
- **Pre-built FastAPI Routes**: Serve agents as HTTP endpoints in minutes
- **Monitoring**: Real-time session and performance monitoring at agno.com (or self-host)
- **AgentOS Runtime**: Run agents as production services with tracing, scheduling, RBAC
- **MCP Integration**: Agent可作为MCP server暴露给coding agent (Cursor/VSCode/Windsurf); docs.agno.com/mcp 支持

## Installation

```bash
pip install -U agno

# With extras for specific providers
pip install -U "agno[openai]"       # OpenAI
pip install -U "agno[anthropic]"     # Anthropic Claude
pip install -U "agno[postgres]"      # PostgreSQL backend
pip install -U "agno[ollama]"        # Local Ollama models

# With Docker (Postgres for production)
docker run -d \
  -e POSTGRES_DB=ai -e POSTGRES_USER=ai -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql -v pgvolume:/var/lib/postgresql \
  -p 5532:5432 --name pgvector agnohq/pgvector:18
```

## Quickstart

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Single agent
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), YFinanceTools(stock_price=True)],
    instructions="Use tables for data. Always cite sources.",
    markdown=True,
)
agent.print_response("What's NVDA's stock price and news?", stream=True)

# Agent team (multi-agent coordination)
from agno.team import Team

web_agent = Agent(
    name="Web Agent",
    role="Research the web",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True)],
)

team = Team(
    mode="coordinate",
    members=[web_agent, finance_agent],
    instructions=["Always include sources", "Use tables for data"],
)
team.print_response("Research AI semiconductor companies", stream=True)
```

## Hermes Integration

Agno is a reference architecture for Hermes:

1. **Agent Team Pattern**: Hermes's multi-agent workflows can adopt Agno's coordinate/collaborate/supervisor patterns
2. **Reasoning as First-Class**: Agno's `ReasoningTools` or reasoning model support can inform Hermes's own reasoning traces
3. **Built-in Evaluation**: Every agent run produces trace logs with token usage, latency, quality scores — useful for Hermes's own self-evaluation
4. **FastAPI Routes**: Agno's pre-built routes could wrap Hermes for HTTP-accessible agent serving

## Performance Benchmarks

- Agent instantiation: **~3μs** (vs LangGraph significantly slower)
- Memory footprint: **~6.5KB** per agent
- Tool call overhead: minimized for high-throughput scenarios

## Why Not LangGraph/CrewAI?

Agno is more modular, more performant, and has reasoning built-in rather than bolted on. CrewAI is higher-level but less flexible. LangGraph is lower-level but more verbose.

## Pitfalls

- Relatively newer than LangChain/LangGraph — community smaller but growing fast
- AgentOS cloud offering is proprietary — OSS is just the SDK
- Production deployment with Postgres/Docker requires DevOps setup
