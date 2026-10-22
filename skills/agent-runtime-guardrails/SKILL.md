---
name: agent-runtime-guardrails
description: Runtime defense layers for tool-calling LLM agents.
---

# Agent Runtime Guardrails

Runtime defense architecture for tool-augmented LLM agents. Complements
`llm-security` (offline red-teaming/audit) — this skill is the **online enforcement** side.

## When to Use

- Designing or reviewing runtime defense for an agent that calls tools
  (terminal, HTTP, MCP, browser, file writes).
- Choosing a guardrail framework, or deciding whether you need detection vs.
  validation vs. governance.
- Hardening a local agent (Hermes-style) against indirect prompt injection.
- NOT for offline red-teaming / OWASP audits — use `llm-security` for those.

## The core insight

**Detecting an unsafe answer is not the same as preventing an unsafe action.**
An output filter catches the response after the agent already sent the email,
deleted the file, or exfiltrated the token. Guardrails must sit at every
**boundary**, and the boundary that actually matters is the **tool-call edge**.

Failure taxonomy — pick the control that matches the job:
- *"Someone will trick it"* → **detection** (injection classifier)
- *"It will say/return the wrong thing"* → **validation** (output validators)
- *"It will **do** something it shouldn't"* → **governance** (tool-call authorization)

A classifier can reject an unsafe answer and still leave the agent
over-permissioned. Both matter.

## The seven control layers

| # | Layer | Protects | Representative techniques |
|---|---|---|---|
| 1 | Input rails | User text, tool returns, retrieved chunks | Injection detectors, jailbreak classifiers, PII redaction, spotlighting |
| 2 | Output rails | Anything leaving toward user/downstream | Content classifiers, schema/JSON validation |
| 3 | Dialog / topic rails | Conversation-level behavior | Colang flows, canonical-form matching, refusal templates |
| 4 | **Tool / action rails** | **What the agent is allowed to DO** | Least-privilege scopes, allowlists, **argument schema validation**, HITL |
| 5 | Retrieval / memory rails | What gets pulled from RAG + long-term memory | Source provenance, signed chunks, write-time moderation |
| 6 | Multi-agent comms rails | Messages between agents | Signed inter-agent messages, capability-based delegation |
| 7 | Verification / oversight | The plan as a whole | Critic agents, self-reflection, task-alignment checks |

Two principles recur in every recent paper and vendor guide:

1. **Defense-in-depth, no single point of trust.** Anthropic's "Swiss cheese"
   model — each layer has holes, but they don't line up. Stacking specialized
   detectors has been reported to drop ASR from ~30% to ~0%.
2. **Treat all external content as untrusted by default.** The agent's
   reasoning context *is* the security boundary. Anything crossing it from
   outside must be labeled, sanitized, or sandboxed.

## Indirect injection: three channels

Tool output is concatenated into conversation history as **trusted observations**.
That is the fundamental flaw. Adversaries exploit it via:

1. **Web/local content injection** — adversarial instructions in any retrieved
   page, document, or search result.
2. **MCP tool poisoning** — malicious instructions in tool *description metadata*
   at registration time, steering tool selection before any call happens.
3. **Skill file injection** — adversarial instructions semantically woven into
   legitimate behavioral guidance in public skill repos.

Memory/RAG indexes are a **persistent** attack surface: one poisoning affects
every future session.

## 2026 framework landscape

### Meta LlamaFirewall — the reference open-source design
Three guardrails, unified policy engine, **used in production at Meta**.
- **PromptGuard 2** — DeBERTa-based jailbreak detector; 22M (xsmall) and 86M
  (mDeBERTa-base) variants. Fast, runs on user prompts *and* untrusted tool output.
- **AlignmentCheck** — few-shot chain-of-thought auditor; inspects the agent's
  *reasoning* for goal hijacking. First OSS guardrail to audit CoT in real time.
- **CodeShield** — online static analysis (Semgrep + regex) for coding agents,
  syntax-aware across 8 languages.

Notable self-documented weakness: AlignmentCheck is itself injectable. Mitigations:
restrict input to the agent's CoT/actions (exclude raw tool output), and
pre-scan with PromptGuard before the auditor ever sees it.

### Agent-Aegis — governance abstraction layer (MIT)
One policy across **12 frameworks** via auto-instrumentation:
`pip install agent-aegis` → `aegis.auto_instrument()` (or `AEGIS_INSTRUMENT=1`).
Hooks into LangChain, CrewAI, OpenAI Agents, Google ADK, Pydantic AI, Anthropic,
LiteLLM, LlamaIndex, Instructor, DSPy, MCP, httpx, Playwright.

Distinctive primitives worth stealing conceptually:
- **Tripartite `ActionClaim`** — every tool call splits into **Declared**
  (agent-authored, *untrusted*), **Assessed** (guard-computed), and **Chain**
  (delegation). This structural separation is what makes *cosmetic alignment*
  detectable — an agent that declares low impact but the guard assesses high
  impact is provably lying.
- **Justification Gap** — 6-dimensional asymmetric scoring,
  `per_dim = max(0, assessed − declared)`. Escalate above 0.15, block above 0.40.
  *Under-reporting* is the violation, not the raw risk level.
- **Selection Audit** — audits what the agent **excludes**, not just what it picks.
  A model that "helpfully" omits risky options is exerting selection power.
- **Monotone Trust Constraint** — delegated agents cannot escalate their own
  authority; trust must be non-increasing along the delegation chain.

Lifecycle: Scan → Instrument → Policy CI/CD → Runtime → Proxy → Audit.
Default guardrails: injection (13 categories, 109 patterns, 9 languages),
PII (13 categories), prompt-leak, toxicity, MCP STDIO injection
(JSON-RPC injection, frame concatenation, unicode escape bypass).
Deterministic regex — no LLM calls, no network. ~2.65ms cold / <1µs warm.

