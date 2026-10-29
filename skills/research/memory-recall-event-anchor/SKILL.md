---
name: memory-recall-event-anchor
description: Use when tracing agent memory recall for attribution.
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags:
      - memory
      - provenance
      - attribution
      - tracing
      - opentelemetry
    related_skills:
      - research/research/skill-uplift-attribution
      - research/research/upliftmem-evsi-probing
---

# Memory Recall Event Anchor

Instrument a self-hosted agent's memory recall so downstream attribution can answer:
**which memory entry was injected, when, and did it help.**

## When to use this

- Extending an existing per-skill execution-uplift attribution system to cover memory recall.
- Adding provenance/tracing to memory injection.
- Choosing an event schema, a trace standard, or a counterfactual method.

## The core problem

Skills have an event anchor (`tool_name='skill_view'` in a `messages` table). **Memory recall
usually does not** — the provider interface returns only a *string*, so the injected entry
IDs are lost at the injection boundary.

Fix: capture the IDs at the boundary, not downstream.

## Step 1 — Anchor at the boundary (the essential change)

Three insertion points, depending on how memory is injected:

| Injection path | Where | Carrier |
|---|---|---|
| Built-in file memory | the render/format function for the memory block | system prompt |
| External provider recall | the manager's `prefetch_all()` | user message |
| Store query (vector/DB) | the provider's `prefetch()` | user message |

Change the provider contract to carry provenance, not just text:

```python
@dataclass
class MemoryEntry:
    id: str                      # stable, server-derived
    content: str
    score: float | None = None
    metadata: dict = field(default_factory=dict)

@dataclass
class MemoryRecall:
    provider: str
    text: str                    # exactly what gets injected
    entries: list[MemoryEntry]
```

**Backwards compatibility:** do NOT change the existing `prefetch(query) -> str` signature
in place — third-party providers implement it. Add a new method
(`prefetch_with_provenance()`) and have `prefetch()` delegate to it.

## Step 2 — Persist one event row, parallel to the skill event

Reuse the same table that already stores skill/tool events. Shape:

```
role='tool', tool_name='memory_recall', tool_call_id=<id>, timestamp=<REAL>, session_id=<sid>
content = {"success": true, "provider": "...", "query": "...",
           "entries": [{"id": "...", "content": "...", "score": 0.87, "metadata": {...}}],
           "count": 3}
```

No schema migration needed if the table already has `tool_name`, `tool_call_id`,
`timestamp`, and a JSON `content` column.

## Step 3 — Emit a trace span (optional but standard)

**OpenTelemetry GenAI has a first-class Memory span.** Use `gen_ai.operation.name =
'search_memory'`, span kind `CLIENT` (or `INTERNAL` for in-process stores).

