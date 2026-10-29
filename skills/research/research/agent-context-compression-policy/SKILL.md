---
name: agent-context-compression-policy
description: Agent上下文压缩策略的2026实证结论：token减少≠成本减少≠成功。含压缩三轴（primitive/trigger/depth）、三条杠杆成本归因（工具schema过滤/内容压缩/历史摘要）、线性vs二次scaling law、recall trap、模型依赖性。用于设计或评估agent的上下文压缩策略。
description_zh: Agent上下文压缩策略的2026实证结论：token减少≠成本减少≠成功。含压缩三轴、杠杆成本归因、scaling law、recall trap。
trigger: 上下文压缩|context compression|compaction|压缩策略|token节省|压缩率|context pruning|summarization|上下文预算|工具schema过滤|tool filtering|recall trap
updated: 2026-10-23
---

# Agent 上下文压缩策略：2026 实证证据

> 与 `research/kv-cache-compaction-2026` **互补不重叠**：
> 那份讲**推理层**（KV-cache 里哪些条目可扔、proxy query 怎么选、错误界）。
> 这份讲**agent loop 层**（压缩什么/什么时候压/压多少，以及压完到底省不省钱）。

---

## 0. 一句话核心结论（最高价值）

> **Token 减少 ≠ 成本减少 ≠ 成功。**
> 三个轴彼此独立，必须分别测量。任何只报"压缩率"的结论都是不完整的。

三篇 2026 年独立研究互相印证：

| 研究 | 样本 | 核心反直觉发现 |
|---|---|---|
| Beyond Token Savings (2609.32961) | 65 policy × 3 model × 2 benchmark，~35,000 次 agent run | 用 1/3 token 的策略，**耗时反而长 20–80%** |
| Token Reduction Is Not Cost Reduction (2607.12161) | Claude Code 生产 trace，100 Haiku task | 压掉 38.4% tool-output token，**账单反而涨 6.8%** |
| Cost Attribution of Compression Gateways (2609.22114) | Paritok 生产网关，Claude Code + Codex | tool-filter 节省是 content 压缩的 **20:1–33:1** |

---

## 1. 压缩策略三轴（可移植的设计空间）

来源：Beyond Token Savings, arxiv 2609.32961（UT Austin, 2026-09）

一个完整压缩策略 = **primitive（怎么压）× trigger（何时压）× depth（压多少）**。

### 1.1 Primitive —— 压什么

| 家族 | 代表 | 机制 | 保留决策依据 |
|---|---|---|---|
| 规则型 | **TR** Truncation | 删最老的 assistant message + tool result | **recency（时间）** |
| 规则型 | **TRC** Tool-Result Clearing | 老 tool output 换成 `[output cleared]`，保留交互结构 | **content type（内容类型）** |
| LLM 型 | **SU** Summarization | LLM 改写成短摘要 | 语义 |
| LLM 型 | **SU-p** Partial Summarization | 只摘要老部分，近期交互逐字保留 | 语义 + recency |
| LLM 型 | **SS** Structured Summary | 摘要但保留预定义信息类别 | 语义 + 结构 |
| LLM 型 | **SS-p** | Structured Summary 的 partial 版 | 同上 + recency |
| 堆叠型 | **TRC+SU / TRC+SS / OTRC+SU-p** | 先清 tool output 再摘要 | 组合 |

**关键区分**：TR 按"新旧"决定保留什么，TRC 按"内容类型"决定保留什么。这是两种完全不同的策略，不是同一策略的强弱版本。

> **TRC 是 2026 年最被低估的策略**：在 SWE-bench 上几乎无损匹配 full context（resolve rate 53.7% vs 53.7%），同时 token 0.57×、latency 0.79×、billed cost 0.71×。

### 1.2 Trigger —— 何时压

- **Threshold trigger (Th)**：token 超阈值触发。
- **Step trigger (St)**：每步都触发。
- **Stacked (St+Th)**：两者结合。

**阈值必须按模型标定，不能用绝对 token 数**。正确做法：先跑无压缩轨迹，统计每条轨迹的 **peak per-call context**，再取其 **5th / 15th / 25th 百分位**作为 tight / primary / loose 三档。理由：不同模型的 context 需求分布差异巨大，统一阈值会让比较失效。

