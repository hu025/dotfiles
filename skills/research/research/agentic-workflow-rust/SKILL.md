---
name: agentic-workflow-rust
description: Use when evaluating or borrowing from AgenticWorkflow, the Rust orchestration engine (agentralabs/agentic-workflow) — 124 MCP tools, .awf binary format. Read this FIRST: the library does NOT execute steps.
metadata:
  type: research
  source: https://github.com/agentralabs/agentic-workflow
  license: MIT
  stars: "~180 (2026-10)"
  verified: 2026-10-24
  rust_loc: 13405
---

# AgenticWorkflow (Rust orchestration engine) — verified assessment

**Read this first: the library is a coordination/state-tracking layer, NOT an execution
engine.** `execute_step` returns `{"status": "prepared"}` with `success: true` for every
real step type (Command / McpTool / HttpRequest / SubWorkflow). There is no
`std::process::Command`, no `reqwest`/`ureq`, and no HTTP client anywhere in the core
crate — 0 runtime deps beyond serde/tokio/chrono/thiserror/uuid/blake3/lz4.

`execute_step` is called **only from `crates/agentic-workflow/tests/`**, never from
`DagEngine::start_execution`. `start_execution` creates an `ExecutionContext` with every
step `StepLifecycle::Pending` and returns an execution id. **The workflow never advances
past Pending.** The paper's "step execution occurs in a single process" is aspirational;
the README roadmap lists "Step execution runners (shell, HTTP, MCP)" as **Planned**.

Do not recommend this to anyone who needs workflows that actually run something.

## What is genuinely good (steal these)

### 1. "No-hardcoded-intelligence" rule
> "All runtime classification—failure type detection, natural language workflow parsing,
> intent routing—delegates to LLM micro-calls rather than hardcoded keyword lists."

Rationale from the paper: a keyword classifier needs a code change per new failure
pattern; an LLM classifier generalizes from training data. Cost ≈ 50 tokens/call
(~$0.00001), negligible vs. maintenance burden.

This is a portable, high-value principle for any agent framework: **let the LLM do the
classification; keep the runtime deterministic.** Hermes already leans this way, but the
explicit "no keyword lists for failure classification" stance is worth copying.
In code it shows up as `// condition evaluation is an LLM task per CLAUDE.md`.

### 2. Single-file state (SQLite-style "application file format")
All workflow state (registry, templates, execution history, schedules, FSM table,
trigger index, audit log, idempotency cache, variable store) lives in **one** `.awf`
binary file. No DB, no daemon, no deployment. "An agent that can write to the filesystem
can use AgenticWorkflow."

Tradeoff the authors state plainly: concurrent writes need external coordination
(file locks); for multi-agent use the single file becomes the coordination bottleneck.

### 3. `.awf` binary format (verified from source, not the docs)
```
magic "AWFL" (4 bytes) | version u32 LE | workflow_count u32 LE | exec_count u32 LE
then repeated sections: section_type u8 | data_len u32 LE | data
```
- 9 section types: WorkflowRegistry=1, TemplateLibrary=2, ExecutionHistory=3,
  ScheduleTable=4, StateMachineTable=5, TriggerIndex=6, AuditLog=7,
  IdempotencyCache=8, VariableStore=9
- Section payloads are JSON, then **LZ4-compressed** (`lz4_flex`, prepend-size framing)
  and **BLAKE3-checksummed**; reader verifies checksum on read.
- Reader rejects `version > AWF_VERSION` (currently 1). **No migration tooling** —
  upgrade = export + reimport.

**Docs are wrong here**: `docs/concepts.md` claims ".awf is a YAML-based declarative
format". It is not — the reader requires the `AWFL` magic bytes. Trust the source.

### 4. Failure-class-keyed retry policy
`FailureClass` enum: `Transient | Permanent | RateLimit | ResourceContention |
Authentication | Network | Timeout | Unknown`. Each `RetryPolicy` holds per-class
`RetryProfile`s plus an optional `RetryBudget` and `RetryEscalation`. The right design
is to classify *first*, then pick a policy — not one blanket backoff for everything.

**Gap worth fixing when copying**: `calculate_delay` has **no jitter**
(`initial_ms * multiplier^attempt`, capped at `max_ms`). Production retry needs jitter
or you get synchronized thundering-herd retries.

### 5. Idempotency keyed on BLAKE3
`IdempotencyEngine::check(key)` / `store(key, step_id, execution_id, input_hash, output)`
— BLAKE3 of the input, TTL expiry, stored output for replay/dedup.

