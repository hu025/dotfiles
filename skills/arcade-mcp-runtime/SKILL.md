---
name: arcade-mcp-runtime
description: Arcade — enterprise MCP runtime with auth/tools/governance. 7000+ tools, SOC 2, multi-tenant. Use when building secure production agent toolchains, multi-user agent authorization, or enterprise MCP governance.
triggers:
  - Arcade MCP runtime
  - enterprise MCP governance
  - agent authorization platform
  - MCP tool authorization
  - secure agent tools
  - agent RBAC
category: agent-engineering
---

# Arcade MCP Runtime — Enterprise Agent Infrastructure Layer

## What It Is

Arcade is the **MCP runtime** that sits between AI agents and external business systems — handling auth, tools, and governance in one unified layer. Not a framework — infrastructure. Apache/enterprise license.

**Data**: 7,000+ agent-optimized MCP tools across 80+ toolkits, SOC 2 compliant, from the team that authored the MCP tool authorization specification.

## Core Problem It Solves

Building agents that actually ship to production hits three walls:
1. **Auth** — every integration needs its own OAuth/token management
2. **Reliability** — raw API wrappers hallucinate parameters, fail silently
3. **Governance** — audit logs, RBAC, and compliance stitched together after the fact

Arcade answers: *"what action did this agent take, on behalf of which user, in which system?"* — for every tool call, every time, without slowing production.

## Architecture

```
Agent → Arcade Runtime → External Systems (Salesforce, Google, etc.)
         ↓
    [Auth + Tools + Governance unified]
```

Every agent action flows through the runtime:
- **Permissions**: evaluated at the intersection of what the user can do AND what the agent is allowed to do
- **Credentials**: injected at execution, never exposed to agents or MCP clients
- **Execution**: parallelized, with automatic failover and intelligent retries
- **Logging**: every tool call records agent/user/scope/policy decision → streams to SIEM via OpenTelemetry

## Key Capabilities

### Auth — Agents Act As Users, Not Around Them
- Dynamic permissions via existing IDP (Okta, Auth0, etc.)
- OAuth broker keeps tokens current through refresh/rotation
- Per-action authorization scoped to user + agent permission intersection
- Pre/post tool-call policy hooks

### Tools — Work First Time
- 7,000+ pre-built agent-optimized tools (Salesforce, Google Workspace, Slack, Jira, ServiceNow, Workday, etc.)
- Natural language → precise API calls (no hallucinated parameters)
- Custom tools: open-source Python framework with built-in OAuth, secrets management, and evals
- MCP Gateway: federate multiple MCP servers into single endpoint

### Governance — Central Control Plane
- RBAC and SSO out of the box
- SOC 2 compliant
- Fine-grained audit logs → OpenTelemetry → SIEM
- Version control for tool/MCP server upgrades
- Shared registry: teams discover and reuse tools, not rebuild them

### Deployment Flexibility
- **Arcade Cloud**: fully managed, zero infra
- **BYO Cloud**: AWS/Azure/GCP, data never leaves your environment
- **Self-managed**: on-prem or air-gapped for classified environments

## Enterprise Impact (from their site)

- First agent ships in **weeks** (not months)
- Second agent ships in **days**
- Prompt injection becomes a **logging event**, not a breach

## Hermes Integration Points

1. **Tool Governance**: Arcade's per-action auth model → Hermes MCP tool execution could add similar auth hooks
2. **Audit Logging**: OpenTelemetry streaming audit → Hermes skill execution audit trail
3. **Tool Reliability**: 7000+ pre-built tools → reference for Hermes MCP tool quality bar
4. **MCP Gateway Pattern**: federate multiple MCP servers into one endpoint → Hermes could expose unified MCP endpoint

## Installation & Quickstart

```bash
# Sign up free at app.arcade.dev
# Docs: docs.arcade.dev

# Python SDK
pip install arcade-sdk

# Or use as MCP client in Claude/Cursor/ChatGPT
# Point any MCP client at your Arcade gateway URL
```

## Sources

- https://www.arcade.dev/
- https://docs.arcade.dev/
- https://toolbench.arcade.dev/ (tool evaluation)
- https://platform.tracxn.com/a/d/company/67f539ec822a945a1536cafa/arcade%20ai
