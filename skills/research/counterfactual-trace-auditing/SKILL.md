---
name: counterfactual-trace-auditing
description: CTA 配对轨迹做技能行为级审计，产出五类 SIP 标签。
triggers: [CTA, counterfactual trace auditing, SIP, skill influence pattern, 行为级审计, 技能行为影响, trace pairing, surface anchoring, concept bleed, redundant exploration, premature closure, 技能副作用审计, 行为差异]
owner: hermes-evolution
created: 2026-10-28
updated: 2026-10-28
paper: arXiv:2605.11946 (CTA, Zhou/Liu/Li/Rossi/Hu — ASU + USC + Adobe Research), NeurIPS 2026 投稿, MIT license
code: https://github.com/WillChow66/CTA (NeurIPS 2026 anonymized repo, 3 stars — 论文代码已公开，可直接跑)
related_work: skills/research/skill-uplift-attribution (结果层 uplift 归因，本技能是行为层) / skills/research/upliftmem-evsi-probing (理论) / skills/research/uplift-rag (单文档 uplift) / arXiv:2608.25500 (CaSKG, 反事实因果技能图 — 检索侧的边置信度校准) / arXiv:2606.10388 (SameCapRisk-Bench, 技能检索的风险暴露)
tags: [cta, counterfactual, trace-auditing, sip, behavioral-attribution, skill-side-effects, baseline-bucket, phase-segmentation]
---

# Counterfactual Trace Auditing (CTA) — 技能影响的行为级审计

## 概述

**一句话**：现有技能评估只报一个标量（pass rate 变化 ΔP）。CTA **配对同一任务的 with-skill / without-skill 轨迹**，把两条轨迹分段对齐，产出结构化的 **Skill Influence Pattern (SIP)** 标注，描述技能**改变了 agent 的行为方式**——而不仅是"任务做成了没有"。

**为什么这不是重复研究**：本仓库已有 `skill-uplift-attribution`（arXiv:2609.36805 思想，2026-10-25 建），它测的是**结果层**——ΔP（通过率变化）。CTA 测的是**行为层**——同一个 ΔP 可以由完全不同的机制产生。论文的核心发现就是这两层会**系统性地脱节**。

---

## 一、核心发现：ΔP 会系统性掩盖行为变化

论文在 SWE-Skills-Bench 全量 49 个任务 + Claude Sonnet 4.5 上的实测：

| 指标 | 数值 |
|---|---|
| 平均 pass rate 变化 ΔP | **仅 +0.3 pp**（中位数 0，标准差 4.4 pp） |
| 同一批配对轨迹里 CTA 检出的 divergence 记录 | **696 条** |
| 检出的 SIP 实例 | **522 条** |

**读法**：只看 ΔP 会得出"这些技能基本没用"的结论；CTA 在**完全相同的轨迹**上找到 522 处结构性变化。两者不矛盾——它们测的是不同的东西。

### 1.1 三条分桶规律（这是论文最可迁移的部分）

论文把任务按 **baseline 表现**分三桶（ceiling: r⁻≥0.9 / mid: 0.5≤r⁻<0.9 / floor: r⁻<0.5）：

| 桶 | 任务数 | ΔP | 主要 SIP 类型 | 论文观察 |
|---|---|---|---|---|
| **Ceiling** | 37 | +0.22 pp | **SURFACE ANCHORING** (4.38/任务) | 已经是天花板，pass rate 无处体现，但技能效应最多 |
| **Mid** | 10 | 0.00 pp | **EDGE-CASE PROMPTING** (3.00/任务) | **可回收增益最大**，但 token 成本显著更高 |
| **Floor** | 2 | 0.00 pp | **EDGE-CASE PROMPTING** (4.50/任务) | 技能被消费了，但没把 agent 挪离失败轨迹 |

**核心洞见**：*「dominant SIP type 可由 baseline bucket 预测」* —— **表面锚定在饱和任务上主导，边角提示在中等/地板任务上主导**。这把"凭直觉说的失败模式"变成了可复现的行为测量。

