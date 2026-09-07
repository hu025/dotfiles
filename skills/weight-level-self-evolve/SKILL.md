---
name: weight-level-self-evolve
description: 权重级自我进化方法论 + Hermes 实践路径（M3/Darwin Gödel Machine 等远期方向）
trigger: 远期阶段权重级进化、模型自我修改、Sakana DGM、自我训练循环
version: 0.1
stage: far-future
---

# Weight-Level Self-Evolution

## 1. 背景：四阶段自我修改路线图

| 阶段 | 对象 | 状态 |
|---|---|---|
| L0 代码级 | 改 SKILL/script/prompt | ✅ 当前 |
| L1 元 agent | DGM-H（Darwin Gödel Machine-Hermes 变体） | 🔨 中期 |
| L2 **权重级** | **直接改 LoRA/适配器/全权重** | 🌱 **远期** |
| L3 架构级 | 搜索 MoE 拓扑/激活函数 | ⏳ 假设性 |

L0-L1 通过编辑代码绕过训练；L2-L3 必须动梯度。**本 skill 只规划 L2**。

## 2. 前沿方法调研（2026）

### 2.1 Darwin Gödel Machine (DGM) — Sakana AI / UBC / Vector
- **出处**: Zhang et al., ICLR 2026 (arXiv:2505.22954)
- **范式**: 用 foundation model 提议自身代码补丁 → 在 SWE-bench/Polyglot 评估 → 把成功变体归档进**演化树**（开放搜索空间），失败变体也保留作为"踏脚石"
- **结果**: SWE-bench 20.0% → **50.0%**；Polyglot 14.2% → **30.7%**
- **关键创新**: 把 Gödel Machine 的形式证明替换成**达尔文式经验搜索**——牺牲理论最优换实用性
- **仍属代码级**，但作者明确写到："Future work … letting it improve the training of the foundation models at its core" → **直接通向权重级**

### 2.2 M3 (Memory, Meta-learning, Modularity) 思想谱系
- 三轴协同：**记忆**（外部 KB/RAG）、**元学习**（MAML/LoRA 快速适配）、**模块化**（MoE/Adapter 替换）
- 2026 趋势：M3 框架被越来越多权重级自演化系统采纳——记忆层承担"事实更新"，元学习承担"技能获取"，模块化承担"能力组合"

### 2.3 其他权重级先驱
- **Self-Taught Optimizer (STOP)** — 反向递归自举：让模型写出比自己更优的训练循环
- **TextGrad / FunSearch** — 用 LLM 作为梯度信号，搜索代码/权重空间
- **AlphaEvolve** — DeepMind 2026，进化搜索 + 代码生成作用于训练流程本身
- **RLHF/RLAIF 自演化** — 让奖励模型与策略相互提升（OpenAI/Anthropic 内部已部分使用）

## 3. 关键技术挑战

| 挑战 | 原因 | 缓解 |
|---|---|---|
| 灾难性遗忘 | 新梯度覆盖旧能力 | EWC + 经验回放 + LoRA 低秩隔离 |
| 评估对不齐 | 训练目标 ≠ 用户价值 | 人类偏好集 + 自动化基准 (SWE-bench 类) |
| 算力爆炸 | 每代重训需 P 级别 | 增量 LoRA + 早停 + 共享基座 |
| 安全护栏 | 权重失控无 diff 可审 | 红队对抗评估 + 影子模型 + 回滚快照 |
| 开放搜索空间 | 无引导易发散 | 演化树剪枝 + 评估函数上界 |

## 4. Hermes 实践路径（分三步走）

### Step 1 · 元数据采集（本周可做）
- 给当前 Hermes 会话加 **trace 层**：记录 prompt → 工具调用 → 结果 → 用户评分
- 产出：`/home/saber/dotfiles/data/hermes-traces/*.jsonl`
- 工具：`logger` skill + 自定义 hook

### Step 2 · 小规模 LoRA 适配（1-3 个月）
- 用上面 trace 微调 Hermes 行为层（不碰基座权重）
- 基座：Qwen2.5-7B 或 Mistral-Small（本地 GPU 可承受）
- 框架：`unsloth` + `axolotl`
- 评估：内部 100 条任务基准 + 用户盲评 A/B
- **验收**: Hermes 在重复任务上 token 数降低 ≥ 20%

### Step 3 · Darwin Gödel Machine-Hermes (DGM-H)（3-12 个月）
- 复用 DGM 思路但作用在**LoRA 权重**而非 Python：
  1. 提议器：LLM 改 `adapter_config.json` / 训练超参
  2. 评估器：内部基准 + 真实用户盲测
  3. 演化树：每代 LoRA 归档，含 lineage
  4. 安全：每次合并前需通过 red-team 子集
- 目标：4 周内完成一个自演化循环，把 Hermes 在 dotfiles/skill authoring 上准确率提升 ≥ 10%

## 5. 安全原则（不可妥协）

1. **人类在环**：每代权重升级必须人工 approve（按钮式确认）
2. **影子模型**：新权重先在沙箱跑 24h 再合并到 main
3. **可回滚**：每次合并 git tag + LoRA 权重 md5 存档
4. **范围限制**：只允许改行为层 LoRA，**禁止动基座**
5. **透明日志**：所有自演化事件写入 `/home/saber/dotfiles/logs/self-evolve.log`

## 6. 不做什么

- ❌ 不尝试在 24B+ 基座上全权重重训（算力/能耗不可接受）
- ❌ 不跳过影子模型直接合并
- ❌ 不替代 L0/L1（代码级改 prompt/skill 永远先于改权重）
- ❌ 不在缺少 trace 数据时启动 Step 2

## 7. 验证清单

- [ ] trace 采集 ≥ 1000 条真实交互
- [ ] LoRA 微调脚本可在 1 张 4090 上跑通
- [ ] DGM-H 评估基准冻结（不漂移）
- [ ] 安全护栏人工 review 通过
- [ ] 第一次完整循环 → 用户显式 enable

## 8. 参考链接

- DGM 论文: https://arxiv.org/abs/2505.22954
- Sakana DGM 主页: https://sakana.ai/dgm
- GitHub: https://github.com/jennyzzt/dgm
- ICLR 2026 Poster: https://openreview.net/forum?id=pUpzQZTvGY
