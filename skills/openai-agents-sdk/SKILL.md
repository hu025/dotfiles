---
name: openai-agents-sdk
description: OpenAI Agents SDK — Python lightweight multi-agent framework with Sandbox isolation, VoicePipeline, Guardrails, Handoffs. 29.3K stars MIT. Use when building multi-agent workflows with安全沙箱 or voice pipelines.
triggers:
  - OpenAI Agents SDK
  - openai-agents-python
  - sandbox agents
  - voice pipeline agent
  - agent guardrails
  - handoffs multi-agent
category: agent-engineering
---

# OpenAI Agents SDK

## What It Does

OpenAI Agents SDK (openai-agents-python) is a lightweight, powerful framework for building multi-agent workflows in Python. Provider-agnostic, supporting 100+ LLMs beyond OpenAI. v0.22.0 (Aug 2026).

## Core Capabilities

- **Provider Agnostic**: OpenAI Responses API + Chat Completions + 100+ other LLMs
- **Sandbox Agents**: Persistent workspace isolation with snapshotting/rehydration, multi-provider (E2B, Modal, Cloudflare, Daytona, Blaxel, Vercel, Runloop)
- **VoicePipeline**: ASR + Agent + TTS pipeline in one
- **Realtime Agents**: WebSocket voice/multimodal via `gpt-realtime-2.1`
- **Guardrails**: Parallel input/output validation, fail-fast on check failure
- **Handoffs**: Decentralized peer-agent delegation (vs manager pattern)
- **Agents as Tools**: Manager-style orchestration (orchestrator calls sub-agents as tools)
- **Tracing**: Built-in tracking, debug, evaluate agent flows
- **Context**: Dependency-injection object passed through Agent.run()
- **@tool Decorator**: Turn any Python function into a tool with auto schema + Pydantic validation
- **Skills System**: SKILL.md-style Markdown封装，LocalDirLazySkillSource懒加载

## Installation

```bash
pip install "openai-agents[docker]"  # Docker-backed sandboxes
pip install openai-agents
```

## Key Concepts

### Agent vs SandboxAgent

```python
# Plain Agent — lightweight orchestration
agent = Agent(name="Assistant", instructions="...", model="gpt-5-nano")

# SandboxAgent — isolated workspace with filesystem, shell, skills
sandbox = SandboxAgent(
    name="Sandbox engineer",
    model="gpt-5-sol",
    instructions="Read repo/task.md before editing...",
    default_manifest=Manifest(entries={"repo": LocalDir(src="./repo")}),
    capabilities=Capabilities.default() + [Skills(lazy_from=LocalDirLazySkillSource(source=LocalDir(src="./skills")))],
)
```

### Multi-Agent Patterns

**Manager (Agents as Tools):**
```python
agent = Agent(
    name="Orchestrator",
    instructions="Delegate to specialists as tools",
    handoffs=[]  # no handoffs needed
)
# Sub-agents exposed as tools
```

**Handoffs (Decentralized):**
```python
specialist = Agent(name="Researcher", instructions="...", handoffs=[])
main = Agent(name="Main", instructions="...", handoffs=[specialist])
# Control transfers to specialist agent
```

### Guardrails

```python
from agents.guardrails import Guardrail, GuardrailResult

def toxicity_check(input: str) -> GuardrailResult:
    if "bad" in input.lower():
        return GuardrailResult(flagged=True, failure_message="Content flagged")
    return GuardrailResult(flagged=False)

agent = Agent(
    name="Safe Assistant",
    input_guardrails=[toxicity_check],
)
```

### VoicePipeline

```python
from agents import VoicePipeline

pipeline = VoicePipeline(
    agent=my_agent,
    # ASR + Agent + TTS combined
)
```

## Unique Innovations vs Hermes

| Feature | OpenAI Agents SDK | Hermes |
|---------|-------------------|--------|
| Sandbox isolation | Native (multi-provider) | External (E2B) |
| Snapshotting/rehydration | Built-in | Via E2B |
| Voice pipeline | Native VoicePipeline | Via TTS tools |
| Skills system | Markdown封装的lazy skills | SKILL.md native |
| Handoffs | Native decentralized | Via context/sessions |
| Guardrails | Parallel input/output validation | Manual check |

## When to Use

- Need **secure sandbox code execution** with snapshot/resume → OpenAI Agents SDK
- Building **voice agents** → VoicePipeline
- **Provider-agnostic** agent runs with 100+ LLMs → OpenAI Agents SDK
- Complex **multi-agent coordination** with handoffs → Both viable

## Links

- GitHub: https://github.com/openai/openai-agents-python
- Docs: https://openai.github.io/openai-agents-python/
- Python 3.10+ required