实测阈值示例：Qwen3.5-35B SWE-bench 用 10K / 15K / 20K；Devstral-24B 用 17K / 21K / 24K；Terminal-Bench 上 Qwen 用 2K / 3K / 4K。

### 1.3 Depth —— 压多少

```
D = 1 - (target tokens / current tokens)
```

D=0.5 表示压到一半。D ∈ {0.3, 0.5, 0.7} 为常见扫描点。

- **depth-tunable**：TR / SU / SS 类（保留多少可调）。
- **depth-invariant**：TRC（有效深度由操作本身决定）。

---

## 2. 三条核心实证结论

### 2.1 结论一：延迟压缩 > 早期压缩（Trigger 效应）

Qwen SWE-bench，阈值 10K→20K，D=0.5：

| 指标 | 10K | 20K |
|---|---|---|
| 压缩次数/attempt | 4.85 | **1.15** |
| SU resolve rate | 50.7% | **62.7%** |
| 输入成本 | 1.10× | **0.92×** |
| 延迟 | 653s | **599s** |

**规则：把阈值放宽到 20K（3-4 倍于 primary）几乎总是赢。** 少压几次 > 压得更狠。跨所有被测 primitive 都成立。

### 2.2 结论二：depth 效果**依赖 primitive，方向相反**

同一 15K 阈值下：

| Primitive | D 0.3 → 0.7 的 resolve rate 变化 | 成本/延迟 |
|---|---|---|
| **TR** | 61.3% → 50.7%（**掉 10.6pp**） | 成本↓ 延迟↑ |
| **SU** | 50.7% → 60.0%（**涨 9.3pp**） | 成本↓ 延迟↓ |

15 个 primitive-threshold 组合中：**浅压缩 8 次给出最高 resolve rate，深压缩 8 次给出最低成本、7 次给出最低延迟**。

> **可操作推论：摘要类 primitive 可以调深，截断类不要调深。** 截断丢的是"最早的推理"，摘要丢的是"细节"。

### 2.3 结论三：任务级结果会漂移，聚合指标掩盖真相

Qwen SWE-bench，100 任务，FC 解 53 / 漏 47：

| Policy | 新解出 | 丢失 | 总解出 |
|---|---|---|---|
| TRC+SU | 7 | 8 | 52 |
| SS-p | 7 | 9 | 51 |
| TR | 3 | **14** | **42** |

TRC+SU 总数 52 vs FC 53，看起来"几乎无损"，但**它解的题和 FC 解的题不是同一批**。

> **规则：评测压缩策略必须做 task-level 的 gains/losses 分解，不能只看聚合 resolve rate。** 建议判据：任务在 ≥2/3 次尝试成功时算解出。

---

## 3. 成本归因：三条杠杆完全不同的收益结构

来源：Cost Attribution of Context-Compression Gateways, arxiv 2609.22114（Paritok, 2026-08）

多轮 agent 账单公式（Anthropic Messages 定价示例）：

```
Cost = Σ_{t=1..N} ( c_cr·P_t^cached + c_in·P_t^new + c_out·O_t )
       c_in = $3/M, c_cr = $0.30/M (cache-read 便宜 10×), c_out = $15/M
```

### 3.1 成本模型的两个直接推论

1. **Turn count 是一阶变量**。同一任务同一配置实测在 **7 到 18 轮**之间摆动。这个方差**压倒**任何 2% 的单轮压缩效应。
2. **省下的 token 不等价**。从重发 prefix 里省掉的是 **cache-read** token（$0.30/M），不是 fresh input（$3/M）。

### 3.2 三条杠杆实测对比

| 杠杆 | 机制 | 单轮收益 | 累计增长 | 可靠性 |
|---|---|---|---|---|
| **① Tool-schema 过滤** | 本地 embedding 筛工具，保留 selection **冻结**（cache 友好） | **~21K–57K token/轮** | **线性 ≈ 21,000·N** | ✅ 唯一"无条件可复现为正" |
| **② 内容压缩**（file read / tool output） | 4B 代码压缩模型压到 ~26% | **~1.5–2K token/轮（~2% prefix）** | **二次 ≈ 3,350·N²** | ⚠️ 依赖会话长度与 recall 率 |
| **③ 历史摘要** | 窗口满时摘要陈旧历史 | — | — | 价值是**容量**不是省钱 |

实测隔离数据（MCP 开启）：

