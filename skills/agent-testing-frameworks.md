---
name: agent-testing-frameworks
description: AI Agent评测框架完全指南：DeepEval/Braintrust/Arize Phoenix/RAGAS/LangSmith/Galileo对比，pytest风格/轨迹评测/LLM-as-judge/offline vs online选型。触发词：agent测试框架/AI评测框架/DeepEval/Braintrust/agent eval
triggers:
  - AI agent testing framework
  - DeepEval vs Braintrust
  - agent evaluation framework 2026
  - pytest style agent eval
  - trajectory evaluation
  - LLM as judge agent
  - agent observability tools
  - production per-turn evaluation
category: agent-engineering
---

# AI Agent 评测框架完全指南 (2026 Q3)

## 核心问题：传统测试为什么失效

AI Agent 引入四个根本性转变：

1. **概率生成**：相同输入 → 不同输出（非确定性）
2. **上下文依赖**：对话历史、系统状态、外部知识（超出无状态函数模型）
3. **涌现能力**：大规模训练中出现，无法用代码逻辑验证
4. **多组件复杂度**：检索、工具调用、多轮交互

**关键洞察**：轨迹与结果同样重要。相同最终答案可能通过可靠路径或脆弱高成本路径达成。

## 三层评测模型

| 层级 | 评测什么 | 例子 |
|------|---------|------|
| **Unit级** | 正确的工具 + 正确的参数 | 调用了 `send_email`，参数正确 |
| **Trajectory级** | 合理的中间步骤路径 | 5步内到达目标，无违规调用 |
| **Outcome级** | 目标达成 | 任务完成，结果正确 |

## 七大框架对比

| 框架 | 开源 | 离线/在线 | 轨迹评测 | LLM-as-Judge | 免费额度 |
|------|------|----------|---------|-------------|---------|
| **DeepEval** | ✅ Apache 2.0 (16.5k⭐) | 两者都有 | ✅ agentic+span级 | ✅ G-Eval, DAG | OSS免费；云平台$9.99/用户/月 |
| **Braintrust** | ❌ (autoevals MIT) | 两者都有 | ✅ | ✅ autoevals | 1GB + 10k评分/月 |
| **Arize Phoenix** | ✅ Elastic 2.0 (10k⭐) | 两者都有 | ✅ 轨迹+路径收敛 | ✅ phoenix.evals | OSS免费；AX $0起 |
| **RAGAS** | ✅ Apache 2.0 (14.5k⭐) | 离线（库） | 部分（工具+目标） | ✅ | 完全免费OSS |
| **LangSmith** | ❌ (helpers MIT) | 两者都有 | ✅ | ✅ | 5k traces/月 |
| **OpenAI Evals** | ✅ MIT (18.5k⭐) | 离线 | 有限 | ✅ YAML | OSS免费；托管服务2026年底停用 |
| **Galileo** | ❌ (Agent Control OSS) | 两者都有 | ✅ 每步动作/工具 | ✅ Luna-2蒸馏 | 5k traces/月；Pro $100/月 |

## 1. DeepEval — 代码优先首选

**v4.0 (2026-05)** 最新特性：
- 50+ 指标：RAG、Agentic、Conversational、Safety、多模态
- G-Eval：自然语言criteria + 字段列表 → 0-1分（LLM judge）
- DAGMetric：确定性决策树（mixed judge + 规则），无需LLM调用
- **Coding-agent eval harness**：针对SWE-bench类任务
- **Terminal trace TUI**：针对 Claude Code / Cursor / Codex 迭代循环
- Confident AI云平台：tracing + 在线评测 + 数据集版本管理

### 核心Agentic指标
```
TaskCompletionMetric     — 任务是否完成
ToolCorrectnessMetric    — 工具调用是否正确
ArgumentCorrectnessMetric — 参数是否正确
StepEfficiencyMetric     — 步数是否高效
PlanAdherenceMetric      — 是否遵循计划
PlanQualityMetric        — 计划质量
```

### pytest风格示例
```python
from deepeval import assert_test
from deepeval.metrics import TaskCompletionMetric

@pytest.fixture
def customer_support_agent():
    return build_agent()

def test_refund_request(customer_support_agent):
    conversation = customer_support_agent.run(
        "I want a refund for order #12345"
    )
    assert_test(conversation, [
        TaskCompletionMetric(threshold=0.8),
        ToolCorrectnessMetric(threshold=0.9),
    ])
```

