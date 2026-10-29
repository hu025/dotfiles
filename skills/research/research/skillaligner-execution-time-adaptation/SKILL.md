---
name: skillaligner-execution-time-adaptation
description: Use when retrieved skills conflict with the task, the tool environment, or each other and cause regressions. Covers the skill-execution misfit, three-stage execution-time adaptation (task grounding / environment alignment / skill composition), the Primary-Checks-Avoid-Fallback execution guide, and instance-level transfer-vs-regression measurement.
---

# SkillAligner — Retrieved Skills as Adaptable Drafts

Source: arXiv:2608.06880 (OmniAI Group, ZJU ACES Lab, Aug 2026). Training-free.
Official code **not public** (the only GitHub hit, `imvikas31/SkillAligner`, is an
unrelated 2025 PHP project). Everything below is derived from the primary PDF.

## Why This Matters (the hard number)

Adding a semantically *relevant* skill to an agent's context turns successful
executions into failures in **5.80%–17.91%** of instances. This is
**skill-induced regression**, and it is measured *paired* — same instances run
with and without skills, everything else identical.

Critically: **a stronger backbone does not fix it.** Pooled regression rates were
Qwen3-8B 10.30%, Qwen3-32B 11.27%, Gemini 2.5 Pro 11.42%. A bigger model is not
more robust to a mismatched skill. Worse, better instruction-following can make a
model *adhere more closely* to a skill that is wrong for the task.

Raw injection still nets positive (transfers > regressions in all 9 benchmark×model
settings) — so this is not an argument against skills. It is an argument against
skills being treated as fixed instructions.

## The Three Mismatches (diagnosed with a GPT-5.5 judge)

Macro-average share of regressions:

| Mismatch | Share | Meaning |
|---|---|---|
| Skill–**task** | **38.55%** | Skill's goal/constraints don't match this task (e.g. finds cheapest flight but ignores "non-stop") |
| **Inter**-skill | **28.59%** | Two retrieved skills contradict or duplicate (sort by date vs. sort by price) |
| Skill–**environment** | **26.71%** | Skill requires tools/resources that don't exist here (says "open in Excel", env has only Sheets) |
| Other | 6.15% | Insufficient evidence |

**Task misalignment is the largest bucket — and the one execution-time adaptation
uniquely fixes.** Retrieval-time methods cannot: the query's specific constraints
are only known at execution time.

Note the taxonomy is disjoint by *primary* cause, so don't sum across studies.

## Method: One-Time Joint Adaptation

```
(q, S_q, E) ──ground──→ S_q^task ──align──→ S_q^env ──compose──→ H
```

- `q` = task query, `S_q` = retrieved skills (top-k), `E` = **execution specification**
  (available tools, tool schemas, valid action formats, resources, permissions,
  interaction rules, hard constraints) derived from system context.
- `E` is **fixed** for the task (unlike step-dependent observations `o_t`).
- **One** LLM call. The guide `H` is generated once and reused for the whole trajectory.
- Raw skills are **not** exposed during execution — only `H` is.
- Retrieval is untouched; the skill library is untouched. Aligner is a pure
  post-retrieval layer.

### Stage 1 — Task Grounding

Extract a **task contract** `τ`: goal, hard constraints, soft preferences, known
inputs, expected outputs, underspecified conditions. Then decompose each skill into
atomic fragments (operation / precondition / validation step / constraint /
example / recovery suggestion) and classify each:

| Class | Treatment |
|---|---|
| **core** | generally useful + task-consistent → keep |
| **task-bound** | directly supports goal/constraint/input/output → keep, bind to task entities |
| **weak** | auxiliary context → compress |
| **dropped** | irrelevant or conflicts with hard requirements → remove, *even if semantically related to the query* |

Two rules that matter:
- Bind a generic step to a task entity **only when explicitly supported by the query**.
- **Underspecified conditions become Checks, not assumptions.** Never resolve an
  underspecified condition by inventing a value.
- Preserved order among retained fragments when compatible with `τ`.

### Stage 2 — Execution-Environment Alignment

