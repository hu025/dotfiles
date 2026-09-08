---
name: localai
description: LocalAI — self-hosted AI engine covering text/audio/video/3D generation, embedded terminal agent (nib), KNN router, vllm-cpp, and distributed clustering. Use when running 100% local LLM inference, building self-hosted AI agents, or replacing OpenAI APIs with local models.
trigger: LocalAI self-hosted local LLM inference audio video 3D generation
---

# LocalAI — Self-Hosted AI Engine (2026)

LocalAI 是开源自托管 AI 引擎，v4.7–v4.9 (Mar–Aug 2026) 引入大量新能力：终端 Agent、vllm.cpp、3D 生成、KNN 路由、Context Compression、分布式集群。

**仓库**: https://github.com/mudler/LocalAI | **文档**: https://localai.io | **Gallery**: 1700+ 模型条目

---

## 核心能力矩阵

| 模态 | 端点 | 引擎 |
|------|------|------|
| Text Generation | `POST /v1/chat/completions` | llama.cpp / vllm-cpp / transformers |
| Audio TTS | `POST /v1/audio/speech` | vibevoice-cpp / qwen3-tts / chatterbox |
| Audio Transcription | `POST /v1/audio/transcriptions` | moss-transcribe-cpp / parakeet.cpp / CrispASR |
| Voice Clone | `POST /v1/audio/speech` + `localai://voice-profiles/` | F5-TTS / chatterbox |
| Video Generation | `POST /v1/video/generations` | longcat-video |
| 3D Generation | `POST /v1/3d/generations` | trellis2cpp (TRELLIS.2 → GLB) |
| Realtime Voice | WebSocket `/realtime` | native |
| Face Detection | `POST /face/detect` | face-detect.cpp (SCRFD/ArcFace) |
| Voice Detect | `POST /voice/detect` | voice-detect.cpp (ECAPA-TDNN) |
| OCR | `POST /ocr` | HunyuanOCR / OvisOCR2 |
| Image Gen | `POST /v1/images/generations` | Ideogram4 / Flux GGML |

---

## 重要新功能 (v4.7–v4.9)

### 1. nib 终端 Agent (v4.8+)
`local-ai chat` 从 REPL 升级为完整 Agent，内嵌 nib harness：

```bash
local-ai chat                    # 启动 Agent
# 工具调用（需审批）: shell / file read / MCP servers / skills
# 只读工具(ls/cat)自动放行
# /compact = 上下文压缩, /models = 模型列表
```

启动 Claude Code/OpenCode 集成：
```bash
local-ai launch claude-code --model qwen3.6:27b
local-ai launch opencode       # 自动设置 ANTHROPIC_BASE_URL
```

### 2. vllm-cpp (v4.8+, alpha)
LocalAI 团队自研 C++20 推理引擎，Apache-2.0 独立仓库：
- paged KV cache / continuous batching / prefix caching
- GGUF + safetensors 双支持
- CUDA 12/13 + Metal + Vulkan + L4T + CPU
- speculative decoding / KV offload
- Qwen3-TTS 通过 llama-cpp backend 覆盖 CUDA/ROCm/SYCL/Vulkan/Metal

```yaml
# gallery entry
- name: qwen3-tts-llamacpp-q4
  backend: vllm-cpp
```

### 3. KNN 路由 (v4.9+)
无分类器模型的相似度路由，基于标注 prompt 语料库：

```yaml
# 模型配置
classifier: knn
knn:
  similarity_threshold: 0.75
  corpus: /router-corpus/{name}.jsonl
```

```bash
# 管理 corpus（API only）
POST /api/router/{name}/corpus     # 添加标注样本
GET  /api/router/{name}/corpus/stats  # 只返回 label 统计
DELETE /api/router/{name}/corpus
```

### 4. Context Compression (v4.9+)
对话历史自动压缩，省 token：

```yaml
# 模型配置
compression:
  model: qwen3:4b    # 用于压缩的本地模型
  ratio: 0.4
```

保留：system prompt / 最新消息 / 完整 tool-call 单元。opt-in，关闭则无效。

### 5. 分布式集群 (v4.4+)
VRAM-aware 智能路由 + NATS 消息总线 + JWT 认证：

```yaml
# 前端配置
distributed:
  backend: nats
  url: nats://localhost:4222
```

关键路由策略：prefix-cache-aware / per-request replica routing / embedding 批处理自动扩缩。

### 6. 语音新引擎 (v4.7–v4.9)
- **moss-transcribe-cpp**: 单次联合多说话人转录+ diarization + 时间戳，CPU 1.6-2.2x 加速
- **F5-TTS in CrispASR**: 零样本声音克隆，22 层 DiT flow-matching
- **vibevoice-cpp**: True streaming TTS，首音延迟从 39.96s 降至 2.38s（~17x）
- **Qwen3-TTS on llama.cpp**: TTS 覆盖全加速矩阵（CUDA/ROCm/SYCL/Vulkan/Metal/L4T）
- **Managed Voice Clone**: UI 录制/上传参考音频，生成 `localai://voice-profiles/{id}` URI，12+ TTS backend 通用

### 7. 安全加固 (v4.9+)
**认证 deny-by-default**：所有 HTTP 路由默认需要凭证。

```yaml
# 显式公开路由
auth:
  public_routes:
    - /health
    - /version
    - /api/v1/models
```

