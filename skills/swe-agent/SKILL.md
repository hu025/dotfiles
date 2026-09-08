---
name: swe-agent
description: SWE-agent — open-source autonomous coding agent. Scores ~43% SWE-bench Verified (Sonnet 4.5). Use for GitHub issue → PR automation, benchmark evaluation, or as Hermes sub-agent.
triggers:
  - SWE-agent
  - autonomous code fixing
  - GitHub issue to PR
  - SWE-bench evaluation
  - ACI scaffold
  - mini-swe-agent
category: coding-agent-cli
---

# SWE-agent — Autonomous Software Engineering Agent

## What It Is

SWE-agent is Princeton NLP's open-source agent for resolving real GitHub issues autonomously. Built on the ACI (Agent-Computer Interface) scaffold — minimal constraints, free-form tool use. Achieves **43.2% on SWE-bench Verified** with Claude Sonnet 4.5, **29.7% with GPT-5.2**.

The original "mini" reference (100 lines, >74%) refers to a stripped-down variant — current mainstream SWE-agent scores are well-documented on the official leaderboard.

## Core Capabilities

- **GitHub Issue → PR**: Autonomous end-to-end fix workflow — read, plan, code, test, PR
- **Model-Agnostic**: Claude, GPT, Gemini, open-weight models via API
- **Sandboxed Execution**: Docker container isolation for safe autonomous operation
- **SWE-bench Harness**: Full evaluation framework for 2,294 Python repos
- **YAML-Configured**: Behavior controlled via `swe_agent.yaml`, no code changes needed
- **mini-swe-agent**: Lightweight variant via `uvx mini-swe-agent`

## Installation

```bash
# Full version
pip install sweagent
swe-agent

# mini variant (recommended starting point)
uvx mini-swe-agent
# or
pip install mini-swe-agent && mini

# From source
git clone https://github.com/SWE-agent/SWE-agent.git
cd SWE-agent && pip install -e .
swe-agent
```

## Usage

```bash
# Interactive
swe-agent

# Single task from issue description
swe-agent -t "Fix the authentication bug in src/auth.py"

# Auto-approve (CI mode)
swe-agent --always-approve

# Resume session
swe-agent --resume
swe-agent --resume <session_id>
```

## Configuration (swe_agent.yaml)

```yaml
model: anthropic/claude-sonnet-4-20250514
max_iterations: 30
tools:
  - bash
  - read
  - write
  - search
  - grep
  - linter
sandbox:
  runtime: docker
  image: ghcr.io/swe-agent/swe-agent:latest
```

## SWE-bench Verified Leaderboard (2026)

| Agent | Model | Verified | Full | License |
|-------|-------|---------|------|---------|
| Augment Code SWE-Agent | Claude Opus 4.6 | 72.0% | 54.1% | Proprietary |
| OpenHands + CodeAct v3 | Claude Opus 4.6 | 68.4% | 51.2% | MIT |
| Cursor Background Agent | Claude Sonnet 4.6 | 65.7% | 48.9% | SaaS |
| SWE-agent v1 | Claude Sonnet 4.5 | **43.2%** | 31.1% | Apache 2.0 |
| SWE-agent v1 | GPT-5.2 | 29.7% | 22.5% | Apache 2.0 |

> **Key insight**: Scaffold matters enormously. Same model (Claude Sonnet 4.5) scores 43.2% in SWE-agent vs 65.7% in Cursor Background Agent vs 68.4% in OpenHands+CodeAct. The agent scaffold drives 20+ point swings.

## Hermes Integration Pattern

```python
# Hermes delegates code-fixing to SWE-agent as specialist sub-agent:
# 1. User reports bug → Hermes classifies the issue
# 2. If code bug → spawn SWE-agent to fix autonomously
# 3. SWE-agent opens PR → Hermes reviews and merges
# Architecture: Hermes as orchestrator, SWE-agent as specialist
```

## Comparison: SWE-agent vs OpenHands vs Aider

| | SWE-agent | OpenHands | Aider |
|--|-----------|-----------|-------|
| **Verified score** | 43.2% | 68.4% | ~63% |
| **License** | Apache 2.0 | MIT | Apache 2.0 |
| **Interface** | CLI | Web UI + CLI + REST | Terminal |
| **Architecture** | YAML-driven | Full platform (SDK+Canvas) | Diff/patch pipeline |
| **Docker required** | Yes | Yes | No |
| **GUI** | No | Yes (Agent Canvas) | No |
| **Best for** | SWE-bench eval, CI | Autonomous PR from issues | Pair-programming |

## Pitfalls

- Docker required for full version
- Python-centric (SWE-bench is Python-only)
- Lower score than OpenHands+CodeAct on same model budget
- Mini-swe-agent variant is the recommended starting point

## Sources

- Official leaderboard: https://www.swebench.com/verified.html
- GitHub: https://github.com/SWE-agent/SWE-agent
- Paper: https://arxiv.org/abs/2405.15793
