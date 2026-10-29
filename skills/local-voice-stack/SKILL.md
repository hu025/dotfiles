---
name: local-voice-stack
description: 本地离线语音助手：Whisper(ASR)+Ollama(LLM)+Piper(TTS)+Wyoming协议，Home Assistant集成，零云依赖
---

# 本地离线语音助手：Whisper + Ollama + Piper

## 技术栈（五件套）

```
[唤醒词检测]
     ↓
[麦克风音频] → faster-whisper (STT/GPU或CPU)
     ↓
[ Wyoming Protocol ]
     ↓
[ Home Assistant Assist / Ollama ] (LLM意图理解)
     ↓
[ Piper TTS ] (文本→音频)
     ↓
[扬声器输出]
```

## 组件详解

### 1. 唤醒词（Wake Word）
- **OpenWakeWord**（MIT，开源，免费）：CPU运行，支持自定义唤醒词
  `pip install openwakeword`
- **Porcupine**（Picovoice）：个人使用免费，预制唤醒词

### 2. STT（语音→文字）
- **faster-whisper**（GPU加速）：`pip install faster-whisper`
  `faster-whisper-base` 或 `faster-whisper-large-v3`
- **Whisper**（原生）：`pip install openai-whisper`

### 3. Wyoming Protocol（粘合协议）
- 各种组件通过Wyoming协议互联
- 项目地址：https://github.com/rhasspy/wyoming

### 4. LLM（意图+回复）
- **Ollama**：`ollama serve` + `ollama run llama3.2`
- 模型选择：`llama3.2:3b`（轻量快速）或 `llama3.3:70b`（高质量）

### 5. TTS（文字→语音）

#### Piper（本地，免费，无API Key）
- 安装：`pip install piper-tts`
- 声音模型：`en_US-lessac-medium`（英文）
- ⚠️ Piper TTS 已于 2025年10月归档（rhasspy/piper），但仍可使用
- ⚠️ hermes-agent venv（`~/.hermes/hermes-agent/.venv/`）有磁盘配额，pip install 可能报 `OSError: 超出磁盘配额`，即使实际磁盘充足 → 改用 `~/.venvs/` 独立 venv 安装

#### Kokoro（2026 TTS Arena #1，推荐）
- 安装：`pip install kokoro-onnx`
- 模型：`hexgrad/Kokoro-82M`（需 HuggingFace 下载，国内可能网络不通）
- 推荐独立 venv：`uv venv ~/.venvs/kokoro --python 3.11 --seed`
- ⚠️ HuggingFace Hub 在国内可能无法连接（`httpcore.ConnectError: Network is unreachable`）

#### Chatterbox（语音克隆，MIT）
- 仓库：https://github.com/resemble-ai/chatterbox（26K⭐）
- ⚠️ 需 GPU 或较强 CPU

**模型矩阵（2026-09）：**

| 模型 | 参数量 | 语言 | 核心特性 | 最佳场景 |
|------|--------|------|----------|----------|
| Chatterbox-Multilingual V3 | 500M | 23+ | 说话人相似度↑、幻觉↓、PerTh水印、零样本克隆 | 跨语言语音克隆 |
| Chatterbox-Turbo | 350M | 英文 | 10步→1步解码、paralinguistic tags `[laugh]` | 低延迟英文代理 |
| Chatterbox-Nano | 110M | 英文 | CPU 3x实时（8核）、on-device | 内存/算力受限部署 |

**中文专属模型**：`ResembleAI/Chatterbox-Multilingual-zh-cmn`（Single Language Pack）。
LatAm Spanish / Brazilian Portuguese / Hindi 也有专属 pack。

**安装与使用：**
```bash
conda create -yn chatterbox python=3.11
conda activate chatterbox
git clone https://github.com/resemble-ai/chatterbox.git
cd chatterbox && pip install -e .
```
```python
from chatterbox import ChatterboxTTS
tts = ChatterboxTTS.from_pretrained("ResembleAI/chatterbox-turbo")
audio = tts.tts("Hello world", audio_prompt_path="reference.wav")
# 中文克隆需 5-20 秒参考音频
tts = ChatterboxTTS.from_pretrained("ResembleAI/Chatterbox-Multilingual-v3")
audio = tts.tts("你好世界", audio_prompt_path="zh_reference.wav")
```

**许可证（MIT）**：全系可商用，无需授权费/版税/收入分成；NVIDIA NIM 也可用于生产。
所有输出含 PerTh 水印（音频溯源，符合 EU AI Act）。

## Ollama 本地模型管理

```bash
ollama pull llama3.2:3b
ollama pull mistral-nemo   # 多语言
ollama list
ollama run llama3.2:3b "解释什么是ETF"
```

