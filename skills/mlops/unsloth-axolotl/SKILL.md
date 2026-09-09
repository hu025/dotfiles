---
name: unsloth-axolotl
description: Unsloth + Axolotl 2026 fine-tuning frameworks. Use when needing consumer-GPU LLM fine-tuning (Unsloth) or production-scale distributed training (Axolotl). Trigger: fine-tune LoRA QLoRA MoE models, 2026 framework updates.
version: 1.0.0
author: Self-evolution engine
license: Apache-2.0 / proprietary
dependencies: [unsloth, axolotl, peft, transformers, torch]
metadata:
  hermes:
    tags: [Fine-Tuning, LoRA, QLoRA, MoE, Unsloth, Axolotl, Consumer-GPU, Distributed-Training, GRPO, RL, NVFP4]
  research:
    date: 2026-09-17
    topic: Unsloth axolotl LoRA fine-tuning 2026
    stars: Unsloth 34k+ GitHub, Axolotl 17k+ GitHub
---

# Unsloth + Axolotl 2026 Fine-Tuning Frameworks

两大主流开源微调框架定位互补：Unsloth 面向消费者/桌面用户，Axolotl 面向生产级分布式训练。

---

## Unsloth AI（消费者/本地优先）

**定位**：no-code 桌面 UI + 内核加速，2X 训练速度，63%+ 显存节省。

### 核心能力（2026年）

| 能力 | 说明 |
|------|------|
| **Unsloth Studio** | 跨 Mac/Windows/Linux 本地桌面 App，100% 离线运行，支持 GGUF/Safetensors |
| **动态 GGUF v3.0** | Qwen3.8-27B 精度比友商高 10%+，1-bit 可在 75GB RAM 运行 |
| **Kimi K3** | MoE 2.8T 总参数/104B 激活，1M context，原生视觉，UD-IQ1_S 仅 595GB |
| **GLM-5.3-Flash** | 320B 模型/18B 激活，1M context，消费级硬件可跑 |
| **Qwen3.8-Flash-Next** | 125B 多模推理，262K context，MTP 加速 2X |
| **Unsloth Desktop** | 一键安装：`curl -fsSL https://unsloth.ai/install.sh \| sh` |
| **Auto Compaction** | 长对话超出 context 后自动归档检索，不用截断 |
| **Remote/LAN Access** | 网络访问预览版，QR 码连接 |
| **MCP 支持** | Gemma 4 12B MCP，原生工具调用 |
| **Projects** | 多聊天/文件/workspace 组织 |
| **Deep Research Mode** | 本地模型规划+读取+引用来源 |
| **Parallel Chat** | 多聊天并行生成 |
| **AMD ROCm** | 正式支持 AMD GPU（2026-07-20） |
| **FP8 GRPO** | 强化学习训练加速 |
| **500K Context** | 长上下文微调 |
| **DoRA** | 新的轻量化微调方法 |
| **MLX (Apple Silicon)** | 优化 Apple Silicon 支持 |

### 新支持模型（2026年）

- MiniMax-Music3 / Higgs / MOSS 音频模型
- Qwen3.8-Flash-Next, GLM-5.3-Flash, GLM-5.2
- Kimi K3 (MoE 104B 激活)
- DeepSeek-V4 0731
- Gemma 4 12B + QAT
- Muse Glimmer (Meta)
- Qwen3.6 MTP
- DiffusionGemma

### 安装

```bash
# Linux/macOS/WSL
curl -fsSL https://unsloth.ai/install.sh | sh

# Windows
irm https://unsloth.ai/install.ps1 | iex

# Python
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"

# Colab (T4 免费 GPU)
pip install unsloth
# 或使用预编译 Colab：比标准快 20x
```

### 使用示例

```python
from unsloth import FastLanguageModel
import torch

# 加载模型（4-bit QLoRA）
model, tokenizer = FastLanguageModel.from_contrast(
    model_name = "unsloth/Qwen3-8B",
    max_seq_length = 2048,
    dtype = torch.float16,
    load_in_4bit = True,
)

# 添加 LoRA adapter
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
)

# 微调
from unsloth import UnslothTrainer, UnslothTrainingArguments
trainer = UnslothTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    args = UnslothTrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        num_train_epochs = 3,
        learning_rate = 2e-4,
    ),
)
trainer.train()

# 导出 GGUF
model.save_pretrained_gguf("model", tokenizer)
# 或导出到 Ollama/vLLM
```

### 适用场景

- 个人开发者/研究者，单卡消费级 GPU
- 快速原型验证（Colab 2 分钟上手）
- 需要图像/视频生成微调（DiffusionGemma, FLUX, Wan）
- TTS/音频模型微调
- 需要完整桌面 UI 而非命令行

---

## Axolotl（生产级/分布式）

**定位**：YAML 配置驱动的微调框架，支持 100+ 模型，分布式 MoE 训练，uv-first 包管理。

### 核心能力（2026年 v0.18.0）

