---
name: agent-memory-frameworks-2026
description: Mem0 vs LangMem vs Zep vs Letta vs Cognee vs AutoMem 六大记忆框架深度对比。Benchmark可信度批判、架构决策树、Hermes落地路径。触发词：agent记忆框架|Mem0对比|Zep|temporal knowledge graph|benchmark方法论|recall/synthesis gap
triggers:
  - agent memory framework comparison 2026
  - Mem0 vs LangMem
  - agent memory benchmark methodology
  - recall synthesis gap
  - temporal knowledge graph agent
  - Hermes memory upgrade path
category: agent-engineering
updated: 2026-09-17
---

# Agent Memory Frameworks 深度对比 2026 Q3

> 核心原则：benchmark数字是信号，不是裁决。选型依据架构和失败模式，而非百分比。

## 架构速查表

| 框架 | 架构 | 许可证 | 自托管 | 框架绑定 | GitHub |
|------|------|--------|--------|--------|--------|
| **Mem0** | vector + entity linking | Apache 2.0 | ✅ Docker | ❌ | 62k ⭐ |
| **Zep/Graphiti** | temporal KG | Apache 2.0 | ✅ | ❌ | Graphiti 3k |
| **Letta** | tiered OS-memory | Apache 2.0 | ✅ Docker | ❌ | 23k ⭐ |
| **LangMem** | KV + vector | MIT | ✅ | ⚠️ LangGraph only | 1.5k |
| **Cognee** | graph + vector | open core | ✅ | ❌ | 3.6k ⭐ |
| **AutoMem** | graph + vector | MIT | ✅ | MCP-native | 350 ⭐ |
| **Supermemory** | vector + KG | closed | ❌ | MCP | 8k ⭐ |

## 核心对比

### Mem0 — 行业基准

**核心机制：Token-Efficient Memory Algorithm**
```
输入 → Single-pass extraction → 事实/偏好/计划/修正结构化记忆
                              → ADD-only存储（不覆盖历史）
                              → Entity linking
                              → Multi-signal retrieval（语义+关键词+实体）
```

**Benchmark数据**（vendor-reported，需持疑）：
- LongMemEval 整体准确率: **93.4%** (GPT-4o)
- LoCoMo: **92.5%**
- BEAM 1M/10M: **64.1 / 48.6**
- 每次检索 ~6.9K tokens（vs Full-context 115K）
- Entity linking: 多跳推理 +29.6分，时序推理 +23.1分

**适用场景**：
- 高流量多用户 agent（客服/coding copilot/账户管理）
- 需要跨周/月召回用户详情
- 需要可预测延迟和成本预算

**不适用**：
- 需要深度多跳图遍历（本质是向量库+轻entity linking，不是完整KG）
- 多会话场景是软肋（Mem0自身分类揭示）

**定价**：Free managed tier / ~$19/月 / $249 Pro

---

### Zep / Graphiti — Temporal Knowledge Graph

**核心机制：Bi-temporal Knowledge Graph**
- 跟踪：事实何时为真（valid time）+ 何时记录（recorded time）
- 回答："我3月份相信什么" ≠ "现在什么是真的"
- Graphiti engine：Neo4j或同类图库

**Benchmark**（vendor-reported）：
- LongMemEval: **71.2%**（GPT-4o，落后Mem0 22分）
- LoCoMo: ~80%（数字有争议，见下方方法论问题）

**适用场景**：
- 支持历史（"客户上次投诉是什么时候？"）
- 事实过期危险的场景
- 需要明确溯源的事实链

**弱点**：
- LongMemEval分数显著落后
- LoCoMo数字有公开争议（84% vs 58% vs 75%，取决于谁在报）
- 自托管需要图库+Graphiti+LLM stack，运维复杂
- Graphiti自2024后无重大更新

**定价**：Free tier（含限量的episode credits） / ~$125/月（远高于Mem0）

---

### Letta (MemGPT Evolution) — Tiered OS Memory

**核心机制：LLM-as-OS**
```
Core Memory (可编辑块: persona + 用户事实)
    ↓ 上下文满时驱逐
Recall Memory (对话日志, 全量存储)
    ↓ 搜索后提取
Archival Memory (LLM生成的事实+摘要, 向量/图存储)
```