| Session | tool-filter 省 | content 省 | 比值 |
|---|---|---|---|
| jinja2（12 req） | 392,000 | 18,000 | **~20:1** |
| rich（34 req） | 1,220,000 | 28,000 | **~33:1** |

### 3.3 Scaling law：线性 vs 二次

内容压缩累计节省实测：3,466 → 14,051 → 31,712 → 56,412 → **83,710**（turn 1→5）

拟合 **≈ 3,350·N²**（每 N² 比值落在 3.35–3.53×10³）。机制是复利：压缩后的 block 留在 history 里，之后每轮都被重发（cache-read），所以**单轮节省本身也在线性增长**。

**交叉点：3,350·N² = 21,000·N → N ≈ 6。**
- 前 ~6 轮：tool-filter 是主要杠杆。
- 6 轮之后：内容压缩反超，差距按二次拉开。
- 但二次不会无限增长：**未压缩 prefix 在 turn 5 已达 87K/轮**，约 turn 12–15 撞上 ~200K 窗口，客户端 compaction 触发，曲线被压平。

> **两个杠杆不是替代品，是增长指数不同的互补品。**

### 3.4 "Proxy tax"：走代理反而更贵

实测 Claude Code：
- `base_url=api.anthropic.com` → **~40K token/轮**工具块
- `base_url=127.0.0.1`（任何代理）→ **~57K token/轮**工具块

**代理本身多收 ~17K token/轮的"过路费"。** 因此过滤掉不相关工具的代理，可能反而比直连更便宜（实测 Sonnet edit 任务：$0.043 vs $0.057）。

> **Hermes 落地提示**：Hermes 自己带 MCP，工具 schema 常常是 prompt 里最大的固定块。任何 prompt 优化，**先量工具块占多少**，再谈压缩历史。

---

## 4. Recall Trap：可逆压缩的隐藏账单

非破坏性压缩（保留原文，agent 可按需 recall 原文）的代价模型：

```
内容压缩净收益 = 累计二次节省 − (recall 次数 × 一个压缩段的长度)
```

**每次 recall 的成本是固定的、有界的**——就是那一段被压缩文本的长度。不是乘法爆炸，因为：
- 累计 prefix 本来就已在 cache 里（cache-read 价），无论 recall 与否下一轮都要重发；
- recall 的原文是**临时**的：只在那一个 turn 返回原始字节，下一轮立刻回退成 `[REF:id]` stub，不会永久撑大 prefix。

实测：
- 摘要已能支撑的改动（如 `max_retries=-1`）→ recall=0 → 压缩净正（~6.5% 输入 token 减少，dollar-neutral）。
- 需要精确原始字节的改动（精确多行替换）→ 稳定 recall 2 次 → 每次成本一个压缩段。

**删除 recall 工具是灾难**：agent 改用 grep/cat/重读来重建精确字节 → **46 轮 / $1.85 = 保留 recall 的 3.2× 成本**。

> **规则：可逆性（recall）必须保留，它有独立于成本的价值。但要在预算里扣掉每次 recall 一个压缩段。**
> 净收益符号只由两个变量决定：**会话长度**（越长越好）和 **recall 频率**（越低越好）。任务叫什么名字不影响。

---

## 5. 模型依赖性：不要跨模型搬运结论

### 5.1 同一策略，不同模型，效果相反

同一 OTRC policy：

| 模型 | resolve rate | latency |
|---|---|---|
| Qwen3.5-35B-A3B | 51.3% | 0.88× |
| GLM-4.7-Flash | 41.3% | 0.94× |
| **Devstral-Small-2-24B** | **38.7%（掉）** | **1.42×（变慢）** |

**策略排序甚至会反转**：OTRC 相对 TR 在 Qwen 上 +7.0pp，在 Devstral 上 **−17.0pp**。

### 5.2 但有些设计选择在所有模型上都有效（可复用组件）

SWE-bench 上三个模型全部受益：

| 设计选择 | Qwen | Devstral | GLM |
|---|---|---|---|
| SS-p vs SS（partial 保留近期原文） | +6.7pp | +8.7pp | +8.0pp |
| TRC+SS vs SS（先清 tool output 再结构化摘要） | +7.7pp | +9.7pp | +9.7pp |

**不跨模型通用的**：OTRC vs TRC（每步清 vs 阈值清）= −2.3 / −14.3 / +2.7pp。
**不跨 workload 通用**：OTRC+SS-p vs OTRC 在 Terminal-Bench 上 −12.5 / −7.5 / −12.5pp。

