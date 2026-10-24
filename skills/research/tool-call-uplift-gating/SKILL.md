---
name: tool-call-uplift-gating
description: 工具调用该不该做、有没有用——tool-use tax、counterfactual margin、hidden-state probe、pre-call gate 四条主线。Use when designing tool/skill gating, diagnosing over-calling or harmful tool calls, or asking "does this retrieved tool actually improve the agent?".
triggers: [tool-use tax, tool uplift, counterfactual margin, CoBRA, ToolGate, Probe&Prefill, When2Tool, tool necessity, tool gating, pre-call gate, execute-skip, 工具调用收益, 工具税, 反事实边际, 工具必要性, 调用门控, 过度调用, 工具伤害]
owner: hermes-evolution
created: 2026-10-24
updated: 2026-10-24
paper: 多篇合流 — arXiv:2605.00136 (Tool-Use Tax) / arXiv:2609.00967 (CoBRA) / arXiv:2605.09252 (When2Tool, Probe&Prefill) / arXiv:2606.03054 (ToolGate) / arXiv:2604.04949 (LRAT, SIGIR 2026)
code: ToolGate = https://github.com/iamlilAJ/toolgate（MIT, 1★, EMNLP 2026, 2026-08-21 最后推送）✅ | When2Tool = https://github.com/Trustworthy-ML-Lab/when2tool（20★, 2026-09-30 最后推送）✅ | CoBRA / Tool-Use Tax / LRAT = **未公开**（2026-10-24 核验 arXiv abs+html 页无 github 链接）
related_work: https://arxiv.org/abs/2609.36805 (UpliftMem, 记忆集合级 uplift — 见 upliftmem-evsi-probing 技能) / https://arxiv.org/abs/2601.11888 (Agentic-R) / https://arxiv.org/abs/2610.21267 (TRACER, 轨迹感知工具检索) / https://arxiv.org/abs/2607.17751 (MagicSelector) / https://arxiv.org/abs/2609.16268 (Spurious Tool Use)
tags: [tool-use, gating, counterfactual, uplift, hidden-state-probe, pre-call-control, over-calling, agent-skills, hermes-self-improvement]
---

# 工具调用的边际收益 — 从"要不要调"到"调了有没有用"

## 概述

**一句话**: 检索有"相关性"和"uplift"两条线（见 `uplift-rag` / `upliftmem-evsi-probing` 技能），但**工具调用这一层有第三个、也是最容易被忽略的问题：这次调用到底该不该做？** 四篇 2026 年的工作从不同角度独立撞上同一件事：

> 工具不是越多越好。**调用的边际收益可以为负**，而且模型**早就知道**该不该调，只是说不出来。

本技能把这四条线合成一套可直接落地的判断框架：

| 主线 | 回答的问题 | 核心机制 |
|------|-----------|---------|
| **Tool-Use Tax** (2605.00136) | 工具为什么有时**反而更差**？ | 因子分解：格式成本 / 协议开销 / 真实收益 |
| **CoBRA** (2609.00967) | 该调还是不调？ | 反事实 margin 分区（内/外/模糊） |
| **When2Tool** (2605.09252) | 模型**自己**知道答案吗？ | hidden-state 线性探针（AUROC 0.89–0.96） |
| **ToolGate** (2606.03054) | 怎么在**执行前**拦掉有害调用？ | 轻量外部门控（execute/skip） |

**为什么 Hermes 特别需要这个**: Hermes 有 200+ 技能 + 一堆 MCP 工具 + 记忆召回。技能列表越长，**过召回（over-retrieval）**和**协议税（protocol tax）**越严重——每次把一个 2000 行的 SKILL.md 塞进上下文都要付 token 成本，而且塞错了不只是浪费，是**污染推理链**。

---

## 一、Tool-Use Tax：工具为什么反而更差

### 1.1 七条件因子分解

论文把 "CoT vs Agent-Full" 的差距拆成一条链：

```
NoTool-CoT → NoTool-FCStyle → Agent-NoopTool → Agent-Full
```

（外加三个诊断探针：`Agent-OracleCalc` / `Agent-OracleEvid` / `Agent-Max1Turn`）

三个分量：

- **Δ_frc（格式成本）**：把答案改成 function-calling 格式本身的损失
- **Δ_cmp（真实计算收益）**：真正执行工具带来的增益
- **Δ_sty（协议开销）**：进入 FC 循环后的额外损耗（早停、under-computation、证据漂移）

