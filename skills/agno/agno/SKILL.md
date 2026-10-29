---
name: agno
description: Agno v3.0 — open-source Python framework for building multi-agent systems. 42K stars, v3.0 (Sep 2026). Use when building production agent platforms with multi-tenancy, durable execution, and context offloading.
triggers:
  - Agno agent framework
  - multi-agent orchestration
  - agent reasoning
  - production agent framework
  - agent team coordination
  - Agno SDK
  - agno v3 production
category: agent-engineering
---

# Agno v3.0 — Production-Grade Multi-Agent Framework

## What It Does

Agno is an open-source Python framework for building production-grade multi-agent systems (**Apache-2.0, ~42K stars**). v3.0 (Sep 2026, latest 3.0.6) is a production-hardening release focused on: context/token cost reduction, durable background execution, multi-tenant isolation, and governance gates. Known for extreme performance (~3μs agent instantiation, ~6.5KB memory footprint).

## Core Capabilities

- **Model Agnostic**: Unified interface to 100+ providers — OpenAI, Anthropic, Gemini, Groq, Mistral, Ollama, LiteLLM, and more
- **Built-in Reasoning**: Three approaches — Reasoning Models, ReasoningTools, or custom chain-of-thought; reasoning is a first-class citizen
- **Agent Teams**: Coordinate, collaborate, or supervisor patterns; narrow-scoped agents with shared context; Team Modes, HITL for Teams, Approval System
- **Knowledge & Retrieval**: Agentic RAG as default (模型决定何时search); Hybrid Search (vector + keyword); 17 VectorDB backends; knowledge is writable = agent can persist learning
- **Memory & Storage**: Built-in `Storage` and `Memory` drivers; entity memory per user; SQLite/Postgres/Mongo/Redis/DynamoDB/Firestore backends
- **Structured Outputs**: Return fully-typed Pydantic responses via model structured outputs or `json_mode`
- **Pre-built FastAPI Routes**: Serve agents as HTTP endpoints in minutes
- **AgentOS Runtime**: Run agents as production services with tracing, scheduling, RBAC, multi-user support
- **MCP Integration**: Agent可作为MCP server暴露给coding agent (Cursor/VSCode/Windsurf); docs.agno.com/mcp 支持

## v3.0 Production Breakthroughs (Sep 2026)

### Tool Result & Media Offloading
- Large tool results offloaded to agent filesystem, model gets preview + id for on-demand fetch
- 113KB image: ~151,000 inline chars → ~2,900 chars (reference in DB row)
- Storage backends: local, S3, GCS, each with async twin
- Set `offload_tool_results=True` for automatic offloading

### Runs Table (Breaking Change)
- Each run gets its own row in `agno_runs` table (v2 packed all runs into session JSON blob)
- v2 write cost grew O(N²); v3 write is constant-cost regardless of session length
- Removes DynamoDB/Firestore item-size ceilings
- **Migration required**: `MigrationManager(db).up()` — non-destructive, idempotent

### Durable Background Execution
- Run committed to database **before** it starts → survives crashes, deploys, restarts
- Any replica can pick up and finish a run
- Queue controls: bounded concurrency, cancellation while queued, idempotency keys, backpressure
- Redis optional (coordination only; DB is source of truth)

### Multi-Tenant Data Isolation (v3.0)
Per-user isolation now covers:
- Sessions, metrics, schedules, evals
- Knowledge, components
- Entity memory
- 17 vector databases (SQL-based stores: fails loudly on unscoped search; schemaless: treated as shared)

### Studio 3.0 — Draft-to-Publish Governance
- Every component edit creates a private draft (not live until published)
- Immutable published versions with rollback
- Compare-and-set guards (typed conflict error on stale write)
- Tombstoned deletes with dependent-tracking

### CodeMode
- Persistent Python kernel for the session; model writes code calling tools as awaitable handles
- Composes multiple tool calls in one step (vs one-call-at-a-time burn)
- **Not a sandbox** — runs with same permissions as the agent process
- Requires `pip install 'agno[code]'`; isolate in container for untrusted inputs

## v3.0 Breaking Changes
- Runs moved to `agno_runs` table → one-time migration required
- `MultiMCPTools` removed → one `MCPTools` per server
- Google tool modules: `agno.tools.google.*` (flat modules deprecated)
- `JWTMiddleware`: `secret_key` → `verification_keys`
- Various agent parameter renames (see v3.0 changelog)

## Installation

```bash
pip install -U agno

# Extras
pip install -U "agno[openai]"       # OpenAI
pip install -U "agno[anthropic]"     # Anthropic Claude
pip install -U "agno[postgres]"      # PostgreSQL backend
pip install -U "agno[code]"          # CodeMode
pip install -U "agno[ollama]"        # Local Ollama models

# Docker (Postgres for production)
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

## Hermes Integration Points

1. **Durable Execution Pattern**: Hermes cron/event-driven runs can learn from Agno's DB-first durable execution — commit state before start
2. **Tool Result Offloading**: Hermes's large tool outputs could use similar offloading to reduce context pressure
3. **Multi-Tenant Isolation**: Hermes user/session isolation can reference Agno's per-user scoping model
4. **Studio Governance**: draft-and-publish workflow pattern for Hermes skill/component lifecycle management
5. **CodeMode Concept**: persistent execution kernel for agent code composition (Hermes execute_code alternative)
6. **MCP as Agent Interface**: Agno MCP server exposure is a mature reference for Hermes MCP tool exposure

## Performance Benchmarks

- Agent instantiation: **~3μs** (vs LangGraph significantly slower)
- Memory footprint: **~6.5KB** per agent
- Tool call overhead: minimized for high-throughput scenarios

## Pitfalls

- v3.0 migration required (runs table) — non-breaking but mandatory before serving traffic
- CodeMode is **not a sandbox** — never use with untrusted inputs
- Studio governance requires explicit publish step; agents won't update live without it
- Vector DB per-user migration on pre-v3 collections: separate script, not automatic
- AgentOS cloud is proprietary; OSS is SDK only
- Production deployment with Postgres/Docker requires DevOps setup
