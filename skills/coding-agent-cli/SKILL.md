---
name: coding-agent-cli
description: "Compare and select mainstream coding-agent CLIs for repo work."
version: 1.0.0
license: MIT
---

# Coding Agent CLI comparison (2026)

Use this guide when choosing a terminal coding agent or delegating repo edits.

## Quick comparison

| Tool | Surface | Model choice | Strength | Trade-off |
|---|---|---|---|---|
| Claude Code | CLI, IDE, cloud | Anthropic; API/subscription | Strong repo reasoning, shell workflows, agents | Proprietary ecosystem/cost |
| Codex CLI | CLI, IDE, cloud | OpenAI models | Sandboxed coding, terminal automation | Provider lock-in; rapidly changing product |
| Aider | Terminal | BYOK, model-agnostic, local | Git-native edits/commits, Architect dual-model mode, Watch mode with AI!/AI? inline comments, tree-sitter 130+ languages, repo-map with graph ranking | Less autonomous orchestration; no native MCP |
| Cline | VS Code/JetBrains, CLI | BYOK, local, any provider | Explicit Plan/Act approvals, MCP | Editor-centric; setup varies by model |
| Continue | IDE, CLI | BYOK/local/open models | Open-source, `.continue/checks/` AI semantic checks on PRs, anti-slop rules, Mission Control CI integration | **ARCHIVED**: Acquired by Cursor (Jul 2026), repo read-only, v2.1.0 final |
| Cursor | AI-native IDE, CLI/cloud | Managed Cursor models/providers | Excellent inline context and background agents | Closed IDE; usage pricing |
| OpenCode | CLI/desktop | Many providers, local | Terminal-first, open source, broad provider support | Fast-moving APIs/community |

## Selection rules

- Choose **Claude Code** for complex multi-file changes, investigation, and high-quality terminal loops.
- Choose **Codex CLI** when OpenAI models, sandboxing, or cloud handoff fit the workflow.
- Choose **Aider** for small, reviewable Git patches and maximum provider flexibility.
- Choose **Cline** when every edit/command needs visible human approval in an IDE.
- Choose **Continue** for team-owned prompts, local models, and extensible IDE workflows.
- Choose **Cursor** when an integrated editor and background execution matter most.
- Choose **OpenCode** when an open, provider-neutral terminal agent is preferred.

## Benchmark guidance

HumanEval measures function synthesis from docstrings; it does not test repository navigation,
terminal use, multi-file edits, or long-running agent behavior. Treat leaderboard numbers as
model evidence, not CLI evidence. For agent selection, prioritize Terminal-Bench, SWE-bench
Verified/Pro, task-specific replay tests, patch quality, cost, latency, and approval controls.

## Safe evaluation protocol

1. Pin identical repositories, prompts, model versions, and timeouts.
2. Run each tool in an isolated worktree with network and secrets restricted.
3. Record pass rate, tests passed, diff size, retries, latency, and spend.
4. Review failures manually; benchmark scores are snapshots and may be stale.
5. Require tests and inspect `git diff` before merging; never grant unrestricted push by default.

## Sources checked

- Artificial Analysis coding-agent comparison (Cursor, Claude Code, Cline, Aider, others).
- IBM, “What Is HumanEval?” (published 2026-02-23).
- BenchLM HumanEval page (September 2026 snapshot; marked stale).
- Aider GitHub releases v0.77–v0.86 (2026 major releases: Architect mode, Watch mode, tree-sitter 130+ languages, Python 3.14, GPT-5/Grok-4/Gemini 3 support). https://github.com/Aider-AI/aider/releases
- MorphLLM 2026 coding-agent comparison (use as secondary, vendor-adjacent source).
