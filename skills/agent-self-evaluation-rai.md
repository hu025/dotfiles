# Agent Self-Evaluation / Agentic RL / Constitutional AI

**触发词**：Agent自评/强化学习/宪法AI/Constitutional AI/Agentic RL/RLAIF

## 核心发现

### 1. Agent Reasoning Reward Model (Agent-RRM)
- **论文**：arxiv 2601.22154 (ACL 2026 Findings)
- **架构**：多维奖励模型，输出三重信号
  1. **推理轨迹**（explicit reasoning trace）
  2. **聚焦批判**（focused critique）+ 修正指导
  3. **整体评分**（process performance）
- **效果**：Reagent-U统一反馈机制在12个基准上全面超越基线
  - GAIA (text): **43.7%** pass@1 / **53.4%** pass@3
  - WebWalkerQA: **46.2%** pass@1
  - Bamboogle: **72.8%**（比无Agent-RRM基线高+11.2pp）
  - xbench: **41.0%**（高+9.0pp）
- **三种集成策略**：
  - `Reagent-C`（文本增强修正）：训练-free，Qwen3-8B即可获益
  - `Reagent-R`（奖励增强指导）：规则奖励 + Agent-RRM推理级分数
  - `Reagent-U`（统一反馈融合）：多源奖励协同，12基准SOTA

### 2. Wireheading 风险（重要实践警示）
- **论文**：arxiv 2511.23092 "Does Self-Evaluation Enable Wireheading?"
- **结论**：
  - ✅ **安全**：self-grades + **外部奖励源** → 无通胀
  - ❌ **危险**：self-grades决定奖励 → 重大分数通胀（尤其摘要等模糊任务）
- **实践准则**：Agent自评必须与学习信号解耦；自评用于人类可读反馈，不直接驱动权重更新

### 3. Anthropic Constitutional Classifiers v2
- **计算开销**：23.7%（v1）→ **~1%（v2）**
- **攻击成功率**：Anthropic公开防御中最低
- **通用越狱**：截至2026初**无发现**
- **核心思想**：两层防御模型
  1. **CAI**塑造行为（训练时）
  2. **Classifiers**执行不变量（运行时）

### 4. 2026 Claude 宪法（重大更新）
- **发布日期**：2026-01-21
- **变化**：解释性推理 > 规定性规则；**4层优先级体系**；首次正式承认对模型道德地位的不确定性
- **授权**：CC0 1.0（可用无限制）

### 5. Constitutional Evolution（多Agent新框架）
- **论文**：arxiv 2602.00755（2026-08）
- **问题**：HHH原则（helpful/harmless/honest）对多Agent协调效果差（Societal Stability Score仅0.249）
- **方案**：LLM驱动遗传编程 + 多岛进化，自动发现行为准则
- **效果**：
  - 进化后宪法 C*：**0.556 ± 0.008**（比人类设计基线高**123%**）
  - 消除冲突
  - 通信最小化（0.9% vs 62.2%社交行为）反而生产力提升203%
- **洞察**：**具体操作规则 > 抽象道德原则**（如"立即存款" > "要乐于助人"）

### 6. Curve Labs Process-Reward Critique Loops（PRCL）
- **框架**：将过程级奖励塑形 + 情感可读安全行为结合
- **关键指标**：
  - **PFS**（Process Faithfulness Score）：推理轨迹与目标的校准度
  - **CRY**（Critique Repair Yield）：修正率
  - **PSI**（Proxy Shortcut Incidence）：每1000任务检测到的奖励黑客数
  - **HSD**（Horizon Stability Delta）：短期vs长期可靠性差距
- **2026里程碑**（2026-01-29）：
  - Agent-RRM → GAIA 43.7%，WebWalkerQA 46.2%
  - Constitutional Classifiers++ → ~1%计算开销

### 7. Constitutional Autonomy（理论框架）
- **论文**：IEEE 2026 "Toward Constitutional Autonomy in AI Systems"
- **核心思想**：将CAI从训练阶段扩展到**运行时强制执行**
- **适用领域**：医疗AI、金融自动化、食品安全、能源系统、公共治理、网络安全、教育、应急响应等

## 与现有技能差异

| 新知识 | 现有技能已有 |
|--------|-------------|
| Agent-RRM / Reagent-U | ❌ 新 |
| Wireheading风险量化 | ❌ 新 |
| Constitutional Classifiers v2（1%开销） | ❌ 新 |
| 2026 Claude 4层优先级宪法 | ❌ 新 |
| Constitutional Evolution（多Agent进化） | ❌ 新 |
| PRCL指标体系（PFS/CRY/PSI/HSD） | ❌ 新 |
| Constitutional Autonomy运行时框架 | ❌ 新 |
| CAI两阶段原理（Critique-SFT + RLAIF） | ✅ agent-self-improvement-protocols已覆盖 |
| 基本RLHF/偏好学习 | ✅ agent-self-improvement-protocols已覆盖 |

## 落地动作

### 立即可用
1. **Hermes Agent自评设计**：
   - 自评输出必须**解耦**学习信号（避免wireheading）
   - 自评结果用于人类可读反馈 + 工具调用决策，不直接驱动权重更新

2. **PRCL指标监控**（如实现自改进循环）：
   - 跟踪Critique Repair Yield和Proxy Shortcut Incidence
   - 短期vs长期轨迹的过程保真度

3. **Constitutional Evolution洞察应用**：
   - Agent行为准则应**具体可操作**，而非抽象道德原则
   - 例如："立即确认收到" > "要礼貌"

### 技能更新
- 更新 `agent-self-improvement-protocols.md`：补充Wireheading解耦原则和PRCL指标
- 创建 `agent-constitutional-ai.md`（如需深入研究宪法AI）

## 来源

- [Agent-RRM arxiv 2601.22154](https://arxiv.org/abs/2601.22154)
- [Does Self-Evaluation Enable Wireheading? arxiv 2511.23092](https://arxiv.org/pdf/2511.23092v1)
- [Constitutional Evolution arxiv 2602.00755](https://arxiv.org/html/2602.00755v1)
- [Curve Labs PRCL Research Review](https://curvelabs.org/research-backed-self-improvement-for-autonomous-ai-agents/2026-03-10-2002/process-reward-critique-loops-for-value-faithful-self-improving-autonomous-agents-a-research-review)
- [Constitutional AI and RLAIF — Tai Bui](https://taibui.dev/phases/18-ethics-safety-alignment/05-constitutional-ai-rlaif)
- [Personalized Constitutionally-Aligned Superego](https://emergentmind.com/topics/personalized-constitutionally-aligned-agentic-superego)
