# Agent Observability & OpenTelemetry

> LLM Agent 生产可观测性标准与工具链。触发词：可观测性/ tracing / span / OTel / agent监控

## 核心概念

**为什么需要可观测性？**
- Agent 非确定性：同样的输入可能产生不同输出
- 多步骤执行：RAG检索 → LLM推理 → 工具调用 → 响应
- 53% 企业在部署后需要大幅重新设计 agent
- 73% 企业表示没有监控不会上线 agent

**四个核心问题 → 五类工具**
1. *What did my agent just do?* → Tracing Tools
2. *Was the output any good?* → Evaluation Tools
3. *How do I route and keep an eye on all this traffic?* → Gateways
4. *Can one platform handle my old-school ML and my GenAI?* → Hybrid Platforms
5. *Can I just run this alongside the infra monitoring I already have?* → Broad Platforms

---

## OpenTelemetry GenAI Semantic Conventions

### 现状
- OTel GenAI SIG 正制定 AI Agent 可观测性标准
- 草案已完成：[OpenTelemetry semantic conventions #1732](https://github.com/open-telemetry/semantic-conventions/issues/1732)
- 基于 Google AI Agent Whitepaper 构建
- 覆盖：LLM/Model / VectorDB / AI Agent 三大语义约定

### 关键 Span 属性
```
gen_ai.operation.name        # 操作类型
gen_ai.response.model        # 模型名称
gen_ai.response.latency      # 延迟
gen_ai.usage.input_tokens    # 输入token
gen_ai.usage.output_tokens    # 输出token
gen_ai.usage.total_tokens     # 总token
gen_ai.usage.cost             # 成本
gen_ai.choices.finish_reason   # 停止原因
gen_ai.choices.input_tokens   # choices级token
gen_ai.choices.output_tokens  # choices级token
```

### Instrumentation
```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span(
    "agent.workflow",
    kind=SpanKind.INTERNAL,
    attributes={
        "agent.name": "my-agent",
        "agent.version": "1.0.0"
    }
) as span:
    # RAG retrieval
    with tracer.start_as_current_span("retrieval.search") as retrieval_span:
        docs = vector_db.similarity_search(query)
        retrieval_span.set_attribute("retrieval.doc_count", len(docs))
    
    # LLM call
    with tracer.start_as_current_span("llm.generation") as llm_span:
        response = llm.complete(prompt)
        llm_span.set_attribute("gen_ai.usage.total_tokens", response.usage.total_tokens)
    
    # Tool call
    with tracer.start_as_current_span("tool.execute") as tool_span:
        result = tool.call(**params)
        tool_span.set_attribute("tool.name", tool.name)
```

---

## 五大工具对比

| 工具 | 类型 | 开源 | 语言 | 特点 | 价格 |
|------|------|------|------|------|------|
| **Langfuse** | Tracing | ✅ MIT | Python/TS | 最广泛采用，OpenAI Agents SDK集成 | Self-host / $29/mo |
| **Laminar** | Tracing | ✅ Apache 2.0 | Rust | 极速摄入，OTel原生，内容去重，存储省20% | Free / Cloud $$-$$$ |
| **MLflow Tracing** | Tracing | ✅ Apache 2.0 | Python | GenAI语义约定原生，trace replay，prompt版本管理 | Free |
| **Arize Phoenix** | Tracing | ✅ ELv2 | Python | OTel原生，4种agent评估器，MCP追踪 | Free / $50/mo |
| **Weave (W&B)** | Tracing | ✅ Apache 2.0 | Python/TS | MCP自动日志，scorer系统 | $60/mo |
| **LangSmith** | 平台 | ❌ | 多语言 | Insights Agent自动聚类生产trace | $139/mo起 |
| **DeepEval** | 评估 | ✅ Apache 2.0 | Python | 6种agent指标，Pytest集成 | Free / $19.99/user/mo |
| **Comet Opik** | 平台 | ✅ Apache 2.0 | 多语言 | 高吞吐trace摄入，生产级规模 | Free |
| **Braintrust** | 评估 | ❌ | 多语言 | OpenAI Agents SDK + Google ADK集成 | $$-$$$ |
| **Monte Carlo** | 平台 | ❌ | 多语言 | **唯一同时监控数据+AI栈**，端到端血缘 | 联系销售 |

---

## Laminar 深度（推荐自托管）

### 为什么选 Laminar
- Apache 2.0 开源，Rust 编写
- OTel 原生，deduplicates 内容
- 单 agent run 可产生数千 spans，Laminar 摄入跟得上
- 自托管：数据不离开基础设施

### 快速部署
```bash
# Docker 部署
docker run -p 4317:4317 -p 4318:4318 laminarai/laminar

# Python SDK
pip install laminar-sdk

# Node.js SDK  
npm install @laminarai/sdk
```

### Python 集成示例
```python
from laminar import Laminar

laminar = Laminar(endpoint="http://localhost:4317")

@lcalar.wrap(framework="openai", span_name="agent.chat")
def chat_with_agent(user_input: str):
    # Your agent logic here
    return response

# 或使用 OpenTelemetry SDK
from laminar.extensions.opentelemetry import LaminarSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

exporter = LaminarSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(exporter)
```

---

## Langfuse 集成（OpenAI Agents SDK）

```python
# Langfuse + OpenAI Agents SDK
from langfuse import Langfuse
from agents import Agent, Runner, WebSearchTool
from agents.sdk import add_trace_processor, OpenAIAgentsTraceProcessor

# Initialize Langfuse
langfuse = Langfuse()

# Create trace processor
processor = OpenAIAgentsTraceProcessor(logger=langfuse)
addTraceProcessor(processor)

# Define agent
agent = Agent(
    name="WebSearchAgent",
    instructions="You are a research assistant.",
    tools=[WebSearchTool()]
)

# Run with tracing
result = Runner.run_sync(agent, "What are the latest AI agent benchmarks?")
```

### 关键指标
```python
# 1. 成本追踪
span.update_trace(
    metadata={"cost_usd": calculate_cost(response)}
)

# 2. 延迟分析
span.update_trace(
    attributes={"step_latency_ms": step_duration_ms}
)

# 3. LLM-as-a-Judge 评估
judge_prompt = "Rate the response for accuracy (1-10)"
judge_response = judge_model.complete(judge_prompt)
span.update_trace(
    evaluation={"accuracy_score": judge_response.score}
)
```

---

## 生产级架构

### 推荐的最小可观测性堆栈
```
┌─────────────────────────────────────────────┐
│              Agent Application              │
├─────────────────────────────────────────────┤
│  OTel SDK (Python/Node)                    │
│  - auto-instrumentation for LLM calls       │
│  - manual spans for tool execution          │
│  - baggage for cross-cutting context        │
├─────────────────────────────────────────────┤
│  OTel Collector                            │
│  - batch + retry                           │
│  - transform metrics                        │
│  - route to multiple backends              │
├──────────────────┬──────────────────────────┤
│  Laminar/Langfuse │  Prometheus + Grafana   │
│  (Traces + Evals)│  (Metrics + Dashboards)│
└──────────────────┴──────────────────────────┘
```

### 评估指标体系
```python
# 必选指标
AGENT_LATENCY_P50 = percent(duration_ms, 50)
AGENT_LATENCY_P95 = percent(duration_ms, 95)
TOKEN_USAGE_TOTAL = sum(input_tokens + output_tokens)
TOOL_ERROR_RATE = errors / total_tool_calls
LLM_ERROR_RATE = errors / total_llm_calls
COST_PER_REQUEST = token_cost * tokens_used

# 可选质量指标（LLM-as-a-Judge）
RESPONSE_FAITHFULNESS = judge("Does response match retrieved context?")
RESPONSE_RELEVANCE = judge("Does response answer the query?")
HALLUCINATION_SCORE = judge("Any fabricated facts detected?")
SAFETY_SCORE = judge("Any unsafe content detected?")
```

### 数据血缘（Monte Carlo 启示）
```
用户输入 → RAG检索 → LLM推理 → 工具调用 → 响应输出
    ↑            ↑            ↑            ↑
  数据源       向量库        模型权重      后处理
  监控         监控          监控          监控
```
**关键洞察**：大多数工具只看 agent 行为，忽视数据层。一张旧表或破损的 pipeline 可以在 trace 看起来完全健康的情况下产生错误答案。

---

## 陷阱与最佳实践

### 陷阱
1. **只监控 LLM 调用**：忽略 RAG/tool 层 → 根因难找
2. **trace 过多**：每个 token 都记录 → 成本爆炸
3. **无采样**：生产流量全量记录 → 存储成本失控
4. **评估后置**：只在离线测试评估 → 线上问题发现滞后
5. **数据层盲区**：数据问题在 trace 里看不到

### 最佳实践
1. **自适应采样**：错误率高的 trace 100% 保留，正常流量 1-10% 采样
2. **端到端血缘**：trace 必须能追溯到数据源
3. **评估闭环**：生产 trace → 评估数据集 → 测试集 → 回归测试
4. **多维度告警**：延迟 + 成本 + 错误率 + 质量分数
5. **根因定位**：数据层监控 + agent 行为监控 联动

---

## OpenTelemetry 资源

- [GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [GenAI SIG #otel-genai-instrumentation](https://github.com/open-telemetry/community/blob/5125996b5d159ff9aaa906f9a25226a821dc7bed/projects/gen-ai.md)
- [Google AI Agent Whitepaper](https://www.kaggle.com/whitepaper-agents)
- [OTel AI Agent 标准草案 #1732](https://github.com/open-telemetry/semantic-conventions/issues/1732)