**核心不等式**：

```
工具净收益 = Δ_cmp − |Δ_frc| − |Δ_sty|
```

### 1.2 实测数字（Qwen3-4B，GSM8K）

| 条件 | Accuracy |
|------|----------|
| NoTool-CoT | **85.44** |
| NoTool-FCStyle | 84.84 |
| Agent-NoopTool | 30.64 ← 只换格式不执行，崩了 |
| Agent-Full | 52.08 |

**Agent-NoopTool 30.64% 这个数字是全篇最狠的一条**：把答案包装成 tool-call 格式但**不真正执行**，准确率从 84.84 崩到 30.64。这证明 **Δ_frc 和 Δ_sty 主要是格式与协议本身的成本，不是工具不好用**。

- GSM8K 上 Agent-Full 比 CoT 低 **14.12–33.36%**
- HotPotQA 上只低 **0.62–2.47%** → 工具税**强烈依赖任务类型**：串行计算任务税重，检索型 QA 税轻

### 1.3 Capability Overlap Principle（能力重叠原则）

> 很多"工具带来的收益"，其实是模型原生 CoT 就能做到的**冗余收益**。

论文测量 "tool-benefited" 样本（Agent-Full 对、NoopTool 错）中，有多大比例 CoT 也能做对。重叠越高，工具增益越抵不上协议税。

**这条对 Hermes 的直接含义**：如果一个技能的内容 90% 是模型本来就会的事（"用 python 算一下"、"查一下当前时间"），那加载它的净收益可能为负——你付了 token 和注意力成本，换来的是冗余信息 + 一次格式切换。

### 1.4 失败分类与归因（诊断用）

**轨迹级失败分类 A–F**（按固定优先级）：
- Type A: Under-computation（工具步数不够，没完成目标计算）
- Type C: 证据选择错误（distractor 敏感）
- Type D: 规划/整合不匹配
- Type F: 早停 / 提前终止

**样本级归因**：把每个失败归到**降解链上最早变坏的那一环**。GSM8K 上 **69.7–79.4%** 的 Agent-Full 错误是 **protocol-induced**（协议诱发），而非真实能力差距。HotPotQA-32B 反过来：**73.3% 是真实能力差距**。

**给 Hermes 的诊断法**：看到一个 agent 表现下降，先问"是协议/格式层坏了，还是真的不会？"
- GSM8K 式计算任务 → 多半是协议层（多步工具循环断了）
- 检索 QA → 多半是真能力（检索没拿到能合成的信息）

### 1.5 G-STEP：可用的缓解

用 **CoT-fixability** 做监督信号训练一个轻量门控：FC agent 失败但纯 CoT 成功 → 判为"协议层可救" → 门控说 continue 时注入 continuation prompt，强制**再多走一步**工具。

效果：GSM8K-4B 50.64% → 69.12%（+CRITIC 74.88%，闭合 75.75% 差距）。但 HotPotQA-32B 上**完全没有增益**（83.02% → 82.90%），因为那里瓶颈是真实能力差距。

> **结论：门控只在"协议主导"的场景有效，在"能力主导"的场景是无效的甚至有害。** 上门控前先分清是哪一种。

---

## 二、CoBRA：反事实 margin 分区

### 2.1 定义

同一 base model 训两个专家：
- **M_int（内部专家）**：不许用工具，直接答
- **M_ext（外部专家）**：必须用工具并整合结果

同一 query 跑两条分支：

```
Δ̂(q) = R(τ_ext | q) − R(τ_int | q)
```

其中 `R = 任务正确性 − λ · 工具成本`（λ 是权衡参数）。

按 Δ̂ 分区：
- **D_int**（Δ̂ < 0）：工具**有害** → 不该调
- **D_ext**（Δ̂ > 0）：工具**有益** → 该调
- **D_amb**（|Δ̂| 小）：模糊 → 最有价值也最难

### 2.2 实测分区统计

| Benchmark | 全体 Δ̂ | D_int | D_ext | D_amb |
|-----------|---------|-------|-------|-------|
| TriviaQA | +0.182 ± 0.589 | −0.942 | +0.891 | −0.107 |
| HotpotQA | −0.009 ± 0.510 | −0.508 | +0.822 | −0.181 |
| 2WikiMultiHop | −0.158 ± 0.457 | −0.400 | +0.800 | −0.201 |