### 1.2 饱和基线是最贵的地方（直接对应 uplift 归因的坑）

论文明确：**high baseline tasks contain most of the observed skill effects, although their pass rate is already saturated and therefore cannot reflect those effects.**

这与本仓库 `skill-uplift-attribution` 修掉的一个真实 bug 是**同一个病**（参见该技能 §5）：拿一个**饱和/不匹配的参照臂**去减另一个总体，差值不承载信息。CTA 的教训是——**参照臂必须按 bucket 匹配**，不能拿全局基线一刀切。

另外 CTA 给出一个论文没放进五分类的**第六种机制**（明确标注"tentative"，不作为正式类）：

> **PREMATURE CLOSURE**：技能结尾有"提交并写文档"步骤，with-skill agent 到此**就停**了，而 baseline 继续跑验证——因为 baseline 发现单测目标依赖它。技能给了 agent 一个它当成**终止条件**的显式完成边界，**压制了默认的验证循环**。

这是典型的**ΔP 会完全看不见的失败**：with-skill 看起来"更规范"（提交了+写了文档），实际**跳过了验证**。

---

## 二、CTA 管线（五个模块）

### 2.1 输入：paired trace bundle

对每个任务 τ：

```
B_τ = { q_τ,  T⁺_τ,  T⁻_τ,  S_τ,  r⁺_τ,  r⁻_τ }
        ↑      ↑      ↑      ↑      ↑      ↑
      任务说明  有技能  无技能  技能文档  有技能  无技能
                    轨迹    轨迹              通过率  通过率
```

**r = 1 的配对设计**：同一模型、同一任务、同一执行器，唯一差异是 skill 挂没挂。

### 2.2 五个处理阶段

```
① 解析     原始日志 → 类型化事件
           READ / WRITE / EXECUTE / SEARCH / THINK
              ↓
② 分段     确定性有限状态机 → 五个 goal-directed phase
           ORIENTATION / IMPLEMENTATION / VALIDATION / DEBUGGING / FINALIZATION
              ↓
③ 对齐     phase 级：动态时间规整 (DTW)
           action 级：phase 内按 intent 对齐
              ↓
④ 抽取     divergence 记录
           intent window = THINK 事件起，到下一个 THINK 或 phase 边界止
           tail action window = 其后的 tool 事件序列
           intent 对齐：reasoning 文本的 TF-IDF 余弦，阈值 δ = 0.5
           ※ 额外保留 UNILATERAL_ACTION（对齐算法会漏掉的单边动作）
              ↓
⑤ 标注     五类 SIP 规则检测器
```

**phase 分布（实测）**：84% 的 divergence 落在 **ORIENTATION (44%) + IMPLEMENTATION (40%)**；VALIDATION/DEBUGGING/FINALIZATION 合计仅 16%。

> **鲁棒性检验**：论文排除掉 16 个命中 M2 empty-phase fallback 的任务后重算，ORIENTATION+IMPLEMENTATION 占比仍是 79%（57%+22%）——说明"技能信号集中在轨迹前半段"**不是** phase 塌缩的伪影。

### 2.3 五类 SIP 分类法（§3.4）

每类都有**确定性规则检测器**，不是 LLM judge。

#### 建设性（constructive）

| 代码 | 名称 | 检测签名 |
|---|---|---|
| **PS** | PROCEDURAL SCAFFOLDING | with-skill 的 phase 顺序跟踪技能某一节；关键实现事件引用了技能某一步；without-skill 省略了对应步骤 |
| **EP** | EDGE-CASE PROMPTING | with-skill 的写入在目标上**多了** if/try/assert 守卫；without-skill 碰同一个目标但没守卫；技能显式列举了该 case |

#### 中性（neutral）

| 代码 | 名称 | 检测签名 |
|---|---|---|
| **RE** | REDUNDANT EXPLORATION | intent 余弦**高**但 action 数**多**；最终 diff 的 AST 距离**小**；with-skill token 数 ≫ without-skill 但结果不变 |

