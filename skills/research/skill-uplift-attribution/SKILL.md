---
name: skill-uplift-attribution
description: 给 Hermes 的技能/记忆召回加执行反馈回路——用 state.db 已有的 skill_view 事件与人类反应做"同会话内配对反事实"，零 rollout 测出每条 skill 的 execution uplift，并按 EVSI 思路排"下一步该测什么"。Use when asking "did that skill actually help?", building uplift attribution for skill/memory retrieval, diagnosing skills that hurt outcomes, or choosing which skill to test next.
triggers: [skill uplift, execution uplift, uplift attribution, 技能增益归因, 技能有没有用, uplift 归因, 反事实对照, counterfactual baseline, 技能反馈回路, probe queue, EVSI 探测, skill utility, 技能效用评估, attribution feedback loop]
owner: hermes-evolution
created: 2026-10-25
updated: 2026-10-25
paper: 理论来源 arXiv:2609.36805 (UpliftMem, 见 upliftmem-evsi-probing 技能) —— 本技能是**自建实现**，非论文复现；论文代码未公开
code: 本机实现 `~/.hermes/self-improvement/skill_uplift.py`（非本仓库文件，运行态脚本）
tests: `~/.hermes/self-improvement/test_skill_uplift.py`（56 个断言）
related_work: skills/research/upliftmem-evsi-probing (理论) / skills/research/uplift-rag (单文档 uplift) / skills/research/tool-call-uplift-gating (调用门控) / arXiv:2607.21106 (AttriMem 归因引导的过程反馈) / arXiv:2605.08374 (MemQ, provenance DAG 上的 TD(λ) 信用分配)
tags: [skill-uplift, execution-uplift, attribution, counterfactual, state-db, feedback-loop, evsi-probe, hermes-self-improvement, zero-rollout]
---

# Skill Uplift 归因 — 给 Hermes 补上"这条 skill 到底帮没帮上忙"的反馈回路

## 概述

**一句话**：`upliftmem-evsi-probing` 技能把 execution uplift 的**理论**讲透了，但它的复现路线（§8）要求**对每个候选记忆集跑两次执行**（有记忆 / 无记忆），成本高昂。本技能给出另一条路：**不跑任何 rollout**，直接利用 Hermes `state.db` 里**已经在记录**的两样东西——skill_view 事件和人类对后续工作的反应——构造一个**同会话内配对反事实**，测出每条 skill 的 execution uplift。

**为什么这不是重复研究**：`upliftmem-evsi-probing`（2026-10-24 建）§7.1 已经点明"Hermes 的 skill 召回目前是纯相关性驱动的，**没有'这条 skill 到底帮没帮上忙'的反馈回路**"，但只停在启发层面，没有实现。本技能把这个缺口**真的补上了**，并产出了一个可运行的脚本。

---

## 一、核心思想：用"同会话内配对"代替"再跑一次"

### 1.1 论文要的 vs 我们能拿到的

UpliftMem 的定义（Eq.3）：

```
Δ(c, S) = V(c, S) − V(c, ∅)        ← 集合 S 相对"无记忆"的期望效用差
```

关键在 `V(c, ∅)`（无记忆参照臂）。论文的做法是**真的跑一遍无记忆执行**——每个标签要两次执行，§8 明说这是主要成本。

Hermes 的处境不同：**同一个会话里，skill 加载之前的工作就是一个天然的"无记忆参照臂"**。

```
会话: [用户提问] → [助手干活，没加载 skill] → [用户反应①]
      → [助手加载 skill S 干活]        → [用户反应②]
                        ↑
              这就是配对反事实的切分点
```

- **参照臂**：第一次 skill_view **之前**的用户反应（同样是对"刚干完的活"的评价）
- **实验臂**：第一次 skill_view **之后**的用户反应
- 两臂**同会话、同任务上下文、同 executor**——会话/人群效应自动抵消

