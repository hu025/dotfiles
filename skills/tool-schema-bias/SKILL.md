---
name: tool-schema-bias
description: Use when designing, reviewing, or debugging an agent's tool-call interface. Tool schemas are one encoding of an action space, not the action space itself; equivalent schemas swing success 0%→97%. Covers Hermes's own tool_search→tool_describe→tool_call bridge.
---

# Tool-Schema Bias

A tool schema is **a coordinate system, not a territory**. The same executable
action can be exposed many equivalent ways — one dispatcher or many small
tools, flat or nested arguments, one call or a begin/write/commit
transaction. An agent that truly learned the task should behave identically
across all of them. It doesn't. Measured across 11 LLMs and 32 verified-equivalent
variants: success swings from **0% to 97%** with nothing but the schema changed.

Source: *Action-Space Shaping for LLM Agents: Measuring and Mitigating
Tool-Schema Bias* (arXiv:2609.34971, Cambridge/Huawei/HKUST(GZ), 2026-09-28).
Code: `github.com/williamLyh/ToolSchemaSpace` (CC BY 4.0).

## When to Use

- Designing or refactoring an agent's tool surface (merging, splitting, renaming).
- Debugging "the agent calls the wrong tool / wrong arguments" when the task
  logic looks correct.
- Interpreting benchmark scores — a score may reflect the interface, not the model.
- Evaluating whether a schema change is safe before shipping it.
- NOT for measuring model capability on a *fixed* interface (that is plain eval).

## The core insight

Benchmarks, RL environments, and deployed systems all quietly assume the tool
schema **is** the environment. τ-bench picks one parameterization of its airline
domain; AppWorld groups 457 APIs into classes one particular way; MCP servers
expose tools however their authors felt like factoring them. Then agents are
scored as if the score measured task competence.

It measures the coordinate system too. Concretely, for `modify_order(order_id,
field, value)` these are all the same action space:

| Encoding | What the model sees |
|---|---|
| Native | `modify_order(order_id, field, value)` |
| Fully merged | `execute(operation="set_window", set_window::position="front_left", …)` |
| Fully split | `modify_order__field_status__value_shipped(order_id)` |
| Transaction | `begin()` → `modify_order__field(txn_id, …)` → `commit(txn_id)` |
| Schema discovery | `list_methods(Order)` → `invoke(Order, modify_order, args)` |
| Reference resolution | `resolve(handle)` → `modify_order(handle, …)` |

All admit a mechanical, invertible translation to the same native action and
reach the same final environment state.

## The nine operators

| Family | Operators | Mechanism |
|---|---|---|
| **Tool-set partitioning** | `merge` | Fuse functions into one tool behind a discriminator; the chosen function becomes an argument value. |
| | `split` | Break one tool apart by an argument's value range (enum split, interval split). |
| **Per-tool surface** | `nest` / `flatten` | Change the parameter-schema tree. |
| | `rename` | Namespaced (`cls__method`) or opaque (`fn_d8abb4`) identifiers. |
| | `strip_desc` | Remove descriptions. |
| | `reorder` | Permute argument order. |
| **Cross-call protocol** | `transaction` | One action → begin / write / commit. |
| | `reference_resolution` | One action → resolve value to handle first, then pass handle. |
| | `schema_discovery` | One action → list the class's methods, then invoke. |

## The findings that matter

### 1. Merging hurts; splitting mostly doesn't

On a 10-step granularity ladder (0.07× → 10.6× native function count), across
9 models: **splitting largely preserves native performance; fully merging
costs a median of 19 points.**

Intuition: splitting bakes the decision *into the name the model reads
directly*. Merging forces the model to route through a dispatcher and
remember namespaced argument conventions.

**No merge encoding is safe for everyone.** The *nested* merged-argument form
cost **every** model 19–73 points — even Qwen3.5, which loses under 7 points on
the flat merge, fell to 0.20–0.25 on the nested one. **Flat is the safe merge
encoding; nested merge is a trap.**

### 2. Semantically-grouped merges beat random ones

At fixed granularity, grouping semantically related operations is consistently
better than random or mismatched grouping, and the gap widens as groups grow.
**Mixing argument structures within one catalog costs more** — for all but one
model, a mixed catalog scores below the average of its constituent structures.

### 3. Per-tool surface changes are cheap

Nesting arguments, stripping descriptions, permuting argument order, and
namespacing tool names leave every model close to its native score. The one
exception: **opaque function names hurt the smallest model** (Qwen2.5-7B), and
that sensitivity vanishes with scale.

### 4. Cross-call protocols are the hardest operators

Transaction and schema discovery collapse most earlier-generation models, often
to near zero. Reference resolution is the exception in the other direction —
models that follow the extra resolver call score **at or above** their native
rate. So a cross-call protocol is not harmful in itself; **whether a model
follows it is model-specific.**

### 5. Closed models are not immune

Two closed models moved by 32 points under equivalent schemas. Their weak spots
were **class dispatch and namespaced names** (large-catalog exposure), *not* the
cross-call protocols that break open models. Schema bias is not an open-model
bug.

