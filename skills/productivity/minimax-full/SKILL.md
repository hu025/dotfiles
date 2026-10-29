---
name: minimax-full
description: MiniMax 全量能力（2026-09 实测）。触发词：MiniMax/图片生成/embeddings/function calling
version: 1.2.1
---

# MiniMax 全量能力（实测 2026-09）

## API 端点
- **Base**: `https://api.minimax.chat/v1`
- **Key**: `MINIMAX_API_KEY`（从 `~/.hermes/.env` 读取，格式 `sk-cp-...`）
- **关键发现**：`api.minimax.chat` 和 `api.minimax.io` 是两套**完全独立**的系统，key 不互通

## ✅ 已确认可用

### 1. 对话补全
- **可用模型**（`GET /v1/models` 实测 9 个）：
  `MiniMax-M3.1-Flash / MiniMax-M3 / MiniMax-M2.7 / MiniMax-M2.7-highspeed /
  MiniMax-M2.5 / MiniMax-M2.5-highspeed / MiniMax-M2.1 / MiniMax-M2.1-highspeed / MiniMax-M`
- `minimax-m3` 小写别名同样可用
- `M3.1-Flash` 实测更快（~2.1s vs M3 ~2.9s）且质量相当，适合轻量任务
- **端点必须用 `/v1/text/chatcompletion_v2`**

> ⚠️ **`/v1/chat/completions` 返回 401 `authorized_error`，即使 key 完全正确。**
> MiniMax 不是 OpenAI 兼容路径，用错端点时的报错完全具有误导性（看起来像key 无效）。
> `GET /v1/models` 返回 HTTP 200，但 chat 必须走 `chatcompletion_v2`。

### 2. 图片生成（image-01）
```bash
set -a
. ~/.hermes/.env
set +a
curl -s -X POST https://api.minimax.chat/v1/image_generation \
  -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"model":"image-01","prompt":"描述词",
       "aspect_ratio":"1:1","response_format":"url","n":1,"prompt_optimizer":true}' \
  -o /tmp/img_resp.json
```
- 返回 `{"data":{"image_urls":[...]}}`，`image_urls` 的 **i 是小写**。
- `aspect_ratio` 取值：`1:1` / `16:9` / `9:16` / `4:3` / `3:4`。
- `prompt_optimizer: true` 会自动扩写 prompt；风格要精确控制时关掉它。
- 出图存到 `~/.hermes/image_cache/<name>.jpg`（gateway 会从那里取图交付）。

#### 图片额度耗尽：`base_resp.status_code == 2056`

```
{"base_resp":{"status_code":2056,"status_msg":"已达到 Token Plan 用量上限：请升级 Token Plan 套餐或购买积分补充用量。"}}
```

- **HTTP 仍然是 200**，只有 `base_resp.status_code` 揭示失败 —— 和其它错误一样，
  只看 HTTP 状态码会把耗尽误判成成功。
- 响应体里 **`data` 字段整个缺失**（不是 `image_urls: []`）。所以
  `resp.json()["data"]["image_urls"][0]` 会抛 `TypeError: 'NoneType' object is
  not subscriptible` —— 那个异常是**症状不是原因**，真正的信息在
  `base_resp.status_msg` 里。看到 TypeError 就去读 `base_resp`。
- **额度会按周期刷新**（实测：耗尽后约半小时，同一请求再次调用即成功）。
  耗尽时不要宣布任务失败，也不要换 provider —— 告知用户稍后重试，或在等待期间
  先做其它工作。
- 每次生成消耗一张的额度，**连续生成 3-4 张容易撞线**。批量出图时先确认当前
  额度余量，并把 prompt 一次写准（多轮改 prompt = 多轮出图 = 多轮消耗）。

#### 读 env 里的 key：用 shell source，不要用 Python 读文件

`.env` 里的真实 key 是明文，但 **`terminal` 工具的输出会把 key 脱敏成 `***`**。
所以在 Python 里 `open('.env').read()` 拿到的也是脱敏串（长度从 125 变成 3），
用 `set -a; . ~/.hermes/.env; set +a` 再用 `${MINIMAX_API_KEY}` 在 shell 内部展开
才是真的可用 —— 关键是 key 从不经过工具输出：