**关键读法**：
1. 同一个 benchmark 内部就有大量 **D_int 样本**（−0.4 到 −0.94）——**benchmark 级标签完全不够，必须 instance 级判断**
2. TriviaQA 整体 +0.182（外部友好），2WikiMultiHop 整体 −0.158（内部友好），HotpotQA 整体 ≈0 但**模糊区最大**（±0.510 方差）
3. D_amb 的 Δ̂ 系统性**为负**（−0.107 / −0.181 / −0.201）——模糊区不是"中性"，是"**平均略微有害**"。这跟 UpliftMem 的发现一致（UpliftMem 的反馈覆盖偏差也说明未被观测的区域不可辨识）

### 2.3 训练两阶段

1. **Boundary-Aware Cold-Start SFT**：只用 **clear-margin** 样本（|Δ̂| 大）教基础路由先验，**回避模糊样本的噪声监督**
2. **MARS-RL**（Marginal Advantage from Reference-Split Rollouts）：强制同一 query 跑两条分支，把 reward 差作为**对称边际优势**注入

优势构造：PBN（Per-Branch Normalized Advantage，防止一支独大）+ BM（Branch Margin）+ λ 的边际优势。

> **可迁移的核心**：**不要用"全部样本"训路由决策**。模糊样本的标签本身噪声大，混进去会把决策边界抹平。CoBRA 明确用 clear-margin 做 SFT、boundary 做 RL。

### 2.4 诚实的边界

- 实验只在 **Qwen3-4B** + 检索工具上做；工业级音乐域数据有迁移验证，但没验证到 Hermes 这种多技能场景
- 每条 query 要跑两次 rollout（int + ext）→ **采集成本翻倍**
- 代码未公开

---

## 三、When2Tool：模型早就知道，只是说不出来

### 3.1 When2Tool 基准

18 个环境（15 单跳 + 3 多跳），1080 训练 / 2700 测试。三类工具必要性：

| 类别 | 问题 | 例子 |
|------|------|------|
| **A 计算规模** | "我能算得出来吗？" | 12+712+7 vs 万亿级乘法、5×5 行列式、C(80,40) |
| **B 知识边界** | "我知道吗？" | 法国首都 vs 虚构实体/自造算法 |
| **C 执行可靠性** | "我能可靠地执行吗？" | print(2+3) vs 20 步动态规划、10+ 会议排期 |

每环境三档难度：**easy**（测**过度调用**）/ **medium**（决策边界）/ **hard**（测**该调不调**）。难度是**经验验证**的（跑无工具强制作答确认）。

### 3.2 两个基线都不行

- **Prompt-only**：改 prompt 劝阻调用 → **必要调用和不必要调用一起被压掉**
- **Reason-then-Act**：先显式推理必要性再行动 → hard 任务精度代价不成比例；Llama-3.1-8B 上工具调用**彻底崩掉**（79.5% → 31.2%），Llama-3.3-70B 83.1% → 47.9%

### 3.3 核心发现：必要性可从 hidden state 线性解码

**做法**：对每个任务，强制模型无工具作答 → 答对标 `y=0`（不需要工具），答错标 `y=1`（需要工具）。取**最后一个输入 token 位置、全部层**的 hidden state 拼接，训 **L2 正则 logistic regression**。

**结果（AUROC / Accuracy）**：

| 模型 | AUROC | Acc | Easy | Med | Hard |
|------|-------|-----|------|-----|------|
| Qwen3-1.7B | 0.894 | 0.847 | 0.864 | 0.831 | 0.904 |
| Qwen3-4B-Instruct | 0.948 | 0.877 | 0.933 | 0.906 | 0.948 |
| Llama-3.1-8B-Instruct | 0.927 | 0.849 | 0.892 | 0.867 | 0.884 |
| Qwen3-14B | **0.957** | 0.892 | 0.955 | 0.907 | 0.941 |
| Qwen3-32B | 0.952 | 0.885 | 0.951 | 0.903 | 0.939 |
| Llama-3.3-70B-Instruct | 0.936 | 0.872 | 0.906 | 0.849 | 0.956 |

**最惊人的一条**：Llama 在 Reason-then-Act 下工具调用彻底崩溃（79.5%→31.2%），**但探针依然 AUROC > 0.9**。信息**在表示里存在**，只是生成过程**翻译不出来**。

> 这直接解释了"为什么 agent 明知该直答却还是去调工具"：**不是不知道，是说不出来。**

### 3.4 Probe&Prefill

