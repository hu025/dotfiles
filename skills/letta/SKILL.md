---
name: letta
description: Letta (formerly MemGPT) — stateful agents with persistent memory. Two repos: letta-ai/letta (landing page) and letta-ai/letta-code (active). Agent SDK v2 (TS) has MemFS/dreaming/mods; V1 SDK (Python) is legacy. Use when building stateful learning agents.
triggers:
  - Letta MemGPT stateful agent
  - agent memory tiered architecture
  - MemFS git-tracked memory
  - Agent SDK v2 TypeScript
category: agent-engineering
---

# Letta — Stateful Agents with Persistent Memory

## REPO SPLIT (Critical — Updated 2026-09)

| Repo | Role |
|------|------|
| `letta-ai/letta` | Landing page + archived v1 server (Python) |
| `letta-ai/letta-code` | Active development — agent harness, CLI, App Server, channels |

**Current focus: `letta-code` for all new work.**

## Two SDKs

| Feature | V1 SDK (legacy) | Agent SDK v2 |
|---------|----------------|--------------|
| Languages | Python, TypeScript | TypeScript only |
| Self-hosting | No (cloud only) | Yes (WebSocket endpoint) |
| MemFS / git-tracked memory | ❌ (blocks only) | ✅ |
| Skills / Subagents / Mods | ❌ | ✅ |
| Channels (Slack/Telegram/Discord) | ❌ | ✅ |
| Pre-made bash toolsets | ❌ | ✅ |
| Persistent filesystem | ❌ | ✅ |
| Similar to | OpenAI Responses API | Claude Agent SDK |

**V1 SDK is legacy. New projects → Agent SDK v2.**

## Core Capabilities

- **MemFS**: Git-tracked memory filesystem — every memory change is versioned with commit messages; dream-time consolidation
- **Agent Dreaming**: Sleep-time compute — sub-agent consolidates memory while main agent sleeps
- **Mods (Self-Modifying Harness Extensions)**: Agents can extend their own tool harness at runtime
- **Subagents**: Hierarchical multi-agent with shared memory blocks
- **Context Repositories**: Git-backed collaboration, multi-agent git sync
- **Channels**: Native Slack/Telegram/Discord integrations via Letta Code
- **Letta Evals**: Open-source evaluation framework for stateful agents (Context-Bench)
- **Memory Omni-Tool (Sep 2025)**: Claude Sonnet 4.5 integration for enhanced memory

## Installation

```bash
# Agent SDK v2 (TypeScript — active development)
npm install -g @letta-ai/letta-code

# Launch interactive terminal
letta

# Run tutorial agent
letta --new-agent --personality tutorial

# App server (local or self-hosted)
letta server

# Docker (self-hosted)
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

## v0.16.7 Key Updates (March 2026)

- Context window default raised from **32k → 128k**
- **MiniMax M2.7** model support added
- Compaction overhauled (fixes double-compaction loops)
- Summarizer now remembers plan files, GitHub PRs, structured content
- Git memory sync deferred until stream close (reduces mid-stream failures
- Block limits deprecated — blocks now grow freely
- Conversation forking with shared message history
- Security: local filesystem access blocked via ImageContent bypass

## Hermes Integration Points

```python
# 1. MemFS-style git memory: Hermes could track skill evolution in git
# 2. Agent dreaming: reflection step after complex tasks → update memory
# 3. Mods/harness extensions: Hermes could adopt plugin-style tool discovery
# 4. Letta Evals: use Context-Bench to evaluate Hermes memory quality

# Architecture pattern worth adopting:
# Task → Execute → Reflection → Memory update → Next task improved
# "Sleep-time compute": sub-agent rewrites memory while main agent sleeps
```

## Pitfalls

- **Two repos**: Don't use `letta-ai/letta` for new work — it's archived
- **Agent SDK v2 is TypeScript-only** — Python dropped; use V1 SDK for Python
- Memory persistence requires a running server (not library-based like Mem0)
- Block limits removed in v0.16.7 — manage block size via other means if needed