这是 UpliftMem "same executor" 要求的**廉价版实现**：不重跑，而是复用已经在日志里发生过的对照。

### 1.2 为什么不能直接用"全局无技能会话"当基线

实测踩过的坑（**必须避开的错误做法**）：

| 基线定义 | n | 结果 |
|---|---|---|
| 全局"无技能会话"的用户消息 | 2 | 基线退化，uplift 变成噪声 |
| 去掉每个会话的首条用户消息（开场prompt）后 | **0** | 基线直接消失 |
| 全局用户消息（不做开场过滤） | 454 | **人群错配**——混入 8691 个单消息 cron 会话的任务prompt |
| **同会话内配对（前技能 vs 后技能）** | **6–35** | ✅ 可用 |

根因：**本机 8691/8702 的"无技能会话"是单条消息的 cron 任务**，那条唯一的用户消息是**任务prompt**，不是对任何工作的反应。用它当基线，等于拿"任务下发"跟"用户评价"比。

> **教训**： uplift 的两个臂必须在**同一总体**上、用**同一个打分器**度量。两个臂一旦总体不同，"增益"就是抽样偏差，不是技能的属性。

---

## 二、Hermes 侧的三个落地障碍（全部实测解决）

### 2.1 障碍一：skill 名字有两套写法，会把证据劈成两半

`state.db` 里同一个 skill 会出现两种名字：

| 来源 | 形态 | 例子 |
|---|---|---|
| JSON 结果 | 短名 | `hermes-deep-inspection` |
| 压缩后的日志行 | 路径限定名 | `agent-engineering/hermes-deep-inspection` |

不归一化的话，`hermes-deep-inspection`（n=3）和 `agent-engineering/hermes-deep-inspection`（n=1）被当成两个 skill，**样本量被劈开、后验方差被虚增**。

**解法**：扫描 `~/.hermes/skills/**/SKILL.md` 建 `短名 → 限定名` 索引（`build_skill_index()`）。**歧义保护**：若同一个短名对应多个限定名（不同目录下重名），**不猜**，保留短名独立并标记 `ambiguous_short_names`。

### 2.2 障碍二：role='user' 的消息里混着系统注入

Hermes 把 cron 任务prompt、后台进程通知、异步委派完成通知、压缩提示**都以 `role='user'` 存储**。实测：**40 条"技能后用户反应"里有 13 条是系统注入**。

更糟的是它们会污染打分：`[IMPORTANT: Background process proc_x exited (exit code 1).]` 会被 `FAILURE_MARKERS` 里的 `exit code 1` / `error` 命中，**把一次成功的任务判成失败，并归咎于刚加载的 skill**。

**解法**：`is_human_reaction()` 用**前缀白名单排除**（`[IMPORTANT:` / `[SYSTEM:` / `[ASYNC` / `[OUT-OF-BAND USER MESSAGE` / `<system-reminder>` 等）。只保留真正的人类消息当反应。

> 这是本实现里**最容易踩且危害最大**的一个坑：不做过滤的话，噪声率超过 1/3，而且噪声是**系统性偏向失败**的。

### 2.3 障碍三：没有现成的"结果信号"表

`state.db` 里有 `messages.tool_name='skill_view'` 的调用记录（实测 57 条），但**没有任何 outcome / reward / feedback 表**——`SELECT name FROM sqlite_master WHERE name LIKE '%outcome%'` 返回空。

**解法**：结果信号从"人类反应文本"里现算，用可审计的**粗粒度标记词**（`success` / `failure` / `correction` 三类），不用 LLM judge——保证零成本、零延迟、可复现。

**打分优先级**（顺序很重要）：

```
correction（"还是不行"/"重做"/"不对"） > failure（error/traceback/失败）
                                      > success（完成/搞定/修复了/all tests pass）
```

混合命中时（既 success 又 error，如 "fixed the error"）判 success；correction 优先级最高——"我说了完成但其实不行"必须算失败。

