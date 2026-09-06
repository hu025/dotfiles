# Browser Web Speech API 参考

## MiniMax Wisemodel 套餐不支持 STT（2026-08-01 确认）

套餐 ¥49/月仅包含 text/image 模型，speech-01 模型返回：

```
model_not_allowed_by_wisemodel_package
您的 Wisemodel 资源包不支持模型 speech-01，请检查资源包的可用模型列表
```

**解法**：用浏览器原生 Web Speech API 替代，零配置，中文识别极好。

---

## Web Speech API 详解

### 基础用法

```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = 'zh-CN';          // 普通话
recognition.continuous = false;       // 单次识别
recognition.interimResults = true;    // 返回临时结果
recognition.maxAlternatives = 1;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const confidence = event.results[0][0].confidence;
  console.log(`识别: ${transcript} (置信度: ${confidence})`);
};

recognition.onerror = (event) => {
  console.error('Error:', event.error); // no-speech / audio-capture / not-allowed 等
};

recognition.onend = () => {
  console.log('识别结束');
};

recognition.start();
```

### 关键属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `lang` | `'zh-CN'` | 普通话 |
| `continuous` | `false` | 单次，检测到静音自动结束 |
| `interimResults` | `true` | 显示实时临时结果 |
| `maxAlternatives` | `1` | 返回最多几个候选 |

### 事件

- `onstart` — 开始监听
- `onresult` — 返回结果（临时+最终）
- `onomresult` — 中间结果（已废弃，用 interimResults）
- `onerror` — 错误
- `onend` — 识别结束
- `onnomatch` — 无法识别

### 错误类型

| error | 含义 | 解法 |
|-------|------|------|
| `no-speech` | 没检测到语音 | 用户没说话或麦克风音量低 |
| `audio-capture` | 没找到麦克风 | 浏览器没权限或系统无输入设备 |
| `not-allowed` | 麦克风权限被拒 | 用户拒绝授权，需要 HTTPS 或 localhost |
| `network` | 网络错误 | 离线或 WebSocket 断连 |
| `aborted` | 被 `.abort()` 中断 | 正常中断，非错误 |

### 权限要求

- **桌面 Chrome/Edge**：localhost 或 HTTPS 自动允许
- **文件协议（file://）**：部分浏览器限制，需启动本地 HTTP 服务器

## 多浏览器兼容性

| 浏览器 | 支持 | 前缀 |
|--------|------|------|
| Chrome 25+ | ✅ | webkitSpeechRecognition |
| Edge 79+ | ✅ | SpeechRecognition |
| Firefox：暂不支持 | ❌ | — |
| Safari 14.1+ | ✅（macOS/iOS） | webkitSpeechRecognition |

推荐用 Chrome 或 Edge。

## 替代方案

### whisper 本地识别

```bash
# 安装（需要 ~3GB 磁盘空间 + Python 环境）
pip install openai-whisper
ffmpeg -f oss-card -i default -ar 16000 -ac 1 audio.wav

# 缺点：磁盘配额容易满（已遇到），模型下载慢
```

### PVDesktop（Picovoice）

```bash
pip install pvrecorder
# 轻量，支持多平台，但需要 Picovoice API key
```

## 本方案最佳路径

```
PC 无麦克风或磁盘满时：
→ 浏览器 Web Speech API
→ MiniMax M2.7（已有，Wisemodel API）
→ edge-tts（已有）
→ 单一 HTML 文件，无需安装
```