> **可复用的组件 = "保留近期原文" + "先清 tool output"。不可复用的 = 具体触发频率和深度。**

### 5.3 Summarizer 模型敏感度（反直觉）

固定 Qwen agent 换 summarizer（25 任务 SWE-bench）：

| Summarizer | SU resolve rate | TRC+SU |
|---|---|---|
| 自摘要（agent 自己） | **53.3%** | 68.0% |
| Qwen3.5-9B | 37.3% | 62.7% |
| Gemma-4-12B | 28.0% | 66.7% |

**小模型 summarizer 没有降低成本，只是降低了成功率。** 且**换成 TRC+SU（先清 tool output）后，summarizer 的影响被大幅吸收**（68.0 → 62.7/66.7，跌幅远小于纯 SU）。

> **规则：优先用规则型 primitive 先减负，再让 LLM 摘要剩下的。** 这样对 summarizer 能力的依赖下降。

---

## 6. 端到端效率的正确测量方法

来源：Token Reduction Is Not Cost Reduction, arxiv 2607.12161（PointFive, 2026-07）

实测 Claude Code，100 个 Haiku task：

- RTK-ML arm：tool-output token 从 5.62M 降到 3.46M delivered（**−38.4%**），但 **billed cost 反而 +6.8%**。
- **tool-output 减少量与 billed cost 变化的相关性极弱**：Pearson r=0.154 [−0.051, +0.356]，Spearman ρ=0.013 [−0.082, +0.339]。Pearson 区间**跨过零**。
- 去掉 5 个最高削减任务后，Pearson 升到 0.24；只在 68 个"真路由了输出"的任务上算，r=0.13 [−0.09, +0.36]。
- **削减高度集中**：100 个任务里 87 个削减 <0.1%；5–20% 区间的 4 个任务平均成本变化 **+24.7%** [+6.3, +46.0]。
- **内生性问题**：压缩 arm 会发不同的命令、走不同轨迹，raw-output 暴露量部分由模型自己行为决定，不是外生处理的剂量。

### 6.1 机制：压缩会改变轨迹

压缩掉的内容让 agent 需要**额外检索、诊断、测试、或者多跑轮次**，抵消本地 token 节省。
阶段分析显示：检索阶段节省是真实的但很小（按 cache 价计），被下游增加的诊断/测试/重检索轮次抵消。

### 6.2 强制方法论（照抄这五条）

1. **报分布，不报单次运行**。同一任务成本摆动 2×（轮次 7/10/13/16/18）。**至少 3 次**试验，比较分布。单次运行的结论反复自我反转。
2. **用 provider 报告的 usage，按 cache tier 计价**。cache-read 约为 fresh input 的 0.1×。省下的量级重要，**省在哪个 tier 同样重要**。
3. **控制工具块**。MCP server 异步加载且不确定（实测两次并发运行 40 vs 90 个工具，首轮 40K 摆动）。用 `--strict-mcp-config` 固定。
4. **去重 streaming usage**。客户端 transcript 有重复条目，按 message id 聚合。服务端 recall 在客户端 transcript 里不可见，必须从网关自己的日志计数。
5. **一次只隔离一个杠杆**。否则 proxy tax 和 MCP 抖动会污染对比。

### 6.3 成功调整后的成本才是正确指标

> **Cost per solved task**，而不是 total token。
> DTOC 实测（DeepSWE, Sonnet 4.6）：solve rate 20% → **50%**，input token −10.3%，cost per solved task **从 $26.27 降到 $8.65（−67%）**。

---

## 7. 三个 2026 新方向（可落地）

### 7.1 DTOC：可逆压缩（Dynamic Tool Output Compression）

arxiv 2609.26121（Pegasystems + Leiden, 2026-08）

**机制**：完整 tool output 存外部内存，active context 里只放 placeholder，需要时选择性重建。

**关键消融结论：可逆性是关键。**
- 只做"禁用/清空"（disable-only）的变体 → **性能退化**。
- 完整 DTOC（可逆）→ 恢复基线准确率，且 context 成本大幅降低。

实测（DeepSWE）：