```bash
set -a
. ~/.hermes/.env
set +a
curl -s -X POST https://api.minimax.chat/v1/image_generation \
  -H "Authorization: Bearer ${MINIMAX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d @/tmp/payload.json -o /tmp/resp.json -w 'HTTP:%{http_code}\n'
```

**不要**把 key 拼进 Python 字符串再 print 出去（会拿到 `***`），也**不要**把 key
写进日志可见的命令行。同理，验证 key 完整性时用长度判断（`${#MINIMAX_API_KEY}`
应为 125）而不是打印值。

#### 下载与验收

`image_urls` 返回的是带签名参数的 OSS 链接，**有有效期**（约 1 小时），拿到后
立即下载到本地再交付：

```bash
curl -sL '<image_url>' -o ~/.hermes/image_cache/<name>.jpg
file <path>   # 确认是 JPEG 且尺寸正确
```

生成后用 `vision_analyze` 确认画面符合预期再发给用户 —— 尤其是「按人设画头像」
这类主观任务，模型捏出来的东西经常和描述不符（发色、氛围、性别都可能偏）。

### 3. 图片理解（Vision，base64）
无需额外 API，直接在 chat 中传入图片。**`MiniMax-M3` 与 `MiniMax-M3.1-Flash` 实测均可读图**：
```python
{"model":"MiniMax-M3","messages":[{"role":"user","content":[
    {"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64}},
    {"type":"text","text":"描述这张图"}
]}]}
```
- ✅ 实测通过（端点同上，必须 `chatcompletion_v2`）
- 可直接用作 Hermes 的 `vision` / `vision_hq` tier

### 4. Function Calling / Tool Use
- ✅ 实测通过（支持单 tool_call 响应）
- ⚠️ 限制：单次响应最多 1 个 tool_call，**不支持 parallel tool_calls**
```python
{"model":"MiniMax-Text-01","messages":[...],"tools":[...]}
# 返回: message.tool_calls = [{"function":{"name":"...","arguments":"{}"}}]
```

### 5. Embeddings（embo-01）
- **维度**: 1536，**模型名**: `embo-01`
- 关键：字段名是 `texts`（数组，不是 `input`），必须加 `type`（`"db"` 或 `"query"`）
```python
requests.post(f"{base}/embeddings",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "embo-01", "texts": ["文本"], "type": "db"})
# 返回: {"vectors": [[...]], "base_resp": {"status_code": 0}}
```
- ❌ `embeddings-v2.5` / `embedding-01` 等名称均不兼容，只有 `embo-01` 可用
- **读取 env 里的 key**：用 `set -a; . ~/.hermes/.env; set +a` 在 shell 内部展开
  `${MINIMAX_API_KEY}`，**不要**在 Python 里读 `.env` 再用该值 —— `terminal` 工具的
  输出会把 key 脱敏成 `***`，读出来就是废串。详见上方「读 env 里的 key」一节。
- **curl 测试**：若 content-length=5 且返回空 content 是正常现象（M3 reasoning 模式），加大 max_tokens（≥200）即可

### 6. Streaming（SSE）
```python
r = requests.post(f"{base}/text/chatcompletion_v2",
    json={...,"stream":True}, stream=True)
for line in r.iter_lines():
    if line.startswith("data: "):
        chunk = json.loads(line[6:])
```
- ✅ 实测 4 个 chunk 完成

### 7. TTS（两条路都通，chat 域已实测）
**MiniMax 自有 TTS 在 `api.minimax.chat` 上可用**，`sk-cp-` 套餐 key 直接能调，无需独立 key：
```bash
curl -s -X POST "https://api.minimax.chat/v1/t2a_v2" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"speech-02-hd","text":"小月在测试语音。","stream":false,
       "voice_setting":{"voice_id":"female-shaonv","speed":1.0,"vol":1.0,"pitch":0,"emotion":"neutral"},
       "audio_setting":{"sample_rate":32000,"bitrate":128000}}'
```
- 响应体 `data.audio` 是 **hex 字符串**（非 base64），要 `bytes.fromhex()` 再写文件
- 实测 HTTP 200 + 64KB 音频，模型 `speech-02-hd`，voice_id `female-shaonv`
- ✅ `api.minimax.chat/v1/t2a_v2` 可用（当前套餐 key）
- ❌ `api.minimax.io/v1/t2a_v2` 需要独立 key，当前套餐返回 2049/401
- ⚠️ 同样只认 `base_resp.status_code == 0`，HTTP 200 不代表成功

