---
name: minimax-platform-api
description: MiniMax platform API capabilities, endpoints, and integration patterns for Hermes Agent — text models, image generation, TTS, video, and music APIs
category: data-science
trigger: minimax api | minimax image generation | mini max 文生图 | minimax tts | minimax 语音 | minimax 套餐 | minimax 模型列表 | minimax image | minimax video | minimax music
---

# MiniMax Platform API Reference

## 确认已启用的 API

### 文生图（image-01）✅ 实测可用

**端点**: `POST https://api.minimaxi.com/v1/image_generation`

**认证**: `Authorization: Bearer {MINIMAX_API_KEY}`

**请求格式**:
```json
{
  "model": "image-01",
  "prompt": "英文或中文描述"
}
```

**响应格式**（实测修正 — URL 是字符串数组，不是对象数组）:
```json
{
  "id": "...",
  "data": {
    "image_urls": ["https://hailuo-image-algeng-data.oss-cn-*.aliyuncs.com/...?Signature=...&Expires=...&OSSAccessKeyId=..."]
  },
  "metadata": {"failed_count": "0", "success_count": "1"},
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```
⚠️ `image_urls` 数组内每个元素是**字符串**（直接是 URL），不是对象
- 错误解析: `first.get("url")` — 报错 `AttributeError: 'str' object has no attribute 'get'`
- 正确解析:
  ```python
  image_list = resp_data.get("image_urls") or []
  first = image_list[0]
  if isinstance(first, str):
      image_url = first
  else:
      image_url = first.get("url")
  ```
⚠️ 统一用 `api.minimaxi.com`，`api.minimax.io` 返回 404

**图片下载**: 返回的 OSS URL 需要用 `curl -L` 下载（跟随重定向），直接用 Python urllib 会 403。**签名有时效**（`Expires` 字段），生成后立即下载本地保存。

# MiniMax image-01 生成提示词参考

## 图像生成风格规则（2026-05-17 更新）
- **写实风格** → 东方美女：亚洲面孔、乌黑长发/黑长直/盘发、汉服或新中式服装
- **动漫风格** → 二次元美少女：吉卜力/动漫风格、大眼睛、精致比例、色彩明丽
- 墨琉写实：保持银白长发+金发饰+双蛇短杖人设不变，面孔改为东方美女
- 墨琉动漫：保持银白长发+金发饰+双蛇短杖人设不变，改为二次元美少女风格

## 写实风格·东方美女版墨琉（已验证，2026-05-17）
- API: `POST https://api.minimaxi.com/v1/image_generation`
- aspect_ratio: portrait（1024x1536）
```
photorealistic, elegant young East Asian woman with flowing silver-white long hair adorned with golden hairpins and delicate silver ribbons, half-up high ponytail with natural soft waves, striking pale grey eyes with subtle golden glint, porcelain fair skin, refined cold beauty with a faint mysterious smile, wearing a fitted silver and gold trimmed short Chinese-inspired combat outfit with intricate embroidery, holding a short ornate staff wrapped by twin coiled snakes, dramatic cinematic lighting, luxury fashion photography style, ultra detailed, 8k, masterpiece, full body portrait
```

## 动漫风格版墨琉（已验证，2026-05-17）
```
anime style, an elegant young woman with long flowing silver-white hair with golden hairpins and silver ribbon decorations, half-up high ponytail with soft waves, pale grey eyes with subtle golden glint, porcelain pale skin, sharp and cold beauty with a faint mysterious smile, wearing a fitted silver and gold trimmed short combat outfit with intricate patterns, holding a short magical staff wrapped by twin coiled snakes, standing in a mystical blue energy field with floating particles, dramatic cinematic lighting, anime illustration, highly detailed, vibrant colors, studio ghibli meets action anime style, 4k
```

## 下载与存储
```bash
curl -s -L -o ~/.hermes/assets/avatar_molu.png "https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/..."
```
- OSS URL 签名有时效（`Expires` 字段），生成后立即下载本地保存

**Hermes 集成状态**: ✅ 已配置 via `plugins/image_gen/minimax/__init__.py`

---

### 文本模型（当前在用）✅ 已配置

**模型列表**（`GET https://api.minimaxi.com/v1/models` 或 provider profile 源码）:

| 模型 ID | 说明 | 用途 |
|---------|------|------|
| `MiniMax-M2.7` | 旗舰推理（当前主模型） | 主用 |
| `MiniMax-M2.7-highspeed` | 低延迟版（同模型族） | 实时场景，可作 auxiliary 快速回退 |
| `MiniMax-M2.5` / `M2.5-highspeed` | 次强 | 备用 |
| `MiniMax-M2.1` / `M2.1-highspeed` | 中端 | 低成本 |
| `MiniMax-M2` | 基础版 | 测试 |

**当前配置**: `HERMES_MODEL: minimax/MiniMax-M2.7`
**API 端点**: `https://api.minimaxi.com/anthropic`（主）, `https://api.minimaxi.com/v1`（备）
**Provider**: `minimax`（global, `api.minimax.io`）或 `minimax-cn`（中国版, `api.minimaxi.com`）

**Provider Profile 源码**: `~/.hermes/hermes-agent/plugins/model-providers/minimax/__init__.py`

**关键发现**（2026-05-13）:
- M2.7 是**旗舰款**，非中低端 — 同一族还有 M2.7-highspeed（同模型低延迟变体）
- `minimax_oauth` provider 默认 auxiliary 模型是 `MiniMax-M2.7-highspeed`，说明高速版与标准版同属旗舰族
- `auxiliary.<task>.model` 为空时，所有辅助任务也走 M2.7

### 辅助任务模型（auxiliary.*）配置 ⚠️

### TTS（语音合成）✅ 实测可用

**端点**: `POST https://api.minimaxi.com/v1/t2a_v2`

**可用模型**: `speech-01`, `speech-01-hd`, `speech-02`, `speech-02-hd`

**请求格式**:
```json
{
  "model": "speech-01",
  "text": "文本内容",
  "stream": false
}
```

**已知问题**: MiniMax TTS API 报错 `code 2013: invalid params, empty field` — 确保 `model` 和 `text` 字段均非空

**本地替代**: `edge_tts`（已安装，工作正常）

---

### 辅助任务模型（auxiliary.*）配置 ⚠️

**关键发现**：`config.yaml` 里所有 `auxiliary.<task>.model` 均为空字符串（默认为 `""`），表示辅助任务也走 M2.7。经验证，M2.7 作为 auxiliary 视觉模型时，API 会忽略 base64 图片输入（静默丢弃），视觉任务自动回退到 `vision_analyze` 工具。

**建议配置**（`~/.hermes/config.yaml`）：
```yaml
agent:
  max_tokens: 8192          # 明确设置输出上限，减少截断风险
  image_input_mode: auto    # auto = 优先原生，fallback 到 vision_analyze
  max_turns: 90
  gateway_timeout: 1800
  api_max_retries: 3

display:
  show_reasoning: true       # 显示推理过程（debugging/development）
  show_cost: true            # 显示 token 消耗
  runtime_footer:
    enabled: true
    fields:
      - model
      - context_pct
      - cwd
```

### 输出截断问题（output new_sensitive 1027）

**错误信息**：
```
APIStatusError [HTTP 200]: output new_sensitive (1027)
⏱  Elapsed: 28.39s  Context: 95 msgs, ~73,477 tokens
```

**含义**：M2.7 模型输出内容触发了安全过滤（1027 = 内容安全/敏感词过滤），响应被截断。这不是 API 参数问题，是平台侧模型内置的输出过滤，无法通过配置绕过。

**缓解措施**：
- `max_tokens` 设置为 8192，上限内触发截断时给用户提示而非静默中断
- 减少触发敏感过滤的 prompt 内容模式
- 拆分为多轮对话

## 已启用但需套餐升级的 API

### 视频生成 ⚠️ 套餐限制
- **端点**: `POST https://api.minimaxi.com/v1/video_generation`
- **模型**: `video-01`
- **状态**: API 端点正常，返回 `{"error": "token plan not support model"}` — ¥49 Plus 套餐不支持，需 ¥119 Max 套餐
- **参考套餐**: ¥49/月 = 2个视频/日，¥119/月 = 更多额度

### 音乐生成 ✅ 实测可用（2026-05-15）
- **端点**: `POST https://api.minimaxi.com/v1/music_generation`
- **模型**: `music-2.6`
- **请求格式**:
  ```json
  {
    "model": "music-2.6",
    "prompt": "音乐风格描述",
    "lyrics": "歌词（可选）"
  }
  ```
