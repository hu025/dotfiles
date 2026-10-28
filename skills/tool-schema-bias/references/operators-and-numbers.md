# Tool-Schema Bias — operational reference

Source: arXiv:2609.34971 (https://arxiv.org/abs/2609.34971v1) ·
Code: https://github.com/williamLyh/ToolSchemaSpace (CC BY 4.0)

## Numbers worth quoting

| Fact | Value | Where |
|---|---|---|
| Success range across equivalent schemas | 0% → 97% | Fig. 2 |
| Models evaluated | 11 (9 open-weight + 2 closed) | §4 |
| Schema variants | 32 verified-equivalent | §4 |
| Merge cost (fully merged, flat args) | median −19 pts | Fig. 3 |
| Merge cost (fully merged, **nested** args) | −19 to −73 pts, every model | §5.1 |
| Schema-discovery base success (Qwen3-4B) | 0.07 | Table 3 |
| Closed-model swing | 32 pts | §5 |
| Probe correlation (no task queries) | ρ=0.52 likelihood, 0.57 compliance | §7 |
| 100 target queries | ρ=0.81 (800 → 0.92) | §7 |
| SFT colloquial vs templated @500 traces | 0.680 vs 0.447 | §G.4 |
| RL KL=0 vs KL=0.01 (mixed data) | 0.75 vs 0.25 | Table 13 |
| Transfer to new *combinations* of trained changes | +8.8 pts | Table 14 |
| Transfer to *new kinds* of change | −2.4 pts | Table 14 |

## Failure taxonomy (first rule that fires wins)

```
livelock          turn limit hit → looped retries, never committed an action
transaction_handle  write/commit names unopened txn | opened never committed |
                    commit precedes writes | double commit
rejected_and_stuck  ≥1 off-schema call rejected AND fewer native actions than required
wrong_class       call routed through the wrong dispatcher/namespace
under_execution   fewer native actions than required, no rejection
over_execution    more native actions than required
wrong_arguments   right functions, wrong values
```

Explicit (first four) vs **silent** (last three). Silent ones end the episode
with the wrong action set and no error surfaced — the dangerous class, because
nothing in the harness complains.

Stable variant→failure mapping observed:
- fully merged → `rejected_and_stuck`
- transaction → `transaction_handle`
- schema discovery → `wrong_arguments` (silent)
- model-specific: some small models over-execute under nearly every variant;
  some livelock on any dispatcher.

## The schema-form gap

Re-run a variant with off-schema calls **executed** as the native action they
decode to, instead of **rejected**. The success delta is the schema-form gap:
how much of the loss is "right decision, wrong form".

- Concentrates on renaming/regrouping variants and earlier model generations.
- Fully merged: by far the largest gap — smaller models keep calling native
  tool names.
- Recovered episodes are mostly `rejected_and_stuck`.

## Operator → Hermes mapping

| Paper operator | Hermes exposure | Paper's verdict |
|---|---|---|
| `merge` / class dispatch | `tool_call` = `calls:[{name, arguments}]` (name becomes an argument) | worst case for closed models; −19 pts median |
| `schema_discovery` | `tool_search` → `tool_describe` → `tool_call` | hardest operator (0.07 base) |
| `reference_resolution` | `tool_describe` resolves name → schema | models score **at/above** native |
| `rename` (namespaced) | `mcp__<server>__{tool}` | harmless except tiny models |
| `rename` (opaque) | — | hurts small models only |
| `strip_desc` / `reorder` / `nest` | listing forms, arg order | ~0 effect |
| `transaction` | — | collapses most models |

Hermes's five listing forms (`full` / `names` / `mixed` / `groups` / `none`,
`tools/tool_search.py` line ~340) are already a per-tool-surface / class-level
arm implementation: `full`+`names`+`mixed` are tier 1, `groups`+`none` tier 2.

## Applying a variant to a Hermes tool_call

The bridge shape `tool_call(calls=[{name, arguments}])` is already a
class-dispatcher. To build an equivalent variant, change one thing at a time:

1. **Flatten → nested merge**: wrap `arguments` in a sub-object
   (`{"name": ..., "arguments": {"__args": {...}}}`) and see if the model
   still routes correctly. Paper: this is the change that cost every model
   19–73 points. Highest-value negative control.
2. **Opaque names**: rename `mcp__server__tool` → `fn_<hash>` in the listing
   only. Expect small-model degradation, large-model no-op.
3. **Strip descriptions**: remove the `description` field from the
   `tool_describe` payload. Paper says ~no effect — a good null result.
4. **Reorder arguments**: shuffle the `properties` order in the emitted
   schema. Paper says ~no effect — another null control.
5. **Semantic vs random merge grouping**: when the deferred catalog is large,
   compare grouping by server (semantic) vs. by hash (random). Semantic wins.

Run each as a separate arm of the existing `evals/core_tool_deferral/`
battery. Its `tasks.py` already has a programmatic grader per task and
`worker.py` runs real `AIAgent`s from pinned checkouts — swap the schema
emission between arms and keep the grader fixed.

**Grade in native-action space**, not in the variant's own vocabulary, or the
effect being measured is exactly what gets hidden.

## Reproducing the paper's method on a new harness

1. Normalize each invocation into an (operation, typed-args) **native action**.
2. Write a **decoder** from variant call form → native actions (may be
   many-to-one: arg order within a transaction shouldn't matter).
3. **Prove losslessness**: replay the gold trace through the variant, decode
   back, assert native actions match exactly. A perfect model must score 1.0 on
   every variant — the paper's validator caught 3 implementation bugs this way
   before any model was evaluated.
4. Score iff the multiset of decoded native actions equals the gold set.
5. Report the **spread** across variants, plus the failure-mode mix.

## Things that did NOT work (don't spend effort here)

- **Query-free probes** (likelihood of correct call sequence ρ=0.52;
  schema-compliance probe ρ=0.57) cannot rank schema difficulty. They omit
  the tasks, not just volume. Use ~100 real task queries instead.
- **SFT on native-only data** does not repair hard variants (schema discovery
  stayed at 0.02–0.05).
- **KL penalty on RL** destroys the repair (0.75 → 0.25).
- **Constrained decoding** only helps the fully-merged variant (+0.29);
  everywhere else ≈0.
- **More SFT data**: gains plateau around 1,000 colloquial traces; phrasing
  dominates volume.
- **Training for general schema robustness**: gains reach new *combinations* of
  trained changes, never new *kinds*.
