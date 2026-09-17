---
name: stackone-defender
description: StackOne Defender — open-source prompt injection protection for AI agents. CPU-only, 22MB, <10ms latency, F1=90.8%. Use when building agentic integrations, MCP tool calling, or any agent that processes external content (emails, docs, PRs).
trigger: prompt injection defense / indirect injection / tool result sanitization / MCP security / LLM safety gate
---

# StackOne Defender — Prompt Injection Defense

## What it is

Open-source (Apache 2.0) prompt injection protection for AI agents calling tools. Detects and gates malicious instructions hidden in tool results (emails, documents, PRs, code) before they reach your LLM.

**Core stats**: 22MB ONNX model, CPU-only, ~10ms latency, F1 = 90.8%

GitHub: https://github.com/StackOneHQ/defender
npm: `@stackone/defender`

---

## Architecture: 3-Tier Defense Pipeline

### Tier 1 — Pattern Detection (sync, ~1ms)
Regex-based, no ML needed:
- Role markers: `SYSTEM:`, `ASSISTANT:`, `<system>`, `[INST]`
- Injection phrases: "ignore previous instructions", "disregard prior directives"
- Encoding signals: Base64/URL/ROT/Morse payloads
- Homoglyph normalization (Cyrillic 'а' → 'a') for detection; content is never normalized in output

### Tier 2 — ML Classification (async, ~10ms)
Fine-tuned **MiniLM-L6-v2** (int8 quantized, 22MB, bundled in package):
- Sentence-level scoring (0.0=safe, 1.0=injection)
- Multi-head architecture: main head + auxiliary head (detects docs quoting injection text without over-flagging)
- Calibrated thresholds baked into model `classifier_config.json`
- Catches attacks that evade Tier 1

Benchmark (F1 at threshold 0.5):

| Benchmark | F1 | Samples |
|---|---|---|
| Qualifire (in-distribution) | 86.86% | ~1.5k |
| xxz224 (out-of-distribution) | 88.34% | ~22.5k |
| jayavibhav (adversarial) | 97.17% | ~1k |
| **Average** | **90.79%** | ~25k |

### Tier 3 — LLM Classification (opt-in, consumer-supplied)
For ambiguous cases. Defender ships only orchestration + interface; you plug in your own LLM endpoint.

Two modes:
- **`cascade`** (default): T1 → T2 → T3, T3 invoked only in gray band `[0.3, 0.85)`
- **`tier3_only`**: T3 verdict alone (T1 still runs for metadata)

---

## Key Features

### Sentence-Level Sanitization
`defendToolResult()` returns:
- `result.allowed`: boolean — block/allow verdict
- `result.sanitized`: sentence-level cleaned copy (high-risk sentences dropped)
- `result.riskLevel`: `critical` / `high` / `medium` / `low`
- `result.tier2Score`: ML confidence score
- `result.detections`: list of what T1 caught

### Risky Field Detection
Tier 1 narrows scans to high-risk fields per tool type:

| Tool Pattern | Scanned Fields |
|---|---|
| `gmail_*`, `email_*` | subject, body, snippet, content |
| `github_*` | name, title, body, description, message |
| `documents_*` | name, description, content, title |
| `hris_*`, `ats_*`, `crm_*` | name, notes, description, summary, bio |
| Default | name, description, content, title, notes, summary, bio, body, text, message, comment, subject |

### Boundary Annotation (opt-in)
Wraps untrusted content in `[UD-{id}]...[/UD-{id}]` tags. Pair with `generateBoundaryInstructions()` in system prompt.

---

## Installation

```bash
npm install @stackone/defender
```

Optional peer deps for Tier 2 ML:
```bash
npm install onnxruntime-node @huggingface/transformers
```
Without them: Tier 1 only + `result.tier2Available === false` (alert on this).

---

## Quick Start

```typescript
import { createPromptDefense } from '@stackone/defender';

const defense = createPromptDefense({
  blockHighRisk: true,
});

// Optional: warmup to avoid first-call latency
await defense.warmupTier2();

// Defend a tool result before passing to LLM
const result = await defense.defendToolResult(rawEmailBody, 'gmail_get_message');

if (!result.allowed) {
  return { error: 'Content blocked by safety filter' };
}
passToLLM(result.sanitized);
```

### With Vercel AI SDK

```typescript
import { generateText, tool } from 'ai';
import { createPromptDefense } from '@stackone/defender';

const defense = createPromptDefense({ blockHighRisk: true });
await defense.warmupTier2();

const result = await generateText({
  model: anthropic('claude-sonnet-4-20250514'),
  tools: {
    gmail_get_message: tool({
      execute: async (args) => {
        const raw = await gmailApi.getMessage(args.id);
        const defended = await defense.defendToolResult(raw, 'gmail_get_message');
        if (!defended.allowed) {
          return { error: 'Content blocked by safety filter' };
        }
        return defended.sanitized;
      },
    }),
  },
});
```

---

## Hermes Integration Points

1. **MCP tool result interception**: Wrap all MCP tool results through `defendToolResult()` before passing to the LLM
2. **Web scraping pipeline**: Insert after `crawl4ai` fetches, before LLM context injection
3. **Email/content ingestion**: Before any external content enters context
4. **Production agent loop**: Layer into the `after_tool_call` hook

---

## Relation to StackOne SaaS (note)

StackOne is primarily a closed SaaS platform (~520 connectors, 32K actions, managed auth). The **Defender** library is the only open-source component. Full platform includes:
- Managed OAuth/SAML authentication
- Falcon execution engine (token optimization, up to 80% tokens saved)
- Advanced Tool Discovery (91.6% first-try accuracy on S1 Search Bench)
- Prompt Injection Guard (89% malicious tool responses caught — this is the commercial version of Defender)
- MCP + A2A + REST API + SDK multi-protocol support
- Pricing: undisclosed enterprise SaaS

---

## Verdict

**Use Defender** (free, Apache 2.0) for prompt injection protection in any agentic pipeline.
**Watch StackOne SaaS** if you need managed connectors + auth + token optimization in production.

---

## Sources

- https://github.com/StackOneHQ/defender
- https://www.stackone.com/
- https://github.com/StackOneHQ/stackone-plugin
