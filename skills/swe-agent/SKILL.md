---
name: swe-agent
description: SWE-agent — autonomous AI software engineering agent that reads GitHub issues and submits PRs. 74%+ SWE-bench Verified. Use when you need code-fixing, PR automation, or autonomous code review capabilities.
triggers:
  - SWE-agent
  - autonomous code fixing
  - GitHub issue to PR
  - software engineering agent
  - SWE-bench
  - mini-swe-agent
category: coding-agent-cli
---

# SWE-agent — Autonomous Software Engineering Agent

## What It Does

SWE-agent takes a GitHub issue and autonomously tries to fix it — end to end, from reading the issue to opening a pull request. It's built on research from the SWE-bench benchmark (real GitHub issues from popular Python repos) and achieves 74%+ on SWE-bench Verified.

## Core Capabilities

- **GitHub Issue → PR Pipeline**: Autonomous end-to-end fix workflow — read, plan, code, test, PR
- **Configurable via YAML**: Single `swe_agent.yaml` file controls behavior — no code changes needed
- **Model-Agnostic**: Works with Claude, GPT-4, open-weight models, or any API-compatible LLM
- **Sandboxed Execution**: Code runs in controlled environments — safe for autonomous operation
- **mini-swe-agent**: Ultra-minimal version — ~100 lines of code, still scores >74% on SWE-bench Verified
- **Massively Parallel**: Run multiple issue-fixing agents simultaneously
- **Docker-Based**: Full isolation via Docker containers

## Installation

```bash
# Full SWE-agent (Python + Docker)
pip install sweagent
swe-agent

# mini-swe-agent (simpler, faster, just as capable)
pip install mini-swe-agent
mini  # run the CLI

# Or with uv
uvx mini-swe-agent

# From source
git clone https://github.com/SWE-agent/mini-swe-agent.git
cd mini-swe-agent && pip install -e .
mini
```

## Usage

```bash
# Interactive mode
swe-agent

# Single task
swe-agent -t "Fix the authentication bug in src/auth.py"

# From file
swe-agent -f requirements.txt

# Auto-approve all actions (CI mode)
swe-agent --always-approve

# Resume previous session
swe-agent --resume
swe-agent --resume abc123  # specific session ID
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

## Hermes Integration

SWE-agent's approach directly enhances Hermes in several ways:

```python
# Hermes could delegate code-fixing tasks to SWE-agent:
# 1. User reports a bug → Hermes classifies it
# 2. If it's a code bug → Hermes spawns SWE-agent to fix
# 3. SWE-agent opens PR → Hermes reviews and merges

# Architecture: Hermes as orchestrator, SWE-agent as specialist
# Similar to how LangGraph uses sub-agents for specific tasks
```

## Key Insight for Hermes: SWE-bench Patterns

SWE-agent's success comes from:
- **Free-form agency**: Maximally gives the LM freedom to act
- **Minimal constraints**: Doesn't force tool-calling schemas
- **Good tooling**: Bash, file read/write, grep, search — the right tools, not too many
- **Test-driven**: Runs tests to validate fixes automatically

## Comparison with OpenHands

| Feature | SWE-agent | OpenHands |
|---------|-----------|-----------|
| SWE-bench Verified | 74%+ | 72% |
| License | Apache 2.0 | MIT |
| Architecture | Simple, YAML-driven | Full platform (SDK+CLI+GUI) |
| Mini version | 100 lines | No |
| Docker required | Yes | Yes |
| GUI | No | Yes (React) |

## When to Use

- **Automated bug fixing**: Feed GitHub issues → get PRs back
- **CI/CD integration**: Run on every new issue/PR
- **Codebase maintenance**: Bulk-fix issues across repositories
- **Research**: SWE-bench evaluation framework

## Pitfalls

- Docker dependency required for full version
- Best suited for Python codebases (SWE-bench is Python-focused)
- Mini-swe-agent is the recommended starting point — simpler, equally capable
