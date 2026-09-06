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

## 下一步：集成到Hermes

Hermes已有TTS工具（text_to_speech），本地语音栈可以作为：
- 唤醒词触发器
- 本地STT替代云端MiniMax ASR
- 完全离线的对话模式
