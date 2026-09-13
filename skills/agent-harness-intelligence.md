# Agent Harness Intelligence: JIT-Agent / AgentFlow / CORAL / AweAgent

> 2026-09-14 research — 新发现框架

## 核心主题

**Harness Intelligence = 模型能力的另一半**

Agent能力 = Foundation Model + Agent Harness（记忆/规划/动作/工具编排）
错误的memory/planner/action protocol可以让强模型失效；
反之，强harness可以让弱模型超越强模型。

---

## 1. JIT-Agent — Just-in-Time Harness Generation

**论文**: arXiv:2608.25593 (2026-08-26, v2)
**作者**: 上海交大LV-NUS Lab
**模型**: JIT-Agent-27B (基于Qwen3.6-27B训练)

### 核心洞察

| 范式 | 描述 | 问题 |
|------|------|------|
| AOT (Ahead-of-Time) | 提前优化harness，期待泛化到未来任务 | 任务异质时难以泛化 |
| **JIT (Just-in-Time)** | **任务来临时即时生成专属harness** | 首次提出 |

### 四模块协议 (Harness Protocol)

JIT-Agent将harness分解为四个可组合模块：

1. **Memory Module** — 记忆管理策略
2. **Planning Module** — 规划策略
3. **Action Module** — 动作执行协议
4. **Capability Orchestration Module** — 工具/技能注册表

不同任务结构 → 不同模块实例 → 专属executable protocol

### 三阶段训练

- **Stage I**: Customization Learning — 从教师生成的protocol-compliant样本学习任务适配
- **Stage II**: Repair Supervision — 将失败生成转为修复轨迹（编译错误/接口不匹配/运行时失败 → 监督信号）
- **Stage III**: Evo-GDPO (Evolutionary Group-Decoupled Policy Optimization) — 从harness archive蒸馏性能信号，使generator自我进化

### 性能结果

| Backbone | Benchmark | 提升 |
|----------|-----------|------|
| DeepSeek-V4-Flash + JIT-Agent | DeepSearchQA | **+9.1** (超越GPT-5.6) |
| DeepSeek-V4-Flash + JIT-Agent | PinchBench | **+8.7** |
| DeepSeek-V4-Flash + JIT-Agent | OdysseyBench | **+4.3** |
| GLM-5.2 + JIT-Agent | xBench-DS | **+12.0** |
| GLM-5.2 + JIT-Agent | AgentIF | **+6.9** |
| GLM-5.2 + JIT-Agent | 平均规划任务 | **+20.2** |

JIT-Agent生成的harness与OpenCode/Claude Code成熟runtime性能持平。

### 关键设计：Harness as Code

```
代码即harness → JIT-Agent生成结构化可执行模块，而非无约束agent程序
```

### 生成harness示例

- **EvidenceGuidedMemory**: 检索任务，首要瓶颈是证据显著性。scorer对每步赋予evidence value，只将top-K传入下轮上下文，完整轨迹保留用于审计。
- **Abacus**: 数值分析任务，聚合移出LLM推理 → StructuredStateMemory中存储typed state (region/country/mean)，最终答案直接来自interpreter派生量。
- **Player Piano**: 批量配置文件迁移，StructuredPlanning发射typed discover/process-file/final-answer步骤，Python dispatcher执行，non-LLM确定性验证。
- **Mulligan**: 短文档任务，线性plan，PlanAwareToolPolicy只暴露plan相关工具，失败时同一step重试(最多2次)。

---

## 2. AgentFlow — In-the-Flow Agentic System Optimization

**论文**: arXiv:2510.05592 (斯坦福大学)
**会议**: ICLR 2026 Oral (Top 1.1%)
**代码**: github.com/lupantech/AgentFlow

### 核心架构

四个模块通过共享Memory M和Toolset K协调：

```
Planner(P) → Executor(E) → Verifier(V) → Generator(G)
```

- **Planner**: 生成sub-goal + 选择工具 + 从Memory检索上下文
- **Executor**: 调用工具
- **Verifier**: 评估执行结果 → 二进制验证信号(v=1终止/v=0继续)
- **Generator**: 产生最终解

### Flow-GRPO训练算法

**问题**: 离线SFT → **灾难性-19.0%崩溃**；在线RL → **+17.2%提升**

Flow-GRPO核心：
- Final-outcome reward广播给所有中间步骤
- Group-normalized advantage减少方差
- 将多步RL分解为可 tractable的单步policy更新

### 性能结果

| 任务类型 | AgentFlow 7B相对基线提升 |
|----------|--------------------------|
| 搜索任务 | **+14.9%** |
| Agentic任务 | **+14.0%** |
| 数学任务 | **+14.5%** |
| 科学任务 | **+4.1%** |

7B模型超越GPT-4o。

### 重要结论

- **在线微调 >> 离线SFT**（对agentic系统）
- **推理时增加turns (3→10) 持续提升性能**
- Flow-GRPO随模型规模(3B→7B)线性提升

---

