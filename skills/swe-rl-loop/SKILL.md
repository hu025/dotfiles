---
name: swe-rl-loop
description: SWE-RL self-play code refinement loop. Use when building self-testing code agents that iterate: generate → test → reflect → fix without GPU training.
trigger: swe-rl self-play code agent reflexion
category: agent-engineering
---

# SWE-RL Loop — 代码自我测试自进化循环

## 1. 原理：Meta SWE-RL (ICML 2026, arXiv 2512.18552)

### 核心思想
Meta 的 **Self-play SWE-RL (SSR)** 证明了一个核心命题：

> **同一个 LLM 扮演两个角色——bug 注入者（proposer）和 bug 修复者（solver），在代码库内自我对弈，实现无需人类标注数据的自我进化。**

### 论文关键设计

| 组件 | 描述 |
|------|------|
| **Proposer（bug 注入者）** | 从干净代码中注入"reverse weakened patch"——把正确 patch 反向操作生成有 bug 的中间态 |
| **Solver（bug 修复者）** | 给定 buggy 代码 + 测试 spec，用工具（bash/git）修复并通过测试 |
| **奖励信号** | Proposer 收到 `r_inject`（bug 难度 × 可解决率）；Solver 收到二元信号（测试全过=1，否则=0） |
| **课程进化** | 失败轨迹升级为"二阶 bug"，难度递增 |
| **无人类数据** | 只需 Docker 镜像（源码 + 依赖），不需要 issue、PR、test command parser |

### 与传统 RL 的区别
- 不需要 human-labeled issues / test commands / test parsers
- Proposer 和 Solver **共享同一套 LLM 参数**（不是两个模型）
- 难度由当前策略自适应调节（curriculum）

---

## 2. 简化版实现：Hermes 中用 Reflexion + 代码执行模拟

> **目标：不依赖 GPU 训练，用 LLM API + 代码执行实现 SWE-RL 的核心循环。**

### 核心循环（5 步）

```
[任务描述] 
    │
    ▼
步骤1：生成代码（LLM as Solver）
    │ code.py
    ▼
步骤2：生成测试用例（LLM as Proposer）
    │ test_code.py  
    ▼
步骤3：运行测试 → 捕获失败信息
    │ 
    ├─ 通过 → 完成 ✓
    │
    └─ 失败 → 步骤4
              │
              ▼
        步骤4：LLM 根据失败信息修复代码
              │
              ▼
        步骤5：重新运行测试
              │
              ├─ 通过 → 完成 ✓
              │
              └─ 失败 → 回到步骤4（循环，最多 N 次）
```

### 关键区别：Proposer/Solver 是同一个 LLM

在完整 SWE-RL 中，Proposer 注入 bug、Solver 修复 bug。
在简化版中，我们把 **Proposer 角色合并到 Solver 的反思阶段**：
- **Solver** = 代码生成 + 测试失败后修复
- **Proposer** = 测试用例生成（相当于主动制造验证压力）

---

## 3. 与 Reflexion 的区别

| 维度 | Reflexion（通用） | SWE-RL Loop（代码专用） |
|------|------------------|------------------------|
| **任务类型** | 任意语言任务（AlfWorld、HotPotQA、LeetCode） | 代码生成 + 测试 + 修复 |
| **反馈形式** | 自然语言 reflection（verbal） | **测试执行结果**（可验证的二元信号） |
| **Proposer 角色** | 无 | 有——主动生成测试用例制造压力 |
| **迭代单位** | 多 trials（12+ 次） | 多 fix 轮次（通常 3-5 次） |
| **训练信号** | 无（verbal only） | **测试通过/失败**——可验证 reward |
| **代码任务优势** | 一般 | 强——测试执行是客观 ground truth |
| **典型提升** | HumanEval 80%→91% | 代码质量 + 自我验证覆盖率 |

### 本质区别

> Reflexion 用**语言描述**的错误反馈学习；SWE-RL Loop 用**测试执行**的客观结果学习。
> 对于代码任务，测试失败信息比"verbal reflection"更精确、更可验证。

---

## 4. 使用方法

### 基本用法

```bash
python ~/.hermes/scripts/swe_rl_executor.py \
  --task "实现一个 LRU Cache，支持 get/put，容量 100" \
  --max-iterations 5 \
  --model deepseek-chat
```

### 作为 Hermes 技能调用

在 Hermes 中加载此技能后，可通过自然语言触发：

```
用 SWE-RL 循环帮我实现一个栈，支持 push/pop/min，要求 O(1)
```

---

## 5. 核心组件

### swe_rl_executor.py

| 函数 | 职责 |
|------|------|
| `generate_code()` | LLM 生成初始代码实现 |
| `generate_tests()` | LLM 生成测试用例（Proposer 行为） |
| `run_tests()` | 执行测试，捕获 stdout/stderr/exit code |
| `fix_code()` | LLM 根据失败信息修复代码（Solver 行为） |
| `swe_rl_loop()` | 主循环 orchestrator |

### 修复历史格式

```json
{
  "iteration": 1,
  "code": "...",
  "tests": "...",
  "test_result": {
    "passed": false,
    "error": "AssertionError: expected 3, got 2",
    "output": "..."
  },
  "reflection": "bug: off-by-one error in boundary condition..."
}
```

---

## 6. 局限性

- **无梯度更新**：不像完整 SWE-RL 有 RL 权重更新，只保留代码层面的迭代
- **无课程进化**：难度不自动调节（完整版有 r_inject 自适应）
- **单文件范围**：适合简单算法/数据结构的实现，不适合大型项目
- **Proposer 能力弱**：测试生成质量依赖 LLM 的测试意识

---

## 7. 进一步扩展

1. **多文件项目**：用 mini-swe-agent（Meta 的极简 SWE-agent）作为底层执行环境
2. **真实沙箱**：用 Docker 容器隔离执行，保护主机
3. **持久化记忆**：将成功的 fix pattern 存入向量数据库（参考 Reflexion 记忆）
4. **课程进化**：记录 bug 难度分布，主动构造更难的任务
5. **真实 SWE-RL**：使用 Meta 的开源实现（如果发布）在 GPU 上做 RL 训练