> RE 合并了 pilot taxonomy 里的 REDUNDANT REITERATION 和 PARALLEL EXPLORATION 两类。

#### 破坏性（destructive）

| 代码 | 名称 | 检测签名 |
|---|---|---|
| **SA** | SURFACE ANCHORING | 技能里的一个 n-gram (n≥3) **字面**出现在 with-skill 的写入里；同一字符串在 without-skill 轨迹中不存在；该字面量与项目实际依赖/配置**不兼容** |
| **CB** | CONCEPT BLEED | with-skill 的**写入目标数严格更多**；新目标不在需求的 File-Operations 列表里；新内容与技能的某个**无关**章节余弦很高 |

**SA 与 CB 的区别在可观测性**：CTA 记录每个效应**发生在哪**、**在哪个 phase**、**哪些 action window 不同**、**匹配到技能的哪段内容**。

### 2.4 SA / CB 的行为学基础

论文把 SA 建立在两条已记录的效应上：**copy bias**（复述偏差）+ **in-context learning 的 token 共现强化效应**。CB 则是技能覆盖过宽导致的溢出。

案例（bash-defensive-patterns，ΔP = **+18.2 pp**）：agent 把技能的防御性 shell 头（`set -Eeuo pipefail`、trap 清理、变量加引号）**逐字抄进项目脚本**，还多写了两个测试文件（UNILATERAL_ACTION）——without-skill 轨迹完全没碰。

> **关键**：**这个任务 pass rate 是涨的**。+18.2pp 的增益里混着 10 次 SA 触发。**只看 ΔP 你看不出这 18.2pp 是"抄对了"还是"抄过头"**。CTA 把建设性和破坏性成分分开——这是它存在的意义。

---

## 三、论文的六个案例（可迁移的失败模式）

| # | 机制 | 可迁移的教训 |
|---|---|---|
| 1 | 技能提供了**显式完成边界**，agent 当成终止条件，**跳过了验证循环** | 技能里的"完成/交付"步骤可能**压制**默认验证。要写"验证"步骤而不是"提交"步骤 |
| 2 | 技能**大幅缩小了实现期搜索**，但**大幅抬高定向期阅读成本** | 净效应为正，但破坏性 SA/CB 成分仍可见——净 ΔP 和结构损伤是两回事 |
| 3 | 防御性 shell 模板被**近乎逐字**应用 | 部分字面复制是**正确的**边角处理（所以有 EP 触发和通过率增益），但主导行为是**检索而非综合** |
| 4 | baseline 已全过测试，with-skill 的额外活动**只是成本** | **"技能规定流程，agent 优化结果"**。饱和任务上，技能会让 agent 在结果已达成后继续劳动 |
| 5 | token 成本 6.80× 但 ΔP = 0，with-skill 继续跑 bash 验证/质量检查 | 质量检查链条的价值取决于 baseline 是否已经收工 |
| 6 | floor 任务上技能被消费但**没把 agent 挪离失败轨迹** | 技能对"规范完整但 agent 知识不足"的场景无能为力 |

**论文明确的"饱和任务"警告**（12 个 ceiling 任务中 ≥1.5× token overhead 且 ΔP ≤ 0）：技能规定流程，agent 优化结果——**在饱和任务上，技能让 agent 在目标已达成后继续做事**。

---

## 四、落地到 Hermes：可借用的方法（按成本/收益排序）

### 4.1 最高价值：把「基线分桶」加进 uplift 归因

论文 §4.2 的分桶规律说明**同一个基线不能一刀切**。本仓库 `skill-uplift-attribution` 修过一个真实 bug：probe 路径拿 Tier-2 自报后验去减 Tier-1 反应基线，导致**三个实际正增益的技能被误判为"有害"**。

CTA 给的修法方向（比单纯的 tier 匹配更进一步）：**按 baseline 表现分桶，每桶用同桶的臂**。本机当前还没有分桶基线，但一旦该技能 §7.3 的轻量反馈通道上线（有👍/👎），分桶就变得可行。

