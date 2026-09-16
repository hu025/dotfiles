---
name: langgraph-production-2026
description: LangGraph production patterns v1.2+ (2026). Use when building stateful agents, multi-agent orchestration, human-in-the-loop, or production scaling with LangGraph.
tags: [agent, orchestration, state-machine, durable-execution, hitl, guardrails]
sources:
  - https://github.com/langchain-ai/langgraph/releases
  - https://dev.to/richard_dillon_b9c238186e/langgraph-20-the-definitive-guide-to-building-production-grade-ai-agents-in-2026-4j2b
  - https://markaicode.com/architecture/agent-architecture-best-practices-2026
  - https://docs.langchain.com/oss/python/langgraph/overview
  - https://langchain.launchnotes.io/announcements/ann_lxOZRCoFw2Qn9
last_updated: 2026-09-17
---

# LangGraph Production Patterns v1.2 (2026)

## 核心定位

LangGraph = **编排运行时**（非框架）：持久执行、流式、人在环、持久化。区别于 LangChain（组件集成）和 LangSmith（可观测性平台）。

- **LangGraph**: 低级编排runtime，适合长时间运行、有状态、需要细粒度控制的agent
- **LangChain**: 线性RAG/chain场景，单次请求足够时用LangChain
- **决策树**: 需要循环/分支/重试/暂停 → LangGraph；否则 → LangChain

## 关键变化 v0.3 → v1.2

### 1. Checkpoint 必需初始化（v2.0 breaking change）

```python
# v0.1.x (DEPRECATED)
graph = StateGraph(AgentState)

# v1.2 (CURRENT) — checkpoint 必传
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/langgraph",
    pool_size=10,          # 连接池配置（新增）
    schema_name="agents"   # 多租户schema支持（新增）
)
graph = StateGraph(AgentState, checkpointer=checkpointer)
```

### 2. interrupt() 替代 NodeInterrupt 异常

```python
# v0.1.x (DEPRECATED)
from langgraph.errors import NodeInterrupt
def review_node(state):
    if state["needs_approval"]:
        raise NodeInterrupt("Awaiting human approval")

# v1.2 (CURRENT)
from langgraph.types import interrupt, Command
def review_node(state):
    if state["needs_approval"]:
        approval = interrupt({
            "question": "Approve this action?",
            "proposed_action": state["proposed_action"],
            "context": state["synthesis"]
        })
        return Command(update={"approval_status": approval})
    return state
```

### 3. Guardrail 节点（企业级安全，原生支持）

```python
from langgraph.guardrails import ContentFilter, RateLimiter, AuditLogger

graph.add_guardrail(
    ContentFilter(
        blocked_patterns=["PII_PATTERN", "PROFANITY"],
        action="redact"  # "block" | "flag"
    ),
    before=["synthesis", "action"]
)
graph.add_guardrail(
    RateLimiter(requests_per_minute=60, burst_limit=10, scope="per_user")
)
graph.add_guardrail(
    AuditLogger(destination="cloudwatch://agents/compliance", include_state=True)
)
```

### 4. trace_policy 在 add_node 暴露

```python
graph.add_node(
    "research",
    research_node,
    trace_policy="full"  # "full" | "args-only" | "none"
)
```

### 5. checkpoint 4.2.0 新特性

- `omit_expired` 参数：读取时跳过过期行，减少无效数据扫描
- delta channel 写入修复：checkpoint写一致性提升

## 生产架构模式

### 单进程（< 50 req/min 适用）

```
LangGraph (单进程) + MemorySaver/PostgresSaver
```

### 事件驱动解耦（≥ 50 req/min 推荐）

```
Gateway → NATS JetStream → LangGraph Orchestrator → Tool Executors
                              ↓
                        PostgresSaver
                              ↓
                         LangSmith
```

**关键原则**：
- 工具调用必须幂等（带 idempotency key）
- 每个edge配置timeout和fallback
- 投资分布式追踪（OpenTelemetry）先于故障发生
- 容量瓶颈顺序：LLM推理 > 工具执行 > 消息代理开销

## 人在环（HITL）模式

| 模式 | 触发时机 | 延迟影响 | 适用场景 |
|------|---------|---------|---------|
| Interrupt Before Tool | 工具执行前 | 高（每工具等待） | 金融/法律/医疗高风险工具 |
| Interrupt Before LLM | agent决定下一步前 | 中（每推理步等待） | 研究agent推理审查 |
| Approval Node | 自定义节点 | 单次等待 | 客服升级/内容发布 |
| Editable State + Resume | 任意时刻 | 低 | 知识注入/修正幻觉 |

## 与其他框架对比

| 维度 | LangGraph | CrewAI | AutoGen |
|------|-----------|--------|---------|
| 定位 | 编排runtime | Agent框架 | 会话协作 |
| 状态管理 | 强制checkpoint | 可选memory | 会话级别 |
| HITL | 原生interrupt | 原生 | 需自定义 |
| 多Agent | 状态机+子图 | 层级+流程 | 对等对话 |
| 企业治理 | Guardrail节点 | AOP面板 | 无 |
| 成熟度 | ★★★★★ | ★★★★ | ★★★ |

## 落地建议

1. **新项目**：直接用 v1.2，checkpoint 必配
2. **迁移 v0.1.x**：运行 `langchain migrate langgraph` 自动检测废弃模式
3. **生产扩展**：先单进程 → 监控瓶颈 → 再演进到事件驱动
4. **监控指标**：per-step latency + error rate，而非仅端到端

## 最新版本（2026-09）

- langgraph: **1.2.11**
- langgraph-checkpoint: **4.2.0**
- langgraph-checkpoint-postgres: **3.1.2**
- langgraph-checkpoint-sqlite: **3.1.1**
- langgraph-sdk: **0.4.4**
- langgraph-cli: **0.4.31**