| 模型 | input token | agent steps | solve rate | cost/solved task |
|---|---|---|---|---|
| Sonnet 4.6 | −10.3% | −2.4% | **2.5×** | **3× 更低** |
| GPT-5.4 | −12.7% | −32.3% | **1.5×** | **3.5× 更低** |
| GPT-5.5 | — | — | 2× | 一半 |
| 其他模型 | 混合 | 混合 | 无影响 | **负面** |

**"context rot" 是本工作的问题陈述**：自注意力 O(n²) 交互随 n 增长，模型从密集 haystack 里检索 needle 的能力退化。

> **落地：Hermes 的 tool 结果永不销毁，外部存储 + placeholder + 按需重建。** 这比"截断"和"摘要"都安全——摘要会引入幻觉风险，截断会丢信息。

### 7.2 TRACER：把压缩当成逐工具的序贯决策

arxiv 2608.29363（清华等, 2026）

**问题命名："compression–consequence gap"** —— 压缩时省下的 token，会因为下游**重新调用被压缩掉的工具**而吐回去（一次补偿性 SQL 调用可消耗数万 token）。

**方法**：轻量 REINFORCE policy，为**每个 tool output** 分配 query-conditioned 的保留比例（连续动作，Beta 分布参数化）。reward 联合三项：task success + token 效率 + **压缩后被重新调用的工具比例**。用 learned outcome model 做单工具反事实以解决 credit assignment。

**结果**：三个压缩后端上，总 token −29~46%（vs 全保留），成功率相当或更高；比 tool-type-conditional 静态 policy 再省 15–18%；跨 backbone/压缩架构迁移仍有效，LOCA-bench 5 环境上 −18~25%。

**核心洞见**：agent 会话中不同 tool output 的下游重要性差异极大——schema 查询可能每步都被引用，权限检查永远不会被回看。**uniform 策略是浪费。**

### 7.3 StateComp：学"什么时候可以压"

arxiv 2609.27298（2026-09-23）

**问题**：固定窗口/周期调度/当前相关性都忽略了更根本的问题——**一段历史什么时候才"安全"到可以被替换？**

**方法**：两阶段标注构造 KEEP / READY 监督 → 在冻结 LM 的 hidden representation 上训练 **imbalance-aware router**。有界状态表示降低评估长历史的成本；相邻 READY 交互被聚成连续 span，执行时替换成紧凑摘要。

**结果**（WorkBuddyBench）：总 agent + summarization token **−52.27%**，任务性能保持，representation 提取 **12.67× 加速**。

### 7.4 ReSum：摘要作为上下文压缩算子

- **ReSum（Web agent，arXiv 2509.13313）**：周期性调用外部摘要工具把交互历史压成 goal-oriented summary，压缩状态 q'=(q,s)，工作历史重置为 (q',)。**Training-free 平均 +4.5% vs ReAct**；ReSum-GRPO 再 +8.2%；仅 1K 训练样本。WebSailor-30B + ReSumTool-30B 在 BrowseComp-en 达 **16.0% Pass@1**，超过 Claude-4-Sonnet（12.2%）和 Kimi-K2（14.1%）。
  - **摘要必须包含三要素**：essential evidence（已有证据）、information gaps（信息缺口）、future directions（下一步方向）。
  - **摘要工具比 agent 模型小得多**：ReSumTool-30B 在 BrowseComp-zh 上 13.7% Pass@1，超过 Qwen3-235B（11.1%）和 DeepSeek-R1-671B（13.0%）作为摘要工具的表现。
  - **世界模型 vs ReSum 的区别**：世界模型做密集的、前瞻的规划以提升决策质量；ReSum 做稀疏的、回溯的上下文压缩以维持决策延续性。摘要是**偶发的上下文管理器**，不是规划器。
- **ReSum（RL 框架，arXiv 2606.13316）**：让模型自己主动摘要。**pilot 发现两条关键机制**：
  1. 自摘要**降低 token 级熵**，稳定生成。
  2. 插入"摘要"这个短语能**显著缓解错误前缀的传播**。
  - 方法：**Artifact Points**（在非摘要位置注入摘要短语，测"如果摘要了会怎样"）+ **Natural Points**（在自发摘要位置遮蔽摘要短语，测"自然摘要是否真的贡献了结果"），构成对比分支树，配 summarization-aware advantage 做细粒度 credit assignment。
  - 结果：准确率平均 **+4%**，rollout 长度 **−18.6%**。
  - **相对提升在更小的模型上更明显**（容量小的模型更容易遗忘和循环推理）。

