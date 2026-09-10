---
name: flue
description: Flue — Astro team's TypeScript agent harness framework (MIT, 6.2K stars). Skills/MCP-native, durable execution, sandbox-first. Use when building TypeScript AI agents that need filesystem/shell access, long-running sessions, or Cloudflare/GitHub Actions deployment.
triggers:
  - Flue agent framework
  - Astro team TypeScript agent
  - agent harness TypeScript
  - flue dev
  - TypeScript AI agent runtime
category: agent-engineering
---

# Flue — Astro Team's TypeScript Agent Harness Framework

## What It Is

Flue is a new open-source TypeScript framework from the Astro team (Fred K. Schott) for building autonomous AI agents. It crossed **6,200 GitHub stars** and is trending in June 2026. MIT license, built by a team with a strong track record (Astro, Snowpack, Skypack).

Flue's core insight: **most "agent frameworks" are just LLM SDK wrappers**. Real agents — like Claude Code, Codex, Cursor's agent mode — need a *harness*: a runtime that owns the sandbox, session store, tool dispatcher, and durable execution engine. Flue provides exactly that.

## Key Innovations

- **Agent harness, not SDK**: Flue owns the full runtime lifecycle — sessions, sandboxes, tools, filesystem, crash recovery
- **Skills + MCP native**: Import `SKILL.md` files directly with `with { type: 'skill' }`, connect MCP servers as tools
- **Durable execution**: Recover from crashes mid-task without losing progress
- **Sandbox-first**: Local Node, virtual sandbox, Daytona containers, custom adapters
- **Provider-agnostic**: Anthropic, OpenAI, Google, OpenRouter — model id is a string like `anthropic/claude-sonnet-4-6`
- **Two primitives**: `createAgent()` for continuing context sessions; `createWorkflow()` for single-shot structured runs
- **Five packages**: `@flue/runtime`, `@flue/cli`, `@flue/sdk`, `@flue/opentelemetry`, `@flue/postgres`
- **Deployment targets**: Node, Cloudflare Workers, GitHub Actions, GitLab CI, Daytona
- **Connectors-as-recipes**: `flue add daytona | claude` pipes a markdown adapter recipe into your coding agent

## Agent Harness vs SDK: Why It Matters

Traditional framework:
```
you → call LLM → parse JSON tool_calls → execute → call LLM again → ...
```

Flue harness pattern:
```
agent → Flue runtime (owns sandbox, session, tools) → LLM → execute → Flue runtime → ...
```

The harness handles: sandbox lifecycle, session persistence, crash recovery, tool dispatch, durable execution state. The agent code just describes *what* to do.

## Minimal Agent in 15 Lines

```typescript
// src/agents/triage.ts
import { createAgent, type AgentRouteHandler } from '@flue/runtime';
import { local } from '@flue/runtime/node';
import triage from '../skills/triage/SKILL.md' with { type: 'skill' };
import verify from '../skills/verify/SKILL.md' with { type: 'skill' };
import * as githubTools from '../tools/github.ts';

export const route: AgentRouteHandler = async (_c, next) => next();

export default createAgent({
  runtime: local(),                    // Local Node sandbox
  skills: [triage, verify],            // Import SKILL.md files
  tools: { github: githubTools },       // Custom tools
  instructions: 'You are a GitHub triage agent.',
  route,                               // HTTP route: POST /agents/triage/:id
});
```

## Installation & First Run

```bash
# Scaffold
npm create flue@latest my-agent
cd my-agent

# Set API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run dev server
npx flue dev
# → POST http://localhost:4321/agents/joke-teller/abc123

# Talk to it
curl -X POST http://localhost:4321/agents/joke-teller/abc123 \
  -H "Content-Type: application/json" \
  -d '{"message": "tell me a typescript joke"}'
```

Hot reload is built in — edit code, server restarts automatically.

## Skill Import Pattern

Skills are standard `SKILL.md` files. Flue imports them natively:

```typescript
import mySkill from '../skills/my-skill/SKILL.md' with { type: 'skill' };

export default createAgent({
  skills: [mySkill],
  // ...
});
```

This makes it trivial to share agent behaviors between Flue and Hermes — the same SKILL.md file works in both runtimes.

## Deployment Targets

| Target | Command | Notes |
|--------|---------|-------|
| Local dev | `npx flue dev` | Hot reload, localhost |
| Node.js server | Deploy the built bundle | Standard Node process |
| Cloudflare Workers | `flue deploy --target workers` | Edge deployment |
| GitHub Actions | Use `@flue/runtime` in action | Autonomous CI agent |
| GitLab CI | Same pattern | Pipeline automation |
| Daytona | `flue add daytona` | Managed sandbox |

## Comparison

| | Flue | Mastra | smolagents |
|--|------|--------|------------|
| **Language** | TypeScript | TypeScript | Python |
| **Stars** | 6.2K (new) | ~23K | ~29K |
| **License** | MIT | Apache 2.0 | Apache 2.0 |
| **Skills native** | Yes (SKILL.md) | No | No |
| **MCP native** | Yes | Yes | Yes |
| **Sandbox** | Daytona / custom | E2B / custom | E2B / Modal / Docker |
| **Durable exec** | Yes | Yes (Harness) | Partial |
| **Deployment** | CF Workers, CI/CD | REST API | Python runtime |
| **Model providers** | Any via API | 40+ | LiteLLM 100+ |

## Hermes Integration

Flue complements Hermes well:

- **Skills compatibility**: Flue and Hermes both use `SKILL.md` — share agent behaviors across runtimes
- **TypeScript runtime**: Use Flue for TypeScript-native agent projects where Hermes (Python/JS hybrid) is less natural
- **CI/CD agents**: Flue deploys to GitHub Actions/GitLab CI — natural for automated code tasks
- **Shared skill library**: A SKILL.md written for Hermes can be imported by Flue agents directly

```typescript
// Flue agent using a Hermes-compatible skill
import triage from './skills/triage/SKILL.md' with { type: 'skill' };

// This SKILL.md also works in Hermes — same format, shared
```

## Pitfalls

- Very new (June 2026) — ecosystem still forming
- Stars (6.2K) modest vs established frameworks
- No Python version — only TypeScript
- Daytona sandbox requires separate account/infrastructure
- Limited production battle-testing vs LangGraph/Mastra

## Sources

- Review: https://andrew.ooo/posts/flue-astro-typescript-sandbox-agent-framework-review
- GitHub: https://github.com/withastro/flue
- Astro team blog: https://astro.build/blog/