### 4.2 中等价值：SATURATION 探测（token 成本 vs 结果）

CTA 案例 4/5 揭示了一类**ΔP 完全看不见的损害**：技能让 agent 在结果已达成后继续劳动。

**可借的检测**（Hermes 侧可行）：对同一 session，比较 with-skill 与 without-skill 段的**token 数 / action 数**，与**结果是否变化**脱钩。若技能显著抬高成本但结果不变 → 疑似 RE（冗余探索）或饱和任务上的空转。

当前 `skill_uplift.py` 已有 action 计数（`n_observed` / `n_sessions`），但**没有把 token/action 成本纳入 uplift 报告**——这是明确的缺口。

### 4.3 长期价值：五类 SIP 的轻量本地版

论文的全套需要配对轨迹（成本高）。但几个检测器**不需要完整 trace 对齐**就能做**单边启发式**：

| SIP | 轻量本地版（只用 with-skill 侧） | 可用数据 |
|---|---|---|
| **SA** | 技能正文里的 n-gram (n≥3) 是否**字面**出现在本轮 assistant 输出/文件写入中 | 技能文本 + assistant 消息 |
| **CB** | 技能里与任务**无关**的章节关键词，是否出现在产出里 | 技能文本 + 产出 |
| **RE** | with-skill 段的 action 数是否显著高于同会话 pre-skill 段，而结果标记相同 | `state.db` 的 tool 事件 |
| **EP** | 产出里是否**多**了 if/try/assert 守卫（相对 pre-skill 段） | 输出文本 diff |
| **PS** | assistant 是否**引用**了技能的步骤（按序） | 输出文本 |

**SA 尤其便宜且高价值**——它是纯文本匹配，不需要配对执行。论文说 SA 在 ceiling 任务上主导（4.38/任务），而 ceiling 任务恰恰是**本机 cron 无人值守场景**的主要形态。

**局限（必须诚实标注）**：单边启发式**无法区分**「SA 导致失败」和「SA 恰好出现在一个成功的技能里」——论文的 SA 检测器需要 without-skill 侧来确认"同一字符串在 baseline 中不存在"。单边版只能报**候选**，不能报**判定**。

### 4.4 PREMATURE CLOSURE 检查（本机最可能踩的坑）

本仓库大量技能是**流程型**的（novel-writing、hermes-deep-inspection、daily-news-compilation），且都有明确的收尾步骤。CTA 的 PREMATURE CLOSURE 机制对本机**高度相关**：

> 技能说"完成/提交/写报告"，agent 就真的停了，**跳过了本该做的验证**。

**可查的具体实例**（本机已有真实候选）：
- `daily-news-compilation` — 报告写完就结束？是否验证了链接可达？
- `system-status-check` — 状态输出完就结束？是否实际跑了检查命令？

**这类 bug 在本机极难被发现**，因为 cron 无人值守，**没人报告"它本该再验一遍"**。

---

## 五、论文代码可直接跑

`https://github.com/WillChow66/CTA`（MIT, 21 commits, 3 stars, NeurIPS 2026 anonymized repo）

```bash
# ① 生成配对轨迹（需要 Docker + Anthropic token，几小时）
python run_all_skills.py --use-skill
python run_all_skills.py --no-use-skill

# ② 评估终态仓库（不做这步 pass_rate_delta 会一直是 0）
python run_all_skills_eval.py --use-skill --use-agent
python run_all_skills_eval.py --no-use-skill --use-agent

# ③ 准备 task metadata
python scripts/cta_prepare_data.py --traces-dir ./claude_process \
    --output ./config/cta_task_metadata.json

# ④ 跑 CTA 分析
python run_cta_analysis.py --all -v

# ⑤ 汇总
python scripts/cta_summarize_results.py --results-dir ./cta_output \
    --output ./cta_output/cta_summary.json
```