三步，推理时 <1ms 开销：
1. 单次 forward pass 取最后 token 的 hidden state（**这是 KV cache 前的标准编码步骤，不额外花 forward**）
2. 探针输出 p，阈值 τ 二值化
3. **prefill** 一句 steering 句子：
   - `p < τ` → `"I can solve this directly without using a tool."`
   - `p ≥ τ` → `"I need to use a tool for this question."`

**软 prefill** 允许模型自己推翻建议；**硬 prefill** 强制输出格式（`\boxed{` 或 tool-call JSON）。Llama 指令跟随差，软 prefill 会被部分忽略 → 硬 prefill 恢复完整控制。

**效果**：
- 工具调用减少 **48%**，精度只掉 **1.7%**
- 对比基线：同等精度下只省 **6%**（差 8 倍）；或同等降幅精度掉 5 倍更多
- 真实 Search-o1 agentic benchmark：API 调用减少 **20–56%**，无精度损失
- τ 从 0.1 到 0.9 可扫出**平滑 tradeoff 曲线**

### 3.5 SFT 对比（重要的负面结论）

SFT（4 GPU 全参微调，2 epoch）精度 +2–3%，但**工具调用反而增加**（Qwen3-4B、Llama-3.1-8B），只有 Qwen3-1.7B 降了 18%。Probe&Prefill 在所有模型上降 21–38%。

> **结论**：SFT 能学会"答得更好"，但学不会**调用决策边界**。改权重不如读表示。

---

## 四、ToolGate：执行前的门控

### 4.1 问题设定

ReAct 风格的 VLM agent 提一个工具调用后，**在输出进入上下文之前**决定执行还是跳过。

### 4.2 基线的局部选择性很差（关键数字）

跨 5 个 benchmark：

- **有用调用 11.8%**
- **有害调用 9.9%**
- **绝大多数调用不改变 immediate forced-answer 预测**

> 有害调用率 ≈ 有用调用率。**agent 对"这次调用值不值"几乎没有判断力。** 这跟 Tool-Use Tax 结论互相印证。

### 4.3 标签构造（forced-answer probe）

在每次执行的工具调用**前后各探一次** agent，追加用户轮：

```
Based on all information available to you so far, what is your best answer
to the original question? You MUST choose exactly one option letter.
Respond with ONLY the letter (A, B, C, or D), nothing else.
```

`max_tokens=1, logprobs=True, top_logprobs=20`，取选项字母 token 概率。probe **只用于离线造标签**，不在部署 agent 里。

**标签是 proxy，不是真反事实 VoI**（作者自己声明）：负标签不等于"值=0"，可能价值是延迟的或分散在后续多步的。

### 4.4 特征（极简，这是最大的意外）

**9 个结构特征** + **文本 embedding**：

- 结构特征 s1..s9，其中 s4..s9 是 6 维 one-hot（6 个工具：ocr / detection / detection_small_object / segmentation / cropping / depth_estimation）
- 轨迹前缀序列化格式：
  ```
  [Q] query + 选项
  [Ti] 每个 thinking 段，截断到 200 字符
  [TOOLi] name(args) -> output，args 截断 80 字符
  ```

**模型**：`all-MiniLM-L6-v2` 冻结 sentence encoder（d=384, mean pooling）→ 拼接 9 维结构特征 → **logistic regression**（L2, C=1.0, class_weight=balanced, LBFGS, 1000 iter）→ 阈值 τ=0.5

### 4.5 结果

**Qwen3-VL-30B**（matched-domain）：

| 变体 | Acc | Δ | Token 成本 | Calls |
|------|-----|---|-----------|-------|
| Baseline | 70.83 | — | 100% | 2.73 |
| **ToolGate 完整** | **72.48** | **+1.65** | **67%** | **1.02** |
| 仅文本 | 70.69 | −0.14 | 75% | 0.98 |
| 仅结构 | 71.81 | +0.98 | 69% | 0.97 |
| 仅工具身份 | 72.14 | +1.31 | 75% | 1.34 |

**跨域（更严格）**：token 成本降到 **64–69%**，精度基本保持。

**对比其他门控方式**（30B）：

| 方式 | Acc | Token | Calls |
|------|-----|-------|-------|
| Baseline | 70.8 | 100% | 2.73 |
| VoI self-report | 60.0 | **126%** | 5.88 |
| Sparse prompt | 69.8 | 99% | 2.40 |
| **ToolGate** | **72.5** | **67%** | **1.02** |

