---
name: agent-live-self-improvement
description: Agent live self-improvement patterns — PILOT supervisor-worker + SAGE failure attribution + MASC cascading error correction. 触发词：实时自我改进、运行中修正、supervisor-worker
---

# Agent Live Self-Improvement — 运行时自我改进模式

## 核心问题

现有自我改进机制（Reflexion、Self-Refine、后验harness更新）都是**事后**改进——在任务完成后才能学习，无法重定向当前运行。

> 致命局限：执行细节占满上下文，导致agent无法识别自己正在失败。

---

## PILOT 模式（arxiv:2608.26530, Aug 2026）

### 核心洞察

**实时自我改进 = 分离执行角色 + 双通道通信**

- **Worker**：负责任务执行，上下文充满执行细节和死路
- **Supervisor**：负责自我改进，上下文聚焦目标 + 近期事件 + 失败模式识别
- Supervisor是**冻结的**（不执行任务），Worker是**动态的**

### 双通道机制

```
Worker → Supervisor 方向：
  1. Notification  — 报告进度/中间结果/潜在风险（不中断执行）
  2. Question      — 请求输入（暂停等待回复）
  3. Result        — 运行时自动传递最终结果

Supervisor → Worker 方向：
  4. Steer         — 重定向当前策略（不等执行结束）
  5. Abort         — 终止当前运行
```

### 实时自我进化

Supervisor在监控过程中**实时**将成功程序凝固为可复用技能，而非等任务完成后才更新harness。

关键数据（Terminal-Bench 2.0）：
- 通过率提升：GLM-5.1 +14.6pp，Kimi-K2.6 +12.4pp
- Token效率：输出token减少42-47%，吞吐量+110-134%

### Hermes映射

```
Hermes delegate_task ≈ Worker
Hermes supervisor (parent) ≈ Supervisor（但缺少双通道 + 实时steer）
缺失：Notification/Question机制，in-flight abort，运行时技能凝固
```

---

## SAGE 模式（arxiv:2606.31478, Multi-Hypothesis Failure Attribution）

### 核心洞察

**一次反射不够**——失败轨迹被压缩成单一verbal critique，导致：
- 局部试错（反复调超参而非改变设计）
- 硬切换（丢弃所有上下文直接重启）

### 三阶段结构

```
1. Divergent Causal Generation（发散因果生成）
   → 产生多个独立的、有证据支撑的失败解释

2. Convergent Scoring（收敛评分）
   → 独立评估每个解释的严重程度和证据支持度

3. Deterministic Routing（确定性路由）
   → 将验证的根因映射到正确干预层级：
     • Hypothesis层 → 假设重构
     • Design层 → 协议重新设计
     • Implementation层 → 代码修复
```

### 与现有skill的关系

- 比 `agent-self-improvement-protocols` 中的"行为契约"更具体——聚焦失败诊断路由
- 比 `autonomous-improvement-loop` 的Ralph Wiggum多步尝试更结构化——多假设并行

---

## MASC 模式（ACL Findings 2026）

### 核心洞察

多Agent系统中的错误会**级联传播**——单步错误会沿Agent链扩散。

### 元认知框架

```
每步执行后 → Prototype-Guided异常检测
           → 发现异常步 → Correction Agent重写输出
           → 阻止错误信息流向后续Agent
```

关键：在错误**传播前**拦截，而非事后检测。

---

## SelfCorrect-Agent（ScienceDirect 2026）

### 核心洞察

教模型从错误中学习，而非记忆observation-action对。

### 训练数据合成

生成**显式包含错误和修正步骤**的多样化轨迹数据，在LLaMA3/Mistral上进行微调。

---

## 落地建议

### 短期（立即可实现）

1. **Notification增强**：在delegate_task返回时增加in-flight通知机制
2. **失败路由检查**：复杂任务失败后，先做多假设诊断再重试
3. **Supervisor上下文分离**：在长任务中显式分离"执行上下文"和"诊断上下文"

### 中期（需要架构改动）

4. **实时Steer**：实现Supervisor对Worker的运行中重定向
5. **运行时技能凝固**：在任务进行中将成功程序保存为技能

---

## 参考

- PILOT: https://arxiv.org/abs/2608.26530
- SAGE (MHFA): https://arxiv.org/abs/2606.31478
- MASC: https://aclanthology.org/2026.findings-acl.1168/
- SelfCorrect-Agent: https://www.sciencedirect.com/science/article/pii/S0925231225032187
