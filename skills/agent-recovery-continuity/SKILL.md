---
name: agent-recovery-continuity
description: Use when designing, reviewing, or using an agent's checkpoint/rollback, /undo, resume, or retry mechanism. Restoring a checkpoint faithfully does NOT make the resumed execution safe — five failure modes break execution continuity even with an uncorrupted checkpoint. Includes a Hermes-specific rollback safety checklist.
---

# Agent Recovery Continuity

**A correctly restored checkpoint does not imply a secure recovery.**
A faithful rollback can resume an execution whose states, assumptions, and
external effects *never coexisted in any valid history*. No checkpoint
corruption, no broken recovery mechanism, no attacker touching the store is
required — the hazard is structural.

Source of record: Wu et al., *"Safe to Resume? Breaking Execution Continuity of
Agent Execution via Rollback"*, arXiv:2608.29381 (cs.CR, 2026-08-29).
First systematic security study of C/R in agent systems; it attacks
**Hermes**, Cline, and LangGraph directly.

## The core requirement: execution continuity

> Security-relevant states, decisions, assumptions, and effects carried
> across recovery must remain jointly consistent with a valid continuous
> execution history.

Recovery breaks it in exactly two ways:

1. **Invalid recovered state** — the restored combination could never occur
   in a valid continuous execution. (Validation result survives; the artifact
   it validated does not.)
2. **Invalid recovery transition** — the restored state is individually
   valid, but rollback enables a *subsequent* transition no valid execution
   would permit. (One-time approval now authorizes a second payment.)

## The five failure modes (SF1–SF5)

| ID | Name | Boundary | One-line test |
|----|------|----------|---------------|
| SF1 | Incomplete internal state coverage | internal | Is a process relevant to the resumed task outside the checkpoint's `K`? |
| SF2 | Inconsistent checkpoint state | internal | Do captured states form one causal cut, or two different points in time? |
| SF3 | External state mismatch | external | Did any external dependency the checkpoint assumed change since it was taken? |
| SF4 | Unbound nondeterministic replay | replay | Can replay take a different branch, reusing a decision made for the old branch? |
| SF5 | Unrecorded external effects | external | Did an effect commit outside the boundary *before* the agent durably recorded it? |

### SF1 — incomplete internal state coverage
The checkpoint omits internal state needed to resume. The omitted process
recovers to some state `ρj ≠ sj^k`. Two directions, both dangerous:
- **Newer-state carryover** — the uncovered process stayed live and kept
  advancing past the checkpoint point (`k' > k`). The resumed run mixes a
  checkpointed state with a *later* state.
- **Older-state fallback** — the process restarted from scratch after a
  failure (`k' < k`), mixing a checkpointed state with an *earlier* state.

### SF2 — inconsistent checkpoint state
The captured states are each individually valid but mutually inconsistent:
`Pn` reflects consuming an event produced by `P1`, while `P1`'s captured
state predates producing it. Both are real; they cannot be one execution cut.

### SF3 — external state mismatch
A compatibility predicate `Γ(s, W)` says whether the security judgments
encoded in state `s` still hold under outside-world state `W`. It held at
checkpoint time (`Γ(s^k, W^tc) = 1`). Rollback does **not** rewind `W`, so
recovery happens under `W^tr` where `Γ(s^k, W^tr) = 0`. The restored
approval, recipient list, or policy binding is now stale.

### SF4 — unbound nondeterministic replay
Post-checkpoint operations re-run. Same operation, same state, different
`ξ` (LLM sampling, tool response, random test selection) → different
security-relevant outcome, and no mechanism binds the new outcome to the
decisions established for the old one. Two shapes:
- **Cross-path reuse** — an approval/validation survives a replay that took
  a different branch where it no longer holds.
- **Retry amplification** — repeated rollback turns one security-sensitive
  nondeterministic decision into repeated trials until a favorable outcome
  appears. (Rollback as brute force.)