> **"让模型自己判断值不值（VoI self-report）"是最差方案**——精度掉 10.8 点，token 反而涨 26%。这和 When2Tool 的 Reason-then-Act 失败是同一个现象：**模型的口头自评不如一个线性探针**。

### 4.6 负面发现（同等重要）

- **更重的特征没用**：图像特征、VLM encoder 特征、模型 log-prob 特征，**都没有超过**轻量的文本+结构门控
- **matched-domain 不是无条件更好**：235B-FP8 的 in-domain 门控**降成本但伤精度**——当 execute-positive 类稀疏且从纯文本特征难以推断时，同域数据会过拟合
- **阈值扫描**：提高阈值单调减少调用次数；**中等阈值**在 30B 上精度最佳

### 4.7 代码可用

`github.com/iamlilAJ/toolgate`（MIT，1★，2026-08-21 最后推送）。结构：
- `scripts/probing/train_probe.py` — 探针训练
- `scripts/probing/collect_info_gain.py` — 信息增益采集
- `scripts/probing/train_skipsafe_ablation.py` / `_focal.py` — skipsafe 消融
- `scripts/probing/generate_threshold_report.py` — 阈值扫描
- `configs/*.yaml` — 12 个配置（含 cross-domain、info_gain_lp、skipsafe 变体）
- `src/cv_agent/` — agent 框架、benchmark loaders、callbacks

**这是四条线里唯一有完整可运行代码的**，且是 EMNLP 2026。

---

## 五、LRAT：轨迹监督的检索训练（补充）

SIGIR 2026accepted。核心：**检索器应该直接用 agent 轨迹训练**，因为检索的消费方已从人变成 agent。

从轨迹里挖三类行为信号：
1. **browsing actions**（浏览动作）
2. **unbrowsed rejections**（没浏览的拒绝 → 负样本）
3. **post-browse reasoning traces**（浏览后的推理痕迹 → 正样本强度）

再通过 **weighted optimization 引入 relevance intensity**（不只是二元相关，是有强度）。

**实测**（Tongyi-DeepResearch-30B + Qwen3-Emb）：

| Benchmark | SR | Evidence Recall | Avg Steps |
|-----------|-----|-----------------|-----------|
| InfoSeek-Eval (ID) | 52.7 → **68.0** | — | 26.7 → **20.7** |
| BrowseComp-Plus (OOD) | 17.8 → **23.7** | 49.2 → **60.7** | 42.9 → **41.0** |

规模：10K InfoSeekQA 查询 × 4 个 retriever = **26,482 条 agent 轨迹 → 91,713 训练对**。

**关键洞察**："**没浏览**"是一个高质量负样本——agent 主动跳过的文档就是"检索到了但没用"的天然负例，**这正是 tool-uplift 的负半边**。这是把 uplift 信号从"需要额外采集"变成"免费从现有轨迹里挖"的路径。

---

## 六、落地到 Hermes 的方案

### 6.1 立刻可做（零风险）

1. **技能调用前先问"我本来会不会做"** —— 用 Capability Overlap Principle 做人工判断。Hermes 里最典型的冗余技能：格式转换类（"转成 JSON"）、简单算术、时间查询。这些走 execute_code / 内置工具比加载 SKILL.md 更划算。
2. **按任务类型区分协议敏感度** —— 串行计算/多步工具链任务要额外检查"工具循环是不是断了"（Type A/F），检索 QA 任务不要指望门控能救（真实能力差距）。
3. **用 explicit 思考**代替"让模型自评" —— 别用 "你觉得这个工具有用吗" 来做决策（VoI self-report 证据最差），改成显式列出"缺什么外部信息"。

### 6.2 可做（中等成本）

4. **给 Hermes 做一个 When2Tool 风格的探针**：
   - 标签：同一 query 跑"无技能"和"有技能"两条分支，答对/答错差 → 这就是 **Δ̂(q)**（和 CoBRA 的定义一致）
   - 特征：Hermes 里拿不到 hidden state（走的是 API），但可以用 **prompt 文本 + 工具身份 + 结构特征**，即 **ToolGate 的做法**——而 ToolGate 证明这条路够用
   - 落地形式：`~/.hermes/scripts/tool_gate.py`，输入 = 候选技能描述 + 当前任务摘要，输出 = execute/skip + 置信度
   - 采集成本：每次要多跑一条无技能分支 → 用 When2Tool 的分级（easy/medium/hard）只在 medium 边界上花这个成本