- **响应格式**: `{"data": {"audio": "<hex encoded MP3>"}}` — 返回十六进制编码的 MP3 音频
- **Hermes 集成**: ✅ 已配置
  - 工具文件: `tools/music_generation_tool.py`
  - 后端: `plugins/music_gen/minimax/__init__.py`
  - toolset: `music`（已注册到 `toolsets.py`）
  - config: `music_gen.minimax`（`config.yaml`）
- **套餐**: ¥49/月 = 100首/天
- **Pitfall**: 生成耗时 ~30-60 秒，超时设置需 ≥120s

---

## WeChat 媒体发送故障排查

### `ret=-1` 故障（所有媒体类型）
- **含义**: iLink `getUploadUrl` 返回 `ret=-1`，CDN 上传完全失败
- **影响**: 图片、语音、文件**全部无法发送**
- **根因**: 微信服务器的 CDN 上传路径不可达（与回调地址问题同源）
- **状态**: ❌ 无解 — 需要公网回调地址

### `ret=-2` 故障（rate limited）
- **含义**: 消息发送频率超限
- **影响**: 文字消息暂时无法发送
- **处理**: 等待 30-60 秒自动恢复
- **状态**: ⚠️ 临时限流，可自愈

### `edge_tts` 正常但 `text_to_speech` 工具失败
- **原因**: 默认 provider（MiniMax）报错 2013
- **处理**: 用 `edge_tts` 本地生成 WAV/MP3 后手动上传

---

## Pitfalls

- ❌ MiniMax 文生图返回的 OSS URL **不能直接用 Python urllib 下载**（403），必须用 `curl -L`
- ✅ 文生图集成已完善（`plugins/image_gen/minimax/__init__.py`）
- ✅ 响应格式：image_urls 是 `List[str]`，不是 `List[dict]`，解析时需 `isinstance(first, str)` 判断
- ⚠️ MiniMax TTS API 需正确填 `model` 字段，空字段会报 2013
- ⚠️ WeChat 媒体上传 `ret=-1` 是服务端问题，本地无法解决
- ⚠️ MiniMax-M2.7 的文本 API **不支持图片输入**（base64 图像被静默丢弃），需使用浏览器视觉或专用视觉 API — 见 `references/minimax-api-vision.md`
- ⚠️ 音乐生成耗时 ~30-60 秒，API 超时设置需 ≥120s；响应是十六进制编码的 MP3，需 `bytes.fromhex()` 解码后再写文件

### MiniMax MCP Server (Token Plan) ⚠️

**Package**: `minimax-coding-plan-mcp` (NOT `minimax-mcp`)
**Run**: `uvx minimax-coding-plan-mcp`
**Entry**: `minimax_mcp.server:main`
**Tools**: `web_search`, `understand_image`

**Required env vars**:
- `MINIMAX_API_KEY` — Token Plan Key (different from standard API key)
- `MINIMAX_API_HOST=https://api.minimax.io`

**Hermes CLI add**:
```bash
hermes mcp add minimax-search \
  --command uvx \
  --args 'minimax-coding-plan-mcp' \
  --env 'MINIMAX_API_KEY=' \
  --env 'MINIMAX_API_HOST=https://api.minimax.io'
```

**⚠️ Critical**: Standard MiniMax API keys do NOT work — must be a Token Plan subscription key. Times out if the key lacks MCP permissions.

**Free alternatives for web_search + web_extract**:
- **Tavily** (recommended — 1000/month, no credit card): `app.tavily.com`, set `web.extract_backend: tavily` in config.yaml
- **MiniMax CLI** (`mmx-cli`): `platform.minimax.io/docs/token-plan/cli-guide`

> Full details: `references/minimax-mcp-investigation-2026-05-18.md`

---

## See Also

- `references/minimax-api-vision.md` — MiniMax API vision capability limits and workarounds
- `references/minimax-image-01-prompt.md` — image-01 prompt engineering reference
- `references/minimax-music-2-6.md` — music-2.6 integration details (API format, hex→MP3 decoding, test code)
- `references/minimax-mcp-investigation-2026-05-18.md` — MiniMax MCP server setup (Token Plan key, uvx, Tavily fallback)
