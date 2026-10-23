---
name: agent-judge-agreement-metrics
description: LLM-as-judge 验证与在线质量闭环。用于校验 judge 与人标的一致性、二分类下多个一致性指标其实是同一个数、abstention(CANNOT_ASSESS)三种处理方式估计的是不同量、rubric 评估的 micro/macro/item 聚合层级、以及在线 drift 检测与自动回滚门控。触发词：LLM-as-judge 验证、judge 一致性、Cohen kappa、judge 校准、在线评估漂移、生产反馈闭环。
triggers:
  - LLM-as-judge validation
  - judge agreement metrics
  - CANNOT_ASSESS abstention handling
  - judge-human agreement ceiling
  - online eval drift detection
  - rubric micro vs macro aggregation
  - eval-driven auto rollback gate
category: research
---

# LLM-as-Judge 验证与生产反馈闭环

## 核心判断：先问"测了什么"，再问"用哪个指标"

绝大多数评估报告的错误不是算错，而是**报的数在语义上有歧义**。同一个标量在二分类 judge
上可以代表五个不同名字的统计量，再叠加 abstention 处理和聚合层级的选择，一个数字能被
解读成三四个不同的量。

**规则：任何一致性数字必须同时声明 5 件事**（缺一件数字不可解释）：
判断尺度 / abstention 与 tie 的处理模式 / coverage / 混淆矩阵 / 聚合层级。

---

## 1. 二分类下 5 个指标塌缩成 1 个数

在非退化二分类 verdict（MET/UNMET）上，以下 5 个统计量**在数值上完全相同**：

`Pearson r` = `Spearman ρ` = `Kendall τ` = `phi 系数` = `MCC`

原因：
- phi ≡ MCC：对二值向量做 Pearson 相关即 phi 系数（Matthews 1975）
- Spearman ≡ Pearson：只有两个取值时，rank 映射是仿射的，而 Pearson 对仿射缩放不变
- Kendall ≡ phi：从混淆矩阵四格直接代入 tie-corrected Kendall 得到同一表达式

**同时报三个相关系数 = 把同一个数算三遍装成三角验证。这是虚假佐证。**

只有 **accuracy** 和 **Cohen's κ** 携带独立信息（κ 与上述值的差距在数学上有意义）。
多分类 ensemble 下 Fleiss' κ ≈ Krippendorff's α ≈ 平均两两 κ（差一个有限样本修正，量级 O(1/N)，
在报告精度下不可见）——**三者选一个即可**。

### κ 差值的唯一诊断含义

κ 与 φ/MCC 的分子相同，分母不同；差距由**judge 的正例率 vs 人的正例率的边际失配**决定：

- 边际完全匹配 → κ = φ/MCC（且二者一阶抽样方差也相等）
- judge 系统性偏严/偏松 → κ 严格更低
- 极端偏斜（正例率接近 0 或 1）时，小的 accuracy 差距会把 κ 打到 0 甚至负值
  = **kappa 悖论**（Feinstein & Cicchetti 1990）

诊断动作：算出 `κ` 和 `φ/MCC`，两者差距拉大 = judge 边际漂了，去查 prompt/模型，不是去调相关性。

---

## 2. 弃权 (CANNOT_ASSESS) 是估计量选择，不是预处理

judge 常被要求输出第三种 verdict `CA`（信息不足无法判定）。三种处理方式估计**不同的总体量**，
不可互换：

| 模式 | 做法 | 估计的是什么 |
|---|---|---|
| **Exclude** | 丢弃任一方弃权的样本对 | 覆盖子集上的 selective accuracy；只在 MAR/MCAR 假设下才等于总体量 |
| **Recode-as-negative** | CA → UNMET | 普通误分类损失；**丢掉了 CA 原本携带的校准信息**，偏差符号随 criterion 正负权重翻转 |
| **Three-class** | 保留为第三类，用多类 κ / 加权距离矩阵 | 真正的三分类一致性；权重矩阵必须显式声明 |

同一张混淆表三种模式给出三个不同的 accuracy/κ（论文 Appendix B 有完整算例）。

**关键陷阱**：recode 模式下，一个"对不确定负例弃权"的 judge 和一个"硬判 UNMET"的 judge 拿到**完全相同的分数**。若训练目标显式奖励校准弃权（selective prediction），recode 等于**抹掉了目标函数所依赖的信号**。

**正确报法（selective prediction 双轴）**：
```
coverage        = 非弃权预测占比
selective_acc   = 覆盖子集上的准确率
```
两个一起报，不要压成一个标量。弃权率本身要作为**独立指标**监控——它漂移通常是 prompt 不稳定
或分布漂移的**最早可观测症状**，早于准确率下滑。

