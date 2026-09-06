---
name: agent-self-modification
description: AI agents that rewrite their own code/prompts/weights to improve themselves. Use when researching meta-learning, recursive self-improvement, or building self-evolving agents.
---

# Agent Self-Modification — 2026 SOTA

## Core Problem (the "infinite regress")
Self-improving AI has two layers: **task agent** (solves the problem) and **meta agent** (improves the task agent). Who improves the meta agent? Adding a meta-meta layer just shifts the problem up. You need a **self-referential** system — the meta mechanism is itself editable.

## SOTA Methods (chronological)

### 1. Gödel Machine (Schmidhuber, 2003 — theoretical)
Self-modifies only when it can *prove* the change improves performance. Safe but impractical — proving utility is harder than coding.

### 2. Darwin Gödel Machine / DGM (Zhang et al., 2025)
- Open-ended evolution: maintain an **archive** of agent variants.
- Each step: select a parent → generate child via LLM code-diff → evaluate on coding task → add to archive if better.
- **Results:** SWE-bench 20.0% → 50.0%; Polyglot 14.2% → 30.7%.
- **Limit:** meta mechanism (how children are generated) is **handcrafted and frozen** — only works for coding where "better coder ≡ better self-improver."

### 3. HyperAgents / DGM-H (Meta FAIR + UBC, arXiv 2603.19461, Mar 2026) — CURRENT SOTA
- Unifies task agent + meta agent into **one editable codebase**.
- Meta mechanism is itself modifiable → "metacognitive self-modification."
- **Domains:** paper review, robotics reward design, olympiad math grading (not just code).
- **Cross-domain transfer:** hyperagent trained on paper-review + robotics transferred to math, achieving **imp@50 = 0.630** (human-designed meta agents: 0.0).
- **Emergent engineering** (self-discovered, not programmed): logging classes, timestamped memory, compute-budget-aware planning, persona switching, multi-stage pipelines.
- Code: github.com/facebookresearch/HyperAgents.

### 4. Weight-level self-evolution: MiniMax M2.7 (Mar 2026)
- 229B MoE model that participated in its own training loop.
- Self-evolution at the **weight level** vs DGM-H at the **code level** — complementary paths.

## Key Papers
- arXiv:2505.22954 — Darwin Gödel Machine
- arXiv:2603.19461 — HyperAgents (Meta, Mar 2026)
- hyperagents.agency — official project page

## Practical Patterns to Adopt
1. **Archive-based exploration** — keep all variants, sample parents from diversity.
2. **Editable meta-mechanism** — never freeze the "how to improve" prompt.
3. **Domain-aligned evaluation** — pick metrics that *reward self-improvement speed*, not just task score.
4. **Self-discovered infrastructure** — let the agent build its own logging/memory tools.
5. **Cross-domain transfer tests** — train in cheap domains, evaluate in expensive ones.

## Pitfalls
- Local-optimum plateaus — self-improvers converge and stop; need diversity pressure.
- Safety: sandboxed envs only; clear eval metrics required.
- DGM (frozen meta) ≠ DGM-H (editable meta) — don't conflate them.

## Trigger to Use
Designing a system where the agent rewrites its own prompts/code; building a self-evolving loop; researching recursive self-improvement benchmarks.

## Verify
- [ ] arXiv IDs 2505.22954 and 2603.19461 fetchable
- [ ] hyperagents.agency reachable
- [ ] Distinguish DGM (frozen) vs DGM-H (editable) when citing