### 6. Failures follow the variant, not the model

The same native tasks produce different *error types* under different schemas:

| Failure mode | Rule | Symptom |
|---|---|---|
| **Livelock** | hits turn limit | loops on retries/clarifications without committing |
| **Transaction handle** | write/commit names an unopened txn, or commit precedes writes, or double-commit | broken begin/write/commit protocol |
| **Rejected and stuck** | ≥1 off-schema call rejected, fewer native actions executed than required | calls a name/arg the schema doesn't expose and can't recover |
| **Wrong class** | call routed through the wrong dispatcher/namespace | operation chosen from the wrong group |
| **Under-execution** | fewer native actions than required, no rejection | required steps skipped |
| **Over-execution** | more native actions than required | extra or repeated actions |
| **Wrong arguments** | right functions, wrong values | right calls, wrong values |

First four are **explicit** (runtime/routing errors). Last three are **silent**
— the episode ends with the wrong action set, and nothing errors out.

Variant→failure mapping is fairly stable: fully-merged catalogs fail as
*rejected-and-stuck*; transaction fails as *broken transaction handles*;
schema discovery fails as **silent wrong arguments**.

### 7. The schema-form gap — knowing the action but not the form

Sometimes the model invokes the **correct native action** but writes it in the
wrong schema (off-schema call that decodes to the right action). Re-running
with off-schema calls *executed* instead of *rejected* measures the gap.

Schema-form failures concentrate on **renaming/regrouping variants and earlier
model generations**. Fully merged has by far the largest gap (Qwen3 and smaller
Qwen2.5 models keep calling native tool names). Recovered episodes are mostly
*rejected-and-stuck*.

> **Design consequence:** an off-schema rejection that carries the correct
> action's intent is a *form* failure, not a *decision* failure. Rejecting
> without telling the model which name was wrong turns a form failure into a
> livelock.

### 8. Cheap probes can't predict difficulty; ~100 real queries can

| Estimator | Spearman ρ vs full-set ranking |
|---|---|
| Likelihood of correct call sequence (no task queries) | 0.52 |
| Schema compliance probe (no task queries) | 0.57 |
| 36 target queries | 0.72 |
| **~100 target queries** | **0.81** |
| 800 target queries | 0.92 |

The probes fall short because they **omit the tasks**, not because they're
small. Difficulty is a joint property of model × schema × task queries: models
often follow a protocol on isolated calls yet fail it inside multi-turn tasks.

**Transfer warning:** a ranking measured on synthetic tasks did *not* predict the
ranking on τ²-bench; a τ²-bench ranking predicted BFCL only moderately. Sample
from **the environment's own task distribution**.

### 9. Training repairs what it sees — and only that

- SFT on native-only data keeps native performance but repairs no hard variant.
  The repair comes from *seeing* a variant, not from more tool-use practice.
- SFT taxes already-robust variants; **the tax depends more on how the
  demonstrations are phrased than on how many there are.** Colloquial data beat
  templated data at every size (0.680 vs 0.447 at 500 traces); more than ~1,000
  colloquial traces didn't help.
- **On-policy RL repairs the trained variants without the tax** — every variant
  at or above its untrained score. Three conditions: the variant appears in
  training data, **no KL penalty** (KL=0.01 undoes the gain: 0.75 → 0.25), and
  **the environment rejects invalid calls**.
- Transfer: gains carry to new *combinations* of trained changes (+8.8) and
  stronger versions of them (+11.2), but **not to new kinds of change**
  (−2.4 for unseen operators, +1.2 for new class-level structures).
- Real benchmarks: the gain appears only where the rewrite matches a trained
  variant; overall τ²-bench and BFCL scores barely moved.

> **Training does not make a model robust to schema changes in general.** It
> reduces the specific biases it targets.

### 10. Training-free mitigation is narrow but free

| Method | Effect |
|---|---|
| Instruction (one sentence describing the calling convention) | +0.28 fully merged, **+0.45 schema discovery**; ~0 elsewhere |
| Constrained decoding (force first call schema-valid) | +0.29 fully merged; ~0 elsewhere |

