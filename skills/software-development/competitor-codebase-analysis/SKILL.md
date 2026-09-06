---
name: competitor-codebase-analysis
description: Study multiple existing codebases in parallel using subagents, extract best patterns, then design a new system that synthesizes the best of each. Use before building any new framework, tool, or platform.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, architecture, design, multi-agent]
    use_case: analyzing-competitors-before-building
---

# Competitor Codebase Analysis

## When to Use

Before building a new system, framework, or tool — study 2-4 existing similar systems **in parallel**, extract their best patterns, then synthesize into a new design.

**Example scenarios:**
- Building a new AI agent framework (study LangChain + AutoGPT + Hermes)
- Building a messaging bot (study Discord.py + Telegram Bot API + OpenClaw)
- Building a web framework (study FastAPI + Express + Rails)
- Any time you need to "learn from existing codebases"

## Process

### Step 1: Setup — Parallel Subagent Analysis

Spawn one subagent per codebase to analyze. Each subagent should focus on:
1. **Architecture** — overall structure, entry points, key abstractions
2. **Core patterns** — how components interact, dependency injection, plugin systems
3. **Tool/tool registration system** — how capabilities are discovered and registered
4. **Session/state management** — how sessions, threads, or state are handled
5. **Extension points** — how to add new features or plugins
6. **What makes it unique** — standout design decisions

### Step 2: Synthesis — Pattern Comparison Table

After all subagents return, create a comparison table:

```
| Aspect          | System A | System B | System C | Best Of |
|-----------------|----------|----------|----------|---------|
| Tool registry   | X        | Y        | Z        | A       |
| Session model   | X        | Y        | Z        | B       |
| Plugin system   | X        | Y        | Z        | A+C     |
```

Extract "best of" from each system. Identify conflicts to resolve in new design.

### Step 3: Design — Write SPEC.md

Design the new system that combines the best patterns. Structure:

1. **Concept & Vision** — What problem does the new system solve?
2. **Design Principles** — 3-5 key principles from each source
3. **Architecture** — Overall structure with ASCII diagram
4. **Core Concepts** — New abstractions, how they differ from sources
5. **Implementation Scope** — v0.1 must/will/out-of-scope

### Step 4: Implementation — Subagent-Driven Development

Use `subagent-driven-development` to implement from spec. Keep SPEC.md updated as implementation reveals necessary design changes.

## Key Insights from OpenClaw + Hermes Analysis

### OpenClaw Strengths
- **Skills as Markdown** — Versioned, agent-readable, lightweight
- **Capability-based plugins** — Clear ownership, `registerProvider()` / `registerChannel()`
- **Session threading** — `platform:account:thread` routing
- **Boot hooks** — `BOOT.md` startup automation
- **Heartbeat system** — Proactive background checks

### Hermes Strengths
- **Tool registry singleton** — Self-registering `registry.register()` pattern
- **Toolset composition** — Recursive resolution with cycle detection
- **Iteration budget** — Prevents infinite loops
- **Path-scoped parallel execution** — Collision detection for concurrent file ops
- **Subagent delegation** — Child agents with depth limits

### Synthesized Design (Aether)
- Skills = Markdown with YAML frontmatter (knowledge)
- Tools = Executable code (actions)
- ToolRegistry singleton (from Hermes)
- Session key format: `{platform}:{account}:{thread}` (from OpenClaw)
- IterationBudget class (from Hermes)
- Skills loaded from `SKILL.md` files (from OpenClaw)

## Notes

- Each subagent needs `file` + `terminal` toolsets for reading code
- Subagents should read SPEC.md before starting their analysis
- Keep the comparison table in the spec — it becomes the "design rationale"
- Implementation subagent should also read the spec and comparison table