### SF5 — unrecorded external effects
The effect committed, the record of it did not. Rollback restores the
pre-action state, so the agent believes the action never ran and issues it
again. Two shapes:
- **Orphaned effect** — the effect lives, its identifier/metadata is gone,
  so it can never be confirmed or revoked.
- **Effect replay** — a non-idempotent external action is executed twice.

## Measured prevalence

1,735 framework-task executions, 347 traces (TerminalBench + AgentBench),
DeepSeek-V4 backend, random checkpoint per trace as the recovery point:

| Framework | SF1 | SF2 | SF3 | SF4 | SF5 |
|---|---|---|---|---|---|
| LangGraph | 300 | 0 | 99 | 228 | 17 |
| CrewAI | 328 | 0 | 0 | 276 | 7 |
| **Hermes** | **254** | **240** | **44** | **220** | **11** |
| Cline | 284 | 249 | 0 | 275 | 4 |
| E2B | 0 | 0 | 55 | 175 | 1 |
| **Overall** | **1166 (67.2%)** | **489 (28.2%)** | **198 (11.4%)** | **1174 (67.7%)** | **40 (2.3%)** |

SF1 and SF4 dominate. SF2 is a *workspace-vs-framework* signature: it needs
two independently-restored state domains. SF5 is rare only because most
benchmark tasks have no persistent external effects — that rate is a property
of the task distribution, **not** of the framework's safety.

Detection pipeline (4 agents: collector → analyzer → checker → validator)
reached 98.7% precision / 99.9% recall / 99.5% accuracy vs manual labels.
30 sampled validated findings were turned into attacks under the
malicious-skill adversary model; **all 30 succeeded**.

## Recovery-boundary taxonomy

| Boundary | Captures | Misses | Examples |
|---|---|---|---|
| Framework-state | conversation, workflow progress, agent memory, pending steps | workspace files, runtime, external services | LangGraph (superstep boundaries), CrewAI (task_completed), LlamaIndex Workflows, Google ADK, MS Agent Framework |
| Workspace-state | project files (often a **shadow git repo**) | process memory, installed system state, running services, files outside the workspace | Hermes, Cline, Gemini CLI, Claude Code |
| OS/VM-state | filesystem + process memory + running processes | framework state stored outside the env, external services | E2B (`create_snapshot()`), CRAB, DeltaBox |

Broader coverage ≠ safe recovery. **External state and persistent effects
sit outside every boundary**, and some designs restore state components
*independently* (Cline: workspace / task history / both).

## Why commit ordering cannot fix SF5

A controlled microbenchmark of 96 persistent external-action workflows
(payments, messages, resource creation) injected a recoverable failure
between the external commit and the state commit:

| External action | n | Execute→Commit | Commit→Execute |
|---|---|---|---|
| Payment | 30 | 28 | 29 |
| Message | 31 | 29 | 30 |
| Resource change | 35 | 33 | 34 |
| **Overall** | **96** | **90 (93.8%)** | **93 (96.9%)** |

*Execute→Commit* can lose the record of an effect that happened (duplicate
payment). *Commit→Execute* can preserve a completion state for an effect
that never happened (skipped payment). **Neither ordering closes the gap.**
Only external coordination — transactions, idempotency keys, durable effect
ledgers — binds agent progress to committed reality.

## The three published attacks

**Case 1 — malware verification bypass (Hermes, SF1).** A malicious skill
instructs the agent to clean a repo, run the project's checks, then load
release metadata from a path that fails. The cleanup forces a file write, so
Hermes checkpoints `C0` *before* the edit, preserving the malicious tree
`XM`; the edit yields clean tree `XC`; the checks pass on `XC`, producing
`VC` in agent-side state. The failure interrupts the release. The user runs
`/rollback` and picks `C0`. The workspace returns to `XM` while `VC` stays
live → the agent releases the *malicious* tree under a *genuine* verification
result. Nothing was forged; the checkpoint was real, the scan was real.
The published malicious skill is **not flagged** by a recent skill-injection
detector.