**代码布局**：`src/cta/`（解析器 / phase 分段 / 对齐 / SIP 检测 / 预测器）、`run_cta_analysis.py`（五模块 CLI，支持 `--module3-only` 逐模块调试）。

**本机不跑全量**（需要 Docker + Anthropic token + 数小时）；但 §4.3 的**轻量本地版**可以直接在 `state.db` 上实现，成本接近零。

---

## 六、与本仓库既有技能的分工

| 技能 | 测什么层 | 本次关系 |
|---|---|---|
| `skill-uplift-attribution` | **结果层**：ΔP / execution uplift | 本技能的**互补**——它看不见 ΔP 相同但行为迥异的情况 |
| `upliftmem-evsi-probing` | 理论（EVSI 闭式解） | 本技能提供了 CTA 这条实证路线 |
| `uplift-rag` | 单文档 uplift | 更细粒度 |
| `tool-call-uplift-gating` | 调用门控 | 互补 |

**读法**：一条技能 "uplift = 0" **不等于** "这条技能没用"。CTA 在 ΔP≈0 的 45/49 个任务里找到 522 处 SIP 实例。反过来，一条技能 "uplift > 0" **也不等于** "它是净收益"——bash-defensive-patterns 的 +18.2pp 里混着 10 次表面锚定。

---

## 七、给 Hermes 技能作者的直接建议（从五类 SIP 反推）

1. **别写"完成"步骤，写"验证"步骤**。PREMATURE CLOSURE 的教训：显式的完成边界会终止 agent 的验证循环。写"跑测试并确认通过再提交"，而不是"提交并写文档"。

2. **给技能里的字面量加护栏**。SA 的检测签名是"字面 token 出现在项目代码里且与项目实际依赖不兼容"。技能里写死版本号/import 路径/参数名时，**标注"这是示例，按项目实际值替换"**——否则 agent 会逐字抄。

3. **控制技能的覆盖面**。CB 的签名是"写入目标数变多，且新内容与技能的无关章节高余弦"。技能章节越宽，agent 越容易顺手做没要求的事。**每节都要能对应一个明确需求**。

4. **饱和任务上是纯成本**。当 baseline 已经做对时，技能的额外流程只是 token 成本（论文实测 12 个 ceiling 任务 ≥1.5× overhead 且 ΔP≤0）。**技能加载策略应该看任务难度，不该无脑加载**。

5. **地板任务上技能无用**。floor 任务（baseline 失败）上技能"被消费但没把 agent 挪离失败轨迹"。**知识缺失不是流程能补的**。

---

## 八、来源

- 主论文: https://arxiv.org/abs/2605.11946 — Counterfactual Trace Auditing of LLM Agent Skills, Zhou/Liu/Li/Rossi/Hu (ASU + USC + Adobe Research), v1 2026-05-12 / v2 2026-05-28, NeurIPS 2026 投稿
- PDF 全文: https://arxiv.org/pdf/2605.11946v2
- 代码: https://github.com/WillChow66/CTA (MIT, 21 commits, 2026-07-28 最后更新)
- 基准: SWE-Skills-Bench (与 CTA 同 repo，含 `README_SWE-Skills-Bench.md`)
- 检索侧对照: https://arxiv.org/abs/2608.25500 — CaSKG, Counterfactual-Causal Skill Graphs（方向条件化的反事实探针：remove / substitute / reorder skill 对，Bayesian 平滑聚合边置信度；code: github.com/ZhiyuanLi218/Caskg）
- 风险侧对照: https://arxiv.org/pdf/2606.10388v4 — SameCapRisk-Bench, "Right Family, Wrong Skill"（技能检索的**风险暴露**评估，与 CTA 的 destructive SIP 互补）
- 技能检索综述: https://aclanthology.org/2026.findings-emnlp.1955.pdf — SRA-Bench（skill retrieval / incorporation / application 三阶段分解评测）
- 近邻: https://arxiv.org/abs/2609.36805 — UpliftMem（execution uplift 理论，本仓库 `upliftmem-evsi-probing` 已覆盖）
