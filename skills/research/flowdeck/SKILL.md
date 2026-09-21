---
name: flowdeck
description: FlowDeck multi-agent orchestration for OpenCode
triggers:
  - OpenCode multi-agent workflow
  - 12 specialist agents orchestration
  - phase-gated development pipeline
  - agent contract governance
tags: [agent-orchestration, multi-agent, governance, workflow]
source: https://github.com/DVNghiem/FlowDeck
stars: 27
license: MIT
updated: 2026-10-21
---

# FlowDeck — Multi-Agent Workflow Orchestration

FlowDeck is an OpenCode plugin that adds structured multi-agent orchestration with built-in governance and safety intelligence.

## Core Architecture

**Layering:** OpenCode (runtime) → FlowDeck Plugin (orchestration + governance + hooks)

**Four subsystems:**
- **Commands** — slash-command entry points (`/fd-task`, `/fd-review`, `/fd-execute`, `/fd-verify`, `/fd-done`, `/fd-checkpoint`, `/fd-resume`, `/fd-status`)
- **Agents** — 12 specialist agents coordinated by orchestrator
- **Services** — governance + intelligence runtime components
- **Hooks** — session-start, session-idle, shell-env, guard-rails

## 12 Specialist Agents

| Agent | Role |
|-------|------|
| `@orchestrator` | Routes work to specialists (primary, visible in UI) |
| `@planner` | Wave-structured implementation plans |
| `@architect` | System design, ADRs, API contracts |
| `@backend-coder` | Backend/API/database features |
| `@frontend-coder` | UI/frontend features |
| `@devops` | Deployment, infra, CI/CD |
| `@tester` | TDD test writing |
| `@reviewer` | Code quality + risk assessment |
| `@debug-specialist` | Root cause analysis + build error resolution |
| `@security-auditor` | OWASP Top 10 + deep security audit |
| `@researcher` | Docs/API research via Context7 + vendor docs |
| `@mapper` | Codebase exploration + affect graph |

All non-orchestrator agents are **subagent** mode (internal only, invoked programmatically).

## Five-Stage Pipeline

```
/fd-task → /fd-review → /fd-execute → /fd-verify → /fd-done
```

Each stage is gated — next stage won't run until current stage passes:

- **/fd-task**: Produces `task.md` + `architecture.md` + `affect.md` + `plan.md`
- **/fd-review**: Gates `/fd-execute` until plan confirmed
- **/fd-execute**: Wave-structured parallel execution, guarded by affect graph
- **/fd-verify**: Regression check
- **/fd-done**: Summary + commit + push

State persists in `~/.fd-plan/<slug>/STATE.md`, survives session restarts.

## Governance Layer (6 Services)

### 1. Agent Contract Registry
Declarative contracts per agent type:
```json
{
  "agent": "coder",
  "allowed-tools": ["read", "edit", "write", "bash", "run-pipeline"],
  "forbidden-tools": ["delete", "remove", "drop"],
  "required-inputs": ["prompt", "files"],
  "success-criteria": ["all edited files pass linter", "no test coverage decrease"]
}
```

### 2. Agent Validator
Three modes: `off` / `advisory` (logs) / `strict` (halts on violation)
- Pre-invocation: contract resolution, required inputs, forbidden tools
- Post-invocation: success-criteria evaluation

### 3. Inter-Agent Trace Graph
Every delegation recorded as causal span in `AGENT_SPANS.jsonl`:
```json
{
  "span_id": "s1a2b3c", "parent_id": "s0a1b2c", "agent": "coder",
  "prompt": "Implement user authentication", "files": ["src/auth/login.ts"],
  "started_at": "...", "finished_at": "...", "violations": [], "result": "success"
}
```
Used by Deadlock Detector + Workflow Scorecard.

### 4. Delegation Budget
Per-agent delegation count limits prevent runaway spawning.

### 5. Deadlock Detector
Identifies circular delegation via trace graph analysis.

### 6. Workflow Scorecard
Scores delegation depth and breadth from span data.

## Intelligence Layer

- **Patch Trust Score** — derived from edit scope, file volatility, agent failure history, rule compliance
- **failure-replay** — reproduce and trace prior failures
- **policy-engine** — evaluate edits against project rules
- **hash-edit** — content-address edits for deduplication

## Install

```bash
# curl (recommended)
curl -fsSL https://raw.githubusercontent.com/DVNghiem/flowdeck/main/install.sh | bash
# npx
npx @dv.nghiem/flowdeck install
```

## Hermes Relevance

**Low immediate value:** FlowDeck is tightly coupled to OpenCode's delegate tool. The key insights that translate:

1. **Phase-gated pipeline** — `/fd-task → review → execute → verify → done` gating pattern is directly applicable to Hermes cron workflows (verify before commit)
2. **Agent Contract Registry** — declarative contracts (allowed/forbidden tools + success-criteria) are a clean governance model for Hermes delegate_task
3. **Inter-Agent Trace Graph** — causal span recording enables post-hoc audit and deadlock detection; could enhance Hermes task tracking
4. **affect.md + file-affection graph** — parallel execution guard prevents file conflicts; Hermes delegate_task parallel workers lack this

**Key differentiator vs existing frameworks:** Phase gating with state files (`~/.fd-plan/<slug>/STATE.md`) that survive session restarts is a simple but effective checkpoint pattern.