---

## 三、统计模型：Beta-Bernoulli 代理 UpliftMem 的高斯代理

论文用**相关高斯模型**下的 EVSI 闭式解（Theorem 2）。我们用 **Beta-Bernoulli 共轭**做代理，只借它的**决策结构**，不声称它的理论保证：

| 论文量 | 我们的代理 | 说明 |
|---|---|---|
| `μ_j`（候选的 uplift） | `uplift = posterior_mean − baseline_rate` | 决策边际 |
| `σ_j`（候选方差） | Beta 后验标准差 | 不确定性 |
| EVSI = 不确定性 × 边际 | `evsi_lite = posterior_sd × \|uplift\|` | 探测优先级 |
| 相关高斯协方差 | 独立 Beta（保守，忽略正相关） | 宁可低估探测价值 |

后验：`alpha = 2, beta = 2`（弱先验，中心 0.5）。

### 3.1 三道闸门（防止假精确）

论文的严谨性体现在"没有信号就不下结论"。我们照做：

**闸门一：基线可用性**
```
baseline_n < MIN_BASELINE_N (=8)  →  全部技能标 "insufficient-baseline"
```
此时 uplift 数值**不可解读为技能质量**，只能用来给 probe 排序。

**闸门二：证据量 + 会话分散度**
```
resolved_outcomes < MIN_SIGNAL_N (=3)  →  "insufficient-signal"
n_sessions < 2                           →  "single-session"
否则                                     →  "usable"
```

> **为什么加"会话数"这一维**：同一会话内的多次观察**不独立**（同一用户、同一任务、同一心情）。`n=5 sess=1` 不是 5 个独立证据。`confidence_label()` 用 `min(n_observed, n_sessions × 2)` 做有效样本量。

**闸门三：证据层级（tier gate）**——本实现独有

```
evidence_tier == TIER_REACTION    →  可以下 "usable" 判定
evidence_tier == TIER_SELF_REPORT →  降级为 "self-report-only"（只排序，不判定）
evidence_tier == "none"           →  uplift=None，不报任何数字
```

**自报证据永远拿不到 "usable"**——助手说"搞定了"不构成对 skill 质量的判定，只能作为排序信号。反应基线 rate=1.0 与自报基线 rate=0.51 的巨大落差，说明这两层如果混算会凭空造出 ±0.45 的假增益/假负增益。

**探针（probe）也受闸门约束**：只有基线可用、且 resolved ≥ 3 时，才允许发出"这个 skill 有害"这种**指控性**结论。否则负估计只是薄数据的伪影。

### 3.2 Probe 队列：三类

对应 UpliftMem 的反馈覆盖问题（Proposition 4：未被执行的候选集，其符号不可辨识）：

| 类别 | 触发条件 | 动作 |
|---|---|---|
| `used-but-outcome-unverifiable` | 加载过但零可判定结果 | 跑一个能产出明确结果的任务 |
| `negative-uplift-suspect` | uplift<0 且证据充分且基线可用 | 审计这个 skill |
| `contested-sign` | \|uplift\|<0.1 且 sd>0.15 | 用决定性任务复跑定符号 |
| `high-usage-low-attribution` | 高使用率但归因结果少 | 补采集归因结果 |

**不探测**已高置信正增益的 skill——那只是花钱确认已知的事。

---

## 四、运行

```bash
python3 ~/.hermes/self-improvement/skill_uplift.py            # 文本报告
python3 ~/.hermes/self-improvement/skill_uplift.py --json     # JSON
python3 ~/.hermes/self-improvement/skill_uplift.py --write    # 落盘到 skill_uplift_store.json
python3 ~/.hermes/self-improvement/skill_uplift.py --since-days 30
```

只读 `state.db`（`mode=ro`），只写自己的 JSON store。**不 patch Hermes 核心**。

