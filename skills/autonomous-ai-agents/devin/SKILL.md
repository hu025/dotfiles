---
name: devin
description: Devin — Cognition's autonomous coding agent. SWE-1.7 (July 2026, Kimi K2.7 base, Cerebras 1000 tok/s), Security Swarm (72% CVE recall, $90.23/run), Fusion multi-model harness (60% cost reduction). Use when delegating whole tickets, security scanning, or studying enterprise agent architecture.
version: 1.0.0
author: Hermes Agent (Nous Research)
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Autonomous, Multi-Model, Security, Vulnerability-Scanning]
    related_skills: [openhands, claude-code, blackbox, codex, swe-agent]
---

# Devin — Cognition Autonomous Coding Agent

## What It Is

Devin (Cognition Labs) is a **cloud-hosted autonomous software engineer** — describe a task in natural language, walk away, return to a PR. Founded 2024, $26B valuation (May 2026 Series D), acquired Windsurf July 2025.

**Pricing (July 2026):**
- Core: $20/mo + $0.60/ACU (ACU = Agent Compute Unit, ~1 task-minute)
- Devin Fusion (multi-model): included in Core plan
- Devin Security Swarm: enterprise, $90.23/scan-run

## Core Products (July 2026)

### SWE-1.7 — Custom Coding Model
- Released July 8, 2026
- Base: Kimi K2.7 (Moonshot), fine-tuned with RL on coding tasks
- Inference: Cerebras — **~1,000 tokens/sec**, 10x faster than typical API
- Entropy-preserving top-p sampling for training stability
- Multi-cluster training (3 continents) with fault tolerance
- Benchmark: FrontierCode 1.1 Main 42.3%, Terminal-Bench 2.1 81.5%, SWE-Bench Multilingual 77.8%
- Free on Core plan, replaces SWE-1.6

### Devin Fusion — Multi-Model Harness (June 29, 2026)
**Two core techniques:**

#### 1. Sidekick Architecture
- Run **two parallel agents**: frontier main agent + cheap sidekick agent
- Both keep own persistent cached context — avoids cache misses on delegation
- Main agent: plan, resolve ambiguity, final review — **"delegate and monitor"**
- Sidekick: explore codebase, write code, fix lint, write tests
- Key insight: main agent reads minimally, acts rarely, delegates most work
- **60% cost reduction** vs pure frontier (Opus 4.8/GPT-5.5) on FrontierCode
- With Fable 5: **41% cost reduction** (Fable access suspended June 12 2026)
- 88% of Cognition's own merged PRs driven entirely by Fusion router

#### 2. Dynamic Mid-Session Routing
- Lightweight classifiers during execution detect when to switch models
- Model switches happen during **context compaction** — cache miss already triggers, so switch is "free"
- Can escalate sidekick → main agent, or switch sidekick model entirely
- Enables sidekick model upgrades without reverting to main

**Key LLMOps insight:** Avoid "Smart Friend" / "Advisor" pattern — calling a separate model re-sends full context at full price. Sidekick dual-context design eliminates this.

### Devin Security Swarm — Autonomous Security Scanner
- Released July 1, 2026
- **Agentic MapReduce architecture**: planner agent writes selectors (routes, auth boundaries, deserialization sinks), parallel agents investigate codebase segments
- Runtime validation in isolated sandbox confirms exploitability before reporting
- Outputs confirmed vulnerabilities with attack paths + PRs for fixes

**Performance on 50 real CVE/GHSA benchmarks (14 languages):**

| Harness | Recall | $/Run |
|---|---|---|
| Devin Security Swarm | **72%** | $90.23 |
| Claude Security | 68% | $131.87 |
| Codex Security | 48% | $118.20 |
| Cursor Security | 26% | $4.60 |

- Found 3 critical vulnerabilities **missed by every other tool**: PHP sandbox bypass (template injection), argument injection (metadata), Spring Kafka deserialization
- Differential: no false positives, not just coverage

**Additional features:**
- Scan profiles from threat model docs, attacker personas, configurable batch size
- Daily/weekly/custom scheduling, incremental scan (only changed code)
- Devin Vulnerability Remediation Program: 6-week enterprise engagement

## Windsurf 2.0 Integration
- July 2025: Cognition acquired Windsurf IP + team
- Windsurf 2.0: plan locally → one click → Devin cloud VM takes over
- Cascade agent inside Windsurf: 30% more token-efficient than before, model picker includes Claude Opus 4.7, GPT-5.5, SWE-1.6
- Most distinctive workflow: local IDE → autonomous cloud handoff

## Key Insights for Hermes Architecture

1. **Sidekick > Smart Friend**: The persistent dual-context pattern (sidekick) dramatically outperforms single-model "ask for advice" routing because it avoids context re-sending costs
2. **Cache-aligned model switching**: Integrate model switches with context compaction events — same cache miss, new opportunity
3. **Agentic MapReduce for security**: Planner writes deterministic selectors, parallel agents investigate, results merged and validated at runtime — more effective than static scanning
4. **Confirmed > Found**: Security value = validated exploitability × fix-ready output, not coverage numbers
5. **FrontierCode benchmark**: Measures both correctness + quality, not just pass rate

## Links

- [Devin Fusion Blog](https://cognition.com/blog/devin-fusion)
- [Devin Security Swarm](https://cognition.com/blog/introducing-devin-security-swarm)
- [Security Swarm Eval](https://devin.ai/blog/security-swarm-eval)
- [SWE-1.7 Announcement](https://cognition.com/blog/swe-1-7)
- [FrontierCode Leaderboard](https://cognition.com/frontiercode)