**Case 2 — unauthorized mail forwarding (Cline, SF3).** The agent tests
forwarding against a disposable mailbox `MT`, then switches the service's
session-level active mailbox to the real one `MR` for a read-only check.
A malicious MCP server induces a failure; the user restores task history
*only*. Task state says "forward to `MT`"; the service resolves against its
current binding `MR`. The authorization is rebound to a live resource.

**Case 3 — duplicate payment under one approval (LangGraph, SF5).** The
payment node submits the transaction, then fetches the receipt from an
attacker-controlled service that returns an error. The node never
completes, so no checkpoint records the payment — but the payment committed.
Recovery from the pre-payment checkpoint re-runs the node; with no stable
idempotency key, a second payment commits under the same approval.

## Hermes-specific findings (verified against this install)

Verified by reading `tools/checkpoint_manager.py` and
`gateway/slash_commands.py` in this checkout.

**Hermes is a workspace-state checkpoint.**
- Checkpoint trigger: automatic, before file-mutating operations
  (`write_file`, `patch`) and recognized destructive terminal commands;
  at most one checkpoint per directory per conversation turn.
- Storage: a **single shared shadow git store** at `~/.hermes/checkpoints/store`
  (content-addressed objects deduped across projects), per-project refs
  `refs/hermes/<hash16>` + per-project index.
- Restore: `/rollback` selects a checkpoint; `restore()` is **filesystem-only**.
  It restores files and rewrites the git tree. It does **not** touch
  conversation history, session state, or external effects.

**Important divergence from the paper.** The paper describes a Hermes build
whose `/rollback` "rolls back the most recent conversation turn", and
attributes Hermes's SF2 to that partial coordination. **This install's
`/rollback` restores the filesystem only** — conversation state is never
rolled back at all. Two consequences:

1. The published Case 1 attack **does not transfer as-is**: rolling the
   conversation back would have *removed* `VC` rather than preserving it
   next to a restored `XM`. Here, `VC` is not rolled back either — but it is
   also not *re-scoped*. The agent keeps its whole history including "the
   checks passed", while the tree under it is the pre-cleanup `XM`. Same
   rebinding outcome, reached differently: **the conversation is not rolled
   back, so the stale verdict is still in context.** Treat the stale-verdict
   hazard as live.
2. SF2's *cause* is present but its *mechanism* differs: the mismatch is
   between the restored filesystem and a conversation state that was never
   rewound — an unbounded version of SF2, not a one-turn mismatch.

**Real, checked scope limits of the Hermes checkpoint** (these are SF1/SF2
sources in practice):
- Files larger than `max_file_size_mb` (default **10**) are excluded from
  every checkpoint — a large artifact restored to an older version is exactly
  the Case 1 rebinding.
- `max_total_size_mb` (default **500**) caps the shared store; size-cap
  passes drop the oldest checkpoints per project.
- `_MAX_FILES = 50_000` — a snapshot is **skipped entirely** above this.
- **Nested git repositories are stored as gitlinks, not their files.** Their
  contents are not captured at all.
- `restore(safe=True)` preserves files the *user* hand-edited after Hermes'
  last write. So a rollback can produce a tree that is a **mix** of the
  checkpoint and post-checkpoint user edits — a textbook SF2 cut.
- Every rollback first takes a *pre-rollback snapshot*, so "undo the undo"
  is possible — but it also means the store accumulates points across
  unrelated states.

## Practical checklist (apply before trusting any rollback)

Before running `/rollback` (or designing one), answer:

1. **What will NOT be rolled back?** (conversation, session state, running
   processes, installed packages, remote resources, sent messages, payments)
   Everything here is a candidate SF1/SF3/SF5 carrier.
2. **Does any earlier conclusion in the context depend on the current state
   of a file?** If the answer is yes, the conclusion must be invalidated
   explicitly at rollback time — the tree and the conclusion now describe
   different worlds.
3. **Was any file excluded from the checkpoint** (>10 MB, nested repo,
   >50k files, pruned by the size cap)? Those files come back from wherever
   they are now, not from the checkpoint.
