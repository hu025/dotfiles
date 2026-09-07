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
- **Piper**：`pip install piper-tts`
- 声音模型：`en_US-libritts-high`（英文）

## Home Assistant Assist 集成

```yaml
# configuration.yaml
conversation_engine: conversation.ollama_conversation
tts_engine: tts.piper
stt_engine: stt.faster_whisper_gpu
```

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

## 与现有系统整合

当前 `xiaozhi-esp32-server` 是专属语音服务，若迁移到PC本地：
1. 停止ESP32端唤醒服务
2. 在PC部署完整Wyoming栈
3. 通过mqtt或http与Home Assistant互联

## ⚠️ Piper 状态（重要更新）
**Piper TTS 已于 2025年10月归档**（rhasspy/piper），但仍可使用。
建议迁移到 **Kokoro TTS** 作为首选方案。

## TTS 方案对比（2026）

| 方案 | 参数量 | 许可证 | CPU性能 | 备注 |
|------|--------|--------|---------|------|
| **Kokoro** | 82M | Apache-2.0 | 6x实时 | TTS Arena #1，音质最佳 |
| Piper | - | - | 实时（RPi5） | 已归档，仍可用 |
| Chatterbox | - | MIT | 需GPU | 10秒音频克隆声音 |
| XTTS | - | 商用 | 需GPU | 语音克隆 |

**Kokoro 安装**：`pip install kokoro-onnx` 或通过 Home Assistant Wyoming 集成

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

## 下一步：集成到Hermes

Hermes已有TTS工具（text_to_speech），本地语音栈可以作为：
- 唤醒词触发器
- 本地STT替代云端MiniMax ASR
- 完全离线的对话模式