### 7.5 Prompt 级压缩（LLMLingua 家族）的真实位置

- **LLMLingua**（EMNLP 2023）：small LM 困惑度 → 蒸馏 → token 级迭代压缩 + budget controller，20× 压缩仅掉 1.5 分。
- **LongLLMLingua**（ACL 2024）：query-aware + **文档重排以缓解 position bias**，4× 压缩下 +17.1%。
- **LLMLingua-2**（ACL 2024 Findings）：把压缩建模成 **token 分类**（binary preserve/discard），用 **Transformer encoder** 取双向上下文，比 LLMLingua 快 **3–6×**，OOD 更稳。
- **LLMLingua-2 的关键工程性质**：`strict_preserve_uncompressed`、`<llmlingua rate=0.3>` 分段压缩、budget controller 保留——**压缩是保证 faithfulness（不引入幻觉内容）的，因为它只做提取式剪枝，不生成新文本**。
- **实测开销**（per prompt）：LLMLingua-2 115ms / 0.25ms per token / 2137MB；LLMLingua 180ms / 5309MB；Selective Context 319ms / 487MB；KiS 2410ms / 1378MB。**LLMLingua-2 内存是 LLMLingua 的 40%。**
- **实测保留模式差异**：LLMLingua 系保留的 token **集中在语义丰富段**（利于摘要）；Selective Context 保留的 token **均匀分布**（利于重建）。
- **Empirical study 2505.00019**（13 数据集 / 3 模型，含多模态）：
  - (Long)LLMLingua / LLMLingua-2 **在高压缩比下总体最好**。
  - **短上下文：性能随压缩比单调下降。长上下文：中等压缩反而提升性能**（LongBench）。
  - **所有方法都增加幻觉**，主因是信息丢失。
  - 压缩影响响应长度，方向依模型而异。

> **定位：LLMLingua 家族是"单次 prompt 内"的压缩器，与 agent loop 层的 compaction 是两个正交轴。**
> **Paritok 论文的明确警告：单次 prompt 压缩基准（如 "SWE-bench Lite 保留 86.5% 质量 @ 25.7% 压缩率"）与多轮 agent 成本是正交的，不能拿它当省钱证据。** 单次基准没有工具块、不重发累积 prefix、用 fuzzy patch 应用 diff——它测的是"压缩下的单次理解"，而真实 agent 的成本差距在"多轮行为 + 工具块"。

---

## 8. 给 Hermes 的可落地建议

按"改造成本 / 收益"排序：

### 8.1 立刻可做（零风险）

1. **先量工具块占比**。Hermes 带 MCP，工具 schema 可能是 prompt 里最大的固定块。工具过滤的收益是内容压缩的 20–33 倍，且**只此一项就是线性增长**。
   - ⚠️ **绝不能 stub agent 的核心执行工具**（shell / exec / apply_patch）。实测：Codex 只有 ~9 个工具，过滤到低于 top-k 会让 agent 瘫痪（停止执行命令，转而要用户粘贴文件）。**必须白名单核心执行工具。**
   - 工具 selection **冻结**在会话内，保证 tools block byte-stable（cache 友好）。
2. **压缩阈值放宽**。把 compaction 触发点从"接近上限"改成"用满 80%+ 上下文"。实测阈值 10K→20K 让压缩次数 4.85→1.15，resolve rate +12pp，成本和延迟同时下降。
3. **TRC > TR**。清老 tool output（留 `[output cleared]` 占位）而不是删老消息。结构保留 + recency 保留，风险最低。
4. **摘要前先清 tool output**（TRC+SU）。这是唯一在三个模型上都一致提升的设计选择（+7.7/+9.7/+9.7pp），且降低对 summarizer 能力的依赖。

### 8.2 值得实现

5. **可逆压缩（DTOC 模式）**：tool 结果永不销毁，外部存储 + placeholder + 按需重建。消融证明 disable-only 会退化，可逆版本能恢复基线准确率。
   - **Hermes 已有基础**：`~/.hermes/cache/` 已经在缓存文档/工具结果。需要补的是"原始字节可按需取回"的显式接口 + 一个 recall 工具。
6. **摘要必须三要素**：essential evidence / information gaps / future directions。这是 ReSum 在 BrowseComp-zh 上击败更大模型作为摘要工具的关键。
7. **保留 recall**。删掉 recall 工具 → agent 改用 grep/cat 重建 → 成本 3.2×。这是最贵的单个错误。