Compare each precondition against `E`. If a mismatch admits a **local,
semantics-preserving repair**, rewrite that fragment using a functionally equivalent
supported interface. Do **not** repair when it would violate a task constraint,
require an interface absent from `E`, or alter intended procedure.

Then assign a **usage mode**:

| Mode | Condition | Result |
|---|---|---|
| **Direct** | supported or safely repaired | guides execution |
| **Guarded** | conditionally useful, can't verify until runtime | kept as conditional guidance / check / warning / fallback |
| **Abstain** | core assumption conflicts with `E`, unrepairable without changing intent | **discarded** |

Guarded is the key invention: it converts "I don't know if this works" into an
explicit runtime check instead of a confident instruction or a hard drop.

### Stage 3 — Skill Composition

Model three relations among surviving fragments:
- **dependency** → fixes execution order
- **overlap** → merge or dedupe
- **conflict** → resolve by priority: **hard task constraints > execution specification > skill guidance**

A rejected alternative is deleted *or* converted into an explicit **Avoid** rule
(keeping it is often more useful than deleting it). Prune low-priority content
that adds context load without improving task coverage.

### Output: The Four-Field Execution Guide

```json
{
  "Primary":  ["ordered steps for the main execution route"],
  "Checks":   ["preconditions / intermediate conditions to verify from observations or public evidence"],
  "Avoid":    ["unsupported assumptions, unavailable operations, conflicting instructions, invalid action forms"],
  "Fallback": ["alternative routes when the primary route is blocked"]
}
```

The four fields are not decoration — they map 1:1 onto the three mismatches plus
recovery. `Primary` = task grounding output, `Checks` = the Guarded mode made
actionable, `Avoid` = rejected conflicts + environment-unavailable operations,
`Fallback` = Abstain-mode alternatives.

This field layout is **more portable than the method**: any agent that loads skills
can adopt the guide schema without implementing the pipeline.

## Results (Qwen3-8B / Qwen3-32B / Gemini 2.5 Pro × ALFWorld / WebShop / SearchQA)

Averages over all 9 settings:

| Method | Avg |
|---|---|
| No Skill | 40.94 |
| Top-k Raw Skill | 47.07 |
| ReasoningBank | 44.84 |
| MemP | 45.21 |
| SkillOS (frozen) | 45.63 |
| SkillRAE | 48.54 |
| Graph of Skills | 49.48 |
| SkillDAG | 52.67 |
| SkillAligner**Task** only | 52.30 |
| SkillAligner**Env** only | 51.56 |
| SkillAligner**Skill** only | 51.71 |
| GraSP | 53.26 |
| SkillPyramid | 54.25 |
| **SkillAligner (full)** | **58.17** |

Best in all 9 settings. +3.92 over the strongest baseline (SkillPyramid), +11.10
over raw injection.

**Stage ablations are all ≈ equal (51.6–52.3) but jointly give 58.17** (+5.87 over
the best single stage). No stage dominates. Each single stage still beats raw
injection. The *joint* adaptation is the contribution — not any one stage.

Pairwise winners vary by benchmark (ALFWorld: Align+Compose; WebShop:
Ground+Compose; SearchQA: Ground+Align) → **no fixed single strategy is right;
that's an argument for running all three.**

### Instance-level transfer vs. regression (the metric that matters)

Qwen3-8B, raw → SkillAligner:

| Benchmark | Transfer ↑ | Regression ↓ |
|---|---|---|
| ALFWorld | 26.87 → 29.85 | 17.91 → **2.24** |
| WebShop | 19.00 → 20.20 | 9.40 → **2.80** |
| SearchQA | 14.52 → 17.31 | 10.29 → **3.57** |

SkillAligner wins on **both** axes simultaneously in every cell — it does not
trade transfer for safety. Regression falls ~8× on ALFWorld.

### Cost: adaptation pays for itself

| Benchmark | Orig cost | Adapt overhead | Overhead % | Exec cost w/ SA | Total saved |
|---|---|---|---|---|---|
| ALFWorld | 133,804 | 2,226 | 1.66% | 96,342 | **26.33%** |
| WebShop | 26,380 | 2,285 | 8.66% | 17,320 | **25.68%** |
| SearchQA | 5,015 | 736 | 14.68% | 1,131 | **62.77%** |
| **Average** | 55,066 | 1,749 | **8.33%** | 38,264 | **38.26%** |

