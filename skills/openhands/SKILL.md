---
name: openhands
description: OpenHands 1.0 — top open-source autonomous coding agent (68% SWE-bench Verified, 87K stars MIT). Docker security sandbox + Agent Canvas control center. Use when you need self-hosted autonomous PR generation, CI/CD GitHub automation, or the best open-source coding agent.
triggers:
  - OpenHands
  - All-Hands-AI
  - CodeAct
  - autonomous PR generation
  - Agent Canvas
  - open source coding agent
  - self-hosted AI developer
category: coding-agent-cli
---

# OpenHands — Open-Source Autonomous Coding Agent

## What It Is

OpenHands (formerly OpenDevin) by All-Hands-AI is the **top-performing open-source autonomous coding agent** as of 2026. MIT-licensed, **87K+ GitHub stars**. Achieves **68% on SWE-bench Verified** with CodeAct v3 + Qwen3-Coder-480B (~$0.30/task) or 72% with Claude Sonnet 4.5 + extended thinking.

Two key components in 2026:
- **CodeAct agent**: The core agent — generates executable Python as actions (not JSON tool calls), runs in sandbox, observes output, iterates
- **Agent Canvas**: Self-hosted browser-based control center with chat panel, file browser, live terminal, per-project token cost tracking

## Core Capabilities

- **GitHub Issue → PR**: Hand it a GitHub issue, it returns a PR — fully autonomously
- **CodeAct Action Format**: Agent writes Python code to modify files, run commands — more expressive than JSON tool schemas, better on complex multi-step tasks
- **Multi-Agent Coordination**: `AgentDelegateAction` lets a main agent spawn specialized sub-agents
- **Browser-Based Canvas UI**: Self-hosted web UI replacing legacy CLI/Local GUI
- **Sandboxed Execution**: Docker isolation — agent can run arbitrary code safely
- **1.0 Security Sandbox (Sep 2026)**: Production-grade Docker sandbox with configurable resource limits (CPU/memory caps per container), non-root execution via `SANDBOX_USER_ID=1000`, and LLM-based security analyzer rating every action LOW/MEDIUM/HIGH. High-risk actions (destructive commands, credential access) pause for human approval before execution. This is the piece that makes self-hosted production deployment viable.
- **15 Benchmarks in One Harness**: SWE-Bench Lite, HumanEvalFix, WebArena, GPQA, GAIA, and more
- **Bring-Your-Own-Model**: Works with any API-compatible LLM (Claude, GPT, Gemini, open-weight)
- **Cross-Platform**: Local, Docker, VM, or cloud backend via Canvas
- **Automation Ready**: Canvas can wire up automations (e.g., "when GitHub issue filed → decompose tasks → open PR")
- **SDK**: Composable Agent SDK for building custom workflows
- **All-Hands-AI raised $23.8M** (Series A led by Madrona, Nov 2025)

## SWE-bench Verified Performance

| Configuration | Model | Verified | Full |
|--------------|-------|---------|------|
| OpenHands + CodeAct v3 | Claude Sonnet 4.5 + ext thinking | **72%** | — |
| OpenHands + CodeAct v3 | Qwen3-Coder-480B | **68%** | — |
| OpenHands + CodeAct v3 | Claude Opus 4.6 | 68.4% | 51.2% |
| OpenHands + CodeAct v2 | GPT-5.2 | 44.7% | 33.9% |
| Augment Code SWE-Agent | Claude Opus 4.6 | 72.0% | 54.1% |
| Cursor Background Agent | Claude Sonnet 4.6 | 65.7% | 48.9% |

> **Key insight**: OpenHands + CodeAct v3 with Claude Opus 4.6 (68.4%) outperforms SWE-agent v1 (43.2%) by 25+ points on the same model family — the CodeAct scaffold is the differentiator.

## Installation & Setup

### Docker (Recommended)

```bash
# Pull runtime sandbox image
docker pull docker.all-hands.dev/all-hands-ai/runtime:latest

# Run Agent Canvas (UI on http://localhost:3000)
docker run -it --rm --pull=always \
  -e SANDBOX_RUNTIME=docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/runtime:latest

# With GPU support (for local models)
docker run -it --rm --pull=always --gpus all \
  -e SANDBOX_RUNTIME=docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/runtime:latest

# Mount current directory
docker run -it --rm --pull=always \
  -e SANDBOX_RUNTIME=docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$(pwd):/workspace" \
  -p 3000:3000 \
  docker.all-hands.dev/all-hands-ai/runtime:latest \
  --mount-cwd
```

### CLI (Headless) via uv

```bash
# Requires Python 3.12+ and uv installed
uv tool install openhands --python 3.12
# Or upgrade
uv tool upgrade openhands --python 3.12
# Run headless (no GUI)
openhands-cli --task "Fix the authentication bug in src/auth.py"
```

### 1.0 Docker Setup (Sep 2026 — with security sandbox)