测试：`python3 ~/.hermes/self-improvement/test_skill_uplift.py`（**56 个断言**，全绿；含 §5.2 的 `uplift=None` 回归测试）

---

## 五、本机实测结果（2026-10-25 实跑）

```
baseline (reaction arm): n=8 rate=1.0 usable=True
  (paired within-session pre-skill arm, same session / same executor)
baseline (self-report arm): n=323 rate=0.5108 usable=True
  (assistant turn-finals in skill-bearing sessions, same scorer)
skills attributed: 26
signal funnel: 47 skill_views -> 28 resolved outcomes (19 unknown);
               T1-reaction=0  T2-self-report=28;
               0 skills with usable signal
```

### 5.1 双层证据模型（关键设计）

人类反应和助手自报**不可混算**——这是本实现最重要的结构性约束：

| 层级 | 来源 | 权重 | 能得出什么结论 |
|---|---|---|---|
| **Tier-1 `R`** | 人类对后续工作的真实反应 | 1.0 | 可下"好/坏"判定 |
| **Tier-2 `S`** | 助手自己说的"搞定了" | 0.5 | **只能排序，不能判定** |
| **`none`** | 没有任何可判定结果 | — | `uplift=None`，**不报数字** |

**分层基线**：Tier-2 证据必须和 **self-report 基线**（rate=0.51）比，不能和人类反应基线（rate=1.0）比——否则一个自报"成功"的技能会被算出 −0.45 的假负增益。两个基线分别报告，读者能看出用的是哪条臂。

**实测后果**：47 次 skill_view 里 **T1（人类反应）= 0 条**，全部 28 条可判定证据都是 Tier-2 自报。所以本机当前**没有任何一个技能能拿到 "usable" 判定**，只有 4 个拿到 "self-report-only"（仅用于排序）。

### 5.2 `uplift=None`——不许把"没证据"报成"有害"

**这是一个真实修过的 bug，值得单独记住。**

观察全部为 `unknown` 的技能，tier=`none`，后验仍是未动的 Beta(2,2) 先验（0.5）。原代码把这个先验去减反应基线，得到一个硬编码的 `-0.500`——而本机反应基线恰好是 n=8 rate=1.0，于是**所有无证据技能的 uplift 都是最大负值**，排在报告最前面，读起来像"这条 skill 有害"。

真相是"我们什么都不知道"。这与本模块在别处对抗的**系统性偏向失败**是同一个错误模式（参见 §2.2 系统注入噪声偏向失败）。

**修法**：tier=`none` → `uplift=None`，文本报告渲染成 `n/a`。修后 10 条无证据技能的 `-0.500` 全部变成 `n/a`，并正确落入 probe 队列的 `used-but-outcome-unverifiable` 类。

> **通用教训**：任何"属性 − 基线"的差值型指标，当被减数是**先验占位值**时，差值不承载信息。缺证据应该报 `None`/NA，不是报一个看起来精确的数字。

### 5.3 Probe 队列（实测输出）

```
[used-but-outcome-unverifiable] autonomous-ai-agents/hermes-agent
    -> run a task that uses this skill and capture a decisive outcome
[used-but-outcome-unverifiable] hermes-optimization
[used-but-outcome-unverifiable] devops/system-status-check
[used-but-outcome-unverifiable] china-etf-technical-analysis
[high-usage-low-attribution] novel-writing
    -> engaged 376x but only 1 attributed outcomes; capture more attributed outcomes
```

`novel-writing` 376 次使用却只有 1 个归因结果——**这个"高使用×低归因"的比值本身就是个有价值的告警**，不需要 uplift 数值来支撑。

### 5.4 诚实的结论

在这个部署上，**信号是稀薄的**：

- 47 次 skill_view 只解析出 28 个可判定结果，**其中 Tier-1 人类反应为 0**
- **0 个技能达到 "usable" 信号等级**
- 反应基线 n=8，恰好卡在阈值线上；且 rate=1.0 说明这 8 条人类反应**全是正面**——这个基线本身没有区分力

