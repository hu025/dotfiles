---
name: assert
description: Microsoft ASSERT — policy-driven AI agent evaluation framework. 触发词：agent评估/行为测试/治理/Spec-driven eval
triggers:
  - agent评估
  - 行为测试
  - 治理
  - Spec-driven eval
  - agent governance
  - policy-driven evaluation
---

# Microsoft ASSERT — Agent Evaluation Framework

## 核心定位

**Assert** (Adaptive Spec-driven Scoring for Evaluation and Regression Testing) 是微软开源的 agent 评估框架，填补了"自然语言需求 → 可执行评估"之间的鸿沟。

> "99% 的组织在 agent 上生产前不做任何评估" — Gartner

## 核心价值

### 4 阶段评估管道

1. **Systematization** — 将模糊行为概念转化为结构化规范（harmful advice / tool governance / unsafe guidance）
2. **Taxonomization** — 生成行为分类树（permissible / impermissible behaviors），可人工审核修改
3. **Test-set Generation** — 从分类树实例化单轮/多轮测试用例，支持对抗探测
4. **Scoring** — LLM Judge 评分，返回标签 + 理由 + 策略引用 + 具体操作证据

### 关键特性

- **Spec-driven** — 测试从产品需求/PRD/策略文档生成，不是通用 benchmark
- **行为库** — 预设 atomic behavior presets（safety / bias / agentic failure modes）
- **框架无关** — 支持 LangGraph / CrewAI / OpenAI Agents SDK / DSPy / LlamaIndex / AutoGen / 自定义
- **OTel Trace-aware** — 捕获完整 agent trace（tool calls / routing / latency）作为评判证据
- **沙箱执行** — Docker 沙箱 + 工具调用 mock/block + 代理审计
- **Local-first** — 所有结果写本地 JSON/JSONL，配合 bundled viewer

### 验证数据

- 覆盖率比直接生成方法高 **1.2x**
- 有意义失败案例多 **1.5x**
- 强弱模型区分度比同类高 **4x**
- 饱和案例（所有模型行为相同）减少 **一半**
- LLM Judge 与人类标注者一致率：**80–90%**

### Guided 模式（推荐）

```
pip install -e ".[phoenix]"
assert-ai --help
```

通过 `run-assert-eval` skill，描述 agent 风险 → 自动生成测试套件 → 评判失败 → 生成 ACS 治理策略。

## 落地动作

适合为 Hermes agent 生态系统建立量化评估标准：

```bash
# 安装
pip install -e ".[phoenix]"

# 评估一个 agent（比如 hermes 自评）
# 1. 写 eval_config.yaml（描述行为规范）
# 2. 运行测试
assert-eval run --config eval_config.yaml

# 本地查看结果
# artifacts/results/ 下 JSON 文件
```

## 来源

- GitHub: https://github.com/responsibleai/ASSERT
- 文档: https://responsibleai.github.io/ASSERT/
- 论文: https://arxiv.org/abs/2608.13840
- Blog: https://commandline.microsoft.com/assert-written-intent-executable-evals/