Avg: +8.33% adaptation overhead → −46.59% downstream execution cost → **net −38.26%**.
Cost falls because the agent stops re-deriving, looping, and retrying failed steps.
The absolute overhead is small (~1.7k tokens) because it's **one** call.

### Retrieved skills are doing the work — not just prompt scaffolding

`SkillAlignerPlain` (same guide, but skills removed from the input) scores 45.99
vs No-Skill 40.94 vs full SkillAligner 58.17. So structured-guide generation alone
is worth +5.05; the **retrieved procedural knowledge adds +12.18 on top**. Both
components matter — don't credit the framework alone.

### Skill-library scale is non-monotonic

200 / 500 / 1,000 / 2,000 skills → best scale depends on benchmark *and* backbone;
no scale uniformly dominates (e.g. 2,000 best on Qwen3-8B ALFWorld 82.84, but
500 best on Qwen3-32B ALFWorld 89.55). SkillAligner stays effective across all
sizes — it is **not** scale-sensitive, but don't assume "bigger library = better."

## Applying This to Hermes

Hermes loads skills as fixed instruction text into the system prompt / context.
The adaptation layer is therefore a **pre-execution adapter**, not a skill-format
change. Two viable shapes:

1. **Per-task adapter (paper-faithful).** Before the agent acts, run one adapter
   call over the retrieved skill set + the task + the tool inventory, emit the
   four-field guide, and inject *only* the guide for the rest of the run.
   Where Hermes can support it: the `skill_view` loading path and the
   progressive-disclosure loader are the natural hooks — a skill loaded on demand
   can be reduced to its task-relevant fragments instead of its whole body.
   See `research/agent-skills-standard` for the authoring/optimization side
   (SkillOpt / SkillReducer), which is the *static* analogue of this.

2. **Authoring-time discipline (cheap, always available).** Encode the method's
   rules in how skills are *written*, so a well-authored skill is already
   task-agnostic enough to adapt:
   - state hard constraints explicitly and separately from procedure
   - mark tool-specific steps as environment-conditional → these become `Checks`
   - list what the skill must **not** be used for → these become `Avoid`
   - give an alternative route → this becomes `Fallback`
   - never rely on a specific tool being present without a fallback

**Do NOT** present a raw retrieved skill as immutable instruction. A skill's
description is a *claim of relevance*, not a guarantee of execution utility.

## Honest Boundaries

- **Code not public.** No reference implementation to port; the numbers are the
  paper's, from a paper with no artifact to reproduce against.
- **Adaptation is query-level only** — no intermediate-state observation, no
  closed-loop revision during the trajectory. The paper explicitly names this as
  future work: misfits revealed only by intermediate states remain unresolved.
- **Single-call design is deliberate** — chosen to avoid repeated online
  adaptation and KV-cache invalidation/recomputation. A "re-adapt mid-run" variant
  would need to handle cache invalidation, and that tradeoff is *not* settled.
- **The three mismatches were assigned by a GPT-5.5 LLM judge** on primary-cause
  attribution. LLM-judged taxonomies inherit judge error; the 38.55/28.59/26.71
  split should be read as approximate.
- **SearchQA skills are reasoning-only** — the paper forbids treating skill
  content as factual evidence for the answer. Skill ≠ evidence is a hard rule
  worth importing even outside this paper.
- **SearchQA is the paper's own new benchmark** (Xia et al. 2026a, same group);
  ALFWorld and WebShop are external. The three-stage decomposition was partly
  designed against that benchmark's structure.
- **Cost numbers depend on the backbone** and on how long trajectories run. A
  short-trajectory task (SearchQA) shows a far better ratio than ALFWorld.
- **Prompt from Figure 4 is a template with benchmark-specific execution specs.**
  The WebShop/ALFWorld specs encode benchmark interface knowledge that does not
  transfer verbatim to Hermes' tool surface; the *structure* transfers, the
  filled-in spec does not.