**这不是 bug，是这个部署的结构性事实**：本机绝大部分会话是无人值守的 cron 任务，**没有人类来对结果打分**。

**因此这个工具当前的最大价值不是"给技能打分"，而是把"我们其实几乎没有证据"这件事量化并暴露出来**——这恰好就是 UpliftMem 反馈覆盖偏差在 Hermes 上的真实表现。

---

## 六、已知缺口（诚实边界）

1. **没有真正的反事实**。同会话配对是**代理**，不是随机化对照：skill 常常是在"任务已经变难了"之后才被加载（选择偏差）。真正的 uplift 需要论文的**双执行**设计。
2. **不实现集合级 joint semantics**。Hermes 每次 `skill_view` 加载一个技能，所以实际退化成单元素集合；论文的核心贡献（集合内互补/冗余/冲突）**没有覆盖**。
3. **不实现论文的 EVSI 闭式解**，只做 EVSI-lite 代理（不确定度 × 边际）。
4. **打分是关键词规则**，会有误判（尤其中文口语里"不行"既可能是批评也可能是自嘲）。
5. **只覆盖 skill，不覆盖 memory 召回**。memory 条目没有 `tool_name='skill_view'` 这样的事件锚点，暂未纳入。
6. **基线 arm 依赖会话内前后对比**，对"第一个动作就加载技能"的任务无参照。
7. **反应基线本身没有区分力**。本机 n=8 rate=1.0——8 条人类反应全是正面。作为对照基线，它无法区分"好技能"和"一般技能"，只能区分"有反应"和"没反应"。要拿到有区分力的基线，需要人类反馈里出现**否定样本**（这也是 §7.3 提轻量反馈通道的原因）。

---

## 七、后续可做

1. **给 memory 召回加事件锚点**：在 memory 注入上下文时打一条 `tool_name='memory_inject'` 的消息，让同一套归因逻辑覆盖 memory 维度。**这是把"skill/memory 反馈回路"从 skill 扩展到 memory 的必要一步**——当前实现只覆盖了 skill 维度。
2. **把"高使用×低归因"变成常驻告警**：不需要 uplift 数值就能算，是最可靠的信号（`novel-writing` 376:1 就是例子）。
3. **用真人类反馈补样本**：让 QQ/飞书端提供一个"👍/👎"或一句话评价的轻量通道，把归因样本从 28 提到几百。**关键在于要能收到否定反馈**——只收正面反馈会让基线永久停在 rate=1.0。
4. **负增益存档**：论文 §4.4 的"无论是否入库都提供 uplift 标签"。当前 Hermes 的技能归档只看 `use_count`，不看"用完是否更糟"。

---

## 八、来源

- 理论来源（已有技能覆盖，本技能只实现）: https://arxiv.org/abs/2609.36805 — UpliftMem, Submitted 2026-09-29, ICLR 2027 under review。**代码未公开**（github.com/mengkunLiang/UpliftMem → 404），§8 复现路线要求双执行
- 前作（单文档 uplift）: https://aclanthology.org/2025.findings-emnlp.511/ — Uplift-RAG, EMNLP 2025 Findings
- 归因/信用分配相关: https://arxiv.org/abs/2607.21106 (AttriMem) / https://arxiv.org/abs/2605.08374 (MemQ)
- 分层评估依据: https://arxiv.org/html/2504.08942 (AgentRewardBench，规则化/自报式评估会低报成功率) / https://aclanthology.org/2026.acl-long.1062/ (Plan-RewardBench，长 horizon 轨迹上所有 evaluator 家族显著恶化)
- Hermes 侧既有资产: `tools/skill_usage.py`（`.usage.json` 计数遥测）、`tools/skill_ledger.py`（变更审计）、`state.db` 的 `messages` 表
- 队列主题 id: `agent-retrieval-utility-audit-2026`