## 性能基准（2026）

| 组合 | 延迟 | GPU需求 |
|------|------|---------|
| Whisper-base + llama3.2:3b | ~2s | 可选 |
| faster-whisper-large + llama3.3:70b | ~5s | 推荐 |
| 全CPU（无GPU） | ~10s | 不需要 |

## TTS 方案对比（2026-09）

| 方案 | 参数量 | 许可证 | CPU性能 | 中文 | 备注 |
|------|--------|--------|--------|------|------|
| **Kokoro** | 82M | Apache-2.0 | 6x实时 | ✅ | TTS Arena #1，需HF下载 |
| **Piper** | - | - | 实时 | ⚠️ | 已归档，hermes venv安装受限 |
| **edge_tts** | - | 免费 | - | ✅ | **Hermes venv内置**，直接可用 |
| **espeak-ng** | - | GPL | - | ✅ | 系统已装，命令行工具，16kHz WAV |
| **Chatterbox** | 500M | MIT | 需GPU | ✅ | 语音克隆，需GPU |
| **XTTS v2** | ~2.1GB | 商用 | 需GPU | ✅ | 语音克隆，商用受限 |

## Hermes TTS 配置（关键）

Hermes `text_to_speech` 工具支持的 providers：

| Provider | API Key | 中文 | 备注 |
|----------|---------|------|------|
| edge | 无需 | ✅ | Hermes venv 内置，`zh-CN-XiaoxiaoNeural` |
| elevenlabs | 需要 | ✅ | 付费 |
| openai | 需要 | ✅ | 付费 |
| minimax | 需要 | ✅ | API Key 可能无效 |
| mistral | 需要 | ✅ | MISTRAL_API_KEY 未配置 |
| gemini | 需要 | ✅ | 免费额度 |
| xai | 需要 | ✅ | 付费 |
| neutts | 无需 | ❌ | 本地，免费，但 hermes venv 安装受限 |
| kittentts | 无需 | ❌ | 本地，25MB模型，hermes venv 安装受限 |
| piper | 无需 | ⚠️ | 本地，hermes venv 安装受限 |
| nous | 无需 | ✅ | Nous 订阅用户专用 |

### 当前 working 配置（2026-09-10）

```bash
# edge_tts 语音合成（Hermes venv 内置，直接可用）
~/.hermes/hermes-agent/.venv/bin/python -c "
import asyncio
from edge_tts import Communicate
async def gen():
    communicate = Communicate('中文文本', 'zh-CN-XiaoxiaoNeural')
    await communicate.save('/tmp/voice.mp3')
asyncio.run(gen())
"
```

```yaml
# ~/.hermes/config.yaml TTS 配置
tts:
  provider: edge
  edge:
    voice: zh-CN-XiaoxiaoNeural
```

### 修复记录（2026-09-10）

**问题**：edge TTS 报错 `No audio was received`，minimax API Key 无效，pip 安装 neutts/piper 报 `OSError: 超出磁盘配额`

**根因**：
1. Hermes Gateway 的 `tts.provider` 配置为 `espeak`（custom command 不被 v0.19.0 支持）
2. minimax API Key 已失效
3. hermes-agent venv 有配额限制（即使实际磁盘充足）

**修复**：
1. `hermes config set tts.provider edge`
2. `hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural`
3. 使用 hermes venv 内置的 `edge_tts`（无需 pip install）

**验证**：`text_to_speech` 工具成功发送中文语音至 QQ

## STT 新方案：Speech-to-Phrase
Home Assistant 2026 新增，比 Whisper 快 8 倍（<1秒 vs 8秒 on RPi4）。
适用场景：简单 home-control 命令（开灯、调温度）。
**注意**：约束性输出，不能转写任意语音。

## Gemma 4 Gotcha（坑点）
Gemma 4 默认强制输出 reasoning trace，导致 tool-call 结果落入 `reasoning_content` 而非 `content` 字段——Home Assistant 收不到 tool call。
**解决**：用 `qwen3:4b` 或 `llama3.2:3b` 替代。

## Home Assistant 2026.6 Wyoming 集成改进
无需编辑 YAML，UI 直接配置：
- Settings → Voice assistants → 新建 Assistant
- 选 Conversation agent / Speech to text / Text to speech
- `prefer_local_intents: true` 仍需在配置中设置

## 与现有系统整合

当前 `xiaozhi-esp32-server` 直连云端，本机只负责 USB 音频输入输出（ESP32 CH340 串口连接到 `/dev/ttyACM0`）。

若迁移到 PC 本地：
1. 停止 ESP32 端唤醒服务
2. 在 PC 部署完整 Wyoming 栈
3. 通过 mqtt 或 http 与 Home Assistant 互联
