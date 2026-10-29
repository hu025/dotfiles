---
name: kv-cache-compaction-2026
description: Agent上下文的KV-cache级压缩：token eviction vs attention matching、proxy query选择、错误有界删除、prefix-preserving调度。用于长程agent的上下文预算设计。
description_zh: Agent上下文的KV-cache级压缩：token eviction vs attention matching、proxy query选择、错误有界删除、prefix-preserving调度。
trigger: KV缓存|上下文压缩|compaction|token eviction|attention matching|proxy query|长程agent|上下文预算|context budget|prompt cache
updated: 2026-10-23
---

# KV-Cache 级上下文压缩（2026 新证据）

> 与 `agent-long-context-memory` 互补：那份讲**应用层记忆/检索**（存什么、怎么找）。
> 这份讲**推理层压缩**（缓存里哪些 KV 可以扔、什么时候扔、扔了会错多少）。

## 1. 核心发现：删除时机比删除规则更重要

LAM（Argonne, 2026）在 600 条 agent 轨迹上的关键结论：

| 调度方式 | 建模端到端耗时 | 占比 |
|---|---|---|
| 已 prefill 后就地删除（需重算后缀） | 1,186,000 s | 98.6% 花在压缩+重prefill |
| 到达时先测、先删，再 prefill | 16,600 s | 压缩开销仅 0.1% |

**71.4×–91.6× 的端到端加速**，且与删除规则无关——任何 prefix-preserving 的测试都适用。原因：删除已 prefill 的记录会移动后续位置，失效其 KV 条目；而在 prefill 之前测试新到达的记录，缓存前缀完整存活，压缩逻辑还能在 CPU 上跑、加速器继续服务。

**可移植规则**：设计压缩时，永远在「记录进入 prefill 之前」做判断，不要「事后修剪已有上下文」。这一条改造成本极低，收益量级最高。

## 2. 两种压缩家族：TE 比 AM 更稳健

在线（online）场景中 agent 必须在**未来相关性未知**时压缩，且压缩耗时要算进运行时预算。

- **Token Eviction (TE)**：用 proxy query 给缓存位置打注意力质量分，保留最高分位置的**原始 KV**。零重建成本。
- **Attention Matching (AM)**：同样做 key 选择，但额外拟合一个加性注意力偏置 + 重建 value，使压缩后缓存的注意力输出逼近全量缓存。更准，但有拟合开销。

**实测（BROWSECOMP-PLUS / WIDESEARCH，Qwen3.5 & Gemma-4 多尺度）**：
- TE 在 KV 减少 **80%** 的同时保留大部分准确率，吞吐甚至优于不压缩基线。
- **代理信号不完美时，TE 比 AM 更鲁棒**——这是选型的决定性依据。

## 3. Proxy Query 是核心设计变量

这是本文档最实用的一节。三种廉价 proxy 源，按质量排序：

| Proxy 源 | 机制 | 实测表现（Qwen3.5-27B, ratio 0.2） |
|---|---|---|
| **Boundary** | 当前轮的边界/首尾 token 作为 query | 立即压缩：48.25；延迟1轮：**52.75**（最佳） |
| **Repeat-prefill** | 轻量重跑 prefill 取查询向量 | 立即压缩：41.75（塌陷最严重） |
| **Delayed future-generation** | **用 agent 自己后续生成的下一轮作为 proxy**，延迟1轮再压缩 | **52.00**（几乎无损） |
| 不压缩基线 | — | 52.50 |

**两条硬结论**：
1. **立即压缩通常有害**。用当前轮的信号去决定要保留什么，代表不了几轮之后的用法。
2. **延迟一轮、用 agent 自己的未来查询做 proxy，能挽回绝大部分差距**（48.25 → 52.00+）。代价是压缩后移到下一轮，而 agent 本来就要生成那一轮。
3. **堆更多 proxy 源反而可能变差**（TE + boundary + tool response = 46.75，低于只加 assistant generation 的 52.00）。加信号不是免费的。

> 转译到 agent 框架层：不要在工具结果返回后立刻决定丢弃什么；等下一轮模型输出成形后，再回头裁剪上一轮。这与 LAM 的 prefix-preserving 调度是同一原则的两面。

## 4. 错误有界的删除（LAM）

LLM 摘要压缩的问题是**没有信息损失上界**。LAM 给出确定性规则 + 界：

- **第一层**：精确哈希（复用同 KV block 的既有机制）抓完全重复。
- **第二层**：单位归一化 embedding 下 `‖a − b‖₂ ≤ δ` 时合并近重复 —— 这是 query-free 测试，等价于余弦的 merge 阈值。
- **定理 1**：每个被删记录都保留了一个 δ 距离内的代表，因此**对任意单位 query，最大检索分数下降至多 δ**。

⚠️ **界的范围**：这是**分数扰动的界，不是排序不变的证书**。作者明确区分了这两者，任务表现单独评估。引用时不要夸大。