**Best for**: 代码优先团队，CI中深度agent指标覆盖，pytest工作流

---

## 2. Braintrust — Eval优先平台

**核心差异化**：
- Eval-first设计：数据集 + 实验 + 评分器一体化
- **原生框架集成**：OpenAI Agents SDK、LangGraph、Mastra、Pydantic AI、LangChain、CrewAI
- autoevals库（MIT）：内置多种评分器，支持自定义代码评分器
- 生产轨迹在线评分

**弱点**：
- 不是开源（autoevals库本身MIT开源）
- LLM-as-judge每次调用有成本

**Best for**: 需要统一eval管理平台、已有多种框架混合使用的团队

---

## 3. Arize Phoenix — 自托管可观测性

**核心差异化**：
- OTel原生 + Elastic 2.0（部分开源）
- **轨迹评测 + 路径收敛分析**
- phoenix.evals：内置多种评测指标
- 自托管免费，云平台AX按量付费

**Best for**: 需要完全自托管、已有OTel基础设施的团队

---

## 4. 生产层：Per-Turn在线评测

**所有离线框架的共同弱点**：
- 离线套件是流量快照，生产分布每日漂移
- 没有框架在每轮运行时进行语义分类
- YC 2026调查：38%的agent builder明确提到评测挑战

- **Letta Context-Bench**：Stateful agent专项评估，填补"有状态"评估空白（2026-09新增）
- **Morph Reflex**（新生代）：
- Per-turn在线语义分类
- <90ms延迟
- $0.001/event（~ $0.49/百万token）
- 比LLM-as-judge便宜10倍

```
两层评测架构（推荐）：
Layer 1: DeepEval离线CI回归套件 → 可重现的回归覆盖
Layer 2: Reflex per-turn生产分类器 → 实时失败拦截
```

---

## Tau2-Bench 与可靠性指标

**Sierra tau-bench 引入 pass^k 可靠性指标**：
- 指数衰减：暴露"有时成功" vs "可靠成功"的差距
- 对话式Agent在双控制环境（agent+用户都能操作）

**排行榜参考（2026-04）**：
```
电信领域 top: ~42% pass rate（顶级开源agent）
零售/航空: ~35-40%
→ 即使最强模型在真实多轮客服场景也只有~40%可靠
```

**生产级可靠性标准**：
- k=1（单次尝试）: pass rate > 80%
- k=3（三次尝试）: pass rate > 95% 才算"可靠"

---

## Hermes评测现状 vs 新框架

**当前Hermes使用的方法**：
- 手动验证（人类review）
- 日志分析（grep/awk）
- SWE-bench排名作为能力参考

**差距**：
- 无自动化agent轨迹评测
- 无pytest风格的CI集成评测
- 无production per-turn监控

**建议落地顺序**：
1. **立即**：DeepEval（Apache 2.0，pip install直接用）→ 写3-5个核心场景的assert_test
2. **短期**：集成到cron任务→验证任务质量
3. **中期**：考虑Morph Reflex做per-turn生产监控

---

## 选型决策树

```
是否需要离线CI评测？
  ├─ 否 → 跳过DeepEval，用LangSmith/Braintrust在线
  └─ 是 → 用DeepEval + 框架集成

是否需要多框架集成？
  ├─ 是 → Braintrust（原生集成最多）
  └─ 否 → DeepEval（最专注离线）

是否需要完全开源？
  ├─ 是 → DeepEval 或 RAGAS
  └─ 否 → Braintrust

是否需要per-turn生产监控？
  └─ 是 → Morph Reflex（两层架构）
```

---

## 来源

- DeepEval: https://github.com/confident-ai/deepeval (Apache 2.0)
- Braintrust: https://www.braintrust.dev
- Arize Phoenix: https://github.com/Arize-ai/phoenix
- RAGAS: https://github.com/explodinggradients/ragas
- Morph Reflex: https://www.morphllm.com/products/reflex
- Zylos Research: https://zylos.ai/en/research/2026-07-15-agent-testing-evaluation-frameworks
- State of YC AI Agents 2026: https://voker.ai/blog/the-state-of-yc-ai-agents-2026
