---
name: ollama
description: Ollama — 本地 LLM 推理引擎 2026 更新。v0.32-v0.34 新模型（Laguna/Kimi/Qwen3.8/DeepSeek V4/Muse Glimmer/Nemotron 3.5）、多平台 Agent 集成（Claude Desktop/ChatGPT Desktop）、Claude Code/OpenClaw/Hermes 一键启动。触发词：ollama本地模型/coding agent/本地推理/Muse Glimmer/Laguna编码
---

# Ollama — 本地 LLM 推理引擎 2026 更新

**2026-09-16 更新 | v0.33-v0.34**

Ollama 是本地 LLM 推理引擎，2026 年新增大量新模型和 Agent 集成能力。180k+ GitHub stars，MIT license。

**仓库**: https://github.com/ollama/ollama | **Library**: https://ollama.com/library | **博客**: https://ollama.com/blog

---

## 新模型速览（2026 新发布）

### 🥇 顶级编码 Agent 模型

| 模型 | 规格 | SWE-bench | 亮点 |
|------|------|-----------|------|
| **laguna-xs-2.1** | 33B total / 3B active MoE | 70.9% Verified | Poolside出品，256K context，最强本地编码Agent |
| **laguna-s-2.1** | 118B-A8B MoE | 70.2% Terminal-Bench | 桌面最强编码，118B总参 |
| **kimi-k2.7-code** | MoE (基于K2.6) | — | Moonshot AI，长程编码会话专用 |
| **kimi-k2.6** | 32B active / 1T total MoE | 80.2% Verified / Pro 58.6 | 前沿编码，Modified MIT |
| **deepseek-v4-pro** | 284B total / 13B active | 93.5% LiveCodeBench | 算法编程最强，MIT |
| **qwen3.8:27b** | 27B dense | 61.7% Verified | 消费级硬件最优，24GB Q4可跑，Apache 2.0 |
| **qwen3.6-35b-a3b** | MoE | 73.4 SWE-bench | Qwen3.6系列编码冠军 |
| **glm-5.3** | 744B total / 40B active MoE | Pro 58.4 | Z.ai，MIT license |
| **deepseek-v4-flash** | 284B / 13B active | 78% real-world | 轻量预算版，78/100 |
| **gpt-oss:20b** | 21B total / 3.6B active | ~o3-mini level | OpenAI出品，16GB可跑，Apache 2.0，可调推理强度 |

### 🎯 特色模型

| 模型 | 规格 | 亮点 |
|------|------|------|
| **muse-glimmer** | 30B multimodal, 128K+ ctx, Apache 2.0 | Meta Superintelligence Labs首个开源模型，原生图像输入，MLX DFlash 1.5-1.8x加速，`ollama run muse-glimmer:30b-mlx` |
| **nemotron-3.5-lightning** | 30B total / 3B active, 1M ctx | NVIDIA出品，MTP/Dflash 4x吞吐，专为长时间运行Agent设计 |
| **gemma4:e4b** | 26B MoE, ~6GB VRAM | Google，MLX多Token预测，Apple Silicon 90%提速，视觉+工具调用 |
| **nemotron-3-nano** | 4B/30B | NVIDIA，Agentic标准，工具调用+思考 |

### 📦 完整命令

```bash
ollama run laguna-xs-2.1      # 最强本地编码Agent MoE
ollama run kimi-k2.7-code     # Moonshot长程编码
ollama run kimi-k2.6          # 前沿编码
ollama run deepseek-v4-pro    # 算法编程
ollama run qwen3.8:27b        # 消费级最优
ollama run muse-glimmer        # Meta多模态Agent
ollama run muse-glimmer:30b-mlx  # Apple Silicon高速版
ollama run nemotron-3.5-lightning  # NVIDIA轻量Agent
ollama run gemma4:e4b         # 视觉+工具调用，6GB显存
ollama run gpt-oss:20b        # 16GB可跑，o3-mini级
```

---

## 版本新能力

### v0.34.0 (Sep 2026)
- **ChatGPT Desktop 集成**：macOS 上将 Ollama 模型直接接入 ChatGPT Desktop，本地推理+商业 UI
- **Apple Silicon 结构化输出提速**：JSON schema 约束输出响应更快
- **OpenAI 兼容工具搜索**：兼容客户端的 tool search API
- **响应压缩图像修复**：压缩后的对话历史图像正确保留

### v0.33.0 (Aug 2026)
- **Claude Desktop 网关**：Ollama 作为第三方网关接入 Claude Desktop
- **KV-cache Prefill 恢复点**：取消的长预填充可从上次停止位置恢复而非从头重算
- **模型元数据缓存**：首次token时间减半（995ms → 524ms）

### v0.32.0 (Jul 2026)
- **交互式 Chat/Code/Work Agent 体验**
- **Codex App → ChatGPT 重命名**

---

## Agent 一键启动 (`ollama launch`)

Ollama 提供统一启动命令，无需配置 env 直接运行各框架：

```bash
ollama launch claude  --model <model>   # Claude Code
ollama launch opencode --model <model>   # OpenCode
ollama launch openclaw --model <model>   # OpenClaw 个人助手
ollama launch hermes   --model <model>   # Hermes Agent（注意：需要验证兼容性）
ollama launch pi       --model <model>   # Pi 轻量编码Agent
ollama launch n8n      --model <model>   # n8n 工作流
```

支持的完整列表：Claude Code, Codex, OpenCode, Hermes Agent, OpenClaw, VS Code, Pi, n8n

---

## 重要注意事项

### 局限性（2026-09 现状）
- **MCP 支持**：ollama 本身没有 MCP server 内置，但作为后端可被 MCP 客户端调用（通过 OpenAI 兼容 API）
- **多Agent编排**：没有内置编排能力，是推理引擎而非框架
- **Windows/Linux 图像生成**：v0.34 仍为 macOS 实验特性
- **Agent框架选择**：Laguna XS 2.1 + `ollama launch claude` = 最强本地编码组合

### 选型决策树
```
本地纯推理 / API替换          → ollama（轻量、OpenAI兼容）
最强本地编码Agent             → Laguna XS 2.1 + Claude Code
前端/视觉/低显存              → Gemma 4 E4B (~6GB)
预算紧张/16GB机器             → gpt-oss:20b（~o3-mini水平）
长程多步骤任务               → Nemotron 3.5 Lightning（1M ctx，4x吞吐）
Meta多模态Agent（Mac）        → muse-glimmer:30b-mlx（DFlash加速）
中文/长上下文                → Kimi K2.6/K2.7-code
算法/实时基准                → DeepSeek V4 Pro
```

---

## 与现有技能关系

- **mlops/llama-cpp**：llama.cpp 是 Ollama 的底层引擎之一，了解底层可排查问题
- **autonomous-ai-agents**：Ollama 是这些 Agent 的本地推理后端
- **localai**：LocalAI 是另一个自托管选择，功能有重叠但定位不同（LocalAI=生成全覆盖，Ollama=通用推理+Agent集成）
- **coding-agent-cli**：Claude Code/OpenCode/Ollama launch 三位一体组合

---

## 来源

- https://ollama.com/blog (2026 全部更新)
- https://ollama.com/library (180k+ stars, 完整模型库)
- https://releasebot.io/updates/ollama (v0.32-v0.34 changelog)
- https://freedom.tech/posts/2026-09-05-ollama-0-34-0/ (v0.34.0 新特性)
