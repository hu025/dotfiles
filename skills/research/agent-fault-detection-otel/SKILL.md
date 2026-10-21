---
name: agent-fault-detection-otel
description: Use when instrumenting agent loops, detecting runaway tool calls, or choosing an OTel span model. Covers fault-detection benchmark data, 9-span-kind taxonomy, trace-to-eval linkage.
---

# Agent Fault Detection with OpenTelemetry

> Agent loop可观测性：从"记录span"到"检测故障"。与 `agent-observability-otel.md`（平台选型）互补——那份选工具，这份定span模型与检测策略。
> 触发词：agent死循环/runaway/tool loop/span模型/故障检测/trace评分/成本爆炸

## 核心判断

**日志无法回答agent的三个问题，span可以：**
1. Agent看到了什么？（system指令 + 历史 + 工具结果如何进入prompt）
2. 它为什么这么决策？（为什么`get_weather`调了3次而不是1次）
3. 为什么停下了？（完成 / 撞工具上限 / 报错）

一个自建agent曾整夜处理工单烧完整晚预算：**日志里全是成功调用、零错误**。trace显示一个`invoke_agent` span下嵌套**40次** `execute_tool get_ticket_status`，每次后面跟着 `finish_reasons: ["tool_calls"]`——工具返回值缺少prompt要求的confidence字段，agent无限重查。修复=prompt承认status字段 + guardrail（连续5次相同工具调用即中止）。**两个修复都无法从日志发现，只能从span层级和finish_reason遥测发现。**

---

## 一、Span 模型：9种Agent专用Kind

标准OTel只懂HTTP/DB/队列。Agent需要额外语义：

| Span Kind | 何时使用 |
|-----------|---------|
| `AGENT` | agent单轮运行（父span，包裹整个loop） |
| `LLM_CALL` | 一次模型调用 |
| `TOOL_CALL` | 工具/函数调用 |
| `PLANNING` | 规划阶段 |
| `REASONING` | 推理阶段 |
| `RETRIEVAL` | 检索步骤 |
| `GUARD_RAIL` | 安全/合规检查 |
| `DELEGATION` | 委派给子agent |
| `MEMORY` | 记忆读写 |

标准`gen_ai.*`命名（跨后端可移植）：
```
gen_ai.operation.name      chat | execute_tool | invoke_agent | embeddings
gen_ai.provider.name       openai | anthropic | aws.bedrock
gen_ai.request.model       gpt-4o-mini
gen_ai.usage.input_tokens  412
gen_ai.usage.output_tokens 96
gen_ai.response.finish_reasons  ["stop"] | ["tool_calls"]   ← 循环检测的关键
gen_ai.agent.name / .id    travel-concierge
gen_ai.tool.name / .call.id
```

Span命名模式 `{operation} {model-or-name}`：`chat gpt-4o-mini`、`execute_tool get_weather`、`invoke_agent travel-concierge`。

两种instrumentation策略：provider/framework wrapper（monkey-patch、callback handler、hook system）适合自动覆盖；context manager手动装饰适合自建agent。

---

## 二、故障检测：唯一有量化数据的对比

**AgentTelemetry**（Apache-2.0，`pip install agenttelemetry`）是少数发布了agent故障检测基准数据的开源库。14类故障 × 7种框架 × 6个mock模型的矩阵（3,528次故障注入 + 252次对照 = 3,780行）：

| 条件 | 故障检出率 FDR | 误报率 FPR |
|------|--------------|------------|
| 无遥测 | **0.000** | 0.000 |
| 原生OTel | 0.429 | 0.000 |
| OTel GenAI（当前规范） | 0.429 | 0.000 |
| OpenInference | 0.429 | 0.000 |
| AgentTelemetry DSM（元数据） | 0.612 | 0.071 |
| AgentTelemetry DSM（完整） | 0.612 | 0.071 |
| _DSM，完备适配器（上界）_ | **1.000** | 0.000 |

**读法（重要，别过度解读）：**
- **0.000 → 0.429 是最大的一跳**：任何OTel都比没有强，但**当前GenAI规范与OpenInference在agent故障上并不比原生OTel更好**——规范尚未覆盖agent特有故障（循环委派、上下文溢出等）。
- 0.612那一档是**部分增益**，且伴随FPR从0升到0.071。
- 1.000是**标注为"上界"的假设值**，不是实测——不要引用它。
- 结论：**不要期待"装上GenAI规范就自动具备agent故障检测"**。检测逻辑需要显式实现。

---

## 三、四个分析模块（AgentTelemetry）

| 模块 | 类 | 检测什么 |
|------|-----|---------|
| 异常检测 | `AnomalyDetector` | 循环委派、无限重试、成本爆炸、上下文溢出 |
| 成本聚合 | `CostAggregator` | 按模型/agent/trace聚合token与USD |
| 决策归因 | `DecisionAttributor` | 把每个工具调用回溯到触发它的LLM决策 |
| 幻觉追踪 | `HallucinationTracer` | 输出未被检索内容支撑（token重叠启发式） |

**决策归因最被低估**：它回答"这个工具调用为什么发生"，而普通trace只能看到工具调用存在。排查错误工具选择时，这是唯一路径。