## 3. CORAL — Autonomous Multi-Agent Evolution

**论文**: arXiv:2604.01658
**会议**: COLM 2026
**代码**: github.com/Human-Agent-Society/CORAL
**Stars**: 980

### 核心设计

CORAL用**共享持久化内存文件系统**替代LLM-to-LLM对话：

```
.git-worktree/ (每个agent独立隔离)
  ├── .coral/public/   ← 共享知识，所有agent可读
  └── .coral/private/  ← grader密码等(隔离)
```

- Manager daemon评分每次commit
- Heartbeat prompts打断agent：`reflect` / `consolidate` / `pivot`
- Docker隔离（agent以非特权用户运行，无法读取.grader private/）

### 性能结果

| 场景 | 结果 |
|------|------|
| SWE-bench APASS (4-agent Claude Opus 4.6) | **89.4%** (SOTA: 87%) |
| APASS单agent基线 | 56.0% |
| Kernel Engineering (4-agent) | 1,103 cycles vs 单agent 1,350 |
| 跨agent交叉授粉 | 66%新记录来自cross-agent parent |

### 关键洞察

- 共享持久化内存比向量数据库简单得多（就是模拟GitHub仓库结构）
- Multi-island runs: agent分区隔离，探索范围更广
- **安全**: agent无法读取.grader/private/（即使用Bash）

### 插件生态

支持多种coding agent harness:
- Claude Code (default)
- Codex
- Cursor Agent
- Kiro
- OpenCode

---

## 4. AweAgent — Unified Composable Agent Framework

**代码**: github.com/AweAI-Team/AweAgent
**架构**: 统一执行核心 + 可组合Scaffold

### 核心设计

Agent拆分为三层：
1. `step(ctx) -> action` policy
2. AgentLoop驱动
3. AgentContext共享总线（messages/trajectory/stats/LLM/tools/tool-call格式/runtime）

**添加新agent = 重新组合这三部分**，无需fork引擎。

### Protocol-centered Extensibility

所有组件通过小协议和entry-point registry暴露：
- LLM backends / tools / runtime sandboxes / agent scaffolds / evaluators

添加新组件 = 实现一个小协议 + 注册一个entry point，**无需修改核心引擎**。

### 内置Scaffold

| Scaffold | 类型 | 备注 |
|----------|------|------|
| SearchSWE | coding | Swebench基线 |
| DeepSearch | 深度搜索 | retry-until-answerable |
| IterResearch | 深度研究 | +interaction scaling |
| Terminus-2 | terminal | tmux JSON keystrokes |
| CalibForge | terminal | bash + file-editing |

### 支持Benchmark

- BeyondSWE / ScaleSWE
- SWE-bench Pro
- DeNovoSWE
- Terminal-Bench 2.0
- NL2Repo

---

## 跨框架对比

| 框架 | 核心创新 | 训练方式 | 关键洞察 |
|------|----------|----------|----------|
| **JIT-Agent** | 即时harness生成 | 3阶段(SFT+repair+Evo-GDPO) | 模型+Harness共同决定能力 |
| **AgentFlow** | 在线流内Planner优化 | Flow-GRPO RL | 离线SFT对agentic系统有害 |
| **CORAL** | 多agent协同进化 | 进化算法+心跳机制 | 共享文件>向量DB，简单更有效 |
| **AweAgent** | 统一可组合核心 | 无（框架） | 协议中心化扩展性 |

---

## 对Hermes Agent的落地价值

### 1. Harness Intelligence认知升级
- Agent能力 = 模型 + Harness（记忆/规划/动作/工具）
- 不只是选模型，**harness设计是first-order determinant**
- JIT-Agent证明：即使DeepSeek-V4-Flash + JIT → 超越GPT-5.6

### 2. Planner在线优化（AgentFlow）
- Hermes的subagent驱动开发可借鉴Flow-GRPO思路
- **不要离线SFT → 在线RL微调Planner策略**
- Verifier模块可增强任务验证能力

### 3. CORAL模式
- 多agent协同持久化内存（.coral/public/结构）
- 可迁移到Hermes的任务协作场景
- Heartbeat prompt模式值得借鉴

### 4. AweAgent的Protocol-extensibility
- Hermes技能系统可借鉴entry-point registry模式
- 让新工具/新LLM backend通过小协议注册，而非修改核心

---

## 来源链接

- JIT-Agent: https://arxiv.org/abs/2608.25593 | GitHub: github.com/bingreeky/JIT | HF: huggingface.co/JIT-Agent
- AgentFlow: https://arxiv.org/abs/2510.05592 | GitHub: github.com/lupantech/AgentFlow | Demo: huggingface.co/spaces/AgentFlow/agentflow
- CORAL: https://arxiv.org/abs/2604.01658 | GitHub: github.com/Human-Agent-Society/CORAL
- AweAgent: https://github.com/AweAI-Team/AweAgent
- Prime Agent: https://github.com/PrimeIntellect-ai/prime-agent (persistent IPython REPL + RLM abstraction)
