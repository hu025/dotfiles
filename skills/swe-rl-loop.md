# SWE-RL Loop / Agent RL Training Pipeline

## 触发词
`agent RL训练`、`RL循环`、`credit assignment`、`多步credit assignment`

## 核心知识

### 生产级 Agent RL 框架生态

| 框架 | 架构 | 规模 | 成熟度 |
|------|------|------|--------|
| **slime** (THUDM) | Megatron + SGLang + Ray DataBuffer | GLM-4.5→5.2生产验证 | ⭐⭐⭐⭐⭐ |
| **Miles** (radixark) | slime fork，Megatron/FSDP双后端 + TITO session | 生产级（2026-01多Agent协同） | ⭐⭐⭐⭐⭐ |
| **Molt** | vLLM + FSDP2，单机4GPU最优 | 实验性质，对比slime无显著优势 | ⭐⭐⭐ |
| **OpenWebRL** | SGLang + Orchard沙箱浏览器 | 视觉web agent在线RL | ⭐⭐⭐ |
| **verl** | FSDP2/Megatron，62K LOC | 最成熟开源，生产验证 | ⭐⭐⭐⭐⭐ |

### slime 架构（生产参考标准）

```
DataBuffer → RolloutManager(Ray) → sgl-router → SGLang engines
                                              ↓ custom_generate hook
                                           RewardHub
                                              ↓
DataBuffer → Megatron actor training → Weight sync (NCCL/disk delta) → SGLang
```

**关键组件**：
- **DataBuffer**：prompt/rollout/reward 元数据管道
- **RolloutManager**：Ray actor 管理多节点 rollout
- **sgl-router**：统一 HTTP 端点，负载均衡 + 前缀共享（GRPO 多 completion 共享同一 prompt）
- **Weight Sync**：NCCL broadcast（同节点）或 disk delta（分离集群）
- **slime/agent/** (v0.3.0)：E2BSandbox + Claude Code/Codex harness + HTTP TITO capture

**Agent-first RL（v0.3.0+）**：
```python
# 自定义 generate hook 示例
--custom-generate-function-path slime.agent.harness.claude_code
# E2BSandbox 执行 + test-based reward
```

**支持算法**：GRPO, GSPO, CISPO, Reinforce++, PPO（`--advantage-estimator`）

**支持模型**：Qwen3.6/3.5/Next/MoE, GLM-4.7/5.x, DeepSeek V3/R1, Gemma4, Llama3
**硬件**：H100/H200/B200，BF16训练+FP8推理

### 多步 Credit Assignment 方法（2026新进展）

| 方法 | 核心思想 | 无需额外模型 | 效果 |
|------|----------|------------|------|
| **DRACO** (2026-09) | Dynamic Rubrics 动态生成评分标准，按 rubric 分布credit | ✅ | +15.9 AppWorld, +5.3 Tau-Bench |
| **VICT** (2026-08) | Verifier内部结构trace到action，通过proof edges重分配 | ✅ | 超越 outcome-only 和 fine-grained credit 基线 |
| **TASPO** (2026-08) | privileged info → outcome-grounded action credit | ✅ | +10.6% over GRPO |
| **ECPO** (2026-06) | Evidence-Calibrated，shrink low-count estimate + variance-gated weighting | ✅ critic-free | +5.2~7.3 ALFWorld/WebShop |
| **GraphGPO** (2026-05) | 所有rollout聚合成状态转移图，按到目标距离算step-level advantage | ✅ | 显著优于 trajectory-level GRPO |
| **EFCA** (2026-05) | 环境短期反馈 + 中期状态历史重复检测，重分配return | ✅ | 超越 GiGPO/HGPO stepwise 基线 |
| **C3** (多Agent) | Contextual Counterfactual，freeze transcript + leave-one-out baseline | ✅ | 多Agent数学/编程基准SOTA |

### 关键发现：Coverage > Targeting
- verifier information density V_d = k/C（因果链中被expose的per-turn比例）
- 低V_d环境（如tau^2-bench，V_d~0.15）中，uniform dense reward 反而优于 sparse binary
- 结论：**coverage（覆盖所有步）优先于 targeting（集中credit到关键步）**

### 离线SFT的灾难性影响
- AgentFlow已证明：离线SFT对agentic系统有 **-19.0% 灾难性影响**
- 必须用 online RL（GRPO/CISPO）在真实环境 rollout

### Sparse Reward Shaping
- 评分 rubric 动态生成（DRACO），跟踪 policy evolving capability
- 环境反馈短期信号（EFCA immediate feedback）
- VLM-as-judge（OpenWebRL）

### Reward Hacking 防治
- TIS/MIS（Truncated/Masked Importance Sampling，Miles 提供）
- Token identity invariant（Molt 三正确性不变式之一）
- Forward consistency（rollout 和 actor 必须同意 MoE routing 语义）

## 落地动作

1. **slime v0.3.0** 是生产级 agent RL 训练标准，Megatron + SGLang 架构已验证
2. 对于 Hermes Agent 自我进化场景，优先考虑 **GRPO + 环境反馈信号**（ECPO/EFCA思路）
3. Credit assignment：先用 uniform dense reward（Coverage > Targeting），再按需引入 GraphGPO
4. 不要离线 SFT warm-start agentic 系统，必须 online RL

## 来源
- slime 官方文档：https://mer.vin/2026/07/slime-rl-framework-megatron-sglang-post-training-for-llm-scaling
- Molt 论文：https://arxiv.org/abs/2607.21653
- DRACO：https://arxiv.org/abs/2609.04094
- Coverage Not Targeting：https://arxiv.org/abs/2609.02417
- VICT：https://arxiv.org/abs/2608.28128
- GraphGPO：https://arxiv.org/html/2605.26684v1
- EFCA：https://arxiv.org/pdf/2608.08255
- ECPO：https://arxiv.org/abs/2606.05885
- Miles：https://github.com/radixark/miles
- OpenWebRL：https://github.com/OpenWebRL/OpenWebRL
