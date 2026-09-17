---
name: openai-agents-sdk
description: OpenAI Agents SDK — lightweight Python multi-agent framework with Sandbox isolation, VoicePipeline, Guardrails, Handoffs + OpenAI Presence enterprise governance layer. Use when building安全沙箱code execution, voice pipelines, or enterprise agent deployments with guardrails/Codex改进环.
triggers:
  - OpenAI Agents SDK
  - openai-agents-python
  - sandbox agents
  - voice pipeline agent
  - agent guardrails
  - handoffs multi-agent
  - OpenAI Presence
  - enterprise agent governance
  - Codex improvement loop
category: agent-engineering
---

# OpenAI Agents SDK

## What It Does

OpenAI Agents SDK (openai-agents-python) is a lightweight, powerful framework for building multi-agent workflows in Python. Provider-agnostic, supporting 100+ LLMs beyond OpenAI. v0.22.0+ (Aug-Sep 2026). OpenAI Presence (Jul 22, 2026) is the enterprise governance layer on top.

## Core Capabilities

- **Provider Agnostic**: OpenAI Responses API + Chat Completions + 100+ other LLMs
- **Sandbox Agents** (Apr 2026 major update): Persistent workspace isolation, snapshot/rehydration, resumable sandbox sessions, multi-provider (E2B, Modal, Cloudflare, Daytona, Blaxel, Vercel, Runloop)
- **VoicePipeline**: ASR + Agent + TTS pipeline in one
- **Realtime Agents**: WebSocket voice/multimodal via `gpt-realtime-2.1`
- **Guardrails**: Parallel input/output validation, fail-fast on check failure
- **Handoffs**: Decentralized peer-agent delegation (vs manager pattern)
- **Agents as Tools**: Manager-style orchestration (orchestrator calls sub-agents as tools)
- **Tracing**: Built-in tracking, debug, evaluate agent flows
- **Context**: Dependency-injection object passed through Agent.run()
- **@tool Decorator**: Turn any Python function into a tool with auto schema + Pydantic validation
- **Skills System**: SKILL.md-style Markdown封装，LocalDirLazySkillSource懒加载
- **OpenAI Presence** (enterprise): SOPs + Guardrails + Approved Actions + Simulations + Evals + Codex改进环

## OpenAI Presence (Jul 22, 2026)

Enterprise production governance platform, not self-serve (limited GA via Forward Deployed Engineers):
- **6组件**: SOPs + Guardrails + Approved Actions + Simulations + Evaluation tooling + Codex-powered improvement loop
- **实测**: OpenAI自家英文电话支持(1-888-GPT-0090)75%无需人工，10天人类交接率降15pp
- **Codex改进环**: 监控生产质量，Codex审查transcript建议更新，团队测试后控量发布
- **EU AI Act**: 上线时间(Jul 22)恰在2026-08-02欧盟高风险AI条款可执行之后，非合规产品为已可执行高风险条款场景
- **不适用场景**: 小规模/自托管/Hermes subagent架构（进程内协作不匹配A2A client-server模型）

## Production Patterns (TURION Deep Dive)

- **Direct instructions > persona theater**: 过度角色扮演反而降低LLM效果，领域特定指令更有效
- **Guardrails = parallel safety nets**: 与主流程并行执行，不阻塞主流程
- **Handoff vs Manager decision tree**: 需要严格控制时用manager，agent专业性明确时用handoff
- **Sandbox Agent**: Apr 2026更新后从"wrapper"变成"完整执行harness"

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
