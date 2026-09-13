---
name: agent-function-calling
description: Agent函数调用/Tool Use SOTA技能文档。BFCL基准/开源模型对比/xLAM/NexusRaven/Hermes-Pro/MCP评测框架/Tool Description优化。2026年最新进展
triggers:
  - function calling model comparison 2026
  - xLAM vs NexusRaven vs Hermes-Pro
  - BFCL leaderboard open weight
  - MCP benchmark evaluation 2026
  - tool description quality MCP
  - open weight function calling model
  - agent tool use benchmarks
category: agent-engineering
---

# Agent Function Calling / Tool Use SOTA (2026)

## 核心基准体系

### BFCL — Berkeley Function-Calling Leaderboard
最权威的工具调用基准，覆盖6类任务：单调用/并行调用/多函数选择/相关性检测/多轮交互/多步推理。v3/v4版本均有评估，AST结构比对评分。

| 类别 | 模型 | BFCL得分 | 备注 |
|------|------|---------|------|
| **闭源最强** | Claude 4.7 Opus | ~92.0% | 闭源榜首 |
| | GPT-5.5 | ~91.0% | |
| | Gemini 3.1 Pro | ~89.5% | |
| **开源最强** | Qwen3-235B-A22B (Tool Mode) | ~88.5% | Apache 2.0 |
| | Llama 4 Maverick | ~87.4% | |
| | Qwen3-32B (Tool Mode) | ~85.7% | 单GPU可跑 |
| | Watt-Tool-70B | ~85.0% | |
| | DeepSeek V4 | ~84.6% | MIT许可 |
| | Granite 3.3 8B | ~82.1% | Apache 2.0，边缘部署首选 |
| | Hermes-4-70B | ~81.7% | Nous Research，社区主流 |
| | xLAM-7B-r | ~78.0% | |
| | NexusRaven-13B V2 | ~71.8% | |

**关键结论**：开源与闭源差距已缩小至5-10个百分点。

### MCP Atlas Benchmark
2026年新出现的MCP专项基准，41个模型评估。

| 排名 | 模型 | 得分 | 备注 |
|------|------|------|------|
| 1 | Muse Spark 1.1 (Meta) | 88.1% | 闭源 |
| 2 | Claude Opus 5 | 85.8% | 闭源 |
| 3 | Kimi K3 (Moonshot) | 84.2% | |
| 4 | Hy4 preview (Tencent) | 83.7% | 开源权重 |
| 5 | Gemini 3.5 Flash | 83.6% | |
| 6 | Claude Opus 4.8 | 82.2% | |
| 7 | Ornith-1.5-397B | 80.0% | 开源权重 |
| 8 | MiniMax M3 | 74.2% | 开源权重 |

### tau-bench
多轮客服+工具+策略约束。Claude Sonnet 4.6领跑（87.5% retail+airline），GPT-5.2 Thinking在tau2电信达98.7%（基准范围窄，有虚高）。

### 其他专项基准
- **MCP-AgentBench**：33个MCP服务器/188工具/600查询（ICLR 2026）
- **MCP-Universe**：Salesforce出品，6领域/231任务，跨域性能差异显著
- **MCP-Bench**：Accenture出品，28 MCP服务器/250工具，多面评估框架
- **UniToolCall**：统一工具学习框架，Qwen3-8B微调后Hybrid-20达93.0%单轮精度
- **MM-ToolSandBox**：视觉工具调用（多图像+多轮+状态化），当前最佳模型仍低于成功率门槛

---

## 专业Function Calling模型

### xLAM (Salesforce Large Action Model)
规模族：1B / 3B / 7B / 70B / 8x22B。明确function calling专项训练。

**vLLM调用**：`--tool-call-parser xlam` + 对应chat template
- Llama基座用：`xlam` parser + `tool_chat_template_xlam_llama.jinja`
- Qwen基座用：`xlam` parser + `tool_chat_template_xlam_qwen.jinja`

**推荐场景**：xLAM-7B是边缘/移动端最强小模型；70B用于企业生产。

### Hermes-Pro / Hermes 4 (Nous Research)
vLLM支持：`--tool-call-parser hermes`。覆盖Hermes 2 Pro*/Hermes 2 Theta*/Hermes 3*。
- `<tool_call>` XML标签格式输出
- 注意：Hermes 2 Theta因merge步骤导致tool call质量下降