**2026年更新**：
- Letta Code: memory-first coding agent，Terminal-Bench #1（Model-agnostic OSS）
- Conversational Flows API: 并行用户对话间共享记忆
- 重构agent循环：从ReAct/MemGPT/Claude Code吸取教训
- **Context-Bench**: 开放评估框架（终于有benchmark数据）

**定价**（2026年）：
- Free: 3 managed agents, BYOK
- Pro $20/月: 20 agents, Letta Auto配额
- Enterprise: 自定义

**最佳点**：需要agent主动管理自己的记忆（主动curation而非被动存储）

**弱点**：
- V1 Python SDK已废弃，新项目用TypeScript Agent SDK v2
- 两仓库结构（`letta-ai/letta` vs `letta-ai/etta-code`）容易混淆
- 需要运行服务器（不是库模式）

---

### LangMem — LangGraph-Native Memory

**核心机制：KV + vector三层记忆**
```
Semantic Memory  — 用户事实
Episodic Memory  — 交互摘要
Procedural Memory — agent自己的系统指令
```

**关键数据**（第三方实测）：
- p95搜索延迟: **59.82秒**（arXiv:2504.19413）
- LoCoMo J-score: **58.10%** vs Mem0 67.13%（同benchmark）

**唯一优势**：零新基础设施——已用LangGraph则开箱即用

**致命弱点**：
- **LangGraph之外无法使用**
- 不是完整知识图谱（flat KV + vector）
- 59秒p95延迟在热路径上不可接受

---

## Benchmark方法论批判（重要）

> 数字来自供应商博客，使用不同模型和裁判，无法头对头比较。

**LoCoMo审计结果**（Penfield Labs, Dec 2025）：
- 答案密钥本身 **6.4%错误**
- LLM裁判接受高达 **63%的故意错误答案**
- 能区分88%和94%的系统？不，误差条吃掉了gap

**其他干扰项**：
- 不同slice：81题 vs 全部1,986题
- 不同judge和answer model：换GPT-5-mini同一系统跳10分
- 供应商数字战：Zep vs Mem0在LoCoMo上分别报了84%/58%/75%

**真正重要的指标被忽视**：
- **Recall@5**：top 5记忆是否包含答题证据 → 接近饱和（~97%）
- **End-to-end accuracy**：证据→推理→答案 → 差距在这里（87%）
- 检索synthesis gap（97% retrieval → 87% synthesis）= field集体在优化已完成的部分

---

## Hermes落地路径

### 当前状态
- `mem0-integration` skill：SQLite+TF-IDF轻量方案（已有）
- 无生产记忆框架评估体系
- 无benchmark质量标准

### 决策树

```
需要跨工具/框架共享记忆？
  └─ 是 → 研究 Membase 或 Memory Store（MCP-native）

主要场景是coding agent？
  └─ 是 → Supermemory（MCP集成，1M-token free tier）或 Memvid（离线）

需要可审计的时序推理？
  └─ 是 → Zep/Graphiti（但接受运维复杂度）

LangGraph已经在用？
  └─ 是 → LangMem（但p95延迟59秒是问题）
  └─ 否 → Mem0（最广泛框架支持，Apache 2.0）

需要agent主动管理记忆？
  └─ 是 → Letta（OS-tiered memory模型）

需要完全自托管 + 免费？
  └─ 是 → Cognee 或 AutoMem（MIT）
```

### 立即行动
1. 更新 `agent-long-context-memory.md` 补充 benchmark批判 + recall/synthesis gap
2. 将 Letta Context-Bench 添加到 `agent-testing-frameworks.md` 评测基准列表
3. LangMem作为 LangGraph-only 方案，不适合Hermes，标记为"不适用"

---

## 来源

- [AutoMem: Agent Memory 2026 Honest Comparison](https://automem.ai/blog/agent-memory-in-2026-an-honest-comparison-of-mem0-zep-letta-and-the-rest)
- [Mem0 vs Zep](https://mem0.ai/blog/mem0-vs-zep)
- [Mem0 vs LangGraph Memory](https://atlan.com/know/ai-agent/ai-agent-memory/langgraph-memory-vs-mem0)
- [LangMem GitHub](https://github.com/langchain-ai/langmem)
- [Letta Research](https://rywalker.com/research/letta)
- [Letta Pricing](https://www.letta.com/)
- [Penfield Labs LoCoMo Audit](https://dev.to/penfieldlabs/we-audited-locomo-6-4-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg)
- [Hindsight vs LangChain Memory](https://vectorize.io/articles/hindsight-vs-langchain-memory)
