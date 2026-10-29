---
name: grove-multi-agent
description: Grove — Rust multi-agent workspace manager (v0.12, MIT). Agent Graph DAG + worktree isolation + Hermes native support.
triggers:
  - Grove workspace manager
  - multi-agent parallel coding
  - Hermes agent Grove
created: 2026-09-27
updated: 2026-09-27
sources:
  - https://garrickz2.github.io/grove
  - https://github.com/GarrickZ2/grove
  - https://github.com/bearlike/Grove
tags:
  - multi-agent
  - workspace-manager
  - rust
  - hermes-integration
  - agent-orchestration
---

# Grove — Multi-Agent Workspace Manager

## Overview

Grove is a Rust-built (MIT) workspace manager for running multiple AI coding agents in parallel. Each agent gets an isolated Git worktree + tmux session. v0.12.4 released August 2026.

**Key differentiator**: First platform to natively support **Hermes** as a built-in agent alongside Claude Code, Codex, Gemini CLI, Cursor, etc.

## Core Architecture

### Worktree Isolation
- Each task/agent = dedicated Git worktree on its own branch
- Zero branch conflicts between agents
- Git history never polluted by Grove (never auto-commits/pushes)

### Agent Graph (DAG-based Orchestration)
- Visual DAG editor — spawn agents, connect edges, assign duties
- Structured `<grove-meta>` envelopes for cross-agent messages (not string concatenation)
- 6 MCP tools: `spawn` · `send` · `reply` · `contacts` · `capability` · `get_spawn_candidates`
- Cycle detection + single-in-flight per edge enforced at DB layer
- Orchestrator agents dispatch workers via MCP

### Multi-Surface Deployment
| Surface | Description |
|---------|------------|
| TUI | Terminal-first, keyboard-driven |
| Web IDE | FlexLayout panels, same workspace via browser |
| Desktop GUI | Ghostty-native, native window |
| Mobile + Voice | Radio: hold-to-talk voice control |

### Built-in Agents (10)
Claude Code, Codex, Gemini CLI, GitHub Copilot, Cursor Agent, Junie, Trae CLI, Kimi, Qwen, **Hermes**, Kiro, OpenClaw

### Studio (Non-Technical Collaboration)
- Upload assets, edit project memory, review artifacts
- Excalidraw sketches agents can read via MCP
- No git knowledge required
- D2 + Mermaid inline rendering

### Skills Marketplace
- Skills installable in one click — applies to all agents globally
- Grove ships its own MCP server for orchestrator agents

### OpenTelemetry Native
- Ships collector stack between agent and trace backend
- Token fields for pricing, host-specific env var reading

## Hermes Integration

Grove v0.12.4 **natively supports Hermes** as a first-class built-in agent. Hermes agent icon is in the official Grove asset set.

This is a notable ecosystem signal: Hermes Agent is being recognized alongside Claude Code, Codex, and Cursor as a top-tier coding agent.

## Installation

```bash
# macOS/Linux
curl -sSL https://raw.githubusercontent.com/GarrickZ2/grove/master/install.sh | sh

# Homebrew
brew tap GarrickZ2/grove
brew install grove

# Windows
irm https://raw.githubusercontent.com/GarrickZ2/grove/master/install.ps1 | iex

# Cargo
cargo install grove-rs
# with desktop GUI:
cargo install grove-rs --features gui
```

**Prerequisites**: tmux, Git 2.5+, one AI coding CLI (Claude Code / Opencode / Codex / Gemini CLI)

## Relevance to Hermes

1. **Ecosystem recognition**: Hermes is a native Grove agent — signals production-grade status
2. **Fleet management**: Grove's worktree isolation pattern could inform Hermes multi-agent workspace design
3. **MCP dispatch**: Grove's agent-graph MCP tools are a reference for Hermes orchestrator→worker patterns
4. **Project memory**: Studio's durable knowledge graph could inspire Hermes persistent context

## Noteworthy Patterns

- **Never commits/pushes** — Grove leaves git history purely to the human
- **Per-task DB isolation** — cross-agent coordination enforced at DB layer, not application code
- **ACP-native** — uses ACP for connection, MCP for action (dual-protocol approach)
- **Agent Graph DAG** — first-class typed graph representation of multi-agent relationships

## References

- Landing: https://garrickz2.github.io/grove
- Main repo: https://github.com/GarrickZ2/grove
- bearlike/Grove (alternative Python/TS fork): https://github.com/bearlike/Grove