---

## 四、隐私三档（默认档就是对的）

```python
from agenttelemetry import configure, PrivacyLevel

configure(service_name="my-agent", privacy_level=PrivacyLevel.METADATA_ONLY)  # 默认
configure(service_name="my-agent", privacy_level=PrivacyLevel.FULL)           # 调试用，需显式开启
configure(service_name="my-agent", privacy_level=PrivacyLevel.NONE)          # 仅结构信息
```
- `NONE`：span kind、时序、状态
- `METADATA_ONLY`（默认）：+ 模型名、token数、成本
- `FULL`：+ prompt/completion内容

**生产默认必须是 METADATA_ONLY**。prompt和工具输出常含客户数据与凭据。实测元数据档与完整档FDR完全相同（均0.612）——**开FULL不换来任何检测增益，只换来泄露风险**。这是本主题最实用的一条结论。

---

## 五、循环检测：可落地的告警规则

`gen_ai.response.finish_reasons` 是循环的指纹。反复 `["tool_calls"]` 而从不到 `["stop"]` = 烧token中。

```promql
# 同一agent token用量超阈值 且 execute_tool span数过多
count by (gen_ai.agent.name) (gen_ai.client.token.usage) > 100000
and
count by (span_name) (span_name=~"execute_tool.*") > 20
```

经验阈值：**一个会话内>20个 `execute_tool` span = 循环**。处理：中止 → 查trace → 找prompt或工具可用性bug。

配套guardrail：**连续N次相同工具调用即中止**（N=5是已验证起点）。这比任何事后检测都便宜。

其他必备指标：
```
gen_ai.client.operation.duration   延迟直方图（秒）
gen_ai.client.token.usage         token直方图，按 gen_ai.token.type 拆分input/output
```

---

## 六、Trace → Eval：同一份span两用

2026默认模式：不重跑agent，直接用产生prompt/completion的同一批span去评分。

```python
from fi.evals import evaluate
result = evaluate("faithfulness", output=span_response_text, context=span_retrieved_docs)
```
再用 `@tracer.chain` 包住评分函数，让eval本身发出 `EVALUATOR` span。整条agent run就成了可查询、可评分、可门禁的trace。

失败trace自动进eval数据集：
```python
if outcome == "failure" or trace.step_count > STEP_THRESHOLD:
    await eval_dataset.add(await trace_to_scenario(trace_id), source="production")
```

---

## 七、采样策略

| 比例 | 对象 |
|------|------|
| **100%** | 失败、超成本阈值、每agent类型每日前N次 |
| **10%** | 成功happy-path |
| **0%** | 健康检查/预热 |

**失败trace永远全量保留**——存一条失败trace的成本远低于无法debug它的成本。

**跨服务传播**：队列边界会杀死trace context，导致孤儿span。每个出站HTTP和消息信封注入 W3C `traceparent`，worker消费时 `extract`。否则工具调用会断成孤立span，waterfall图失效。

---

## 八、Claude Platform 原生OTel导出（2026-10-14 公测）

Anthropic已让 Managed Agents / Messages API / Claude SDKs 直接发标准OTel trace。

- **Messages API + Managed Agents**：在 Claude Console 加destination即可，无需改应用代码
- **Claude SDK**：应用内配置OTel provider/exporter，SDK自动导出
- 每次trace含：时长、状态、token数、模型、工具名、request ID（可匹配到具体API响应）
- 完整内容导出（prompt/response/工具输入输出）是**可选开关**，原因就是含敏感数据
- **已知缺口**：Managed Agents会话内model request span**不导出**内部prompt和response——preview为空不等于导出失败

官方已发布12家后端指南：Arize、Braintrust、Databricks、Datadog、Grafana Cloud、Honeycomb、Langfuse、LangSmith、New Relic、PostHog、Sentry、Splunk。

启动后约1分钟trace开始出现。

---

## 陷阱

1. **以为GenAI规范=agent故障检测**：实测二者与原生OTel持平（均0.429），规范未覆盖agent特有故障
2. **为调试开FULL捕获**：元数据档与完整档FDR完全相同，只增泄露风险
3. **引用1.000那个数**：那是标注的上界假设，不是实测
4. **只记LLM span**：agent故障往往在tool/retrieval层——工具返回空串，模型自己填了
5. **队列边界不传播traceparent**：产生孤儿span，waterfall失效
6. **无采样**：全量记录存储成本失控

---

## 来源

- AgentTelemetry — https://github.com/Krishnachaitanyakc/AgentTelemetry （基准数据、FDR表）
- traceAI (Future AGI, Apache-2.0) — https://futureagi.com/blog/traceai-opentelemetry-tracing-2026 （span kinds、trace-to-eval）
- OTel GenAI 语义约定实操 — https://tobias-weiss.org/content/articles/devops/agent-observability-opentelemetry （循环检测、finish_reasons）
- Claude Platform OTel 导出 — https://claude.com/de/resources/articles/agent-observability-on-the-claude-platform
- Trace树与采样实践 — https://blog.michaelsam94.com/agent-observability-tracing-spans