---
name: speech-to-text-2026
description: 语音转文字 2026 全景：Whisper v4 / Distil-Whisper / Parakeet / Canary / GPT-4o-transcribe 选型对比。触发词：ASR/Whisper/语音转文字/Parakeet
---

# 语音转文字（ASR）2026 全景

## 2026 格局速览

Whisper（OpenAI, MIT）仍是最广泛使用的开源 ASR，支持 99+ 语言，但精度已非最高。

## 核心模型对比

| 模型 | 类型 | 精度 | 速度 | 语言 | 备注 |
|------|------|------|------|------|------|
| Whisper Large v3 | 开源 | ~5-8% WER | 基线 | 99+ | 生态最广，MIT |
| Distil-Whisper | 开源 | ≈ Large v3 | **6.3x faster** | 99+ | 幻觉更少，插入错误低 |
| NVIDIA Parakeet 1.1B | 开源 | **超越 Whisper** | RTFx>2000 | 英文优化 | Open ASR leaderboard 领先 |
| NVIDIA Canary-Qwen | 开源 | 超越 Whisper | 中等 | 多语言 | 多语言高精度 |
| Qwen3-ASR | 开源 | 超越 Whisper | 中等 | 多语言 | 阿里 |
| GPT-4o-transcribe | API | 超越所有开源 | 批量+流式 | 多语言 | OpenAI, $0.006/min |
| GPT-4o-mini-transcribe | API | 高 | **流式支持** | 多语言 | $0.003/min, streaming |
| ElevenLabs Scribe v2 | API | 高 | **150ms 延迟** | 多语言 | 实时场景 |
| Deepgram Nova-3 | API | 领先 | 流式延迟最低 | 多语言 | 低延迟场景 |

## Distil-Whisper 关键数据
- 精度: 1% 内 vs Whisper Large v3（短/长 form）
- 速度: 6.3x faster than Large v3
- 质量: 5-gram 重复减少 1.3x，插入错误率降低 2.1%
- 地址: huggingface.co/distil-whisper

## 本地部署推荐栈

```
faster-whisper (CTranslate2加速) + Distil-Whisper Large v3
  → ~6x 速度提升 + 更少幻觉 + 全本地 + MIT
```

## 社区生态
- **whisper.cpp**: CPU 高效推理（Apple Silicon 优化）
- **faster-whisper**: CTranslate2 加速，GPU 推荐
- **WhisperX**: whisper + word-level timestamps + speaker diarization
- **pyannote.audio**: 独立说话人分离（需单独集成）

## 选型决策树

```
场景?
├── 追求精度，预算充足 → GPT-4o-transcribe API
├── 本地部署，通用场景 → faster-whisper + Distil-Whisper Large v3
├── 英文专注，GPU 资源充足 → NVIDIA Parakeet 1.1B
├── 多语言高精度 → NVIDIA Canary-Qwen 或 Qwen3-ASR
└── 实时低延迟 → ElevenLabs Scribe v2 或 Deepgram Nova-3
```

## 与本地语音栈的关系

现有 `local-voice-stack` 技能使用 faster-whisper 作为 STT 引擎，建议：
- **升级路径**: Distil-Whisper Large v3 替换 Whisper Large v3（速度 6.3x）
- **幻觉缓解**: VAD 前处理 + Temperature=0
- **下一步**: 考虑 Parakeet（英文场景精度超越 Whisper）

## 来源
- Whisper: openai/whisper
- Distil-Whisper: huggingface.co/distil-whisper
- VBench 替代: https://whispernotes.app/blog/whisper-transcription
- ASR Leaderboard: huggingface.co/spaces/open-asr-leaderboard
- GPT-4o-transcribe: OpenAI API (Mar 2025)