迁移注意：启用 API key 后，`/version` 和生成的 audio/image/video URL 也需要凭证。

**PII 可逆假名化**：opt-in，`pii.reverse_in_response: true`，假名在响应中自动还原。

### 8. MiniMax-H3 视频生成 (v4.9+)
vllm-cpp 加载 H3 checkpoint set，联合渲染视频+音频（MP4 + AAC track）：

```yaml
# gallery entry
- name: minimax-h3-fl2va-q4
  backend: vllm-cpp
```

### 9. 3D 生成 (v4.8+)
`trellis2cpp` backend，image → GLB 模型：

```bash
curl -X POST http://localhost:8080/v1/3d/generations \
  -H "Content-Type: application/json" \
  -d '{"input": "data:image/jpeg;base64,..."}'
```

UI 内置 GLB 查看器，可旋转预览，支持打印级重网格化。

### 10. LongCat 视频 & Avatar (v4.7+)
- `longcat-video`: text-to-video / image-to-video
- `longcat-video-avatar-1.5`: 音频驱动 talking avatar

---

## 常用命令

```bash
# 安装（推荐）
curl http://localai.ai/install.sh | sh

# Docker
docker run -p 8080:8080 localai/localai:latest

# Homebrew (macOS)
brew install localai

# 启动
local-ai run qwen3.6:27b

# CLI Agent
local-ai chat --model qwen3.6:27b

# 启动 coding agent
local-ai launch claude-code --model qwen3.6:27b
local-ai launch opencode

# Gallery 安装（自动选最优量化）
local-ai models apply qwen3.6:27b

# 安装特定变体
local-ai models apply qwen3.6:27b --variant q4_K_M

# TTS
curl http://localhost:8080/v1/audio/speech \
  -d '{"model":"qwen3-tts","input":"Hello world"}'

# 语音转文字
curl http://localhost:8080/v1/audio/transcriptions \
  -F file=@audio.wav -F model=moss-transcribe-cpp-0.9b

# 上传声音克隆参考
curl -X POST http://localhost:8080/api/voice-profiles \
  -F "audio=@ref.wav" -F "name=my_voice"
```

---

## 模型选择指南 (2026)

| 场景 | 推荐模型 | VRAM | 说明 |
|------|---------|------|------|
| 通用本地主力 | Qwen3.6 27B | 24GB Q4 | 77.2% SWE-bench，256k context |
| 本地编码 | Qwen3.5-Coder 32B | 32GB Q4 | 最强开源本地编码模型 |
| 推理/R1 类 | DeepSeek-R1 32B | 24GB Q4 | 多步推理最优 |
| Apple Silicon | Qwen3.8 27B MLX | M4 Max | MLX 优化，~90% 加速 |
| 消费级推荐 | Qwen3.6 8B | 8GB Q4 | 日常可用 |
| 长上下文 | Llama 4 Scout | 10M context | 多模态 |
| 声音合成 | Qwen3-TTS | - | 通过 llama-cpp backend |
| 零样本声音克隆 | F5-TTS | - | CrispASR 集成 |

---

## 与 Ollama 对比

| 维度 | LocalAI | Ollama |
|------|---------|--------|
| 定位 | 全功能 AI 引擎（text/audio/video/3D） | 本地模型运行时 |
| 多模态 | 原生支持 TTS/ASR/Video/3D/Face/Voice | 有限 |
| Agent | nib 内嵌 + MCP Server | `ollama launch` 集成 Claude Code |
| 集群 | 原生分布式 + NATS | 第三方代理 |
| API 兼容 | OpenAI + Anthropic + Ollama | OpenAI + Anthropic |
| 路由 | KNN / 模型选择器 / 分布式感知 | 基础 |
| 安全 | deny-by-default auth | API key |
| 目标用户 | 需要 self-hosted 全栈 AI 平台 | 需要简单本地 LLM |

---

## 典型使用场景

1. **替代 OpenAI API**：完全本地运行，通过 OpenAI-compatible API 对接 LangChain/LlamaIndex
2. **自托管 TTS + ASR**：voice-detect.cpp / vibevoice-cpp / moss-transcribe-cpp 零云依赖
3. **分布式 GPU 集群**：VRAM-aware 路由，multi-node inference
4. **嵌入式 Agent**：`local-ai chat` 作为服务器端 AI assistant
5. **声音克隆**：UI 管理 voice profiles，跨 TTS backend 通用
6. **RAG + 路由**：KNN router 对接 local RAG pipeline

---

## 安全注意

- **v4.9 之前**：默认公开路由多（`/version`/`/models` 等），需升级或手动配置 `public_routes`
- **Fine-tuning inline code**：v4.8 修复任意代码执行漏洞，inline reward code 需显式开启 `LOCALAI_TRL_ALLOW_INLINE_REWARD=true`
- **分布式 NATS**：生产环境必须配置 TLS/mTLS + JWT 认证

---

## Links

- [LocalAI GitHub](https://github.com/mudler/LocalAI)
- [LocalAI Docs](https://localai.io/docs/)
- [vllm.cpp Engine](https://github.com/mudler/vllm.cpp)
- [Gallery](https://github.com/mudler/LocalAI/tree/master/gallery)
- [nib Agent](https://github.com/mudler/nib)
- [audio.cpp](https://github.com/0xShug0/audio.cpp)
- [LongCat Video](https://github.com/localai-org/longcat)