### 引入第三类时二分类等价性彻底失效

仿射-rank 论证要求取值恰为 2 个。三值（MET / UNMET / CA 序数编码）时 rank 映射只在
MET 与 UNMET 流行率相等时才是仿射的，泛型下 Pearson ≠ Spearman。phi 没有规范的三分类对应物，
Gorodkin 的多分类 MCC 扩展既不等于任一编码下的 Pearson 也不等于 Kendall。

三分类下 Fleiss' κ 把 MET–UNMET 和 MET–CA 混淆**等价惩罚**；Krippendorff's α 配二次序数
difference function 则认为 CA "在中间"，惩罚更轻。**同一批 judge 两种统计量可能给出不同排名。**

---

## 3. rubric 评估的聚合层级：micro / macro / item-level

rubric 评估是嵌套结构（criteria 在 items 内、items 在 prompts 内、ensemble 内同一模型多次判定），
三个聚合层级回答不同问题：

- **Micro**：把所有 criterion 判定池化成一张长表算指标 → 被"高频易判"criterion 主导
- **Macro**：每个 criterion 单独算再无权平均 → 每条标准等权，与训练难度无关
- **Item-level**：先按 rubric 权重把一个 item 的多个 verdict 压成单 pass/fail 再算

**两条关键机制**：
1. 聚合层级与 bootstrap 单位必须匹配。criterion-level cluster bootstrap 配 macro；
   item-level cluster bootstrap 配 item-level；**平坦 decision-level bootstrap 只在（通常为假的）
   独立假设下配 micro**。critia 聚集在 item 内且同一 judge 的一次错误会传播到该 item 的多条标准，
   聚集相关为正时平坦重采样**低估不确定性**。
2. criteria 超过个位数时**三个都报**；只报一个数时必须显式命名层级。

**退化 criterion 处理**：rubric 标准常是罕见的。人工标签恒定或 judge 预测恒定的 criterion 会让
Pearson/φ/Spearman/Kendall 未定义、κ 无意义。这类必须**带计数标 NA 报出**，不能静默丢弃或
强塞为 0。

---

## 4. 相关性不等于一致性（judge 能力诊断）

常见误判：看到 r = 0.95 就认为 judge 可用。

- 相关性只衡量**相对关系**，不衡量**绝对一致**，也不扣除**偶然一致**
- 场景 1：judge 系统性低打 0.3 分 → r = 0.95 但 κ 只有 0.45，**不通过**人类相似性检验
- 场景 2：judge 像真人一样有正常波动 → r = 0.88，κ = 0.79，**通过**

**人类相似性 z 检验**（"judge 版图灵测试"）：
```
z = (κ_LLM − μ_human) / σ_human
```
μ/σ 来自 human-to-human 两两 κ 分布。**|z| < 1 才是"像人"**，κ 高但 |z| 极大意味着
"超人般一致地系统性偏离"——理解力有但打分刻度错了。

另一个诊断量：**inter-judge agreement**（ensemble 内部一致）能标出 rubric 本身没说清的条目，
与跟真值的一致性是两个独立的量。

其他可移植结论（来自 Judge's Verdict / LLM-R empirical study）：
- **同时给参考答案和分数描述**是可靠评估的关键；缺任一个都会显著降低与人标的一致性，尤其在弱 evaluator 上
- **greedy decoding 分数零方差，但与人类判断的相关性更低**；采样引入方差但更贴近人类偏好纹理
- **二元/低保真打分比 1–5 高精度打分可靠**——LLM 无法稳定校准细粒度区分
- **pairwise 优于绝对打分**（相对判断比校准到抽象刻度更容易）；但生产监控需要逐条打分，
  所以 pairwise 用于选型/回归，criteria-based 用于在线监控
- **长度偏置**：必须对抗性测试，打乱输出长度，否则长回答无理由地赢
- **不重新验证的人工 spot check 一旦分歧率上升，说明 rubric 需改或生产行为已变**

---

## 5. 生产反馈闭环：在线评估 → 校准 → 回滚

### 分层选型（混合评估栈）

```
确定性规则     → 格式/长度/必需要素。快、便宜、100%可靠。做第一道关口
LLM judge      → 有用性/准确性/语气/幻觉。字符串匹配查不出来的维度
人工标注队列    → 高风险域（医疗/法律）+ 建 golden dataset + 校准 judge
传统指标        → 有参考答案的结构化任务（exact match / 语义相似度）
```
**不要在有 ground truth 时用 LLM judge 换更简单的指标。**

