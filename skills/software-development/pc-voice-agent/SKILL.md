---
name: pc-voice-agent
description: Browser-based PC voice AI agent — zero-setup, no microphone required. Web Speech API (STT) + MiniMax M2.7 (LLM) + edge-tts (TTS), delivered as a single local HTML file.
triggers:
  - pc voice assistant
  - 电脑语音助手
  - browser voice AI
  - web speech API
  - 无麦克风 语音
  - voice agent PC
  - 语音对话 电脑
---

# PC Voice Agent（浏览器语音助手）

零安装、双击即用、无需物理麦克风的 PC 语音助手。

## 架构

```
┌─────────────────────┐     ┌─────────────┐     ┌──────────────────┐
│  浏览器（Web Speech  │ ──► │  MiniMax    │ ──► │  edge-tts        │
│  API 做语音识别)     │     │  M2.7 LLM   │     │  zh-CN-Xiaoxiao  │
│  双击 HTML 打开      │ ◄── │  (已有)     │ ◄── │  (已有)          │
└─────────────────────┘     └─────────────┘     └──────────────────┘
```

- **STT**：浏览器原生 Web Speech API（Chrome/Edge 内置，普通话识别率极高，零配置）
- **LLM**：MiniMax M2.7（已配置，via 始智AI Wisemodel）
- **TTS**：edge-tts（已装，中文女声 zh-CN-XiaoxiaoNeural）

## ⚠️ MiniMax STT 套餐限制

始智AI Wisemodel 套餐（¥49/月）**不支持** speech-01 / speech-01-hd 模型：

```
{"error":{"code":"model_not_allowed_by_wisemodel_package",
  "message":"您的 Wisemodel 资源包不支持模型 speech-01，
  请检查资源包的可用模型列表"}}
```

→ 不要尝试用 MiniMax API 做 STT，直接用浏览器 Web Speech API

## 文件：单一 HTML 文件

关键 API：

### Web Speech API（语音识别）
```javascript
// 创建识别对象
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'zh-CN';
recognition.continuous = false;
recognition.interimResults = true;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  // 发送到 MiniMax
};

recognition.onerror = (event) => {
  console.error('Speech recognition error:', event.error);
};

recognition.start();
```

### MiniMax LLM 调用
```javascript
// fetch 到本地 Hermes gateway
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    model: 'minimax-m2.5-highspeed',
    messages: [{ role: 'user', content: transcript }]
  })
});
const data = await response.json();
// data.choices[0].message.content
```

## VAD（语音活动检测）

Web Speech API 自动处理 VAD，无需自己实现。检测到静音自动触发 `onresult`。

## 开发步骤

1. 创建 `/home/saber/pc-voice-agent/index.html`
2. 实现 Web Speech API 录音 + MiniMax 对话 + edge-tts 播放
3. 双击浏览器打开即可使用

## 参考

- `references/browser-voice-api-notes.md` — Web Speech API 详解、已知坑、多浏览器兼容性
