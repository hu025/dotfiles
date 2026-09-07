---
name: letta
description: Letta (formerly MemGPT) — stateful agents with tiered memory architecture, sleep-time compute, and git-backed Context Repositories. Use when building agents that learn and self-improve over time.
triggers:
  - Letta agent memory
  - stateful AI agent
  - agent self-improvement
  - MemGPT replacement
  - tiered memory architecture
  - sleep-time compute
category: agent-engineering
---

# Letta — Stateful Agents with Persistent Memory

## What It Does

Letta builds AI agents that maintain persistent memory across sessions — they learn, adapt, and improve over time rather than starting fresh each conversation. Formerly MemGPT, now a full platform with CLI, GUI, server, and cloud.

## Core Capabilities

- **Tiered Memory Architecture**: Organizes memory into tiers (recent, archived, core) with automatic archival — mimics human memory hierarchy
- **Sleep-Time Compute**: "Memory editing agents" run in parallel during idle — the main agent focuses on tasks while a subconscious agent consolidates memory
- **Context Repositories (Feb 2026)**: Git-backed memory filesystem — every memory change is versioned with commit messages; enables multi-agent collaboration via git
- **Self-Improvement in Token Space**: Agents programmatically rewrite their own context/prompts to improve behavior
- ** `/palace` — Memory Visualization**: View agent's memory state as a palace/loci visualization
- ** `/doctor` — Memory Audit**: Diagnose and fix memory quality issues
- **Agent File Format (.af)**: Open serialization format for sharing stateful agents across frameworks
- **Multi-Channel**: Terminal CLI, Web GUI, Desktop apps (macOS/Windows/Linux), Slack/Telegram/Discord, Cloud

## Installation

```bash
# npm (fastest)
npm install -g @letta-ai/letta-code

# Launch interactive terminal
letta

# Run tutorial agent
letta --new-agent --personality tutorial

# App server (local or self-hosted)
letta server

# Docker
docker run -p 8282:8282 lettaai/letta:latest
```

## Key Commands

```
/palace         — Visualize agent's memory structure
/doctor         — Audit and fix memory quality
/sleeptime      — Enable sleep-time memory consolidation
/memory-repository set git@github.com:...  — Sync memory to GitHub
/skills         — View available skills
/skill-creator  — Create new skill
/search         — Search across all messages and agents
```

## Hermes Integration

Letta's self-improvement mechanisms are the most relevant for Hermes:

```python
# Letta's agent can programmatically update its own memory blocks
# Hermes can adopt similar patterns:
# 1. Store "lessons learned" in a memory block
# 2. On task completion, agent reflects and updates memory
# 3. Sleep-time consolidation → refine/improve stored knowledge

# Letta also exports .af agent files — Hermes could:
# - Import/export agent state for backup/migration
# - Share agent configurations between Letta and Hermes
```

## Architecture Insight for Hermes

Letta's key insight: **agents should be able to edit their own memory**. Hermes can borrow this pattern:

- Add a "reflection" step after complex tasks — agent stores what worked/didn't
- Implement a "memory importance" score — frequently used facts get higher weight
- Use `/doctor` style self-audit to identify memory gaps

## Self-Improvement Loop

```
Task → Agent executes → Reflection →
Memory update (what worked?) → Next task improved
```

Letta's "sleep-time compute" is the extreme version: dedicated sub-agent that rewrites memory while main agent sleeps.

## Pitfalls

- Letta v1 server is archived; active development is in `letta-ai/letta-code`
- Memory persistence requires a running server (not fully library-based like Mem0)
- Tiered memory management adds complexity — start with simple flat memory if new to agent memory