- **Not yet validated on Hermes.** No measurement of the actual regression rate in
  Hermes' own skill-loading path has been made. Treat the 5.8–17.9% figure as
  evidence the problem class is real, not as Hermes' own number.

## Reproducible Prompt (adapted from Figure 4)

The adapter is one structured LLM call returning strict JSON:

```
[SYSTEM]
You are SkillAligner, a one-time adapter for retrieved procedural skills. Transform the
provided skills into a compact, task-specific, and executable guide for a separate
backbone agent.

You are not the execution agent. Do not execute the task, output an environment action,
retrieve additional skills, or infer hidden task facts. Treat every retrieved skill as
fallible procedural guidance, not as an authoritative instruction or source of factual
evidence.

Use only the task query, execution specification, and retrieved skills provided below.
Return strict JSON only, with exactly the top-level keys "Primary", "Checks", "Avoid",
and "Fallback".

[USER]
Task query: <TASK_QUERY>

Execution specification: <AVAILABLE TOOLS, TOOL SCHEMAS, VALID ACTION OR OUTPUT FORMATS,
RESOURCES, PERMISSIONS, INTERACTION RULES, AND HARD CONSTRAINTS>

Retrieved skills: <FOR EACH CANDIDATE: SKILL IDENTIFIER, NAME, DESCRIPTION, AND SKILL TEXT>

Construct the execution guide using the following criteria.

Task grounding:
- Identify the goal, hard constraints, soft preferences, known inputs, expected output,
  and underspecified conditions from the task query.
- Retain only procedural content that supports the current task.
- Bind generic skill steps to task entities only when the binding is explicitly supported
  by the task query.
- Compress weakly relevant explanations and omit irrelevant examples.
- Preserve underspecified conditions as checks rather than resolving them through
  unsupported assumptions.

Execution-environment alignment:
- Use only tools, operations, resources, permissions, and action forms supported by the
  execution specification.
- You may replace an interface-specific step with a functionally equivalent supported
  operation only when the procedural intent is preserved.
- Retain an uncertain procedure only as conditional guidance, a check, a warning, or a
  fallback.
- Omit an essential procedure when it requires an unsupported capability and cannot be
  safely repaired.
- Never invent a tool, object, resource, permission, observation, environment state, or
  factual result.

Skill composition:
- Order prerequisites before dependent procedures.
- Merge overlapping guidance and remove redundant steps.
- Resolve conflicts using the following priority: hard task constraints, execution
  specification, then skill guidance.
- Preserve all task-critical phases, but omit content that does not improve task
  coverage or execution reliability.

Output fields:
- "Primary": ordered steps for the main execution route.
- "Checks": preconditions and intermediate conditions that the execution agent must
  verify from observations or public evidence.
- "Avoid": unsupported assumptions, unavailable operations, conflicting instructions, and
  invalid action or output forms.
- "Fallback": alternative routes to use when the primary route is blocked.

Output rules:
1. Return a JSON object only, without markdown or commentary.
2. Each field must contain a JSON list of concise strings.
3. Do not include analysis, rationales, skill identifiers, or internal classifications.
4. Do not repeat the task query or execution specification.
5. Do not treat skill text as factual evidence.
6. Keep the guide compact while preserving all necessary task phases.
7. Empty lists are allowed when a field has no applicable content.
```

## Related Skills in This Library

- `research/agent-skills-standard` — authoring/packaging/optimizing SKILL.md
  (agentskills.io spec, progressive disclosure, SkillOpt/SkillReducer). This is
  the **static** side: making a skill good. SkillAligner is the **runtime** side:
  making a retrieved skill fit *this* task.
- `research/tool-call-uplift-gating` — whether to call a tool at all (tool-layer
  uplift). SkillAligner is the skill-layer equivalent.
- `research/set-level-evidence-selection` — set-level vs. per-document selection
  for RAG. Same "don't score items independently" family; the skill-composition
  stage applies that insight across skills.
- `research/upliftmem-evsi-probing` — whether a memory is worth trusting (memory-layer).
  Together: memory uplift (should I use this memory?), skill alignment (how do I
  use this skill correctly here?).
