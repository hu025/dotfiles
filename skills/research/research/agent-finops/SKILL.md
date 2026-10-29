---
name: agent-finops
description: Use when attributing, budgeting, or cutting LLM/agent token spend. Covers per-agent cost attribution, shared-cost amortization, kill switches, and prompt-cache economics. Trigger on: cost attribution, token spend, budget cap, prompt cache, FinOps, cost per agent run, why is the bill high.
---

# Agent FinOps — cost attribution & budget control

Governance for token spend inside agent loops. Visibility is not control; the
signal must close the loop inside the request path.

## The one governing fact

Unit inference price falls ~10x/year (LLMflation), yet total spend rises.
This is Jevons paradox, not price. **The lever is governance of consumption,
not renegotiating price.** Do not waste time shopping for cheaper tokens when
an uncapped agent loop is the actual problem.

## The attribution rule

> Attribute private lines to their owner. Split shared lines across every
> consumer. Then confirm the parts sum back to the total.

Any scheme whose per-task/per-user/per-agent views disagree has a double-count
or an orphan hiding in it. The reconciliation check catches both.

### Tag at the call site, not in the invoice

Every request must resolve to a 4-tuple **before** it reaches the provider:

| Dimension | Tag | Mechanism |
|---|---|---|
| Member | which engineer/team | per-member virtual key (no shared secrets) |
| Agent | which agent/run | session-id request header |
| Department | cost center | workspace mapping / department key |
| Feature | product surface | free-form request tag |

Add `prompt_version` and `deployment` if you run evals or A/B tests — those
are the two dimensions that let you answer "was v3 worth it".

### The two traps

**Cache-attribution trap.** The worker that *writes* a shared cache pays the
write premium; readers pay a discount. Three subtasks doing *identical* work
then bill 1.93x apart on the raw usage object. That spread is a pure ordering
artifact — rerun in a different order and a different subtask carries the fee.
*Fix:* amortize the write fee across all readers. Verified reproduction:

```
worker A (wrote cache) $0.03575 | worker B (read) $0.01850  -> 1.93x spread
amortized per subtask              $0.02425                 -> identical
cache-write line $0.01875 = 25.8% of worker spend  <- mis-parked, not rounding
```

**Orphaned-overhead trap.** A judge/combiner/planner that spans N subtasks maps
to no single task. Parking it under its own role under-prices every task badly
(a judge at 19.6% of the bill → every task under-priced by ~2/3 of truth).

### Where the money actually goes

Two independent studies converge on the same shape:

- **Coordinator agents (planner/router) consume 40–60% of total budget** in
  multi-agent systems — not the workers doing the actual work.
  (Salim et al., "Tokenomics", arXiv:2601.14470)
- In a measured 3-agent pipeline: planner 51–58%, judge 19–24%, workers 22%.
- **Input tokens dominate the bill, even with caching enabled.** Optimizing
  output length is the wrong lever; shrink what you send *in*.
- Same task varies **30x** in total tokens across runs, with **zero
  correlation to accuracy**. You cannot predict cost from task description —
  only run-level attribution tells you anything.
- LLMs underestimate their own token use (max r=0.39). Never trust a model's
  "this will take about N tokens".

## Roll-ups to build, in this order

1. **Cost per user per day** — baseline; spikes trigger first investigation.
2. **Cost per feature** — is PR review costing more than code generation?
3. **Cost per agent run: median + p99** — median $0.50 with p99 $12 means
   your task scoping is broken. Variance is where budget surprises hide.
4. **Cost per successful eval** — north star for eval-driven development.
5. **Cost per customer** — the gross-margin line for B2B multi-tenant.

Run attributed monitoring for 4–6 weeks *before* hardening any limit.
Teams that set caps with no baseline set them either too tight (breaks normal
work) or too loose (catches nothing).

## Enforcement: three tiers, not one

| Tier | Mechanism | Behavior |
|---|---|---|
| Soft alert | rolling per-feature baseline | fires investigation trigger, **never pages** |
| Hard cap | per-user daily ceiling at gateway | 429, scoped to that key only |
| Kill switch | per-run token/tool-call/span-depth ceiling | hard stop the runaway run |

**Degrade, don't kill.** Near budget, downshift the model tier, shrink context,
or serve a cached answer. A deny policy that takes production offline is worse
than the overspend you were preventing.

Always cap three things on an agent run: **total tokens**, **tool-call count**
(50 tools without a result = something is wrong), and **span depth**
(stop agents spawning agents spawning agents).

## Security: token amplification is a threat, not a variance

- **Denial-of-wallet**: individually valid, token-maximizing requests that burn
  your budget. Monitor tokens/user and tokens/key with anomaly detection.
- Runaway reasoning loops are the same class of failure.
- Treat it as an owned security risk with an alert, not a month-end finance
  review. A single un-gated path (a dev holding a raw provider key) is a hole
  no downstream policy can close.

## Economics of the levers (use before building anything)

| Lever | Effect | Note |
|---|---|---|
| Prompt caching | cached input ~90% discount | vendor-side prefix reuse; write costs a premium (1.25x) |
| Batch API | flat 50% discount | **stacks with caching** |
| Semantic cache | up to 68.8% fewer calls | keyed by embedding similarity |
| Model cascades / routing | frontier quality at a fraction of cost | preference-trained routers capture most savings, small quality gap |

Enable caching + batch **before** any model project, not after.

## Compliance driver

EU AI Act Article 12 took full effect **2026-08-02**: you need an audit
trail of model calls per user, per system, per time period. Attribution baked
in now is a compliance requirement, not just cost hygiene.

## Pitfalls

- Do not report totals. Total token volume is a vanity metric that rises with
  adoption; budget in unit economics (cost per resolved task).
- Do not trust per-task numbers that don't reconcile to the invoice.
- Do not attribute shared-cache writes to whoever happened to run first.
- Do not let a coordinator/router agent silently eat 50%+ of budget.
- Do not set a limit without a measured 4–6 week baseline.
- Do not alert on soft-threshold breaches by paging anyone.

## References

- Salim et al., "Tokenomics", arXiv:2601.14470 — coordinator agents 40–60% of budget
- Bai et al., arXiv:2604.22750 — 30x run-to-run variance, no accuracy correlation
- Gartner (Mar 2026) — agentic workloads 5–30x chat cost per task
- tmls.nyc/research/agentic-finops — autonomous FinOps controller architecture
- FinOps Foundation 2025 — AI spend governance doubled 31%→63% of practitioners