```bash
# Production-grade sandbox with security analyzer
docker run -it --rm \
  --pull=always \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.26.0-python \
  -e SANDBOX_USER_ID=$(id -u) \
  -e SANDBOX_VOLUMES=$HOME \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/root/.openhands \
  --add-host host.docker.internal:host-gateway \
  --name openhands-cli-$(date +%Y%m%d%H%M%S) \
  python:3.12-slim \
  bash -c "pip install uv && uv tool install openhands --python 3.12 && openhands"
```

Key: `SANDBOX_USER_ID=$(id -u)` ensures non-root execution (sandbox user matches host user permissions). `SANDBOX_VOLUMES` restricts which directories the sandbox can access.

### Agent Canvas (Web UI)

```bash
# Install and launch Canvas UI
uv tool install openhands --python 3.12
openhands serve          # GUI on http://localhost:3000
openhands serve --gpu    # With GPU support
openhands serve --mount-cwd  # Mount current directory
```

### Python SDK

```bash
pip install openhands-ai
```

```python
from openhands.agent import CodeActAgent
from openhands.llms import get_llm

llm = get_llm('anthropic/claude-sonnet-4-20250514')
agent = CodeActAgent(llm=llm)

result = agent.run(
    task='Fix the authentication bug in src/auth.py',
    workspace='/path/to/repo'
)
```

## CodeAct: Why Python Actions Beat JSON Tool Calls

CodeAct's core insight: generating **executable Python code** as agent actions outperforms structured JSON tool schemas on complex multi-step tasks.

```python
# Instead of JSON tool calls like:
# {"tool": "read", "path": "src/auth.py"}
# CodeAct generates:
import ast
with open('src/auth.py', 'r') as f:
    content = f.read()
tree = ast.parse(content)
# ... analyze and modify the AST ...
exec(modified_code)
```

This allows:
- Dynamic tool construction
- Composable operations
- Direct AST manipulation
- Full Python expressiveness

## Agent Canvas Automations

Canvas supports trigger-based automations:

```yaml
# Example: Auto-fix GitHub issues
triggers:
  - type: github.issue.opened
    repo: owner/repo
actions:
  - agent: CodeActAgent
    task: |
      1. Read the issue description
      2. Analyze the codebase
      3. Write a fix
      4. Open a PR
```

## Comparison: OpenHands vs SWE-agent vs Aider

| | OpenHands | SWE-agent | Aider |
|--|-----------|-----------|-------|
| **Verified score** | 68.4% | 43.2% | ~63% |
| **License** | MIT | Apache 2.0 | Apache 2.0 |
| **Interface** | Web UI + CLI + REST | CLI | Terminal |
| **Action format** | CodeAct (Python) | JSON tools | Diff/patch |
| **GUI** | Yes (Canvas) | No | No |
| **Multi-agent** | Yes (DelegateAction) | No | No |
| **Docker required** | Yes | Yes | No |
| **GitHub stars** | 76K+ | 14K | 39K |

## Hermes Integration

OpenHands fits into Hermes as:

```python
# Pattern 1: Sub-agent for autonomous code fixing
# Hermes identifies a bug → spawns OpenHands CodeActAgent
# OpenHands opens PR → Hermes reviews and merges

# Pattern 2: Agent Canvas as unified control plane
# Canvas can orchestrate OpenHands, Claude Code, Codex
# from one self-hosted dashboard

# Pattern 3: CI/CD automation
# GitHub issue filed → Canvas trigger → OpenHands fixes → PR
```

## Real-World Production Metrics (vs SWE-bench)

| Metric | OpenHands + Sonnet 4.6 | Claude Code | Devin |
|--------|------------------------|-------------|-------|
| PR acceptance rate | ~45% | ~48% | ~38% |
| Median time-to-PR | ~18 min | ~14 min | ~22 min |
| Test pass rate before review | ~69% | ~71% | ~63% |

> MSR 2026 (7,156 real PRs across 5 agents): ~46% of AI-proposed fixes are rejected. SWE-bench Verified scores are ~20-25pp above real-world PR acceptance rates due to implicit codebase conventions benchmarks don't capture.
>
> **Devin Fusion (June 2026):** 88% of Cognition's own merged PRs driven entirely by automated Fusion router. 60% cost reduction vs pure frontier on FrontierCode benchmark.

## Pitfalls

- **Docker is mandatory** — no way around it
- GPU recommended for local model usage
- Agent Canvas requires port 3000 available
- More heavyweight than SWE-agent (full platform vs single agent)
- Best suited for autonomous workflows, not lightweight in-editor edits

## Sources

- GitHub: https://github.com/All-Hands-AI/OpenHands
- Paper (ICLR 2025): https://arxiv.org/abs/2407.16741
- CodeAct paper: https://arxiv.org/abs/2407.16741
- Agent Canvas docs: https://docs.all-hands.ai
- Series A: Madrona led $18.8M (Nov 2025)