Exact attribute keys (verified against the spec's attribute registry):
- `gen_ai.operation.name` (**Required**) — `search_memory`
- `gen_ai.memory.record.id` — single-record ops
- `gen_ai.memory.store.id` — which store
- `gen_ai.memory.record.count` (Recommended) — how many entries returned
- `gen_ai.provider.name`
- `gen_ai.memory.query.text` (**Opt-In**) — the query; gated on explicit user opt-in
- `gen_ai.memory.records` (**Opt-In**) — array of records; MUST follow the JSON schema
  `MemoryRecord` = `{content (required), id, score, metadata}`

**Privacy rule from the spec:** `gen_ai.memory.query.text` and `gen_ai.memory.records`
"SHOULD NOT capture this attribute by default. Capture SHOULD be gated by an explicit user
opt-in." → **emit IDs and counts by default; content only behind opt-in.** Redact the
query with the same redaction used for the provider-bound query.

There is **no** `gen_ai.memory.type` attribute — store kind belongs in
`gen_ai.memory.store.id` or in the record `metadata`.

For the retrieval half: `gen_ai.operation.name = 'retrieval'`, span name
`{operation} {gen_ai.data_source.id}`, `gen_ai.retrieval.documents` (Opt-In) with
`RetrievalDocument` = `{id, score}` (**no content field** — that's the difference from
`MemoryRecord`).

For Phoenix/Arize UI, also emit OpenInference's `retrieval.documents` +
`document.id` / `document.score` / `document.content` / `document.metadata` on the same
span. For Langfuse, the OTel endpoint maps spans to observations for free.

## Step 4 — Inline provenance header (optional, model-visible)

Precedent: OpenClaw ships `<!-- ctx:provenance source="..." injected_at="..." volatile="..." -->`.

Field names to reuse: `source`, `injected_at`, `volatile`. For memory, add the
memory-specific `query` and `retrieved_at`.

**Two hard rules:**
1. **Generate tags from server-side state, never from entry content.** An entry containing
   `-->` could break out of the comment and inject instructions. Use the server-computed
   entry ID/fingerprint, never raw text, inside a tag.
2. **Never `.format()` memory text.** Use plain `replace("{context}", context)` — string
   formatting interprets `{`, `}`, `%` in untrusted content.

**Prefer the HTML-comment form** over a JSON manifest: it is inert for the model and
costs far fewer tokens. A 50-entry manifest of 40-char IDs is ~2 KB every turn.

**Declare injected tags in one registry** so every consumer (compaction, memory retain,
chat display, output scrubber) reads one list instead of each re-deriving its own
hardcoded list. Duplicate strip-vs-inject registries are the documented cause of
"silent data leakage (observed in the wild)".

## Step 5 — Did it help? (counterfactual methods)

| Method | Model calls | Measures |
|---|---|---|
| Leave-one-out | N | Δ when entry i is dropped |
| Randomized ablation + LASSO | 64 | per-entry causal contribution |
| **Logit-difference** | **2** | Δ logprob of answer tokens with/without entry |

**ContextCite** (arXiv:2409.00729, `github.com/MadryLab/context-cite`) is the reference
method: partition context into sources → build `num_ablations=64` random masks keeping each
source with prob `ablation_keep_prob=0.5` → re-generate → collect token-level logit probs →
aggregate with `logsigmoid` (log-odds) → fit `LassoRegression(lasso_alpha=0.01)` over the
masks → `weight[i]` is source i's attribution. Score semantics: `log(10)` ≈ a 10× drop in
probability. Cost is the problem (64 calls).

**Practical recommendation for a self-hosted agent:** implement the **2-call logit-difference**
variant (same forward pass shape, same aggregation, 2 calls instead of 64) on a sampled
subset of turns. And do the **zero-rollout proxy** first: pair the anchor with the human's
reaction to the reply that followed — a recall preceding a correction is strong *negative*
evidence. This needs only the anchor, which is why the anchor is the prerequisite.

For relevance scoring (not causality), RAGAS has `IDBasedContextPrecision` and
`IDBasedContextRecall` which compare **IDs** directly (`retrieved_context_ids` vs
`reference_context_ids`) — exactly what an anchor enables. `ContextUtilization` compares
retrieved contexts against the *generated response* (no gold reference needed).

## Pitfalls

- **Prefix-cache safety.** If the memory block is frozen at load time for provider prompt
  caching, changing its rendered text invalidates the cache on every memory edit. Put
  per-turn manifests in the non-cached carrier (user-message sidecar), not in the frozen
  system-prompt block.
- **System-prompt injection risk.** Memory recalled into the *system prompt* occupies the
  highest-privilege slot. Prefer the provider's data channel (user message / tool result)
  for untrusted content, and treat "recall into system prompt" as a security finding.
- **Stable entry IDs.** Derive the ID from the entry *text* (e.g. `sha256(text)[:12]`), not
  from its position: text-derived IDs are stable across edits of other entries, and a
  rewritten entry correctly fails to match an old ID (no false attribution). Include the
  source in the ID so identical texts in different stores stay distinguishable.
- **Don't put full manifests inline.** Keep the complete list in the DB event; inline only a
  count + hash, or a truncated top-k.

## Prior art to cite

- **Zep** (`zep-langgraph`): `create_zep_pre_model_hook()` → returns context via the
  `llm_input_messages` key so it is re-fetched fresh each turn, not baked into history.
  `context_builder: async (ctx: ContextInput) -> str | None` where `ContextInput` bundles
  `zep`, `user_id`, `thread_id`, `user_message`. Raises are logged and treated as `None`.
  Explicit security guidance: keep retrieved context out of privileged instructions.
- **LangGraph**: `create_react_agent(pre_model_hook=…)`; return under `llm_input_messages`
  (LLM-input only) vs `messages` (overwrite persisted state). LangMem's
  `SummarizationNode(output_messages_key="llm_input_messages")`.
- **Cognee**: `get_memory_provenance_graph(include_memory=True)` → `(nodes, edges)`; the
  `mentions` edge links a source file to each memory node extracted from it.
- **Letta**: `BlockResponse` = `{id, value, label, limit, metadata, tags}`;
  `PassageSearchResponseItem` = `{passage, score, metadata}` — maps 1:1 onto `MemoryRecord`.
- **Mem0**: `search(query, filters=…)` → `{"results": [{id, memory, user_id, categories,
  score, created_at, …}]}`.

## Verification checklist

Before claiming this works, confirm against the live system:
- The anchor event is queryable in the same store as the skill/tool events.
- Entry IDs in the event resolve back to real entries (round-trip a fingerprint).
- Content is NOT captured unless opt-in is enabled.
- A provenance tag containing hostile entry text cannot break out of its fence.
