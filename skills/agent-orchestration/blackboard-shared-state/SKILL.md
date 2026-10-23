---
name: blackboard-shared-state
description: Use when coordinating multiple agents or subprocesses over a shared artifact (plan file, repo, task queue, findings doc). Decides blackboard/shared-state vs message-passing, designs the state schema, conflict handling, and termination. Triggers: multi-agent, orchestration, parallel agents, subtask fan-out, shared state, blackboard, handoff, "agent team", subagent coordination.
---

# Blackboard / Shared-State Orchestration

Blackboard (shared mutable state + trigger-based activation) vs message-passing (agent→agent handoff) is the **first** design decision in a multi-agent system — it precedes topology. Every topology in current use (fan-out, pipeline, debate, supervisor, swarm) can be expressed on either substrate.

## Pick the substrate first

| | Blackboard (shared state) | Message passing |
|---|---|---|
| Agents know what others did by | **reading** state | being **told** via message |
| Failure blast radius | conflicts/races/overwrites | delivery risk, information loss |
| Add/remove an agent | no code change elsewhere | update addressing everywhere |
| Termination decided by | explicit state flag | who owns the full picture |
| Debugging | harder (no single "the plan") | easier (the transcript) |
| Fits | specialists contributing partial answers to one problem | ordered chains, independent workstreams, heavy writes to shared mutable state |

Neither is free. Message passing trades conflicts for delivery risk; shared state trades delivery risk for conflicts. Do not call either failure-free.

## Why this is now the default answer

Every agent-to-agent message is a **lossy re-summarization performed by a model under token pressure**. Chain three handoffs and you are playing telephone with your own architecture — nuance is hallucinated away in the summary and the final instruction is unrecognizable from the original.

MAST (Multi-Agent System Failure Taxonomy, NeurIPS 2025 D&B; 1600+ traces, 7 frameworks, κ=0.88) measured where MAS actually break:

- **System design issues 41.8%** · **Inter-agent misalignment 36.9%** · **Task verification 21.3%**
- 14 failure modes, including `2.4 Information Withholding` (15.2%), `2.5 Ignored Other Agent's Input` (13.61%), `1.4 Loss of Conversation History` (9.16%), `2.6 Reasoning-Action Mismatch` (8.64%), `3.2 No or Incomplete Verification` (7.59%)

**Coordination failures outnumber capability failures.** Blackboards make a whole class of them *structurally impossible* rather than merely less likely. Separately: simply improving agent role specs gave ChatDev **+9.4%** success with identical prompt and model — specification is a lever.

## Three primitives

1. **The Blackboard** — shared, structured state holding the objective, all partial results, hypotheses, and terminal flags. Persist outside any single agent's context window.
2. **Knowledge Sources (KS)** — specialized workers that know nothing about each other. They only read/write the board.
3. **The Control Shell** — decides *which* KS may write next, from the board's current state. Often a cheap fast model or plain code. The routing decision is inspectable state, not vibes buried in a prompt.

Lineage: Hearsay-II → Hayes-Roth → Nii (1970s–80s). Not new; its revival is evidence, not novelty.

## Design rules that pay off

**Rule 1 — Structure the shared state into levels.** Never a blob of prose. Typed JSON with per-section ownership.

**Rule 2 — Every contribution carries its evidence and confidence.** A board entry without provenance is a rumor. Conflicts stay *visible* in public state where the shell or a human resolves them; in message-passing each conflicting belief lives privately in a different context window and you meet the disagreement at merge time as a mystery diff.

**Rule 3 — Treat "what runs next" as explicit inspectable knowledge** with a value estimate behind it.

**Rule 4 — Trigger model, not assignment model.** KS declare activation conditions and *volunteer* when state matches. This removes the coordinator's need to model every worker's capability up front — worth double-digit success-rate improvements in the 2025 data-discovery results (13–57% over master–worker).

**Rule 5 — Rerunnable/rewindable by construction.** Any KS can be rerun, rewound, or replaced without losing artifacts other KS produced. Message passing gives you none of this.

**Rule 6 — Propose → Validate → Commit, never write direct.** Agents propose; the system validates for conflicts and commits atomically. This is how you keep conflicts from corrupting the board. `priority-wins` is a workable conflict-resolution policy. Log every state change with agent ID + timestamp + signature — then "why did agents act this way" becomes a query, not archaeology.

**Rule 7 — Make termination a board field, not a guess.** Set a `consensusReached` / `status` flag that the Control Shell owns. Otherwise you get premature termination, a top-3 MAST failure mode.