**推荐场景**：社区agent工作流主流选择。

### NexusRaven V2 (13B)
完全开源（Apache 2.0），不依赖任何GPT系数据。
- 单轮零样本函数调用强
- 支持嵌套调用+并行调用
- 可生成详细解释（可关闭以节省token）
- vLLM原生支持

### Watt-Tool (70B / 8B)
Apache 2.0许可。70B达85.0% BFCL，与xLAM-70B（82.7%）竞争。

---

## MCP评测方法论关键洞察

### MCP专用基准对比
| 基准 | 服务器数 | 工具数 | 查询数 | 评分方法 |
|------|---------|--------|--------|---------|
| MCP-AgentBench | 33 | 188 | 600 | MCP-Eval (LLM-judge) |
| MCP-Universe | 多域 | - | 231 | 细粒度评估器 |
| MCP-Bench | 28 | 250+ | - | 多面框架 |
| MCP Atlas | - | - | - | 标准化评分 |

### Tool Description质量是关键瓶颈
(arXiv:2602.14878v1) 研究了856个MCP工具描述，发现：
- 工具描述质量对agent性能影响巨大
- 当前模型在多图像工作记忆上存在瓶颈
- 描述增强（description augmentation）可显著提升BFCL分数
- 不同规模模型表现出不同的失败模式

### Toloka 12类失败分类法（生产诊断）
**工具执行故障**：选错工具/参数无效/顺序错误/漏用必需工具
**数据接地问题**：误读返回数据/实体混淆/遗漏必需字段/引用未检索数据
**推理失败**：多步约束跟踪/策略应用错误/无依据推断/领域知识缺口

---

## 生产选型建议

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 最高质量通用agent | Qwen3-235B-A22B (Tool Mode) | BFCL 88.5%，开源最强 |
| 单GPU生产agent | Qwen3-32B (Tool Mode) | BFCL 85.7% |
| 企业Apache 2.0合规 | Granite 3.3 8B / Qwen3-32B | |
| 边缘/移动端 | xLAM-7B / NexusRaven-13B | 最低硬件需求 |
| MCP协议集成 | Claude Opus 5 | MCP Atlas 85.8% |

---

## vLLM Tool Calling配置速查

```bash
# Hermes模型
vllm serve <model> --tool-call-parser hermes

# xLAM (Llama基座)
vllm serve <model> --tool-call-parser xlam \
  --chat-template examples/tool_chat_template_xlam_llama.jinja

# xLAM (Qwen基座)
vllm serve <model> --tool-call-parser xlam \
  --chat-template examples/tool_chat_template_xlam_qwen.jinja

# Qwen原生 (Hermes风格tool use)
vllm serve <model> --tool-call-parser hermes
```

---

## 关键发现

1. **开源已接近闭源**：Qwen3-235B-A22B (88.5%) vs Claude 4.7 Opus (92.0%)，差距<4%
2. **MCP协议成主流**：Anthropic推动的MCP正在成为agent工具调用标准协议
3. **Tool Description优化**：MCP工具描述质量直接影响agent执行正确率，是易被忽视的优化点
4. **专业模型vs通用模型**：xLAM/NexusRaven等专用模型在特定场景优于通用模型
5. **评测harness影响巨大**：同一模型在不同harness下分数差异可达17+分

---

## 来源

- [Presenc AI: Open-Weight Function Calling 2026](https://presenc.ai/research/open-weight-function-calling-tool-use-2026)
- [Awesome Agents: Function Calling Leaderboard](https://awesomeagents.ai/leaderboards/function-calling-benchmarks-leaderboard)
- [BenchLM: MCP Atlas Leaderboard](https://benchlm.ai/benchmarks/mcpatlas)
- [Toloka: MCP Evaluations](https://toloka.ai/blog/how-to-test-ai-agents-in-real-environments)
- [ICLR 2026: MCP-Bench](https://iclr.cc/virtual/2026/poster/10008216)
- [arXiv: UniToolCall](https://arxiv.org/pdf/2604.11557v1.pdf)
- [arXiv: MCP Tool Description Quality](https://arxiv.org/html/2602.14878v1)