4. **Did anything external happen after the checkpoint?** A sent message, an
   issued credential, an uploaded file, a committed transaction — SF5.
5. **Will the resumed step re-execute a nondeterministic decision?** (LLM
   sample, random test subset, retry loop.) Cross-path reuse (SF4) and retry
   amplification are both live.
6. **Does the resumed step depend on external state that may have changed**
   (permissions, recipients, active session/binding, policy, time)? SF3.
7. **After restoring, is the resulting tree a single coherent point in time**
   — or a mix of checkpoint content, post-checkpoint user edits, and
   uncaptured files? A mix is SF2 by construction.

### Rules that follow

- **Never treat a post-rollback resume as continuation of the same run.**
  Treat it as a *new* run whose starting state happens to be an old file
  tree, and re-establish the facts the next step depends on.
- **Re-verify, do not re-assert.** After a rollback, re-run the validation
  whose result is still sitting in the conversation. A verdict produced
  against `XC` says nothing about `XM`.
- **Do not roll back to make an irreversible external action repeatable.**
  That is the duplicate-payment primitive.
- **Prefer concrete references over semantic ones** in anything a checkpoint
  will carry. The paper counted 1,357 context-dependent semantic references
  across the executions ("now" 222, "current state" 178, "this environment"
  87, "currently" 83, "earlier" 52, "previous run" 44, "this task" 41,
  "here" 39). Bind concrete values — timestamp, object id, version,
  checksum — so recovery stays deterministic and SF3's surface shrinks.
- **Constrain the replay.** Under-specified recovery (missing procedure,
  missing correctness condition, missing environment detail) lets a small
  sampling difference fork into a different, unsafe path. After a rollback,
  write down the procedure and the success condition before continuing.
- **For non-idempotent external effects, keep a durable effect ledger**
  outside the rollback boundary (idempotency key + recorded outcome).
  Commit ordering alone is provably insufficient (93.8% / 96.9% failure).
- **Do not let a rollback interface be reachable by an adversarial component**
  without a guard. In the paper, inducing a recoverable failure is often
  enough; the adversary never needs to touch the checkpoint.

## Related work named by the paper

Useful for follow-up research:
- **ACRFence** (arXiv:2603.20625) — semantic rollback attacks in
  agent checkpoint-restore.
- **AgentRewind** (arXiv:2608.14380) — jointly checkpoints agent context
  *and* execution environment. This is the design that closes SF1/SF2 for
  the agent-side domain by construction.
- **CRAB** (arXiv, semantics-aware checkpointing), **DeltaBox**
  (low-latency sandbox checkpoint/rollback).
- **Shepherd** (arXiv:2605.10913) — reversible agentic execution traces.
- **LogAct** (arXiv:2604.07988) — shared logs for agentic reliability.
- **Fork, explore, commit** (arXiv:2602.08199) — OS primitives for agentic
  exploration.
- **Atomix** (arXiv:2602.14849) / **Cordon** (arXiv:2606.17573) —
  transactional / semantic-transaction tool use for external effects.
- **Resume Means Resume** [16] — conformant resume semantics.
- **DART** [17] — formalizing semantic recoverability.

## References

- Wu, Li, Jiang, Niu, Wang, Zhang. *"Safe to Resume? Breaking Execution
  Continuity of Agent Execution via Rollback."* arXiv:2608.29381v1, cs.CR,
  2026-08-29. https://arxiv.org/abs/2608.29381
- Hermes checkpoint implementation: `tools/checkpoint_manager.py`,
  `gateway/slash_commands.py` (this checkout).
- Hermes checkpoint docs: `website/docs/user-guide/checkpoints-and-rollback.md`
- Sagas (Garcia-Molina & Salem, 1987) — compensating transactions for
  external effects; Chandy–Lamport — consistent global state cuts (SF2).
- Koo & Toueg (1987) — checkpointing/rollback for distributed systems.
- Parno et al. (2011), *Memoir: Practical State Continuity for Protected
  Modules* — anti-rollback/state-continuity security framing.