5. **阈值即旋钮**：τ 是一个连续旋钮，可以按"成本敏感度"调。低 τ 省调用，高 τ 保精度。ToolGate 的扫描显示**中等阈值最优**。

### 6.3 需要谨慎

6. **不要把"探针结论"当成"技能质量结论"**。探针判断的是"这次要不要调"，不是"这个技能好不好"。一个技能可能整体很好但此刻不适用，反之亦然。
7. **模糊区不要硬判**。CoBRA 的 D_amb 占 10–20%，其平均 Δ̂ 系统性为负——**模糊区倾向于"不调"**，但也要接受这部分会有损失。
8. **Hermes 的技能列表 ≠ ToolGate 的工具注册表**。ToolGate 只有 6 个视觉工具，工具身份one-hot 就占 6 维；Hermes 有 200+ 技能、描述长度方差巨大，特征设计要重新做。**论文结论不能直接外推**。

---

## 七、方法论纪律（从这批工作里提炼）

1. **"要不要调"和"调了有没有用"是两个问题**，必须分开测。CoBRA 管前者，UpliftMem 管后者，ToolGate 管"执行前的局部决策"。
2. **benchmark 级标签不够用**。CoBRA 证明同一个 benchmark 内 Δ̂ 从 −0.94 到 +0.89 都有，必须 instance 级判断。
3. **prompt 和 verbalized reasoning 是最差的门控信号**。Reason-then-Act 在 Llama 上崩到 31.2%；VoI self-report 精度掉 10.8 点且 token 涨 26%。**读表示 > 改 prompt > 让模型口头自评**。
4. **区分"协议诱发"和"真实能力差距"**再做干预。前者门控有效（GSM8K 闭合 75.75% 差距），后者门控无效甚至有害（HotPotQA-32B 零增益）。**先归因，再上工具**。
5. **"没调用"是免费的负样本**。LRAT 证明了 unbrowsed rejections 可以直接当检索负例——Hermes 的会话日志里同样可以挖"被召回但没用"的技能条目，零额外采集成本。
6. **门控标签是 proxy 不是因果**。ToolGate 作者明确声明其标签来自 forced-answer probe，不是真反事实 VoI；正标签只应读作"execute-positive 监督"，不应读作"所有负调用价值为 0"。
7. **matched-domain 数据不保证更好**。ToolGate 的 235B in-domain 门控降成本但伤精度。

---

## 八、诚实边界

- **CoBRA / Tool-Use Tax / LRAT 三篇代码均未公开**（2026-10-24 核验），只有论文
- **ToolGate 只有 1★，作者是单人学生项目**，未经验证的大规模复现；仓库最后推送 2026-08-21
- **When2Tool 的探针方案依赖能拿到 hidden state**，Hermes 走第三方 API 拿不到 → 只能退化到 ToolGate 的文本+结构路线
- **ToolGate 在 VLM + 6 个感知工具上验证**，没有在"LLM + 200 技能"的场景验证过；Hermes 场景是外推
- **所有 uplift 类工作都需要反事实分支**（多跑一遍无技能/无工具），采集成本翻倍是固有代价，不是实现问题
- **CoBRA 只在 Qwen3-4B 上验证**，工业音乐域有迁移但场景不同
- LRAT 的 26,482 条轨迹来自 Tongyi-DeepResearch-30B 这个特定 agent，换 agent 后行为信号强度未知

---

## 来源

- Tool-Use Tax: https://arxiv.org/abs/2605.00136 （张凯卓等，2026-04-30）
- CoBRA: https://arxiv.org/abs/2609.00967 （2026-09-01）
- When2Tool / Probe&Prefill: https://arxiv.org/abs/2605.09252 （UCSD, 2026-05-10）— 代码 https://github.com/Trustworthy-ML-Lab/when2tool
- ToolGate: https://arxiv.org/abs/2606.03054 （UCL/HKUST(GZ), 2026-06-02, EMNLP 2026）— 代码 https://github.com/iamlilAJ/toolgate
- LRAT: https://arxiv.org/abs/2604.04949 （RUC GSAI, SIGIR 2026）— https://yuqi-zhou.github.io/LRAT-homepage/
- TRACER（轨迹感知工具检索）: https://arxiv.org/abs/2610.21267
- MagicSelector: https://arxiv.org/abs/2607.17751
- Spurious Tool Use: https://arxiv.org/abs/2609.16268
- ToolGate 简称说明: https://arxiv.org/abs/2606.03054 （同第 6.2 节 Table 2 数字）
