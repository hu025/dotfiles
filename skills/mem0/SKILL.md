---
name: mem0
description: Mem0 memory layer for AI agents — multi-level persistent memory, cross-session personalization. Use when building agents that remember user preferences, session state, or agent learned facts across interactions.
triggers:
  - agent memory layer
  - persistent user memory
  - cross-session context
  - personalization for AI agents
  - Mem0 integration
category: agent-engineering
---

# Mem0 — Memory Layer for AI Agents

## What It Does

Mem0 ("mem-zero") is a dedicated memory layer for AI applications — the closest thing to a "operating system for agent memory." It provides persistent, adaptive memory that survives across sessions and evolves from interactions.

## Core Capabilities

- **Multi-Level Memory**: User memory (long-term preferences), Session memory (within-conversation), Agent memory (learned facts) — all with adaptive self-editing when facts conflict
- **Hybrid Vector + Graph Retrieval**: Combines semantic vector search with relationship graphs for precise recall
- **Self-Improving**: Learns from interactions — when conflicting facts appear, it self-edits rather than appending duplicates
- **Memory Compression Engine**: Automatically condenses chat history into compact memories, reducing token costs
- **Cross-Platform**: Works as library (`pip install mem0ai`), self-hosted server (Docker), or managed cloud
- **Model-Agnostic**: OpenAI, Anthropic, Gemini, Ollama, Groq, Mistral, Cohere
- **Import/Export**: Import from Mem0 Platform, export COGX archives; integrates with LangChain, AutoGen, LlamaIndex

## Installation

```bash
# Library (fastest — no external deps)
pip install mem0ai

# With NLP/BM25 keyword matching
pip install "mem0ai[nlp]"
python -m spacy download en_core_web_sm"

# CLI
pip install mem0-cli  # or: npm install -g @mem0/cli
mem0 init
mem0 add "Prefers dark mode" --user-id alice
mem0 search "What does Alice prefer?" --user-id alice
```

## Hermes Integration

Mem0 gives Hermes a persistent memory layer it currently lacks. Connect via Python SDK in a Hermes skill:

```python
from mem0 import MemoryClient
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# On each user interaction — store context
messages = [{"role": "user", "content": user_input}]
client.add(messages, user_id="hermes")

# On startup — retrieve relevant memory
memories = client.search(user_input, user_id="hermes", limit=5)
# Inject memories into system prompt
```

## Key Advantages for Hermes

1. **Replaces manual context management**: Hermes can remember user preferences across weeks/months, not just the current session
2. **Self-improving**: Memory quality improves automatically — no manual memory pruning needed
3. **Drop-in**: Single `pip install` — no infrastructure changes
4. **Multi-agent ready**: Shared memory across multiple Hermes sub-agents or sessions

## Quickstart

```python
import os
from mem0 import MemoryClient

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# Add interaction
client.add(
    [{"role": "user", "content": "I prefer Python over JavaScript"}],
    user_id="dev_saber"
)

# Retrieve when relevant
results = client.search(
    "What are this user's language preferences?",
    user_id="dev_saber"
)
print(results)
```

## Self-Hosted Option

```bash
docker compose up  # Mem0 server with Postgres/vector DB
```

Then point the SDK at your server instead of the cloud API.

## Pitfalls

- Default uses OpenAI embeddings — set `MEM0_API_KEY` or specify alternative provider
- Requires `user_id` for memory partitioning — use consistent IDs across sessions
- Cloud platform requires signup at app.mem0.ai
