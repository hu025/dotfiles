---
name: agent-s
description: Agent S — OSWorld SOTA computer use agent (72.6%, surpasses human baseline)
triggers: [computer use agent, GUI agent, OSWorld benchmark, desktop automation, screen-based agent]
owner: hermes-evolution
updated: 2026-10-20
tags: [agentic-ai, computer-use, benchmark, grounding, multi-model]
---

# Agent S — Computer Use Agent Framework

## Core Identity
- **Type**: Open-source computer use agent framework (Apache 2.0)
- **GitHub**: [simular-ai/Agent-S](https://github.com/simular-ai/Agent-S) — 12.3k stars, 1.4k forks
- **Paper**: [arXiv:2510.02250](https://arxiv.org/abs/2510.02250) (TMLR 2026) — "Scaling Agents for Computer Use"
- **Also see**: [Sai](https://www.sai.work/) — hosted product, 73% on OSWorld 2.0 (Aug 2026)

## Key Achievement
**First agent to surpass human performance on OSWorld benchmark**
- Agent S3 alone: 66% (100-step setting)
- Agent S3 + Behavior Best-of-N (8 rollouts): **72.6%** — surpasses human baseline (~72.36%)
- Production Sai (Aug 2026): **73%** on OSWorld 2.0
- vs GPT-5.6 Sol: 62.57% (OpenAI reported)
- Zero-shot generalization: WindowsAgentArena 56.6%, AndroidWorld 71.6%

## Architecture

### Core Innovation: Behavior Judge (BJudge)
BJudge is the key scaling primitive:
- **Problem**: Single-rollout execution is brittle — small errors compound over long horizons
- **Solution**: Represent agent executions as "behavior narratives", compare candidate behaviors at narrative level
- **Result**: Structured trajectory understanding + selection enables scaling

### Two-Model Setup
1. **Main Agent Model**: Handles reasoning, planning, action selection
   - Recommended: OpenAI `gpt-5-2025-08-07`
2. **Grounding Model**: Translates agent actions to executable code
   - Recommended: UI-TARS-1.5-7B (or UI-TARS-72B for higher quality)
   - Output: screen coordinates, click/keyboard actions

### Action Space
- `click`, `type`, `scroll`, `hotkey`, `drag`
- `call_code_agent`: Execute code for data processing, file ops, system automation, code development, text processing
- No API integration or per-app scripting required

### Multi-Platform Support
- macOS, Windows, Linux
- Works with: OpenAI, Anthropic, Gemini, Open Router, vLLM

## Key Findings for Hermes

### 1. Behavior Best-of-N > Single Rollout
Scaling over multiple rollouts with behavior-level judging is the right way to improve reliability. Single-shot execution is fundamentally brittle for long-horizon tasks. Hermes cron tasks with complex multi-step workflows could benefit from this pattern.

### 2. Grounding Model Separation
Separating visual grounding (UI-TARS) from reasoning (GPT-5) is architecturally sound. Hermes could explore similar separation for browser-based tasks — a small vision model for DOM understanding, a reasoning model for planning.

### 3. Code Agent Integration
`call_code_agent` action pattern: when GUI is insufficient, delegate to code execution. This is exactly the browser-use + coding agent hybrid pattern Hermes could adopt for complex workflows.

### 4. Benchmark Insight
OSWorld 2.0 (108 tasks, professional everyday tasks) is the definitive computer use benchmark. Any Hermes desktop automation skill should be evaluated against OSWorld.

## Hermes Integration Potential
- **Medium priority**: Hermes browser-use skill could adopt BJudge-style multi-rollout evaluation
- **Medium priority**: Grounding model separation pattern for GUI tasks
- **Low priority**: Direct integration (requires real display/GUI environment)
- **Watch**: Sai API (https://www.sai.work/) for hosted computer use

## Installation
```bash
pip install gui-agents
```

CLI usage:
```bash
agent_s \
    --provider openai \
    --model gpt-5-2025-08-07 \
    --ground_provider huggingface \
    --ground_url http://localhost:8080 \
    --ground_model ui-tars-1.5-7b \
    --grounding_width 1920 \
    --grounding_height 1080
```

## Related Skills
- `browser-use`: Browser automation agent
- `computer-use`: OS-level desktop control
- `opencode`: Terminal coding agent