**edge_tts 作为零依赖备选**（无需任何 key，hermes venv 内自带）：
```python
from edge_tts import Communicate
tts = Communicate(text, voice="zh-CN-XiaoxiaoNeural")
await tts.save("/tmp/output.mp3")
```
- edge_tts 必须用 hermes venv 的解释器：`~/.hermes/hermes-agent/.venv/bin/python`
  （系统 python 调它会 HTTP 400）
- Hermes `text_to_speech` 工具走 `tts.provider` 配置，两条路都可设为默认

### 8. ASR 语音识别
- 端点存在于 `api.minimax.io/v1/speech_to_text`，需要独立 key
- 当前套餐 key 在 `api.minimax.io` 下全部返回 401/2049 invalid key

## 关键发现：两套 API 系统

| 系统 | Base URL | key 格式 | 能力 |
|------|----------|----------|------|
| **Chat** | `api.minimax.chat` | `sk-cp-...` | 对话/图片生成/Vision/Function/Embeddings/**TTS** |
| **IO** | `api.minimax.io` | 独立 key | ASR/Hailuo视频（IO 侧 TTS 亦需独立 key） |

当前套餐 key 可在 Chat 系统内调用**对话/图片/Vision/Function/Embeddings/TTS** 全套；
IO 系统的 ASR/视频需单独申请 key。注意 TTS 在 Chat 侧也有实现（`/v1/t2a_v2`），
不要因为「IO 侧 TTS 要独立 key」就以为 Chat 侧 TTS 也不可用。

## 关键陷阱

- **端点路径**：`chat` 必须用 `/text/chatcompletion_v2`。用 OpenAI 风格的 `/chat/completions` 会得到 401 `authorized_error`，看起来像 key 无效但实际 key 是好的。
- **`base_resp.status_code` 才是真结果**：HTTP 200 不代表成功。响应体里 `base_resp.status_code` 为 0 才算成功；1004 = 鉴权失败。仅看 HTTP 状态码会误判。
- **M3 reasoning 特性**：M3 的 `reasoning_content` 字段在低 max_tokens（≤50）时会占满整个 context，导致 `content` 为空。这是模型行为，**不是错误**，加大 max_tokens（≥200，建议 2000）即可正常输出。
- **`hermes config set` 超时/错位**：`hermes config set` 不能可靠地编辑嵌套路径，可能静默创建新的顶层键。改配置请直接编辑 config.yaml 文本，详见 `autonomous-ai-agents/hermes-agent` 的「Editing config.yaml safely」。
- **`yaml.safe_dump` 会损坏 config 里的 key**：脱敏器会把 `api_key` 替换成占位符后写回，且 `safe_load` 读回来也是占位符。验证脚本要用正则读原文。

| 能力 | 状态 | 替代方案 |
|------|------|----------|
| 视频生成 | 超用量 | 无 |
| ASR 语音识别 | key 不匹配 | 无（IO 域需独立 key） |
| JSON Mode | 可用（提示词约束亦可）| 返回 ```json 围栏，需自行剥离 |
| Parallel tool_calls | 不支持 | 单 tool 分步调用 |
| Moderation | 需 GroupId | 需要正确 group_id 参数 |
| 文件上传 API | 需 batch 权限 | POST /files 返回 403 |

## Model List（实测）
```
MiniMax-M3.1-Flash / MiniMax-M3 / minimax-m3 / M2.7 / M2.7-highspeed
/ M2.5 / M2.5-highspeed / M2.1 / M2.1-highspeed / M2
```

## 快速调用模板
见 `references/quick-templates.md`

## 验证脚本
`scripts/verify_tiers.py` — 逐个调用 config.yaml 里每个 tier 模型并报告可用性。
改完配置必跑，它会同时绕开「端点路径」和「凭据脱敏」两个坑。
```bash
python3 scripts/verify_tiers.py --config ~/.hermes/config.yaml
```
全绿才算接线完成；只看 HTTP 200 不够，要看 `base_resp.status_code`。