### 8.3 不要做

8. **不要用单次 prompt 压缩基准（如 LLMLingua 的 20×）作为 agent 成本证据**。正交轴。
9. **不要跨模型照搬策略**。同一 OTRC 在 Qwen +7.0pp、在 Devstral −17.0pp。阈值必须按模型的 peak-context 分布标定（5th/15th/25th 百分位）。
10. **不要只报压缩率**。至少报：resolve rate、cost per solved task、latency、task-level gains/losses。

### 8.4 评测模板（照抄）

```
评测维度（缺一不可）：
  1. task success（resolve rate），≥3 次运行取分布
  2. token 用量（分 fresh input / cache-read 两个 tier 计价）
  3. cost per solved task（不是 total cost）
  4. end-to-end latency（含 tool 执行 + 压缩开销）
  5. task-level gains/losses（相对 full context 的任务集合差异）
  6. provider-reported usage，按 message id 去重
环境控制：
  - 固定 MCP 工具块（--strict-mcp-config 思路）
  - 阈值按模型 peak-context 百分位标定
  - 一次只隔离一个杠杆
```

---

## 9. 与相邻技能的关系

| 技能 | 层次 | 关注点 |
|---|---|---|
| `research/kv-cache-compaction-2026` | 推理层 | KV 条目淘汰、proxy query 选择、错误有界删除、prefix-preserving 调度 |
| `agent-long-context-memory.md` | 应用层 | 存什么、怎么检索、Memory vs Context |
| `research/memm-ai-context-os` | 存储层 | 文件为 canonical 存储、L0/L1/L2 分层 |
| **本技能** | **agent loop 层** | **压什么/何时压/压多少，以及压完省不省钱** |

---

## 10. 来源

- Beyond Token Savings: A Systematic Study of Context Compression in LLM Agents — arXiv:2609.32961 (2026-09-26, UT Austin) — https://arxiv.org/abs/2609.32961
- Token Reduction Is Not Cost Reduction: An Empirical Study of End-to-End Efficiency in API-Based Coding Agents — arXiv:2607.12161 (2026-07, PointFive) — https://arxiv.org/abs/2607.12161
- An Empirical Cost Attribution of Context-Compression Gateways in Multi-Turn Coding Agents — arXiv:2609.22114 (2026-08-19, Paritok) — https://arxiv.org/abs/2609.22114
- DTOC: Dynamic Tool Output Compression for Adaptive Context Management in AI Agents — arXiv:2609.26121 (2026-08-06, Pegasystems + Leiden) — https://arxiv.org/abs/2609.26121
- TRACER: Per-Tool Context Retention for LLM Agents via Consequence-Attributed RL — arXiv:2608.29363 (2026) — https://arxiv.org/abs/2608.29363
- StateComp: Learning When to Compress History in Long Horizon Agents — arXiv:2609.27298 (2026-09-23) — https://arxiv.org/abs/2609.27298
- ReSum: Unlocking Long-Horizon Search Intelligence via Context Summarization — arXiv:2509.13313 (Alibaba-NLP) — https://github.com/alibaba-nlp/deepresearch/blob/main/WebAgent/WebResummer/README.md
- ReSum: Synergizing LLM Reasoning and Summarization with Reinforcement Learning — arXiv:2606.13316 (2026) — https://arxiv.org/abs/2606.13316
- Evaluating Memory Condensation Strategies for Coding Agents in Data-Driven Scientific Discovery — arXiv:2605.18854 (2026-05-13) — https://arxiv.org/abs/2605.18854
- Less Context, Better Agents: Efficient Context Engineering for Long-Horizon Tool-Using LLM Agents — arXiv:2606.10209 (2026) — https://arxiv.org/abs/2606.10209
- An Empirical Study on Prompt Compression for Large Language Models — arXiv:2505.00019 — https://arxiv.org/abs/2505.00019
- LLMLingua — arXiv:2310.05736 / EMNLP 2023 — https://arxiv.org/abs/2310.05736
- LLMLingua-2 — arXiv:2403.12968 / ACL 2024 Findings — https://arxiv.org/abs/2403.12968
- Prompt compression toolkit — https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression
- Paritok-4B (open source, Apache 2.0) — https://github.com/Paritok-official/paritok-4b-v1