## Two proven shapes

### Opportunistic blackboard (full classical)

Board state → Control Shell routes → KS volunteers and writes → shell re-routes. Workflow *emerges* from state. Max decoupling, hardest to trace.

### Deterministic blackboard pipeline (DLBP, IAIT'26)

Classical opportunistic KS firing produces emergent, un-traceable execution — the reason blackboards were skipped in practice. DLBP keeps shared persistent state + KS specialization but swaps the opportunistic scheduler for a **deterministic pipeline**. A five-role skeleton — Normalizer → Proposer → Critic → Verifier → Correlator — ports across domains (cyber, medical triage, fraud, legal discovery, industrial monitoring) by swapping KS prompts only, with no change to pipeline or coordination logic. Reports per-KS latency profiles, fallback behavior, prompt regression recovery, and cost tradeoffs.

**Choose DLBP unless you genuinely need emergent routing.** You give up traceability for flexibility you usually don't need.

## Context economics

Pass **pointers to state**, never the whole transcript. Message-passing chains force you to copy full conversation history into every downstream prompt to avoid degradation — that is the token bill. A blackboard lets each agent read only the sections relevant to its specialization. In the age of expensive inference, context economy is the difference between viable and not.

Corollary: **LLMs are effectively the locking mechanism.** They are slow enough and semantically aware enough to manage shared-state concurrency without deadlocking — which is why blackboards are viable now when they weren't in traditional distributed engineering.

## The consensus loop

Never exit on the first answer. Board mandates iteration until it stabilizes: agent A writes a proposed fix; agent B (adversarial reviewer) writes a critique; A updates; B re-evaluates and marks approval. Only when the Control Shell flips the terminal flag does output leave. This drives hallucination rate down by orders of magnitude because the result has been cross-checked by a specialized adversarial perspective — and it directly targets MAST `3.2/3.3` verification failures.

## Map existing frameworks onto the substrate

| Framework | Native substrate |
|---|---|
| LangGraph StateGraph | shared state (typed state, nodes read/write, edges route) |
| OpenAI Agents SDK / Swarm | message passing (handoffs, shared message context) |
| CrewAI Flows | shared state (reducer-style: read state, work, write back) |
| AutoGen Swarm / SelectorGroupChat | message passing (broadcast message context) |
| MCP-hosted board | shared state (agent-blackboard persists the board over MCP) |

When a framework's state API is implicit (conversation history only), that is the real problem: state fragments across message history and you cannot trace why an agent acted. Fix by adding an explicit structured state object agents read and write, external and durable — Redis for distributed, file/SQLite for single node. Schema with Pydantic; structured logging with correlation IDs.

## Known implementations

- **agent-blackboard** (MIT, Python, ~14 stars) — Blackboard + Coordinator + 9 specialized agents, board persisted over MCP, embedding-based knowledge retrieval, DDD workflow with automated RFC generation. Small, but the reference implementation of the shape.
- **SE-Blackboard** (IEEE, 2026) — shared-state architecture for multi-agent SWE pipelines. On 50 SWE-bench Lite issues, blackboard improved Coder-stage IFS **62% over message passing (0.586 vs 0.362)** with higher correct-patch rate.
- **network-ai LockedBlackboard** — TypeScript, propose/validate/commit with priority-wins conflict resolution and a cryptographic audit trail, plus AutoGen/CrewAI/LangChain adapters.

## Failure modes you are choosing to inherit

Do not adopt shared state without owning these:

- **Consistency conflicts** — two writes in the same window, one silently survives.
- **Race conditions / overwrite bugs** — a field reverts to an earlier value with no error thrown.
- **Termination ambiguity** — no single place holds "the plan."
- **Termination cost** — an explicit verifier/Consensus Loop adds latency and tokens; budget it.

Countermeasures, in order of leverage: propose/validate/commit → typed schema + validation → audit log with correlation IDs → explicit terminal flag.

## Applying this to Hermes

Hermes' own fan-out is message-passing: a parent spawns children and only summaries return. When a fan-out's children need to see each other's intermediate results, do **not** relay them through the parent — write findings to a shared file both children can read. This is exactly the blackboard move Anthropic made building its multi-agent research system, where the fix for subagents "distracting each other with excessive updates" was: lead agent writes the plan to persistent external memory so it survives context truncation; subagents write findings to shared state rather than relaying everything through conversational handoffs.

The blackboard you already have is **git**: a plan file, a repo, a findings doc everyone reads and writes. The point is to make it structured, leveled, and provenance-carrying — not to adopt a framework.