One sentence describing the convention fixes habits one sentence can describe.
Neither helps per-tool surface variants (which aren't broken anyway).

## What this means for Hermes specifically

Hermes's own bridge **is** one of the paper's harder encodings, deliberately:

- `tool_search` → `tool_describe` → `tool_call` is **schema discovery**
  (list methods, then invoke only with names you were given) — the operator
  with the *lowest* base score in the paper (Qwen3-4B: **0.07**).
- `tool_call` is `calls: [{name, arguments}]` — a **class-dispatcher / merged
  dispatcher**, where the tool name becomes an argument value. This is the shape
  the closed models were weakest on (32-point swings) and where nested argument
  structures cost 19–73 points.
- `tool_describe` is a **reference-resolution** step: resolve a name to a schema
  handle, then use that handle. This is the one cross-call protocol the paper
  found models handle *at or above* native rate — the best of the three for
  Hermes's shape.

**What Hermes already does right** (and why):
- The bridge descriptions are explicit one-sentence conventions — exactly the
  "instruction" mitigation the paper shows is worth +0.45 on schema discovery.
- `tool_search` returns names + one-line descriptions, and the description
  says "go straight to `tool_describe` when you see the exact name" — this is
  the reference-resolution path, kept cheap.
- `tool_describe` takes an array of names → batched schema load, keeping the
  cross-call protocol to one extra round trip.
- **Off-schema rejections are corrective, not merely refusals.** Hermes already
  implements the paper's "a form failure must not become a livelock" rule:
  - `not_deferrable_error` distinguishes *two different mistakes* that need
    **opposite** corrections — a directly-listed tool ("call it directly
    instead of via tool_call") vs. an unknown name (usually a deferred MCP tool
    cited by its bare suffix instead of the full `mcp__<server>__{tool}` name).
    Telling the second group "call it directly" is the opposite of what they
    must do, so it does not.
  - It then resolves candidates by suffix and emits **"Did you mean 'x'?"**,
    falling back to "Use tool_search to find the exact name." That converts a
    schema-form failure into a one-turn correction.
  - `scope_block_reason` separately names the *missing surface* for
    session-gated GUI tools, so the model isn't sent on a `tool_search` round
    trip that can never succeed.
  - `validate_deferred_call_args` produces a path-anchored validation error
    plus "Retry tool_call with 'arguments' matching the parameters schema above."

**Concrete risks and their mitigations:**

| Risk | Mitigation |
|---|---|
| Model calls a native tool name that isn't exposed (schema-form failure) | **Already handled** — `not_deferrable_error` names the correction and offers suffix-resolved candidates. Keep it that way: any new rejection path must carry a *corrective* name, not just "unknown". |
| `tool_call` argument structure drifts toward nested | Keep `arguments` a flat object matching the described schema. Paper: nested merged args cost every model 19–73 points. |
| Model treats `tool_call.calls` as a batch when calls are dependent | Paper: dependent calls in one batch → wrong-class / under-execution. Batch only independent calls. |
| Large deferred catalog → class-dispatch weakness | Prefer the listing form that lets the model skip `tool_search` when it sees the exact name; don't force a search when the name is visible. The closed models' weak spot was large-catalog exposure. |
| Off-schema rejection loop | The paper's livelock mode. Hermes's corrective errors address the cause; still cap retries on the *same* off-schema call so a model that ignores the correction can't burn the turn budget. |

**Hermes's eval harness is already the right instrument.** `evals/core_tool_deferral/`
runs real `AIAgent`s from two pinned checkouts with a programmatic grader over
a 14-task battery. The paper's methodology extends it directly: add a
**verified-equivalent schema arm** — same task, same grader, one variable
changed (the schema encoding). The existing harness's A/B structure maps onto
"native vs one variant."

## How to test a schema change

The paper's method is the model to copy — **make the equivalence verifiable, not
assumed**:

1. **Define the native action space.** Normalize each invocation into an
   operation + typed arguments. That record is the *native action*.
2. **Write a decoder** from the variant's call form back to native actions.
   (Many-to-one is fine: a model may set transaction args in different orders
   and still be correct.)
3. **Prove the variant lossless.** Replay the native gold trace through the
   variant, decode it back, and assert the native actions match exactly. A
   perfect model must score 1.0 on every variant or the variant is buggy.
   (The paper's validator caught 3 implementation bugs *before* any model ran.)
4. **Score schema-independently.** An episode succeeds iff the multiset of
   *decoded native actions* exactly matches the gold set. Never score on the
   variant's own vocabulary — that would hide exactly the effect being measured.
5. **Grade in native-action space** so all variants are comparable.
6. **Sample from the real task distribution** when estimating difficulty.
7. **Report the variant spread**, not one number. A schema change with a 19-point
   median cost is not a refactor — it's a behavior change.

## Anti-patterns

- ❌ Merging tools into one dispatcher "to reduce tool count" — median −19 points,
  and −19 to −73 for nested argument structures.
- ❌ Assuming a benchmark score transfers to a re-factored schema.
- ❌ Using opaque tool names for small models (hurts; harmless at scale).
- ❌ Rejecting an off-schema call without saying which name was correct.
- ❌ Randomly grouping merged tools — semantic grouping is consistently better.
- ❌ Believing more SFT data fixes schema bias — it doesn't, and it taxes
  already-robust variants.
- ❌ Assuming schema bias is an open-model problem — closed models moved 32 points.

## References

- Paper: https://arxiv.org/abs/2609.34971 (html: arxiv.org/html/2609.34971v1)
- Code + benchmark + variant specs: https://github.com/williamLyh/ToolSchemaSpace
- Related: τ²-bench, BFCL v3 multi-turn, AutomationBench, MCP-Atlas adapters
  live in `adapters/` of the repo.
- Hermes side: `~/.hermes/hermes-agent/tools/tool_search.py`
  (`bridge_tool_schemas`), `tools/tool_search_catalog.py`,
  `evals/core_tool_deferral/`.