### ClawGuard — deterministic tool-call boundary enforcement
Shifts defense from *alignment-dependent* to *deterministic and auditable*.
- **Pre-session rule induction** — derives task-specific access constraints
  `R(task)` from the user's stated objective *before* the first tool call, so
  the rule set is uncontaminated by adversarial content. No per-deploy hand rules.
- **Per-call enforcement** — Content Sanitizer (redact secrets in args and
  in returned content before it enters history), Rule Evaluator over tool
  invocations / local paths / outbound destinations, Skill Inspector with
  mandatory user confirmation before first execution, and an Approval Mechanism
  routing ambiguous verdicts to the user.

Key idea: enforcement becomes **task-specific, not deployment-wide**. Instead of
"allow reads anywhere in the project dir," constrain to what the current task needs —
attack surface shrinks in proportion to task scope.

### Bulwark — five-layer compliance-oriented pipeline
Sanitizer (strips HTML/Unicode/bidi) → Injection Detector (22 regex signatures,
severity-weighted, <5ms, optional DeBERTa blend) → Compartmentalized RBAC
(role × tool, default-deny on unknown) → Human Gate (async webhook/Slack/email
approval) → Encrypted Audit Trail (AES-128-GCM). MCP-native.

### Others
- **Vigil / Rebuff** — YARA rules + transformer classifier + vector-DB
  similarity to known attacks + **canary words planted in the system prompt**
  to detect leakage.
- **agent-runtime-security** — `shadow` / `warn` / `enforce` rollout modes and a
  YAML/JSON policy file; good pattern for shipping guardrails **without
  breaking prod on day one**.

## Architectural (non-classifier) defenses

Classifiers are probabilistic. These are structural:

- **Dual-LLM** — a *Privileged* LLM that can call tools never sees untrusted text;
  a *Quarantined* LLM sees the text but cannot call tools. Privileged side only
  receives typed, structured output.
- **IPIGuard** — plan a Tool Dependency Graph from the user request *first*,
  then constrain execution to that graph. Untrusted tool output cannot introduce
  new tool calls.
- **Task Shield** — evaluate every proposed action against the user's stated task;
  block anything off-task even if the underlying request looks benign.
- **AgentSpec** — DSL of triggers/predicates/enforcement; rules auto-generatable by
  a strong model. Millisecond overhead.
- **AgentSafe** — capability-scoped sandboxes via syscall filtering, API-scoped
  keys, network allowlists; machine-readable and version-controllable.
- **ceLLMate** — browser-agent sandbox interposing on HTTP requests and enforcing
  a "sitemap" policy at the browser layer, agnostic to agent internals.
- **AgentSentry** — models multi-turn injection as "temporal causal takeover" and
  localizes *which earlier tool output* caused the current bad action, enabling
  targeted context purification instead of killing the whole session.

## Applying this to Hermes

Concrete hardening for a local agent with terminal + web access:

1. **Classify every tool by blast radius.** Read-only (web_search, file read) vs
   mutating (terminal, file write, send). Only mutating tools warrant a HITL gate.
2. **Terminal is the real perimeter.** Treat any web-derived or file-derived string
   that reaches a shell command as untrusted input. Never interpolate raw external
   content into a command line.
3. **Skill files are untrusted content.** Installing a third-party skill is
   equivalent to executing third-party code — review before enabling, and treat
   any newly added skill as a supply-chain event (maps to LLM03).
4. **Scan before delegation.** Subagents receive tool output too; injection rides
   through delegation. Validate untrusted content *before* it enters a child's
   context.
5. **Keep an append-only audit** of tool calls with declared-vs-actual arguments —
   the Declared/Assessed split from Aegis is cheap to implement and catches a
   whole class of "helpful misalignment."
6. **Roll out progressively** — start in `shadow` mode (log what *would* be
   blocked), measure false positives on real traffic, then promote to `enforce`.
   Never ship a blocking rail on day one.
7. **Measure separately.** Report ASR/interception and FPR/utility as two numbers.
   Never blend them into a single F1 — a rail that blocks everything scores 1.0
   on ASR and is useless.

## Selection guide

| Need | Reach for |
|---|---|
| Self-hosted injection classifier, Python | NeMo Guardrails or Agent-Aegis |
| Production-grade jailbreak detection, willing to use SaaS | Lakera Guard / Bedrock Guardrails |
| Tool-call governance across many frameworks | Agent-Aegis |
| Reference architecture, CoT auditing, code safety | Meta LlamaFirewall |
| Deterministic task-scoped tool boundary enforcement | ClawGuard |
| Compliance evidence out of the box | Bulwark |
| Shadow-mode gradual rollout | agent-runtime-security |

Most production stacks **combine** two or three — one hosted detector plus one
framework for your own rules. There is no single winner; there is a stack.
Note LLM Guard (Protect AI) was **archived in July 2026** — treat as frozen.
Guardrails AI was acquired by Harvey (Sept 2026); OSS future unclear.

## References

- https://github.com/meta-llama/llama-firewall
- https://arxiv.org/html/2505.03574v1 (LlamaFirewall)
- https://github.com/Acacian/aegis
- https://github.com/Claw-Guard/ClawGuard/ · https://arxiv.org/html/2604.11790 (ClawGuard)
- https://github.com/anilatambharii/bulwark
- https://github.com/NVIDIA-NeMo/Guardrails
- https://github.com/hellocosmos/agent-runtime-security
- https://github.com/krishddd/SEC_Guardrails_Agent (7-layer gateway reference + survey)
- OWASP Top 10 for LLM Applications / for Agentic Applications (T1–T15)