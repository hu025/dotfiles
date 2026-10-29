---
name: microsoft-agent-framework
description: Microsoft Agent Framework (MAF) — Semantic Kernel + AutoGen successor, 13.5k stars, Python/.NET/Go
triggers: [Microsoft Agent Framework, MAF, Semantic Kernel successor, AutoGen successor, multi-language agent]
owner: hermes-evolution
updated: 2026-10-20
tags: [agentic-ai, framework, multi-language, production, orchestration]
---

# Microsoft Agent Framework (MAF)

## Core Identity
- **Type**: Production-grade multi-agent framework (open-source)
- **GitHub**: [microsoft/agent-framework](https://github.com/microsoft/agent-framework) — 13.5k stars, 2.3k forks, 2,290 commits
- **Docs**: [learn.microsoft.com/agent-framework](https://learn.microsoft.com/en-us/agent-framework/)
- **Unifies**: Semantic Kernel + AutoGen (next generation of both)

## Key Features

### Multi-Language Support
- **Python**: `pip install agent-framework`
- **.NET**: `dotnet add package Microsoft.Agents.AI`
- **Go**: [microsoft/agent-framework-go](https://github.com/microsoft/agent-framework-go)

### Orchestration Patterns
- Sequential, concurrent, handoff, group collaboration
- Graph-based workflows with checkpointing, streaming, human-in-the-loop, time-travel

### Middleware System
- Request/response processing
- Exception handling
- Custom pipelines (Python + .NET)

### Provider Support
- Azure Foundry, Azure OpenAI, OpenAI, GitHub Copilot SDK
- Extensible provider model (more being added)

### Foundry Hosted Agents (New)
- Deploy to Foundry-hosted infrastructure with 2 additional lines of code

### Declarative Agents
- YAML-based agent definitions for faster setup and versioning

### Agent Skills
- Domain-specific knowledge bases from files, inline code, class libraries
- For agent discovery and use

### Observability
- Built-in OpenTelemetry integration (distributed tracing, monitoring, debugging)

## Architecture (vs Previous Frameworks)
```
AutoGen (research) + Semantic Kernel (enterprise)
         ↓
   Microsoft Agent Framework (unified)
         ↓
  Python / .NET / Go + Graph Workflows + Checkpointing + OTel
```

## Key Insight: MAF = Semantic Kernel + AutoGen Convergence
Both Semantic Kernel and AutoGen pioneered different aspects:
- **Semantic Kernel**: Enterprise robustness, thread-based state, telemetry, type safety
- **AutoGen**: Research simplicity, multi-agent orchestration
- **MAF**: Next generation unifying both — production-ready with graph-based workflows

## Migration Path
- Semantic Kernel users → MAF (backward compatible guides available)
- AutoGen users → MAF (migration guides available)
- AutoGen 0.4 now in maintenance mode → MAF is the successor

## Hermes Integration Potential
- **Medium priority**: MAF's graph-based workflow + checkpointing pattern is reference for Hermes orchestrator
- **Medium priority**: Middleware system (request/response interception) could inspire Hermes skill hooks
- **Low priority**: Direct Python/.NET integration (not Hermes ecosystem)
- **Watch**: Agent Framework's Go SDK for future multi-language Hermes plugins

## Important Notes
- Public preview (as of Oct 2025)
- Third-party systems used at own risk
- Azure-focused but not Azure-exclusive

## Related Skills
- `autogen-maintenance`: AutoGen (now in maintenance, MAF is successor)
- `semantic-kernel`: SK (predecessor to MAF)
- `langgraph-production`: Graph-based orchestration comparison