### 6. Rollback with receipts
`define_action` / `preview` (dry-run) / `execute_rollback` → `RollbackReceipt`
(verification + receipt history per execution). The `preview`-before-`execute` split is
worth copying regardless of language.

### 7. Audit trail that is actually queryable
`AuditEngine::record(execution_id, workflow_id, step_id, event_type, actor, resource,
input, output, outcome)` and `query(AuditQuery)` filtering on
workflow_id / execution_id / actor / resource / from / to / event_type.
Structured actor+resource+outcome records are what make post-hoc "who did what to what"
answerable — worth copying into Hermes cron/agent audit logging.

### 8. MCP-as-sole-interface
They deliberately did **not** ship a parallel "native" API as primary; MCP is the
interaction surface, Rust lib is the developer API. Every capability is reachable from
any MCP client with zero framework integration. Serialization overhead acknowledged and
measured as negligible.

## Tool surface (verified count)
~122-124 MCP tools across 10 modules:
`dag_tools` (6) · `execution_tools` (8) · `schedule_tools` (5) · `trigger_tools` (6) ·
`resilience_tools` · `governance_tools` · `processing_tools` · `state_tools` (6) ·
`template_tools` · `intelligence_tools`.
Naming: `workflow_<domain>_<verb>` — e.g. `workflow_retry_configure`,
`workflow_evolve_drift`, `workflow_audit_timeline`, `workflow_var_promote`.

## Intelligence layer — heuristic, not ML
`PredictionEngine::predict_duration` = historical average with
`confidence = min(n/10, 1.0)`. `predict_success`, `predict_cost`, `predict_resources`
are the same shape. `EvolutionEngine::detect_drift` / `suggest_optimizations` /
`outdated_steps` are heuristics over execution fingerprints. `ArchaeologyEngine` does
retrospective analysis. None of it can be populated in practice, because executions
never run.

`DreamEngine` ("dream_optimize") and `CollectiveEngine` ("collective_share/private")
are thinly-veiled metaphors for background optimization and multi-agent knowledge
sharing — the naming is marketing, the bodies are small (71 and 126 LOC).

## Also present
- `FsmEngine` — explicit state machine per workflow (states/transitions/history),
  separate from the DAG. Useful separation: DAG for dataflow, FSM for lifecycle.
- `StreamEngine` — `checkpoint(stream_id, offset, items_processed)`, `fork`, `pause`.
- `SchedulerEngine` — adaptive schedule recommendations (explicitly a placeholder).
- `FanOutEngine` + `CompletionPolicy` = `WaitAll | WaitAny | WaitN(n) | WaitTimeout(ms)`.
- `EdgeType` = `Sequence | Parallel | Conditional{expr} | Loop{max_iterations, condition}`.
- C FFI (`awf_init`, `awf_workflow_create`, `awf_workflow_run`, `awf_version`, …) for
  embedding from non-Rust hosts.
- CLI `awf` with `create/list/run/status/validate/visualize` (Mermaid output).

## Verification notes (how to re-check)
```bash
git clone --depth 1 https://github.com/agentralabs/agentic-workflow
# does it execute anything?
grep -rn "std::process::Command\|reqwest\|ureq" crates/agentic-workflow/src/
# is execute_step wired into the engine, or only tests?
grep -rn "execute_step" crates/
# real tool names
grep -rhoE '"workflow_[a-z_]+"' crates/agentic-workflow-mcp/src/tools/ | sort -u
```
Paper metrics all verified exact against source: 13,405 total Rust LOC, 89 `.rs` files,
281 `#[test]`/`#[tokio::test]`, max file 362 lines, 0 runtime deps.

## Relation to Hermes
- `.awf` single-file state ≈ Hermes' per-project `.hermes/` dirs but without the DB.
- The `execute_step`-returns-"prepared" pattern is the **anti-pattern to avoid**: a
  Hermes "orchestration" layer must never report `success: true` for work it did not
  perform. If we ever build a workflow layer, the executor contract must be: an
  unmaterialized step is `Pending`/`Blocked`, never `Success`.
- The audit-event shape (actor / resource / outcome / input / output / timestamp) is a
  drop-in for improving Hermes cron run logging.
- Failure-class-keyed retry + budget + escalation is better than a single exponential
  backoff; and it must include jitter.

## Sources
- https://github.com/agentralabs/agentic-workflow
- https://github.com/agentralabs/agentic-workflow/blob/main/docs/api-reference.md
- https://github.com/agentralabs/agentic-workflow/blob/main/docs/concepts.md
- paper: `paper/paper-i-orchestration/agenticworkflow-paper.tex` (in-repo)
- https://lib.rs/crates/agentic-workflow