**证据保留实测（600 条 SWE 轨迹）**：
- 删除 22.47% observation token，保留 **99.984%** gold-patch 证据。
- 保留阈值 0.999 时，**所有 observation-masking 配置都不达标**；SemDeDup 删 19.60%（略少）。
- 删除率随上下文规模增长：1K token 时 0.80% → 33K 时 25.58%。
- 不同 scaffold 差异大：LHTB（28 个模型 1,459 条轨迹）删 33.39%，SWE-smith 13.81%，LoCoMo 对话式近乎无收益。

**成本**：每到达一次 18.1 ms（p99 115 ms）。若存储层已有 embedding，成本降到 1.49 ms（vs 纯 L0 的 0.0963 ms）。embedding 编码占 T=10⁶ 时总成本的 99.989% —— **先把 embedding 缓存做对，比优化去重规则收益大得多**。

**增长记账的坑**：到达去重后上下文是 `C ← C + Δ(1−r)`，不是 `C ← C(1−r)`。后者每轮都对全量上下文重复计算同一批重复项。硬预算下所有方法最终都撞到 `B_ctx`，所以额外去重在延迟上是 1.00× 收益 —— 它买的是**更晚驱逐非冗余内容**（质量效应），不是延迟效应。建模时要如实这样记账，否则会高估收益 1.22×。

## 5. KV-streams：训练侧对齐（RL 场景）

把「删除的 turn 的 KV 保留下来」+「自定义 attention mask 在训练时屏蔽同一段」，使推理与训练看到**同一条淘汰历史**。

- 若 serving 忘了某 turn 而训练仍能看见，两条路径会学到并执行不同的策略 —— 这是必须成对修改的原因。
- 在受控检索任务上，RL 本身能教会模型「从缓存条目中召回一个事实，即使引入它的那一轮已被删除」。
- 与保留策略**正交**：不提出更好的摘要或更优选择规则，只改缓存计算的生命周期。

## 6. 反直觉警告：Semantic Materialization

「删掉源事件后没观察到精度下降」**不能证明源事件不必要**。

在稀疏 Event-KV serving 中测试：在其他完全相同的历史里省略一个早期 observation，服务下游事件的答案**绝大多数会跟随被省略的值**，尽管没有任何被服务的片段说过哪个值才对。这被称为 semantic materialization：下游事件的缓存行独立承载了「输入已消失的计算」。

- 故意措辞、**不含答案**的事件能把 donor-aligned recovery 从 6% 提到 **51%**（Qwen3-8B）。
- 被动 harvest 自然对话中的提及则无检出收益。
- 承载内容是**有界且特异的**：紧凑状态能存活，大载荷衰减至随机水平。
- 构造是否写入**取决于措辞而非仅含义** —— 两个模型理解程度相同的措辞可能结果截然不同。

**对 eviction 策略的含义**：任何「丢了没掉分就说明可以丢」的实证结论都需要重新审视。

## 7. 实施清单

给 Hermes / 自建 agent loop 的可执行顺序：

1. **调度先于规则** —— 压缩判断放在 prefill 之前，不要事后修剪。这是最大的单项收益，且与用哪种规则正交。
2. **去重优先于摘要** —— 到达时先跑确定性去重（哈希 + 阈值近重复），只有剩余内容才值得送 LLM 摘要。
3. **复用 embedding** —— 存储层已有 embedding 就复用；否则编码成本会吃掉全部预算。
4. **延迟压缩一轮** —— 用 agent 自己下一轮的生成作 proxy，而非当前轮信号。必要时可开一个 token 级预算，观察「保留最近 k 条 + 显式声明焦点」的滑窗策略，暂不做 TE/AM 级 KV 压缩。
5. **记录可恢复性** —— Session snapshot / event log / checkpoint 使长程运行可检查、可恢复、可回放（与 `AgentForge` 的 Persistence 三层一致）。
6. **基准别只跑 LoCoMo** —— 对话式记忆里近重复稀少、收益接近零；用真实 agent 轨迹（SWE / BrowseComp 类）评估才有区分度。

## 8. 来源

- LAM: A Lossy Agent Memory Framework With a Retrieval-Score Error Bound — https://arxiv.org/abs/2609.32256
- Practical Online KV Cache Compaction for LLM Agents: An Empirical Study — https://arxiv.org/pdf/2608.00902
- KV-streams for Efficient Compaction in Agentic RL — https://arxiv.org/abs/2609.35750
- Compute Globally, Materialize Locally: The Memory Contract of Sparse Event-KV — https://arxiv.org/pdf/2607.23693
- Kamera: Position-Invariant Multimodal KV Cache — https://arxiv.org/abs/2606.23581

## 9. 引用纪律

这批工作多数为 2026 年预印本，**未经同行评审**。数值结论（22.47%、99.984%、71.4–91.6×、80%、6%→51%）均来自各论文自身的实验设置，不要跨论文比较，也不要当作普适常数。定理 1 只界分数扰动，不界排序或任务结果。