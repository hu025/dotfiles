---
name: graphbit
description: GraphBit — Rust-core enterprise agent framework (581 stars, Apache 2.0)
triggers:
  - "GraphBit agentic framework"
  - "Rust Python agent workflow"
  - "enterprise agent efficiency benchmark"
created: 2026-10-21
updated: 2026-10-21
stars: 581
license: Apache-2.0
repo: github.com/InfinitiBit/graphbit
docs: docs.graphbit.ai
---

# GraphBit — High Performance Agentic Framework

## 核心定位

Rust核心 + Python包装的Enterprise级agent框架，主打68× lower CPU / 140× lower memory vs Python框架，已在Grant Thornton Germany生产部署。

## 架构

三层设计：
- **Rust Core**: workflow引擎、agents、LLM providers
- **Orchestration Layer**: 项目管理和执行
- **Python API**: PyO3异步绑定

## 核心差异化

### 性能基准（内部测试）
| Metric | GraphBit | Other Frameworks | Gain |
|--------|----------|-----------------|------|
| CPU Usage | 1.0× baseline | 68.3× higher | ~68× |
| Memory | 1.0× baseline | 140× higher | ~140× |
| Execution Speed | ≈ equal/faster | — | — |
| Determinism | 100% success | Variable | Guaranteed |

### 可靠性特性
- **Circuit Breaker**: 三态（CLOSED/OPEN/HALF_OPEN），failure_threshold触发
- **Retry Policies**: 指数退避，自动分类transient/permanent/system/unknown错误
- **Health Monitoring**: 内置健康检查 + 自动化告警阈值

### 监控特性
- **WorkflowMetrics**: workflow_id / duration_ms / status / node_count 全链路
- **WorkflowMonitor**: start_execution / end_execution / get_metrics_summary
- **Performance Baselining**: P95延迟基线建立
- **Automated Alerting**: 自定义阈值触发（error_rate/memory/success_rate）

### 其他特性
- **Type Safety**: 强类型贯穿执行管道
- **Multi-LLM**: OpenAI / Anthropic / Ollama / DeepSeek / Azure / OpenRouter / Replicate / TogetherAI
- **Dynamic Graph Generation**: 运行时自动生成workflow结构
- **Document Processing**: PDF / DOCX / TXT 加载 + 文本分割
- **Tool Registry**: 同步/异步工具注册，@tool装饰器模式
- **Guardrail FFI**: 独立guardrail_ffi crate支持企业合规

## 与现有框架对比

- vs LangChain/LangGraph: 68× lower CPU，无沉重Python包袱
- vs CrewAI: 图原生设计，动态边，超越简单角色定义
- vs Strands/VoltAgent: Rust核心性能优势明显
- vs OpenFang (394MB idle): GraphBit目标<10MB idle

## 生产部署参考

Grant Thornton Germany已用于将AI从"permanent pilot"移至生产，配合监管合规要求。

## 安装

```bash
pip install graphbit
```

## 快速开始

```python
from graphbit import init, LlmClient, LlmConfig, Workflow, Node, Executor

init()
config = LlmConfig.openai("sk-...")
client = LlmClient(config)

# Workflow模式
workflow = Workflow("Analysis Pipeline")
smart_agent = Node.agent(name="Smart Agent", prompt="...", agent_id="smart")
processor = Node.agent(name="Data Processor", prompt="...", agent_id="processor")
id1 = workflow.add_node(smart_agent)
id2 = workflow.add_node(processor)
workflow.connect(id1, id2)

executor = Executor(config)
result = executor.execute(workflow)
```

## GuardrailPolicy

```python
result = executor.execute(workflow, policy=GuardRailPolicyConfig.from_json('{"guardrail_policy": {"pii_rules": [...]}}'))
```

## 新知识总结

**核心发现**: GraphBit的Rust-first架构解决了所有Python agent框架的性能痛点。68× CPU / 140× memory改善是真实企业内部基准。Circuit Breaker + Retry三层分类 + Health Monitoring构成完整可靠性体系，比Hermes当前实现在生产可靠性上领先一代。

**对Hermes的参考价值**:
1. Circuit Breaker模式可用于Hermes API调用层的熔断保护
2. Health Monitoring的metrics收集模式可移植到Hermes skill hook
3. 性能对比方法（内部基准测试）值得Hermes学习

**不适合直接集成**: Apache 2.0但无Hermes官方集成确认，Rust核心与Hermes Python架构整合成本高。

**来源**:
- https://github.com/InfinitiBit/graphbit
- https://docs.graphbit.ai/
