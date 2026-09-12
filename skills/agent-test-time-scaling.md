# Agent Test-time Compute Scaling · 技能文档

## 触发词
Agent推理优化 / TTC / test-time compute / 推理时间 scaling / 并行采样 / Reflection / 验证器

## 核心价值
用推理时间换性能——不升级模型，通过推理策略让 32B 模型超越 671B。

---

## 一、ATTS 框架（OAgents · OPPO PersonalAI）

arXiv:2506.12928 · [GitHub](https://github.com/OPPO-PersonalAI/OAgents)

### 四类策略

#### 1. 并行采样（Parallel Sampling）
| 方法 | 原理 | 效果 |
|---|---|---|
| Best-of-N (BoN) | 生成 N 条独立轨迹，用 reward model 选最优 | 基线，简单有效 |
| Step-wise BoN | 每个中间 step 都做 BoN 采样 | 误差累积时效果更好 |
| Beam Search | 维护 top-K 剪枝劣质候选 | 适合长轨迹 |
| DVTS | 多样性验证树搜索 | 探索空间更广 |

#### 2. 选择性 Reflection（Sequential Revision）
**关键发现**：每步 reflection 不一定有效；在**表现差时**触发 reflection 效果更好。

> 知道何时 reflection，比每步都 reflection 更重要。

#### 3. 验证与结果融合（Verifier & Merging）
List-wise 方法显著优于逐项投票和评分方法。

#### 4. 多样化 Rollout
多 Agent 协同采样 > 单 Agent 采样。

### 生产建议
```
简单任务（Level 1）→ BoN
中等任务（Level 2）→ 选择性 Reflection + BoN
复杂任务（Level 3）→ Beam Search + List-wise Verifier + 多Agent
```

---

## 二、SWE-Reasoner：32B > 671B 的实证

arXiv:2503.23803 · [GitHub](https://github.com/yingweima2022/SWE-Reasoner)

### 核心发现
- 4-bit 量化 32B 模型 + TTC = **46% SWE-bench Verified**
- 超越 DeepSeek R1 671B（更大模型）
- 超越 OpenAI o1

### 内部 TTC + 外部 TTC

**内部 TTC**：开发上下文轨迹合成
- 真实软件仓库 bootstrapping 多阶段推理
- 拒绝采样：按准确性和复杂度筛选轨迹

**外部 TTC**：开发过程搜索策略
- Reward Model 引导的关键决策点计算分配
- 克服"仅终点验证"的局限性

### 适用场景
- 私有代码库（不能上云 API）
- 单 GPU 部署（RTX 4090 即可）
- 需要精确故障定位 + Patch 生成

---

## 三、Multi-Agent Reasoning 的 Pareto 最优性

arXiv:2605.01566 · [Multi-Agent-LLMs](https://github.com/Multi-Agent-LLMs/lm-evaluation-harness)

### 四种范式对比（MMLU-Pro, Llama 3.1 70B）

| 范式 | 计算模式 | 延迟 | 准确性 |
|---|---|---|---|
| Self-Consistency | 并行 | 低 | 中 |
| Self-Refine | 串行 | 高 | 中 |
| **Debate** | 并行 | 低 | **高** |
| **MoA (Mixture of Agents)** | 混合 | 中 | **最高** |

### 关键洞察
- CoT 本质是串行，延迟是瓶颈
- Multi-Agent Debate 并行扩展，延迟低，准确性高
- **Score vs Compute/Time 是评估 Agent 的正确方式**
- 共识在 100 samples 后趋于平坦

---

## 四、生产 Agent 架构 5 件套（2026 最佳实践）

来源：[Mindlyctica · Anatomy of a production AI agent in 2026](https://www.mindlyticai.com/blog/agent-architecture-2026)

```
Planner  →  规划层（现在模型足够好，规划不再是瓶颈）
Worker   →  执行层
Verifier →  验证层（真正的瓶颈！）
Memory   →  记忆层
KillSwitch → 熔断层（大多数 Agent 缺少这个）
```

### 时间预算分配示例（4 秒管道）
- Intake: 100ms
- Plan: 800ms
- Execute: 2.5s
- Verify: 300ms
- Persist: 300ms

### 关键认知
1. **验证层 > 规划层** — 2026 年模型规划能力已足够，验证才是瓶颈
2. **Preflight 工具** — 用 agent 意图参数 dry-run 工具，而不是猜测
3. **双 Agent 并行** — 高风险决策跑两个 Agent，不同意时升级人类

### 框架推荐

| 场景 | 推荐框架 |
|---|---|
| 单 Agent 生产 | **ReAct + Reflexion** |
| 需要验证器 | + verifier-critic 模式 |
| 规划是瓶颈 | + plan-and-execute |
| 多 Agent 协作 | **CrewAI** / OpenAI Agents SDK |
| 企业级图编排 | **Microsoft Agent Framework** (AutoGen 继任者) |
| 状态持久化 | **LangGraph**（循环 + 持久化）|

### Agent Architecture Patterns（2026 Taxonomy）

来源：[DigitalApplied · Agent Architecture Patterns](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026)

1. **ReAct** — 单 Agent 默认（观察→思考→行动）
2. **Reflexion** — 自我反思，重复失败模式时用
3. **Plan-and-Execute** — 规划 + 执行分离，便宜可扩展
4. **Supervisor/Worker** — 上限更高的复杂任务
5. **Verifier-Critic** — 输出质量是瓶颈时
6. **Mixture of Agents (MoA)** — 多 Agent 聚合，准确性最高
7. **Hierarchical** — 层级编排，企业场景

> ReAct + Reflexion = 生产级单 Agent 堆栈
> 加 verifier-critic 当输出质量是瓶颈

---

## 五、对 Hermes 的落地建议

### 短期（本周）
1. **给关键任务加 Verifier**：在 execute_code / terminal 调用外层包裹验证逻辑
2. **选择性 Reflection**：任务失败时触发 self-reflection，成功时不浪费 token
3. **Kill Switch**：长时间运行任务加硬超时

### 中期（本月）
4. **BoN 采样**：对高风险决策生成 N 个候选，用 reward model 选最优
5. **双 Agent 并行**：关键决策同时跑两个模型，不一致时告警
6. **时间预算感知**：给每个工具调用设超时，超时后降级策略

### 不适用
- 单 GPU 场景（当前 Hermes 无此约束）
- 私有代码推理（可探索 SWE-Reasoner 的拒绝采样思路）

---

## 来源链接

- [Scaling Test-time Compute for LLM Agents (OAgents)](https://arxiv.org/html/2506.12928v1)
- [SWE-Reasoner: Thinking Longer, Not Larger (Alibaba)](https://arxiv.org/html/2503.23803v2)
- [Multi-Agent Reasoning Pareto-Optimal TTS (Kaesberg et al.)](https://arxiv.org/pdf/2605.01566)
- [Anatomy of a production AI agent 2026 (Mindlyctica)](https://www.mindlyticai.com/blog/agent-architecture-2026)
- [Agent Architecture Patterns: 2026 Taxonomy (DigitalApplied)](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026)
- [Stanford CS224r: RL for LLMs Reasoning (Noam Brown)](https://cs224r.stanford.edu/slides/10_cs224r_rl_for_llms_reasoning_2026.pdf)
- [RAND: When AI Takes Time to Think](https://www.rand.org/pubs/commentary/2025/03/when-ai-takes-time-to-think-implications-of-test-time.html)