| 能力 | 说明 |
|------|------|
| **NVFP4 MoE-LoRA** | ScatterMoE (W4A16) + SonicMoE (W4A4)，Blackwell/Hopper 显存几乎平坦 |
| **Expert Parallelism (EP)** | DeepEP 分布式 MoE 训练，多节点扩展 |
| **Context Parallelism** | 混合 SSM 模型（Nemotron-H, Falcon-H1, Bamba） |
| **BitNet 1.58-bit** | 极致低位宽微调 |
| **Async GRPO** | 强化学习步骤快 58% |
| **Flash Attention 4** | Hopper/Blackwell 自动回退到 FA2/3 |
| **NeMo Gym + EBFT** | 新 RL 环境与优化器 |
| **2D Expert Parallelism** | GLM-5.2 分布式微调 |
| **GRPO Flattening & Packing** | 批量打包，token 效率提升 10% |
| **MoE Expert Quantization** | `quantize_moe_experts: true` 大幅降低显存 |
| **SageAttention** | 高精度注意力优化 |
| **EAFT** | 熵感知焦点训练 |
| **Scalable Softmax** | 长上下文注意力改进 |
| **GDPO** | 广义 DPO 对齐 |
| **AI Agent 文档** | `axolotl agent-docs` 内置 AI 编程助手支持 |
| **Tinker API** | 远程训练 API |
| **uv-first** | 使用 uv 包管理器 |

### 新支持模型（2026年）

- Muse Glimmer, North Micro Vision Instruct, Shieldstral (08)
- GLM-5.2 (DSA), GLM-5.3 (08)
- Mistral Medium 3.5, Mistral Small 4
- Gemma 4 (26b-a4b MoE NVFP4 LoRA)
- Qwen3.5 / Qwen3.5 MoE / Qwen3.6
- DeepSeek-V4 / V3.1
- gpt-oss (OpenAI 开源模型)
- Kimi K3

### 安装

```bash
# uv (推荐，uv-first)
uv pip install axolotl

# Docker (避免依赖问题)
docker pull axolotl-ai/cloud:latest
docker run --gpus all -v ./data:/data axolotl-ai/cloud axolotl train config.yaml

# 从源码
git clone https://github.com/axolotl-ai-cloud/axolotl.git
cd axolotl
pip install -e .
```

### 使用示例（YAML 配置）

```yaml
# examples/qwen3/30b-a3b-nvfp4-lora.yaml
base_model: Qwen/Qwen3-30B-A3B
model_type: AutoTransformer
quantize: nvfp4
load_in_4bit: true

# ScatterMoE NVFP4 LoRA
moe:
  scattermoe:
    enabled: true
    num_experts: 8
    lora:
      r: 16
      alpha: 16

# 或 SonicMoE W4A4
# moe:
#   sonicmoe:
#     enabled: true
#     nvfp4_merge_aware: true  # adapter merge 后保持 bitwise 一致

trainer: axolotl
sequence_len: 8192
num_epochs: 3
learning_rate: 2e-4

# GRPO 强化学习
# grpo:
#   enabled: true
#   async_steps: true  # 58% 步骤加速
```

```bash
# 启动训练
axolotl train examples/qwen3/30b-a3b-nvfp4-lora.yaml

# 查看 agent 文档
axolotl agent-docs sft
axolotl agent-docs grpo
axolotl agent-docs preference_tuning

# 导出配置 schema
axolotl config-schema
```

### 适用场景

- 生产级训练，多 GPU/FP16/BF16
- MoE 模型分布式微调（Gemma 4, DeepSeek-V4）
- 需要 BitNet/FP8/FlashAttention4 等极致优化
- 强化学习（GRPO/DPO/KTO/ORPO）
- 团队协作（YAML 配置标准化）
- AI Agent 辅助微调（内置 agent-docs）

---

## 选型决策树

```
需要微调 LLM?
├── 单卡消费级 GPU (Mac/Win/Linux 桌面)
│   └── Unsloth Studio / Desktop
│       ├── 快速原型 → Colab + pip install unsloth
│       ├── 图像/视频/音频生成微调 → Unsloth
│       └── Apple Silicon → Unsloth MLX
│
├── 生产级 / 多 GPU / MoE 大模型
│   └── Axolotl
│       ├── MoE 分布式训练 → EP + DeepEP
│       ├── 极致显存优化 → NVFP4 ScatterMoE/SonicMoE
│       ├── 强化学习微调 → GRPO / DPO / KTO
│       └── 多团队标准化 → YAML 配置
│
└── 仅需 LoRA adapter（小参数量）
    ├── PEFT（Hermes 已有技能）
    └── 结合使用：Axolotl 训练 → PEFT 部署
```

## 关键区别

| 维度 | Unsloth | Axolotl |
|------|---------|---------|
| 定位 | 消费者/本地/桌面 | 生产级/分布式 |
| 安装 | 一行脚本 / pip | uv / Docker / 源码 |
| 接口 | Python API + 桌面 UI | YAML 配置 + CLI |
| MoE 优化 | Dynamic GGUF | ScatterMoE / SonicMoE NVFP4 |
| 强化学习 | FP8 GRPO | Async GRPO / DPO / KTO |
| 硬件 | 消费级 GPU | 数据中心多 GPU |
| AI Agent 支持 | 无 | 内置 agent-docs |

---

## 来源

- https://unsloth.ai (changelog + blog)
- https://github.com/unslothai (34k+ stars)
- https://github.com/axolotl-ai-cloud/axolotl (17k+ stars)
- Axolotl v0.18.0 releases