### 在线评估的三个运营控制

- **采样率**：按比例评估生产 trace，避免全量成本爆炸
- **过滤与定向**：面向用户的全评，内部测试 trace 降采样
- **保留/定价副作用**：在线评估器在 trace 上跑会自动把该 trace 升级为扩展保留，
  直接影响存储时长与 trace 计费——策略必须与数据保留政策一起设计

### 对齐循环（替代 prompt 猜谜）

```
收集人工纠正  →  把它做成 few-shot 校准样例  →  跟踪 agreement 随时间变化
```
prompt 迭代无法关闭"技术上正确"与"可以信任"之间的差距，必须靠可测量的对齐循环。

### 数据飞轮

```
生产 trace → Insights 分析 → 抽出问题 case 进 dataset → 变成回归测试
     ↑                                              ↓
  更好的 trace  ←  改进  ←  评估  ←  更可信的 judge（靠人工纠正校准）
```
被 judge 标记为幻觉的 trace → 路由到人工复核队列 → 人工确认 → **加入 golden dataset** →
修复后重测。这是把"用户投诉才发现问题"变成"实时发现问题"的唯一机制。

### Auto-rollback 门控（推导，非直接引用）

生产 judge 的用途不是打分，是**触发动作**。因此门控阈值必须基于上面的度量语义：

1. **只对二元 MET/UNMET 判据设自动门控**。序数 1–5 分的高精度刻度不适合做硬阈值——
   LLM 无法稳定校准细粒度区分，阈值抖动会产生大量假回滚。
2. **门控信号用混淆矩阵的 FP 方向（偏严/偏松）而非单一准确率**。对称指标无法区分
   "漏掉正例"和"过度预测正例"，而这两者的处置完全不同（前者查覆盖不足，后者查过度触发）。
3. **必须设 coverage 门**。judge 弃权率突然飙升 → 它已经不可用了，此时任何分数都不能触发
   自动回滚（分数只在覆盖子集上有意义）。**弃权率漂移应作为独立的、优先级更高的告警。**
4. **回滚前看 macro 而非 micro**。micro 被高频标准掩盖，macro 更容易先发现某条低频关键标准的退化。
5. **保留回滚证据**。回滚事件必须落盘当时的 trace + 混淆矩阵，否则事后无法区分
   "是真退化"还是"judge 自己漂了"。

---

## 上报清单（11 项，可直接复用为 review 项）

1. 先声明判断尺度，再声明指标（二值/成对偏好带tie/序数/连续/带弃权名义）
2. 二分类下 Pearson/Spearman/Kendall/φ/MCC **至多报一个**
3. accuracy 必须与一个边际敏感的一致性指标（Cohen's κ）同时报
4. **必须报混淆矩阵**，或至少 precision + recall——否则无法诊断 judge 偏严还是偏松
5. 退化 criterion 带计数标 NA，不得静默丢弃
6. 每个数字都要标注 CA/tie/invalid 的处理模式
7. **弃权率、tie 率、invalid 率作为独立指标上报**
8. exclude 模式下 coverage 与覆盖子集表现必须成对上报
9. 三分类/多分类必须显式给出权重（代价）矩阵
10. 显式声明聚合层级（micro/macro/item-level）
11. ensemble 只报一个 inter-judge 统计量 + 每个 judge 的混淆矩阵

---

## 来源

- Rao & Callison-Burch, *Agreement Metrics for LLM-as-Judge Evaluation: What to Report and Why*
  https://arxiv.org/abs/2606.00093 — 指标塌缩证明、三种 abstention 模式、聚合层级、11 项清单
- *Judge's Verdict: LLM Judge Capability Through Human Agreement*
  https://arxiv.org/abs/2510.09738 — κ vs 相关性、Turing Test z 分数
- *An Empirical Study of LLM-as-a-Judge: How Design Choices Impact Evaluation Reliability*
  https://arxiv.org/abs/2506.13639 — 参考答案+分数描述、greedy vs 采样
- LangChain, *How to Calibrate LLM-as-Judge with Human Corrections* (2026-03)
  https://www.langchain.com/resources/llm-as-a-judge — 对齐循环、数据飞轮、在线评估运营控制
- Braintrust, *What is an LLM-as-a-Judge* — 长度偏置对抗测试、CI/CD 评估
  https://www.braintrust.dev/articles/what-is-llm-as-a-judge
- LLM-RUBRIC (ACL 2024) https://aclanthology.org/2024.acl-long.745/ — 个性化校准网络；
  关键结论：直接问 LLM 总体满意度几乎无效，必须拆成细粒度维度再校准